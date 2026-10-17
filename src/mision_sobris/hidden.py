"""Things hidden in the floor in Classic mode, found by walking over them."""

import math
import random

import pygame

from mision_sobris import settings
from mision_sobris.entities import draw_accessory, draw_held

DIRT_COLOR = (150, 105, 60)
DIRT_DARK = (115, 75, 40)
BONE_COLOR = (245, 238, 215)
BONE_SHADOW = (190, 175, 145)


def along(points, count):
    """count points evenly spaced along the polyline through points."""
    points = [pygame.Vector2(p) for p in points]
    lengths = [a.distance_to(b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    result = []
    for i in range(count):
        target = total * i / (count - 1)
        for a, b, length in zip(points, points[1:], lengths):
            if target <= length or b is points[-1]:
                result.append(a.lerp(b, min(1.0, target / length)))
                break
            target -= length
    return result


def bone(surface, a, b, width=4):
    pygame.draw.line(surface, BONE_COLOR, a, b, width)
    for end in (a, b):
        pygame.draw.circle(surface, BONE_COLOR, end, width * 0.6)


def vertebrae(surface, spine, start_size, end_size):
    for i, point in enumerate(spine):
        pygame.draw.circle(surface, BONE_COLOR, point, start_size + (end_size - start_size) * i / (len(spine) - 1))


def ribs(surface, spine, length):
    for point in spine:
        bone(surface, point, point + pygame.Vector2(-3, length), 3)


def leg(surface, hip, knee, foot, toe_length=7, width=4):
    bone(surface, hip, knee, width)
    bone(surface, knee, foot, width)
    bone(surface, foot, foot + pygame.Vector2(-toe_length, 0), width - 1)


def skull(surface, center, size, eye_offset):
    head = pygame.Rect(0, 0, *size)
    head.center = center
    pygame.draw.ellipse(surface, BONE_COLOR, head)
    pygame.draw.circle(surface, DIRT_DARK, pygame.Vector2(center) + eye_offset, max(2, size[1] * 0.15))
    return head


def horn(surface, base, tip, width):
    """A tapering horn or spike from base to tip."""
    base, tip = pygame.Vector2(base), pygame.Vector2(tip)
    side = (tip - base).rotate(90).normalize() * width / 2
    pygame.draw.polygon(surface, BONE_COLOR, [base + side, tip, base - side])


def draw_trex(surface, c):
    spine = along([c + (-36, -20), c + (-18, -12), c + (12, -8), c + (40, -2), c + (62, 6), c + (80, 12)], 16)
    ribs(surface, spine[2:7], 16)
    leg(surface, c + (12, -6), c + (18, 14), c + (10, 32), 9, 5)
    leg(surface, c + (6, -6), c + (10, 14), c + (2, 32), 9, 5)
    bone(surface, c + (-22, -8), c + (-28, 0), 2)  # the tiny arms
    bone(surface, c + (-28, 0), c + (-33, -1), 2)
    vertebrae(surface, spine, 6, 2.5)
    head = skull(surface, c + (-56, -26), (38, 22), (6, -3))
    jaw = pygame.Rect(0, 0, 30, 8)
    jaw.topright = (head.right - 6, head.bottom - 3)
    pygame.draw.rect(surface, BONE_SHADOW, jaw, border_radius=3)
    for i in range(4):
        tooth = pygame.Vector2(jaw.left + 2 + i * 7, jaw.top)
        pygame.draw.polygon(surface, BONE_COLOR, [tooth, tooth + (5, 0), tooth + (2.5, 6)])


def draw_triceratops(surface, c):
    spine = along([c + (-30, -8), c + (-5, -14), c + (22, -12), c + (45, -4), c + (62, 2), c + (74, 8)], 14)
    ribs(surface, spine[1:7], 14)
    for x in (-22, -14, 16, 24):
        leg(surface, c + (x, -8), c + (x + 2, 12), c + (x, 30), 6, 5)
    vertebrae(surface, spine, 6, 2.5)
    frill = c + pygame.Vector2(-36, -10)
    pygame.draw.circle(surface, BONE_SHADOW, frill, 19)
    pygame.draw.circle(surface, BONE_COLOR, frill, 19, 4)
    skull(surface, c + (-52, -2), (32, 20), (2, -3))
    horn(surface, c + (-50, -10), c + (-72, -26), 6)  # two long horns over the eyes
    horn(surface, c + (-44, -12), c + (-62, -30), 6)
    horn(surface, c + (-64, -4), c + (-74, -12), 5)  # and a short one on the nose


def draw_brontosaurus(surface, c):
    spine = along([c + (-56, -30), c + (-46, -20), c + (-34, -8), c + (-15, -4), c + (15, -4),
                   c + (40, 2), c + (60, 8), c + (80, 12)], 30)
    ribs(surface, spine[9:16], 16)
    for x in (-18, -10, 18, 26):
        leg(surface, c + (x, -4), c + (x + 1, 14), c + (x, 32), 5, 5)
    vertebrae(surface, spine, 4.5, 2.5)
    skull(surface, c + (-64, -32), (20, 11), (-2, -1))


def draw_stegosaurus(surface, c):
    spine = along([c + (-44, 4), c + (-28, -6), c + (-8, -14), c + (10, -15), c + (28, -10),
                   c + (46, -2), c + (62, 4), c + (76, 8)], 16)
    for i, point in enumerate(spine[2:12]):
        height = 10 + 6 * math.sin(math.pi * i / 9)
        plate = [point + (-6, 0), point + (0, -height), point + (6, 0)]
        pygame.draw.polygon(surface, BONE_COLOR, plate)
        pygame.draw.polygon(surface, BONE_SHADOW, plate, 1)
    ribs(surface, spine[3:9], 14)
    leg(surface, c + (-22, -6), c + (-20, 12), c + (-22, 30), 6, 4)
    leg(surface, c + (-14, -8), c + (-12, 12), c + (-14, 30), 6, 4)
    leg(surface, c + (18, -10), c + (24, 10), c + (18, 30), 6, 5)
    leg(surface, c + (26, -8), c + (32, 10), c + (26, 30), 6, 5)
    vertebrae(surface, spine, 5, 2.5)
    for dx, dy in ((-4, -14), (8, -12)):  # tail spikes
        horn(surface, spine[-2], spine[-2] + (dx, dy), 5)
        horn(surface, spine[-1], spine[-1] + (dx + 6, dy), 5)
    skull(surface, c + (-54, 8), (20, 11), (-2, -1))


# Spanish name shown to players -> how to draw its skeleton.
DINOSAURS = {
    "Tiranosaurio rex": draw_trex,
    "Triceratops": draw_triceratops,
    "Brontosaurio": draw_brontosaurus,
    "Estegosaurio": draw_stegosaurus,
}


def draw_dino_fossil(surface, center, species):
    """A dinosaur skeleton lying in a patch of dug-up dirt, looking left."""
    patch = pygame.Rect(0, 0, 200, 100)
    patch.center = center
    pygame.draw.ellipse(surface, DIRT_COLOR, patch)
    pygame.draw.ellipse(surface, DIRT_DARK, patch, 4)
    DINOSAURS[species](surface, pygame.Vector2(center) + (0, -4))


def draw_fossil_card(surface, center, species, found, font, scale=0.5):
    """A small fossil for the collection, or a buried "?" if it hasn't been found yet."""
    size = (round(210 * scale), round(110 * scale))
    if found:
        big = pygame.Surface((210, 110), pygame.SRCALPHA)
        draw_dino_fossil(big, (105, 55), species)
        small = pygame.transform.smoothscale(big, size)
        surface.blit(small, small.get_rect(center=center))
    else:
        patch = pygame.Rect(0, 0, size[0] - 6, size[1] - 6)
        patch.center = center
        pygame.draw.ellipse(surface, (215, 195, 165), patch)
        pygame.draw.ellipse(surface, (190, 165, 130), patch, 2)
        mark = font.render("?", True, (160, 130, 95))
        surface.blit(mark, mark.get_rect(center=center))


def draw_medal(surface, center, radius):
    """A gold medal on a ribbon, for completing the fossil collection."""
    cx, cy = center
    r = radius
    for dx, color in ((-0.45, (200, 40, 50)), (0.45, (40, 80, 180))):
        pygame.draw.polygon(surface, color, [(cx + dx * r - r * 0.4, cy - r * 1.9), (cx + dx * r + r * 0.4, cy - r * 1.9),
                                             (cx + dx * r * 0.2 + r * 0.25, cy - r * 0.5),
                                             (cx + dx * r * 0.2 - r * 0.25, cy - r * 0.5)])
    pygame.draw.circle(surface, (235, 185, 40), center, r)
    pygame.draw.circle(surface, (185, 135, 25), center, r, max(2, round(r * 0.15)))
    star = [pygame.Vector2(center) + pygame.Vector2(0, -r * (0.6 if i % 2 == 0 else 0.25)).rotate(i * 36)
            for i in range(10)]
    pygame.draw.polygon(surface, (255, 235, 150), star)


def draw_reward_icon(surface, center, reward, won, font):
    """A prize with its name under it, faded out if it hasn't been won yet."""
    icon = pygame.Surface((90, 50), pygame.SRCALPHA)
    if reward == "hat":
        draw_accessory(icon, pygame.Vector2(45, 52), 30, "explorer_hat", settings.EXPLORER_HAT_COLOR,
                       pygame.Vector2(1, 0))
    else:
        draw_held(icon, pygame.Vector2(12, 8), 34, "magnifier", pygame.Vector2(1, 0))
    if not won:
        icon.set_alpha(55)
    surface.blit(icon, icon.get_rect(center=(center[0], center[1] - 8)))
    label = font.render(REWARD_NAMES[reward], True, settings.TEXT_COLOR if won else (190, 170, 145))
    surface.blit(label, label.get_rect(center=(center[0], center[1] + 26)))


# What each find gives: its short name, and the line shown when it's found.
REWARD_NAMES = {"hat": "Sombrero", "magnifier": "Lupa"}
REWARD_TEXT = {
    "hat": "Ganaste un sombrero de arqueología",
    "magnifier": "Ganaste una lupa de arqueología",
}


class HiddenDino:
    """A dinosaur fossil buried somewhere on the floor. Finding it gives a reward."""

    def __init__(self, avoid_positions, reward, species, hard=False, need=None):
        self.reward = reward
        self.need = need  # None, "big", or "small": the size needed to dig it up
        self.marked = False  # stepped on at the wrong size, so its spot shows
        self.find_distance = settings.HIDDEN_HARD_FIND_DISTANCE if hard else settings.HIDDEN_FIND_DISTANCE
        self.hint_distance = settings.HIDDEN_HARD_HINT_DISTANCE if hard else settings.HIDDEN_HINT_DISTANCE
        self.species = species
        self.title = f"¡Encontraste un {species}!"
        self.note = None  # set when found, e.g. to say it's new for the collection
        margin = 100
        for _ in range(100):
            self.pos = pygame.Vector2(
                random.uniform(margin, settings.WIDTH - margin),
                random.uniform(margin + 20, settings.PLAY_HEIGHT - 70),
            )
            if all(self.pos.distance_to(avoid) > 250 for avoid in avoid_positions):
                break
        self.found = False
        self.dig_timer = 0.0
        self.message_timer = 0.0
        self.specks = [pygame.Vector2(random.uniform(-25, 25), random.uniform(-14, 14)) for _ in range(9)]
        self.flying_dirt = []

    def right_size(self, player):
        if self.need == "big":
            return player.radius >= settings.HIDDEN_BIG_RADIUS
        if self.need == "small":
            return player.radius <= settings.HIDDEN_SMALL_RADIUS
        return True

    def need_text(self, player):
        """What the player still has to do to dig it up, as shown to players."""
        if self.need == "big":
            count = math.ceil((settings.HIDDEN_BIG_RADIUS - player.radius) / settings.PLAYER_GROWTH)
            return "¡Necesitás ser más grande!", f"Comé {count} galletita{'s' if count > 1 else ''} más"
        count = math.ceil((player.radius - settings.HIDDEN_SMALL_RADIUS) / settings.BURNT_SHRINK)
        return "¡Necesitás achicarte!", f"Comé {count} quemada{'s' if count > 1 else ''} más"

    def update(self, dt, player):
        """Returns True on the frame the find is fully dug up."""
        if not self.found:
            if player.pos.distance_to(self.pos) < self.find_distance + player.radius * 0.3:
                if self.right_size(player):
                    self.found = True
                    self.dig_timer = settings.HIDDEN_DIG_TIME
                else:
                    self.marked = True
            return False
        self.flying_dirt = [(pos + vel * dt, vel + pygame.Vector2(0, 500) * dt, life - dt)
                            for pos, vel, life in self.flying_dirt if life > 0]
        if self.dig_timer > 0:
            for _ in range(3):
                angle = random.uniform(math.pi * 1.1, math.pi * 1.9)
                velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * random.uniform(120, 260)
                self.flying_dirt.append((self.pos.copy(), velocity, random.uniform(0.3, 0.6)))
            self.dig_timer -= dt
            if self.dig_timer <= 0:
                self.message_timer = settings.HIDDEN_MESSAGE_TIME
                return True
            return False
        self.message_timer = max(0.0, self.message_timer - dt)
        return False

    def draw(self, surface, player):
        """Draw what's on the floor: hint specks, the dig, or the fossil. Goes under the player."""
        if not self.found and self.marked:
            # A mound with an arrow: up to grow, down to shrink.
            mound = pygame.Rect(0, 0, 54, 24)
            mound.center = self.pos
            pygame.draw.ellipse(surface, DIRT_COLOR, mound)
            pygame.draw.ellipse(surface, DIRT_DARK, mound, 3)
            x, y = self.pos.x, self.pos.y - 32
            if self.need == "big":
                arrow, color = [(x, y - 14), (x + 12, y), (x + 5, y), (x + 5, y + 12), (x - 5, y + 12),
                                (x - 5, y), (x - 12, y)], (60, 160, 70)
            else:
                arrow, color = [(x, y + 14), (x + 12, y), (x + 5, y), (x + 5, y - 12), (x - 5, y - 12),
                                (x - 5, y), (x - 12, y)], (50, 110, 200)
            pygame.draw.polygon(surface, color, arrow)
            pygame.draw.polygon(surface, settings.TEXT_COLOR, arrow, 2)
            return
        if not self.found:
            closeness = 1 - self.pos.distance_to(player.pos) / self.hint_distance
            for i, speck in enumerate(self.specks):
                if closeness > i / len(self.specks):
                    pygame.draw.circle(surface, DIRT_DARK, self.pos + speck, 3.5)
            return
        if self.dig_timer > 0:
            size = 1 - self.dig_timer / settings.HIDDEN_DIG_TIME
            hole = pygame.Rect(0, 0, 40 + 130 * size, 20 + 70 * size)
            hole.center = self.pos
            pygame.draw.ellipse(surface, DIRT_COLOR, hole)
        else:
            draw_dino_fossil(surface, self.pos, self.species)

    def draw_effects(self, surface, fonts, player):
        """Flying dirt, the "you need..." bubble, and the "you found..." banner, over everything else."""
        for pos, _, _ in self.flying_dirt:
            pygame.draw.circle(surface, DIRT_DARK, pos, 4)
        if not self.found and self.marked and self.pos.distance_to(player.pos) < 110:
            title, detail = self.need_text(player)
            title = fonts["small"].render(title, True, settings.HIGHLIGHT_COLOR)
            detail = fonts["tiny"].render(detail, True, settings.TEXT_COLOR)
            bubble = pygame.Rect(0, 0, max(title.get_width(), detail.get_width()) + 28, 58)
            bubble.midbottom = (self.pos.x, self.pos.y - 52)
            bubble.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.PLAY_HEIGHT))
            pygame.draw.rect(surface, settings.BG_COLOR, bubble, border_radius=12)
            pygame.draw.rect(surface, settings.HIGHLIGHT_COLOR, bubble, 3, border_radius=12)
            surface.blit(title, title.get_rect(center=(bubble.centerx, bubble.top + 19)))
            surface.blit(detail, detail.get_rect(center=(bubble.centerx, bubble.top + 41)))
        if self.message_timer > 0:
            lines = [(self.title, fonts["hud"], settings.TEXT_COLOR),
                     (REWARD_TEXT[self.reward], fonts["small"], settings.TEXT_COLOR)]
            if self.note:
                lines.append((self.note, fonts["small"], settings.HIGHLIGHT_COLOR))
            banner = pygame.Rect(0, 0, 680, 40 + 32 * len(lines))
            banner.midbottom = (settings.WIDTH / 2, settings.PLAY_HEIGHT - 12)
            pygame.draw.rect(surface, settings.BG_COLOR, banner, border_radius=16)
            pygame.draw.rect(surface, settings.HIGHLIGHT_COLOR, banner, 4, border_radius=16)
            for i, (text, font, color) in enumerate(lines):
                rendered = font.render(text, True, color)
                surface.blit(rendered, rendered.get_rect(center=(banner.centerx, banner.top + 34 + i * 32)))
