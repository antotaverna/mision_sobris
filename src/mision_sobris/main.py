import asyncio
import random
import sys
import time

import pygame

from mision_sobris import settings
from mision_sobris.collection import Collection
from mision_sobris.entities import Chaser, Cookie, Player
from mision_sobris.hidden import (DINOSAURS, RARE_DINOSAUR, REWARD_NAMES, SHORT_NAMES, HiddenDino,
                                  draw_argentine_medal, draw_banner, draw_fossil_card, draw_medal,
                                  draw_reward_icon, render_fit)

# Running in the browser (built with pygbag), where there is no window to close.
WEB = sys.platform == "emscripten"

# (key, title shown to players, description lines shown to players)
MODES = [
    ("classic", "Clásico", ("Comé galletitas a tu ritmo.", "¡Las quemadas te achican!")),
    ("challenge", "Desafío", (f"{settings.CHALLENGE_TIME} segundos.", "¡Esquivá las quemadas y las enojadas!")),
]

# Tappable areas, for touch screens and the mouse.
# Character cards in a 2x2 grid.
CHARACTER_RECTS = [pygame.Rect(0, 0, 230, 300) for _ in settings.CHARACTERS]
for i, rect in enumerate(CHARACTER_RECTS):
    rect.center = (settings.WIDTH // 2 + (i % 2 - 0.5) * 250, 410 + i // 2 * 320)
MODE_RECTS = [pygame.Rect(0, 0, settings.WIDTH - 60, 140) for _ in MODES]
for i, rect in enumerate(MODE_RECTS):
    rect.center = (settings.WIDTH // 2, 500 + i * 170)
# The secret player peeks out of the bottom-right corner of the character select.
SECRET_SPOT = pygame.Vector2(settings.WIDTH - 16, settings.HEIGHT - 10)
SECRET_RECT = pygame.Rect(settings.WIDTH - 70, settings.HEIGHT - 60, 70, 60)
CHANGE_CHARACTER_BUTTON = pygame.Rect(16, 16, 190, 44)
MENU_BUTTON = pygame.Rect(settings.WIDTH - 126, 12, 110, 40)
PLAY_AGAIN_BUTTON = pygame.Rect(0, 0, 220, 60)
PLAY_AGAIN_BUTTON.center = (settings.WIDTH // 2 - 120, settings.HEIGHT // 2 + 90)
BACK_BUTTON = pygame.Rect(0, 0, 220, 60)
BACK_BUTTON.center = (settings.WIDTH // 2 + 120, settings.HEIGHT // 2 + 90)
# Clearing a player's collection: a small button on their menu, then an "are you sure?" box.
RESET_BUTTON = pygame.Rect(settings.WIDTH - 196, 20, 180, 36)
RESET_DIALOG = pygame.Rect(0, 0, settings.WIDTH - 40, 260)
RESET_DIALOG.center = (settings.WIDTH // 2, settings.HEIGHT // 2)
RESET_YES_BUTTON = pygame.Rect(0, 0, 200, 56)
RESET_YES_BUTTON.center = (settings.WIDTH // 2 - 110, RESET_DIALOG.bottom - 55)
RESET_NO_BUTTON = pygame.Rect(0, 0, 200, 56)
RESET_NO_BUTTON.center = (settings.WIDTH // 2 + 110, RESET_DIALOG.bottom - 55)

# A touch can arrive both as a finger event and as an emulated mouse click;
# taps closer together than this are treated as one.
TAP_COOLDOWN = 0.25  # seconds


class Round:
    """One play-through of a mode, from start until time runs out or the player is caught."""

    def __init__(self, mode, character, collection):
        self.mode = mode
        self.character = character
        self.collection = collection
        self.challenge = mode == "challenge"
        self.player = Player(settings.WIDTH / 2, settings.PLAY_HEIGHT / 2, character)
        self.cookies = [self.new_cookie() for _ in range(settings.COOKIE_COUNT)]
        self.cookies += [self.new_cookie(burnt=True) for _ in range(settings.BURNT_COUNT)]
        self.score = 0
        self.result = None  # set to a message when the round ends
        if self.challenge:
            self.chasers = [Chaser(self.player.pos, speed) for speed in settings.CHASER_SPEEDS]
            self.time_left = settings.CHALLENGE_TIME
        else:
            self.chasers = []
            self.time_left = None
        # Classic mode hides things in the floor to find by walking over them; once both
        # are dug up, a new pair gets buried after a short pause.
        self.hidden = []
        self.rebury_timer = None
        self.announce_timer = 0.0
        if not self.challenge:
            self.bury_dinosaurs()

    def bury_dinosaurs(self):
        """Hide two different dinosaurs, the ones this player is missing first."""
        character = self.character
        have = self.collection.fossils(character["name"])
        if all(kind in have for kind in DINOSAURS):
            # Saves from before medals existed can hold a full collection; give its medal now.
            self.collection.complete(character["name"])
            have = []
        missing = [kind for kind in DINOSAURS if kind not in have]
        others = [kind for kind in DINOSAURS if kind in have]
        random.shuffle(missing)
        random.shuffle(others)
        species = (missing + others)[:2]
        # hard_finds characters can only dig each one up when the cookie is big or small.
        hard = character.get("hard_finds", False)
        needs = [random.choice(("big", "small")) if hard else None for _ in species]
        # An Argentinosaurus not dug up yet stays buried; otherwise one may turn up now and then.
        self.hidden = [find for find in self.hidden if find.rare and not find.found]
        for reward, kind, need in zip(("hat", "magnifier"), species, needs):
            avoid = [self.player.pos] + [find.pos for find in self.hidden]
            self.hidden.append(HiddenDino(avoid, reward, kind, hard, need))
        if not any(find.rare for find in self.hidden) and random.random() < settings.RARE_CHANCE:
            avoid = [self.player.pos] + [find.pos for find in self.hidden]
            # It's a giant, so players who need a size to dig always need to be big for it.
            self.hidden.append(HiddenDino(avoid, "argentine_medal", RARE_DINOSAUR, hard, "big" if hard else None))

    def give_reward(self, reward):
        """Dress the player up with what a hidden find gave, for the rest of the round."""
        character = self.player.character
        if reward == "hat":
            if character["accessory"] in settings.ACCESSORIES_KEPT_UNDER_HAT:
                character = {**character, "hat": "explorer_hat"}
            else:
                character = {**character, "accessory": "explorer_hat", "accent": settings.EXPLORER_HAT_COLOR}
        elif reward == "magnifier":
            character = {**character, "held": "magnifier"}
        self.player.character = character

    def new_cookie(self, burnt=False):
        return Cookie(self.player.pos, self.player.radius, burnt)

    def update(self, dt, pointer=None):
        if self.result:
            return
        self.player.update(dt, pointer)

        for cookie in self.cookies[:]:
            if self.player.pos.distance_to(cookie.pos) < self.player.radius:
                self.cookies.remove(cookie)
                self.cookies.append(self.new_cookie(cookie.burnt))
                self.player.eat(cookie)
                if not cookie.burnt:
                    self.score += 1

        for find in self.hidden:
            if not find.update(dt, self.player):
                continue
            name = self.character["name"]
            if find.rare:
                self.collection.add_rare(name)
                # Carry the flag for the rest of the round.
                self.player.character = {**self.player.character, "flag": True}
                find.note = "¡Un dinosaurio gigante de Argentina!"
                continue
            self.give_reward(find.reward)
            self.collection.add(name, "rewards", find.reward)
            if self.collection.add(name, "fossils", find.species):
                count = len(self.collection.fossils(name))
                if count == len(DINOSAURS):
                    self.collection.complete(name)
                    find.note = "¡Completaste la colección! Ganaste una medalla"
                else:
                    find.note = f"¡Nuevo en tu colección! ({count} de {len(DINOSAURS)})"

        self.announce_timer = max(0.0, self.announce_timer - dt)
        # A buried Argentinosaurus doesn't hold up the next pair; one being dug up does.
        if self.hidden and all(find.done() for find in self.hidden if not find.rare or find.found):
            if self.rebury_timer is None:
                self.rebury_timer = settings.REBURY_DELAY
            self.rebury_timer -= dt
            if self.rebury_timer <= 0:
                self.rebury_timer = None
                self.bury_dinosaurs()
                self.announce_timer = settings.HIDDEN_MESSAGE_TIME

        for chaser in self.chasers:
            chaser.update(dt, self.player.pos)
            if chaser.touches(self.player):
                self.result = "¡Te comieron!"

        if self.time_left is not None and not self.result:
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left == 0:
                self.result = "¡Se acabó el tiempo!"

    def draw(self, screen, fonts):
        screen.fill(settings.BG_COLOR)
        for find in self.hidden:
            find.draw(screen, self.player)
        for cookie in self.cookies:
            cookie.draw(screen)
        self.player.draw(screen)
        for chaser in self.chasers:
            chaser.draw(screen)
        for find in self.hidden:
            find.draw_effects(screen, fonts, self.player)
        if self.announce_timer > 0:
            draw_banner(screen, fonts, [("¡Hay más dinosaurios enterrados!", "hud", settings.TEXT_COLOR),
                                        ("Buscalos por toda la pantalla", "small", settings.TEXT_COLOR)])
        draw_progress_panel(screen, fonts, self.character, self.collection)

        # The score and timer sit on solid cards so cookies passing under them don't hide them.
        score = fonts["hud"].render(f"Galletitas: {self.score}", True, settings.TEXT_COLOR)
        cheer = fonts["small"].render(f"¡Vamos, {self.character['name']}!", True, settings.HIGHLIGHT_COLOR)
        draw_card(screen, pygame.Rect(6, 6, max(score.get_width(), cheer.get_width()) + 20, 72))
        screen.blit(score, (16, 12))
        screen.blit(cheer, (16, 48))
        if self.time_left is not None:
            color = settings.HIGHLIGHT_COLOR if self.time_left < 5 else settings.TEXT_COLOR
            timer = fonts["hud"].render(f"Tiempo: {self.time_left:4.1f}", True, color)
            timer_rect = timer.get_rect(topright=(settings.WIDTH - 16, MENU_BUTTON.bottom + 10))
            draw_card(screen, timer_rect.inflate(20, 12))
            screen.blit(timer, timer_rect)

        if self.result:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill(settings.OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            card = pygame.Rect(24, settings.HEIGHT / 2 - 150, settings.WIDTH - 48, 340 if not WEB else 290)
            draw_card(screen, card, settings.HIGHLIGHT_COLOR)
            result = render_fit(fonts, self.result, settings.WIDTH - 40, settings.TEXT_COLOR, ("title", "big"))
            screen.blit(result, result.get_rect(center=(settings.WIDTH / 2, settings.HEIGHT / 2 - 80)))
            draw_centered(screen, fonts["hud"], f"Galletitas comidas: {self.score}", settings.HEIGHT / 2 - 10)
            draw_button(screen, fonts["hud"], PLAY_AGAIN_BUTTON, "Otra vez")
            draw_button(screen, fonts["hud"], BACK_BUTTON, "Menú")
            if not WEB:
                draw_centered(screen, fonts["small"], "Enter: otra vez    Esc: menú", settings.HEIGHT / 2 + 160)
        else:
            draw_button(screen, fonts["small"], MENU_BUTTON, "Menú")


def draw_card(screen, rect, border=settings.TEXT_COLOR):
    """A solid rounded box to put text on."""
    pygame.draw.rect(screen, settings.CARD_COLOR, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, width=3, border_radius=14)


def draw_centered(screen, font, text, y, color=settings.TEXT_COLOR):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(settings.WIDTH / 2, y)))


def draw_button(screen, font, rect, label):
    pygame.draw.rect(screen, settings.COOKIE_COLORS[1], rect, border_radius=12)
    pygame.draw.rect(screen, settings.TEXT_COLOR, rect, width=3, border_radius=12)
    text = font.render(label, True, settings.TEXT_COLOR)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_character(screen, character, center, radius):
    """A still portrait of a character's cookie, looking straight ahead."""
    portrait = Player(*center, character)
    portrait.radius = radius
    portrait.facing = pygame.Vector2(0, 0)
    portrait.draw(screen)


def draw_progress_panel(screen, fonts, character, collection):
    """The bar along the bottom during a round: this player's fossils, prizes, and medals,
    and how the others are doing."""
    panel = pygame.Rect(0, settings.PLAY_HEIGHT, settings.WIDTH, settings.PANEL_HEIGHT)
    pygame.draw.rect(screen, settings.PANEL_COLOR, panel)
    pygame.draw.line(screen, settings.TEXT_COLOR, panel.topleft, panel.topright, 3)
    top = panel.top
    total = len(DINOSAURS)

    def text(message, font, center, color=settings.TEXT_COLOR):
        rendered = fonts[font].render(message, True, color)
        screen.blit(rendered, rendered.get_rect(center=center))

    # This player's fossils, across the top.
    name = character["name"]
    fossils = collection.fossils(name)
    missing = total - len(fossils)
    status = f"te faltan {missing}" if missing else "¡todos!"
    text(f"Fósiles de {name}: {len(fossils)} de {total} ({status})", "small", (panel.centerx, top + 20))
    for j, species in enumerate(DINOSAURS):
        spot = (panel.centerx + (j - 1.5) * 128, top + 62)
        draw_fossil_card(screen, spot, species, species in fossils, fonts["tiny"], scale=0.45)
        text(SHORT_NAMES.get(species, species) if species in fossils else "???", "tiny", (spot[0], top + 100))
    pygame.draw.line(screen, settings.TEXT_COLOR, (16, top + 118), (panel.right - 16, top + 118), 1)
    pygame.draw.line(screen, settings.TEXT_COLOR, (290, top + 128), (290, panel.bottom - 10), 1)

    # Prizes and medals, bottom left.
    rewards = collection.rewards(name)
    for j, reward in enumerate(REWARD_NAMES):
        draw_reward_icon(screen, (48 + j * 80, top + 158), reward, reward in rewards, fonts["tiny"])
    draw_medal(screen, (196, top + 152), 13)
    text(f"x{collection.medals(name)}", "small", (196, top + 186))
    # The Argentine medal stays faded until the first Argentinosaurus.
    rare = collection.rare(name)
    medal = pygame.Surface((40, 50), pygame.SRCALPHA)
    draw_argentine_medal(medal, (20, 32), 13)
    if not rare:
        medal.set_alpha(55)
    screen.blit(medal, medal.get_rect(center=(254, top + 150)))
    text(f"x{rare}", "small", (254, top + 186), settings.TEXT_COLOR if rare else (190, 170, 145))

    # Everyone else, bottom right.
    text("Los demás", "small", (415, top + 137))
    others = [other for other in settings.CHARACTERS if other["name"] != name]
    step = 22 if len(others) < 4 else 18
    for j, other in enumerate(others):
        y = top + (166 if len(others) < 4 else 159) + j * step
        draw_character(screen, other, (310, y), 9)
        label = fonts["tiny"].render(other["name"], True, settings.TEXT_COLOR)
        screen.blit(label, label.get_rect(midleft=(326, y)))
        count = fonts["tiny"].render(f"{len(collection.fossils(other['name']))}/{total}", True, settings.TEXT_COLOR)
        screen.blit(count, count.get_rect(midright=(466, y)))
        other_medals = collection.medals(other["name"])
        if other_medals:
            draw_medal(screen, (484, y + 2), 7)
            mark = fonts["tiny"].render(f"x{other_medals}", True, settings.TEXT_COLOR)
            screen.blit(mark, mark.get_rect(midleft=(494, y)))


def draw_character_select(screen, fonts, highlighted):
    screen.fill(settings.BG_COLOR)
    draw_centered(screen, fonts["title"], settings.TITLE, 110)
    draw_centered(screen, fonts["hud"], "Elegí tu galletita", 190)
    for i, (character, rect) in enumerate(zip(settings.CHARACTERS, CHARACTER_RECTS)):
        color = settings.HIGHLIGHT_COLOR if i == highlighted else settings.TEXT_COLOR
        pygame.draw.rect(screen, color, rect, width=3, border_radius=16)
        draw_character(screen, character, (rect.centerx, rect.top + 125), 65)
        name = fonts["hud"].render(character["name"], True, color)
        screen.blit(name, name.get_rect(center=(rect.centerx, rect.bottom - 40)))
    draw_character(screen, settings.SECRET_CHARACTER, SECRET_SPOT, 34)


def draw_mode_menu(screen, fonts, character, selected, confirm_reset):
    screen.fill(settings.BG_COLOR)
    draw_character(screen, character, (settings.WIDTH / 2, 205), 70)
    draw_centered(screen, fonts["title"], f"¡Hola, {character['name']}!", 350)
    for i, ((_, name, description), rect) in enumerate(zip(MODES, MODE_RECTS)):
        color = settings.HIGHLIGHT_COLOR if i == selected else settings.TEXT_COLOR
        pygame.draw.rect(screen, color, rect, width=3, border_radius=14)
        draw_centered(screen, fonts["hud"], f"{i + 1}. {name}", rect.top + 36, color)
        for j, line in enumerate(description):
            draw_centered(screen, fonts["small"], line, rect.top + 78 + j * 28)
    draw_button(screen, fonts["small"], CHANGE_CHARACTER_BUTTON, "Cambiar sobri")
    if WEB:
        draw_centered(screen, fonts["small"], "Mantené el dedo apretado", settings.HEIGHT - 78)
        draw_centered(screen, fonts["small"], "para mover la galletita", settings.HEIGHT - 50)
    else:
        draw_centered(screen, fonts["small"], "Clic en un modo o Arriba/Abajo + Enter", settings.HEIGHT - 64)
        draw_centered(screen, fonts["small"], "Esc: cambiar sobri", settings.HEIGHT - 36)

    if not confirm_reset:
        pygame.draw.rect(screen, (190, 170, 145), RESET_BUTTON, width=2, border_radius=10)
        label = fonts["tiny"].render("Borrar mi progreso", True, (165, 140, 110))
        screen.blit(label, label.get_rect(center=RESET_BUTTON.center))
        return
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    overlay.fill(settings.OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))
    pygame.draw.rect(screen, settings.CARD_COLOR, RESET_DIALOG, border_radius=18)
    pygame.draw.rect(screen, settings.HIGHLIGHT_COLOR, RESET_DIALOG, width=4, border_radius=18)
    draw_centered(screen, fonts["hud"], f"¿Borrar el progreso de {character['name']}?", RESET_DIALOG.top + 45)
    draw_centered(screen, fonts["small"], "Se borran sus fósiles, premios y medallas.", RESET_DIALOG.top + 88)
    draw_centered(screen, fonts["small"], "No se puede deshacer.", RESET_DIALOG.top + 116)
    draw_button(screen, fonts["hud"], RESET_YES_BUTTON, "Sí, borrar")
    draw_button(screen, fonts["hud"], RESET_NO_BUTTON, "No")


async def run():
    if WEB:
        # The browser build starts from the same random state on every page load,
        # which would put the cookies in the same places each time.
        random.seed(time.time_ns())
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()
    fonts = {
        "title": pygame.font.Font(None, 72),
        "hud": pygame.font.Font(None, 40),
        "small": pygame.font.Font(None, 28),
        "tiny": pygame.font.Font(None, 22),
        "big": pygame.font.Font(None, 56),
    }

    collection = Collection()
    confirm_reset = False  # asking whether to clear the chosen character's collection
    character = None  # the chosen character, or None while picking one
    highlighted = 0  # character highlighted with the keyboard
    selected = 0  # mode highlighted with the keyboard
    current = None  # the Round being played, or None while in a menu
    pointer = None  # where a finger or the mouse button is held down, if anywhere
    last_tap = 0.0

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000
        tap = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pointer input: fingers report positions as fractions of the screen.
            elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
                pointer = pygame.Vector2(event.x * settings.WIDTH, event.y * settings.HEIGHT)
                if event.type == pygame.FINGERDOWN:
                    tap = pointer
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pointer = tap = pygame.Vector2(event.pos)
            elif event.type == pygame.MOUSEMOTION and pointer is not None:
                pointer = pygame.Vector2(event.pos)
            elif event.type in (pygame.FINGERUP, pygame.MOUSEBUTTONUP):
                pointer = None

            elif event.type != pygame.KEYDOWN:
                continue
            elif confirm_reset:
                if event.key == pygame.K_ESCAPE:
                    confirm_reset = False
            elif character is None:
                count = len(settings.CHARACTERS)
                if event.key == pygame.K_ESCAPE and not WEB:
                    running = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    highlighted = (highlighted - 1) % count
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    highlighted = (highlighted + 1) % count
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    highlighted = (highlighted + 2) % count
                elif pygame.K_1 <= event.key < pygame.K_1 + count:
                    highlighted = event.key - pygame.K_1
                    character = settings.CHARACTERS[highlighted]
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    character = settings.CHARACTERS[highlighted]
                elif event.key == pygame.K_1 + count:
                    character = settings.SECRET_CHARACTER
            elif current is None:
                if event.key == pygame.K_ESCAPE:
                    character = None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MODES)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MODES)
                elif event.key in (pygame.K_1, pygame.K_2):
                    selected = event.key - pygame.K_1
                    current = Round(MODES[selected][0], character, collection)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    current = Round(MODES[selected][0], character, collection)
            elif event.key == pygame.K_ESCAPE:
                current = None
            elif current.result and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                current = Round(current.mode, character, collection)

        now = time.monotonic()
        if tap is not None and now - last_tap > TAP_COOLDOWN:
            last_tap = now
            if character is None:
                for i, rect in enumerate(CHARACTER_RECTS):
                    if rect.collidepoint(tap):
                        highlighted = i
                        character = settings.CHARACTERS[i]
                if SECRET_RECT.collidepoint(tap):
                    character = settings.SECRET_CHARACTER
            elif current is None and confirm_reset:
                if RESET_YES_BUTTON.collidepoint(tap):
                    collection.reset(character["name"])
                    confirm_reset = False
                elif RESET_NO_BUTTON.collidepoint(tap):
                    confirm_reset = False
            elif current is None and RESET_BUTTON.collidepoint(tap):
                confirm_reset = True
            elif current is None:
                if CHANGE_CHARACTER_BUTTON.collidepoint(tap):
                    character = None
                for i, rect in enumerate(MODE_RECTS):
                    if character and rect.collidepoint(tap):
                        selected = i
                        current = Round(MODES[i][0], character, collection)
            elif current.result:
                if PLAY_AGAIN_BUTTON.collidepoint(tap):
                    current = Round(current.mode, character, collection)
                elif BACK_BUTTON.collidepoint(tap):
                    current = None
            elif MENU_BUTTON.collidepoint(tap):
                current = None
                pointer = None

        if character is None:
            draw_character_select(screen, fonts, highlighted)
        elif current is None:
            draw_mode_menu(screen, fonts, character, selected, confirm_reset)
        else:
            current.update(dt, pointer)
            current.draw(screen, fonts)
        pygame.display.flip()
        # Hand control back to the browser each frame (no-op on desktop).
        await asyncio.sleep(0)

    pygame.quit()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
