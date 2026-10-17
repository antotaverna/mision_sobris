import math
import random

import pygame

from mision_sobris import settings


def random_chips(count):
    """Chip offsets, as fractions of the radius, scattered inside the cookie."""
    chips = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        chips.append(pygame.Vector2(math.cos(angle), math.sin(angle)) * random.uniform(0, 0.7))
    return chips


def rim_chips(count):
    """Chip offsets evenly spaced around the rim, leaving the middle free for a face."""
    return [
        pygame.Vector2(math.cos(a), math.sin(a)) * 0.72
        for a in (i * 2 * math.pi / count + 0.3 for i in range(count))
    ]


def draw_cookie(surface, center, radius, chips, colors=settings.COOKIE_COLORS):
    edge, dough, chip = colors
    pygame.draw.circle(surface, edge, center, radius)
    pygame.draw.circle(surface, dough, center, radius * 0.88)
    chip_radius = max(2, radius * 0.12)
    for offset in chips:
        pygame.draw.circle(surface, chip, center + offset * radius, chip_radius)


def draw_eyes(surface, center, radius, facing, angry=False):
    look = facing * radius * 0.15
    for s in (-1, 1):
        eye = center + pygame.Vector2(s * radius * 0.32, -radius * 0.22) + look
        pygame.draw.circle(surface, (255, 255, 255), eye, radius * 0.18)
        pygame.draw.circle(surface, (0, 0, 0), eye + facing * radius * 0.07, radius * 0.09)
        if angry:
            # Eyebrows slanting down toward the middle.
            outer = eye + pygame.Vector2(s * radius * 0.2, -radius * 0.28)
            inner = eye + pygame.Vector2(-s * radius * 0.12, -radius * 0.14)
            pygame.draw.line(surface, (40, 15, 5), outer, inner, max(2, round(radius * 0.09)))


def random_position(radius, avoid_pos, min_distance):
    """A random on-screen position at least min_distance away from avoid_pos."""
    margin = radius + 10
    for _ in range(100):
        pos = pygame.Vector2(
            random.uniform(margin, settings.WIDTH - margin),
            random.uniform(margin, settings.HEIGHT - margin),
        )
        if pos.distance_to(avoid_pos) > min_distance:
            break
    return pos


class Cookie:
    """A small cookie lying on the floor. Burnt ones shrink whoever eats them."""

    def __init__(self, avoid_pos, avoid_radius, burnt=False):
        self.radius = settings.COOKIE_RADIUS
        self.burnt = burnt
        self.chips = random_chips(3)
        self.pos = random_position(self.radius, avoid_pos, avoid_radius + self.radius + 40)

    def draw(self, surface):
        colors = settings.BURNT_COLORS if self.burnt else settings.COOKIE_COLORS
        draw_cookie(surface, self.pos, self.radius, self.chips, colors)


