"""Things hidden in the floor in Classic mode, found by walking over them."""

import math
import random

import pygame

from mision_sobris import settings

DIRT_COLOR = (150, 105, 60)
DIRT_DARK = (115, 75, 40)
BONE_COLOR = (245, 238, 215)
BONE_SHADOW = (190, 175, 145)


def draw_dino_fossil(surface, center):
    """A dinosaur skeleton lying in a patch of dug-up dirt, looking left."""
    cx, cy = center
    patch = pygame.Rect(0, 0, 170, 90)
    patch.center = center
    pygame.draw.ellipse(surface, DIRT_COLOR, patch)
    pygame.draw.ellipse(surface, DIRT_DARK, patch, 4)

    # Spine: a curve of vertebrae from the neck, over the back, down the tail.
    spine = []
    for i in range(14):
        t = i / 13
        x = cx - 45 + t * 110
        y = cy - 8 - 14 * math.sin(math.pi * min(1.0, t * 1.4)) + max(0.0, t - 0.7) * 30
        spine.append(pygame.Vector2(x, y))
    for i, bone in enumerate(spine):
        pygame.draw.circle(surface, BONE_COLOR, bone, 5.5 - i * 0.2)

    # Ribs hanging from the back.
    for bone in spine[3:8]:
        pygame.draw.line(surface, BONE_COLOR, bone, bone + pygame.Vector2(-3, 18), 3)

    # Legs: two bones each, ending in little feet.
    for hip_index, dx in ((3, -2), (8, 4)):
        hip = spine[hip_index]
        knee = hip + pygame.Vector2(dx, 16)
        foot = knee + pygame.Vector2(-dx, 14)
        pygame.draw.line(surface, BONE_COLOR, hip, knee, 4)
        pygame.draw.line(surface, BONE_COLOR, knee, foot, 4)
        pygame.draw.line(surface, BONE_COLOR, foot, foot + pygame.Vector2(-7, 0), 4)

    # Skull with an eye hole and a toothy jaw.
    skull_center = spine[0] + pygame.Vector2(-13, -4)
    skull = pygame.Rect(0, 0, 34, 20)
    skull.center = skull_center
    pygame.draw.ellipse(surface, BONE_COLOR, skull)
    pygame.draw.circle(surface, DIRT_DARK, skull_center + pygame.Vector2(3, -2), 3)
    jaw = pygame.Rect(0, 0, 24, 7)
    jaw.topright = (skull.right - 4, skull.bottom - 2)
    pygame.draw.rect(surface, BONE_SHADOW, jaw, border_radius=3)
    for i in range(3):
        tooth = (jaw.left + 4 + i * 6, jaw.top)
        pygame.draw.polygon(surface, BONE_COLOR, [tooth, (tooth[0] + 4, tooth[1]), (tooth[0] + 2, tooth[1] + 4)])


# What each find gives, and the line shown when it's found.
REWARD_TEXT = {
    "hat": "Ganaste un sombrero de arqueología",
    "magnifier": "Ganaste una lupa de arqueología",
}


class HiddenDino:
    """A dinosaur fossil buried somewhere on the floor. Finding it gives a reward."""

    title = "¡Encontraste un dinosaurio!"

    def __init__(self, avoid_positions, reward):
        self.reward = reward
        margin = 100
        for _ in range(100):
            self.pos = pygame.Vector2(
                random.uniform(margin, settings.WIDTH - margin),
                random.uniform(margin + 40, settings.HEIGHT - margin),
            )
            if all(self.pos.distance_to(avoid) > 250 for avoid in avoid_positions):
                break
        self.found = False
        self.dig_timer = 0.0
        self.message_timer = 0.0
        self.specks = [pygame.Vector2(random.uniform(-25, 25), random.uniform(-14, 14)) for _ in range(9)]
        self.flying_dirt = []

    def update(self, dt, player):
        """Returns True on the frame the find is fully dug up."""
        if not self.found:
            if player.pos.distance_to(self.pos) < settings.HIDDEN_FIND_DISTANCE + player.radius * 0.3:
                self.found = True
                self.dig_timer = settings.HIDDEN_DIG_TIME
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
        if not self.found:
            closeness = 1 - self.pos.distance_to(player.pos) / settings.HIDDEN_HINT_DISTANCE
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
            draw_dino_fossil(surface, self.pos)

    def draw_effects(self, surface, fonts):
        """Flying dirt and the "you found..." banner, drawn over everything else."""
        for pos, _, _ in self.flying_dirt:
            pygame.draw.circle(surface, DIRT_DARK, pos, 4)
        if self.message_timer > 0:
            banner = pygame.Rect(0, 0, 620, 96)
            banner.center = (settings.WIDTH / 2, settings.HEIGHT - 70)
            pygame.draw.rect(surface, settings.BG_COLOR, banner, border_radius=16)
            pygame.draw.rect(surface, settings.HIGHLIGHT_COLOR, banner, 4, border_radius=16)
            for text, font, y in ((self.title, fonts["hud"], banner.centery - 18),
                                  (REWARD_TEXT[self.reward], fonts["small"], banner.centery + 20)):
                rendered = font.render(text, True, settings.TEXT_COLOR)
                surface.blit(rendered, rendered.get_rect(center=(banner.centerx, y)))
