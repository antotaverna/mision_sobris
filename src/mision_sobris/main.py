import asyncio
import random
import sys
import time

import pygame

from mision_sobris import settings
from mision_sobris.entities import Chaser, Cookie, Player

# Running in the browser (built with pygbag), where there is no window to close.
WEB = sys.platform == "emscripten"

MODES = [
    ("Classic", "Eat cookies at your own pace. Burnt ones shrink you!"),
    ("Challenge", f"{settings.CHALLENGE_TIME} seconds. Avoid burnt cookies and the angry ones!"),
]

# Tappable areas, for touch screens and the mouse.
MODE_RECTS = [pygame.Rect(0, 0, 680, 80) for _ in MODES]
for i, rect in enumerate(MODE_RECTS):
    rect.center = (settings.WIDTH // 2, 262 + i * 100)
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

    def __init__(self, mode):
        self.mode = mode
        self.challenge = mode == "Challenge"
        self.player = Player(settings.WIDTH / 2, settings.HEIGHT / 2)
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
                self.result = "You got eaten!"

        if self.time_left is not None and not self.result:
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left == 0:
                self.result = "Time's up!"

    def draw(self, screen, fonts):
        screen.fill(settings.BG_COLOR)
        for cookie in self.cookies:
            cookie.draw(screen)
        self.player.draw(screen)
        for chaser in self.chasers:
            chaser.draw(screen)

        screen.blit(fonts["hud"].render(f"Cookies: {self.score}", True, settings.TEXT_COLOR), (16, 12))
        if self.time_left is not None:
            color = settings.HIGHLIGHT_COLOR if self.time_left < 5 else settings.TEXT_COLOR
            timer = fonts["hud"].render(f"Time: {self.time_left:4.1f}", True, color)
            screen.blit(timer, timer.get_rect(topright=(settings.WIDTH - 16, 12)))

        if self.result:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill(settings.OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            draw_centered(screen, fonts["title"], self.result, settings.HEIGHT / 2 - 80)
            draw_centered(screen, fonts["hud"], f"Cookies eaten: {self.score}", settings.HEIGHT / 2 - 10)
            draw_button(screen, fonts["hud"], PLAY_AGAIN_BUTTON, "Play again")
            draw_button(screen, fonts["hud"], BACK_BUTTON, "Menu")
            draw_centered(screen, fonts["small"], "Enter: play again    Esc: menu", settings.HEIGHT / 2 + 160)
        else:
            draw_button(screen, fonts["small"], MENU_BUTTON, "Menu")


def draw_centered(screen, font, text, y, color=settings.TEXT_COLOR):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(settings.WIDTH / 2, y)))


def draw_button(screen, font, rect, label):
    pygame.draw.rect(screen, settings.COOKIE_COLORS[1], rect, border_radius=12)
    pygame.draw.rect(screen, settings.TEXT_COLOR, rect, width=3, border_radius=12)
    text = font.render(label, True, settings.TEXT_COLOR)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_menu(screen, fonts, selected):
    screen.fill(settings.BG_COLOR)
    draw_centered(screen, fonts["title"], settings.TITLE, 110)
    for i, ((name, description), rect) in enumerate(zip(MODES, MODE_RECTS)):
        color = settings.HIGHLIGHT_COLOR if i == selected else settings.TEXT_COLOR
        pygame.draw.rect(screen, color, rect, width=3, border_radius=14)
        draw_centered(screen, fonts["hud"], f"{i + 1}. {name}", rect.centery - 16, color)
        draw_centered(screen, fonts["small"], description, rect.centery + 18)
    hint = "Tap a mode to play" if WEB else "Click a mode or use Up/Down + Enter    Esc: quit"
    draw_centered(screen, fonts["small"], hint, settings.HEIGHT - 40)
    if WEB:
        draw_centered(screen, fonts["small"], "Touch and hold to move the cookie", settings.HEIGHT - 70)


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

    selected = 0
    current = None  # the Round being played, or None while in the menu
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
            elif current is None:
                if event.key == pygame.K_ESCAPE and not WEB:
                    running = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MODES)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MODES)
                elif event.key in (pygame.K_1, pygame.K_2):
                    selected = event.key - pygame.K_1
                    current = Round(MODES[selected][0])
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    current = Round(MODES[selected][0])
            elif event.key == pygame.K_ESCAPE:
                current = None
            elif current.result and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                current = Round(current.mode)

        now = time.monotonic()
        if tap is not None and now - last_tap > TAP_COOLDOWN:
            last_tap = now
            if current is None:
                for i, rect in enumerate(MODE_RECTS):
                    if rect.collidepoint(tap):
                        selected = i
                        current = Round(MODES[i][0])
            elif current.result:
                if PLAY_AGAIN_BUTTON.collidepoint(tap):
                    current = Round(current.mode)
                elif BACK_BUTTON.collidepoint(tap):
                    current = None
            elif MENU_BUTTON.collidepoint(tap):
                current = None
                pointer = None

        if current is None:
            draw_menu(screen, fonts, selected)
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