def draw_accessory(surface, center, radius, kind, color, facing):
    """Draw a character's accessory on a cookie of the given radius."""
    cx, cy = center
    r = radius
    side = 1 if facing.x >= 0 else -1
    look = facing * r * 0.15  # same offset draw_eyes uses
    if kind == "cat_ears":
        # A headband with two pointy cat ears, lighter inside.
        inner_color = tuple(round(c + (255 - c) * 0.55) for c in color)
        for center_angle in (125, 55):
            def ear_point(angle, distance):
                a = math.radians(angle)
                return (cx + math.cos(a) * r * distance, cy - math.sin(a) * r * distance)
            pygame.draw.polygon(surface, color, [ear_point(center_angle - 17, 0.9), ear_point(center_angle, 1.5),
                                                 ear_point(center_angle + 17, 0.9)])
            pygame.draw.polygon(surface, inner_color, [ear_point(center_angle - 9, 1.0), ear_point(center_angle, 1.33),
                                                       ear_point(center_angle + 9, 1.0)])
        band = pygame.Rect(0, 0, r * 2.0, r * 2.0)
        band.center = (cx, cy)
        pygame.draw.arc(surface, color, band, math.radians(25), math.radians(155), max(3, round(r * 0.12)))
    elif kind == "headphones":
        band = pygame.Rect(0, 0, r * 2.3, r * 2.2)
        band.center = (cx, cy + r * 0.05)
        pygame.draw.arc(surface, color, band, math.radians(20), math.radians(160), max(3, round(r * 0.14)))
        for s in (-1, 1):
            cup = pygame.Rect(0, 0, r * 0.38, r * 0.62)
            cup.center = (cx + s * r * 1.02, cy)
            pygame.draw.rect(surface, color, cup, border_radius=round(r * 0.15))
    elif kind == "crown":
        base_y, top_y, half = cy - r * 0.78, cy - r * 1.35, r * 0.55
        points = [(cx - half, base_y), (cx - half, top_y + r * 0.15), (cx - half * 0.5, base_y - r * 0.3),
                  (cx, top_y), (cx + half * 0.5, base_y - r * 0.3), (cx + half, top_y + r * 0.15),
                  (cx + half, base_y)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.circle(surface, (200, 30, 60), (cx, base_y - r * 0.14), r * 0.08)
    elif kind == "spider":
        # Spider-Man mask over the upper face: red with a web, big white lenses, mouth left free.
        size = math.ceil(r * 2)
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        hub = pygame.Vector2(size / 2, size / 2 + r * 0.05)
        pygame.draw.circle(mask, color, (size / 2, size / 2), r * 0.88)
        web = (25, 15, 15)
        thin = max(1, round(r * 0.035))
        spokes = [math.radians(a) for a in range(180, 361, 30)]
        for a in spokes:
            pygame.draw.line(mask, web, hub, hub + pygame.Vector2(math.cos(a), math.sin(a)) * r * 0.86, thin)
        for frac in (0.3, 0.55, 0.8):
            ring = [hub + pygame.Vector2(math.cos(a), math.sin(a)) * r * frac for a in spokes]
            pygame.draw.lines(mask, web, False, ring, thin)
        # Cut the mask off just under the eyes.
        mask.fill((0, 0, 0, 0), pygame.Rect(0, hub.y, size, size))
        surface.blit(mask, (cx - size / 2, cy - size / 2))
        for s in (-1, 1):
            eye = pygame.Vector2(cx + s * r * 0.32, cy - r * 0.22) + look
            lens = [eye + pygame.Vector2(s * dx, dy) * r
                    for dx, dy in ((-0.14, 0.02), (0.06, -0.16), (0.24, -0.12), (0.16, 0.1), (-0.04, 0.12))]
            pygame.draw.polygon(surface, (255, 255, 255), lens)
            pygame.draw.polygon(surface, (20, 20, 20), lens, max(2, round(r * 0.06)))


def draw_hair(surface, center, radius, kind, color):
    """Draw hair peeking out from behind the cookie."""
    r = radius
    shade = tuple(round(c * 0.75) for c in color)
    if kind == "curls":
        # Two ringlets hanging from the nape, a few twists each.
        for angle in (35, 145):
            a = math.radians(angle)
            top = pygame.Vector2(center) + pygame.Vector2(math.cos(a), math.sin(a)) * r * 0.9
            for i in range(3):
                size = r * (0.22 - i * 0.03)
                curl = top + pygame.Vector2(math.copysign(i * r * 0.05, math.cos(a)), i * r * 0.22)
                pygame.draw.circle(surface, color, curl, size)
                ring = pygame.Rect(0, 0, size * 1.2, size * 1.2)
                ring.center = curl
                pygame.draw.arc(surface, shade, ring, 0.5, 5.5, max(1, round(r * 0.05)))

        # A short curl on each side, just above each ringlet.
        for angle in (18, 162):
            a = math.radians(angle)
            curl = pygame.Vector2(center) + pygame.Vector2(math.cos(a), math.sin(a)) * r * 0.9
            pygame.draw.circle(surface, color, curl, r * 0.2)
            ring = pygame.Rect(0, 0, r * 0.24, r * 0.24)
            ring.center = curl
            pygame.draw.arc(surface, shade, ring, 0.5, 5.5, max(1, round(r * 0.05)))


def draw_ride(surface, center, radius, kind):
    """Draw what a character rides on, sitting under the cookie."""
    cx, cy = center
    r = radius
    if kind == "skateboard":
        deck = pygame.Rect(0, 0, r * 1.7, r * 0.2)
        deck.midtop = (cx, cy + r * 0.86)
        pygame.draw.rect(surface, (40, 170, 170), deck, border_radius=round(r * 0.1))
        pygame.draw.line(surface, (240, 90, 150), (deck.left + r * 0.2, deck.centery),
                         (deck.right - r * 0.2, deck.centery), max(2, round(r * 0.06)))
        for s in (-1, 1):
            wheel = (cx + s * r * 0.55, deck.bottom + r * 0.1)
            pygame.draw.circle(surface, (60, 60, 60), wheel, r * 0.14)
            pygame.draw.circle(surface, (235, 235, 235), wheel, r * 0.07)


class Player:
    def __init__(self, x, y, character=None):
        self.character = character
        self.pos = pygame.Vector2(x, y)
        self.radius = settings.PLAYER_RADIUS
        self.chips = rim_chips(7)
        self.facing = pygame.Vector2(1, 0)
        self.chomp_timer = 0.0
        self.yuck_timer = 0.0

    def update(self, dt, target=None):
        """Move with the keyboard, or toward target (a finger or mouse held down) if given."""
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        step = settings.PLAYER_SPEED * dt
        if direction.length_squared() == 0 and target is not None:
            to_target = target - self.pos
            if to_target.length() > 4:
                direction = to_target
                # Stop on the finger instead of jittering past it.
                step = min(step, to_target.length())
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.facing = direction
        self.pos += direction * step
        self.pos.x = max(self.radius, min(settings.WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(settings.HEIGHT - self.radius, self.pos.y))
        self.chomp_timer = max(0.0, self.chomp_timer - dt)
        self.yuck_timer = max(0.0, self.yuck_timer - dt)

    def eat(self, cookie):
        if cookie.burnt:
            self.radius = max(settings.PLAYER_MIN_RADIUS, self.radius - settings.BURNT_SHRINK)
            self.yuck_timer = 0.4
        else:
            self.radius = min(settings.PLAYER_MAX_RADIUS, self.radius + settings.PLAYER_GROWTH)
            self.chomp_timer = 0.15

    def draw(self, surface):
        r = self.radius
        colors = self.character["colors"] if self.character else settings.COOKIE_COLORS
        if self.character and "hair" in self.character:
            draw_hair(surface, self.pos, r, self.character["hair"], self.character["hair_color"])
        draw_cookie(surface, self.pos, r, self.chips, colors)
        draw_eyes(surface, self.pos, r, self.facing)

        mouth_center = self.pos + pygame.Vector2(0, r * 0.32) + self.facing * r * 0.15
        mouth_color = (80, 20, 20)
        width = max(3, round(r * 0.11))
        if self.yuck_timer > 0:
            # Disgusted wavy mouth after eating a burnt cookie.
            points = [mouth_center + pygame.Vector2((i - 2) * r * 0.12, (-1) ** i * r * 0.05) for i in range(5)]
            pygame.draw.lines(surface, mouth_color, False, points, width)
        elif self.chomp_timer > 0:
            pygame.draw.circle(surface, mouth_color, mouth_center, r * 0.3)
        else:
            smile = pygame.Rect(0, 0, r * 0.7, r * 0.45)
            smile.center = (round(mouth_center.x), round(mouth_center.y - r * 0.12))
            pygame.draw.arc(surface, mouth_color, smile, math.pi * 1.1, math.pi * 1.9, width)

        if self.character:
            draw_accessory(surface, self.pos, r, self.character["accessory"], self.character["accent"], self.facing)
            if "ride" in self.character:
                draw_ride(surface, self.pos, r, self.character["ride"])


class Chaser:
    """A big angry cookie that walks toward the player."""

    def __init__(self, avoid_pos, speed):
        self.radius = settings.CHASER_RADIUS
        self.speed = speed
        self.chips = rim_chips(8)
        self.pos = random_position(self.radius, avoid_pos, settings.CHASER_SPAWN_DISTANCE)
        self.facing = pygame.Vector2(1, 0)

    def update(self, dt, target):
        to_target = target - self.pos
        if to_target.length_squared() > 0:
            self.facing = to_target.normalize()
            self.pos += self.facing * self.speed * dt

    def touches(self, player):
        # A little forgiveness so grazing the edge doesn't count.
        return self.pos.distance_to(player.pos) < (self.radius + player.radius) * 0.8

    def draw(self, surface):
        r = self.radius
        draw_cookie(surface, self.pos, r, self.chips, settings.CHASER_COLORS)
        draw_eyes(surface, self.pos, r, self.facing, angry=True)
        # Toothy open mouth.
        mouth = pygame.Rect(0, 0, r * 0.7, r * 0.32)
        mouth.center = self.pos + pygame.Vector2(0, r * 0.35) + self.facing * r * 0.15
        pygame.draw.rect(surface, (60, 10, 10), mouth, border_radius=round(r * 0.1))
        for i in range(3):
            tooth = pygame.Rect(0, 0, r * 0.13, r * 0.12)
            tooth.midtop = (mouth.left + mouth.width * (i + 1) / 4, mouth.top)
            pygame.draw.rect(surface, (255, 255, 255), tooth)
