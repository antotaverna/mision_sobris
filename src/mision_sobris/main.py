import asyncio
import random
import sys
import time

import pygame

from mision_sobris import settings
from mision_sobris.entities import Chaser, Cookie, Player

# Running in the browser (built with pygbag), where there is no window to close.
WEB = sys.platform == "emscripten"

# (key, title shown to players, description shown to players)
MODES = [
    ("classic", "Clásico", "Comé galletitas a tu ritmo. ¡Las quemadas te achican!"),
    ("challenge", "Desafío", f"{settings.CHALLENGE_TIME} segundos. ¡Esquivá las quemadas y las enojadas!"),
]

# Tappable areas, for touch screens and the mouse.
CHARACTER_RECTS = [pygame.Rect(0, 0, 200, 250) for _ in settings.CHARACTERS]
for i, rect in enumerate(CHARACTER_RECTS):
    rect.center = (settings.WIDTH // 2 + (i - (len(CHARACTER_RECTS) - 1) / 2) * 225, 300)
MODE_RECTS = [pygame.Rect(0, 0, 680, 80) for _ in MODES]
for i, rect in enumerate(MODE_RECTS):
    rect.center = (settings.WIDTH // 2, 262 + i * 100)
CHANGE_CHARACTER_BUTTON = pygame.Rect(16, 16, 190, 44)
MENU_BUTTON = pygame.Rect(0, 0, 110, 40)
MENU_BUTTON.midtop = (settings.WIDTH // 2, 10)
PLAY_AGAIN_BUTTON = pygame.Rect(0, 0, 220, 60)
PLAY_AGAIN_BUTTON.center = (settings.WIDTH // 2 - 130, settings.HEIGHT // 2 + 90)
BACK_BUTTON = pygame.Rect(0, 0, 220, 60)
BACK_BUTTON.center = (settings.WIDTH // 2 + 130, settings.HEIGHT // 2 + 90)

# A touch can arrive both as a finger event and as an emulated mouse click;
# taps closer together than this are treated as one.
TAP_COOLDOWN = 0.25  # seconds


class Round:
    """One play-through of a mode, from start until time runs out or the player is caught."""

    def __init__(self, mode, character):
        self.mode = mode
        self.character = character
        self.challenge = mode == "challenge"
        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2, character)
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
        for cookie in self.cookies:
            cookie.draw(screen)
        self.player.draw(screen)
        for chaser in self.chasers:
            chaser.draw(screen)

        screen.blit(fonts["hud"].render(f"Galletitas: {self.score}", True, settings.TEXT_COLOR), (16, 12))
        cheer = fonts["small"].render(f"¡Vamos, {self.character['name']}!", True, settings.HIGHLIGHT_COLOR)
        screen.blit(cheer, (16, 48))
        if self.time_left is not None:
            color = settings.HIGHLIGHT_COLOR if self.time_left < 5 else settings.TEXT_COLOR
            timer = fonts["hud"].render(f"Tiempo: {self.time_left:4.1f}", True, color)
            screen.blit(timer, timer.get_rect(topright=(settings.WIDTH - 16, 12)))

        if self.result:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill(settings.OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            draw_centered(screen, fonts["title"], self.result, settings.HEIGHT / 2 - 80)
            draw_centered(screen, fonts["hud"], f"Galletitas comidas: {self.score}", settings.HEIGHT / 2 - 10)
            draw_button(screen, fonts["hud"], PLAY_AGAIN_BUTTON, "Otra vez")
            draw_button(screen, fonts["hud"], BACK_BUTTON, "Menú")
            if not WEB:
                draw_centered(screen, fonts["small"], "Enter: otra vez    Esc: menú", settings.HEIGHT / 2 + 160)
        else:
            draw_button(screen, fonts["small"], MENU_BUTTON, "Menú")


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


def draw_character_select(screen, fonts, highlighted):
    screen.fill(settings.BG_COLOR)
    draw_centered(screen, fonts["title"], settings.TITLE, 70)
    draw_centered(screen, fonts["hud"], "¿Quién sos?", 135)
    for i, (character, rect) in enumerate(zip(settings.CHARACTERS, CHARACTER_RECTS)):
        color = settings.HIGHLIGHT_COLOR if i == highlighted else settings.TEXT_COLOR
        pygame.draw.rect(screen, color, rect, width=3, border_radius=16)
        draw_character(screen, character, (rect.centerx, rect.top + 105), 55)
        name = fonts["hud"].render(character["name"], True, color)
        screen.blit(name, name.get_rect(center=(rect.centerx, rect.bottom - 35)))
    hint = "Tocá tu galletita" if WEB else "Hacé clic en tu galletita o usá Izq/Der + Enter    Esc: salir"
    draw_centered(screen, fonts["small"], hint, settings.HEIGHT - 40)


def draw_mode_menu(screen, fonts, character, selected):
    screen.fill(settings.BG_COLOR)
    greeting = fonts["title"].render(f"¡Hola, {character['name']}!", True, settings.TEXT_COLOR)
    greeting_rect = greeting.get_rect(center=(settings.WIDTH / 2 + 40, 140))
    screen.blit(greeting, greeting_rect)
    draw_character(screen, character, (greeting_rect.left - 60, greeting_rect.centery), 40)
    for i, ((_, name, description), rect) in enumerate(zip(MODES, MODE_RECTS)):
        color = settings.HIGHLIGHT_COLOR if i == selected else settings.TEXT_COLOR
        pygame.draw.rect(screen, color, rect, width=3, border_radius=14)
        draw_centered(screen, fonts["hud"], f"{i + 1}. {name}", rect.centery - 16, color)
        draw_centered(screen, fonts["small"], description, rect.centery + 18)
    draw_button(screen, fonts["small"], CHANGE_CHARACTER_BUTTON, "Cambiar sobri")
    if WEB:
        draw_centered(screen, fonts["small"], "Mantené el dedo apretado para mover la galletita", settings.HEIGHT - 70)
        draw_centered(screen, fonts["small"], "Tocá un modo para jugar", settings.HEIGHT - 40)
    else:
        draw_centered(screen, fonts["small"], "Hacé clic en un modo o usá Arriba/Abajo + Enter    Esc: cambiar sobri",
                      settings.HEIGHT - 40)


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
    }

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
            elif character is None:
                count = len(settings.CHARACTERS)
                if event.key == pygame.K_ESCAPE and not WEB:
                    running = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    highlighted = (highlighted - 1) % count
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    highlighted = (highlighted + 1) % count
                elif pygame.K_1 <= event.key < pygame.K_1 + count:
                    highlighted = event.key - pygame.K_1
                    character = settings.CHARACTERS[highlighted]
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    character = settings.CHARACTERS[highlighted]
            elif current is None:
                if event.key == pygame.K_ESCAPE:
                    character = None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MODES)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MODES)
                elif event.key in (pygame.K_1, pygame.K_2):
                    selected = event.key - pygame.K_1
                    current = Round(MODES[selected][0], character)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    current = Round(MODES[selected][0], character)
            elif event.key == pygame.K_ESCAPE:
                current = None
            elif current.result and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                current = Round(current.mode, character)

        now = time.monotonic()
        if tap is not None and now - last_tap > TAP_COOLDOWN:
            last_tap = now
            if character is None:
                for i, rect in enumerate(CHARACTER_RECTS):
                    if rect.collidepoint(tap):
                        highlighted = i
                        character = settings.CHARACTERS[i]
            elif current is None:
                if CHANGE_CHARACTER_BUTTON.collidepoint(tap):
                    character = None
                for i, rect in enumerate(MODE_RECTS):
                    if character and rect.collidepoint(tap):
                        selected = i
                        current = Round(MODES[i][0], character)
            elif current.result:
                if PLAY_AGAIN_BUTTON.collidepoint(tap):
                    current = Round(current.mode, character)
                elif BACK_BUTTON.collidepoint(tap):
                    current = None
            elif MENU_BUTTON.collidepoint(tap):
                current = None
                pointer = None

        if character is None:
            draw_character_select(screen, fonts, highlighted)
        elif current is None:
            draw_mode_menu(screen, fonts, character, selected)
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
