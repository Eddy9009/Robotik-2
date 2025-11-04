#!/usr/bin/env python

import random, os.path

#import basic pygame modules
import pygame
from pygame.locals import *

import random
import math
import sys
import os

# --- Initialisierung ---
pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Bartagame Toy – Insekten & Licht mit Sound")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
FPS = 60

# --- Farben ---
YELLOW = (255, 255, 100)
GREEN = (100, 255, 100)
ORANGE = (255, 180, 50)
WHITE = (255, 255, 255)
BG_COLOR = (10, 10, 10)

# --- Insektenarten ---
INSECT_TYPES = [
    {"name": "buzz", "color": YELLOW, "size": 12, "speed": 2.8},
    {"name": "chirp", "color": GREEN, "size": 18, "speed": 1.6},
    {"name": "buzz", "color": ORANGE, "size": 8, "speed": 3.5},
]
NUM_INSECTS = 8

# --- Sounds laden ---
def load_sounds(folder="sounds"):
    sounds = {"buzz": [], "chirp": []}
    for sound_type in sounds.keys():
        for i in range(1, 4):
            path = os.path.join(folder, f"{sound_type}{i}.wav")
            if os.path.exists(path):
                sounds[sound_type].append(pygame.mixer.Sound(path))
                sounds[sound_type][-1].set_volume(0.15)  # leise halten
    return sounds

SOUNDS = load_sounds()

# --- Insektenklasse ---
class Insect:
    def __init__(self, insect_type):
        self.kind = insect_type["name"]
        self.color = insect_type["color"]
        self.radius = insect_type["size"]
        self.speed = insect_type["speed"]
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.angle = random.uniform(0, math.pi * 2)
        self.pause_time = 0

    def play_sound(self):
        """Spielt zufällig einen passenden Soundeffekt ab."""
        if self.kind in SOUNDS and SOUNDS[self.kind]:
            sound = random.choice(SOUNDS[self.kind])
            sound.play()

    def update(self):
        if self.pause_time > 0:
            self.pause_time -= 1
            return

        # zufällige Richtungsänderung
        if random.random() < 0.02:
            self.angle += random.uniform(-math.pi / 3, math.pi / 3)
            self.play_sound()  # beim Richtungswechsel Summen/Zirpen

        # zufällige Pausen
        if random.random() < 0.01:
            self.pause_time = random.randint(10, 30)
            self.play_sound()  # beim Anhalten auch Sound

        # Bewegung
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Bildschirmbegrenzung
        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.angle = math.pi - self.angle
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.angle = -self.angle

    def draw(self, surface):
        # sanft leuchtender Effekt
        glow_radius = self.radius * 3
        for i in range(3, 0, -1):
            alpha = int(50 * i)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha),
                               (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (self.x - glow_radius, self.y - glow_radius), special_flags=pygame.BLEND_ADD)
            glow_radius //= 2

        # Kern des Insekts
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


# --- Lichtfleckklasse ---
class LightSpot:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 60
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = 2
        self.color = WHITE
        self.phase = 0

    def update(self):
        self.phase += 0.03
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.radius = 60 + int(20 * math.sin(self.phase))
        if random.random() < 0.01:
            self.angle += random.uniform(-math.pi / 4, math.pi / 4)
        if self.x < 0 or self.x > WIDTH:
            self.angle = math.pi - self.angle
        if self.y < 0 or self.y > HEIGHT:
            self.angle = -self.angle

    def draw(self, surface):
        for i in range(4, 0, -1):
            alpha = int(40 * i)
            glow_radius = self.radius * (i * 0.7)
            glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha),
                               (int(glow_radius), int(glow_radius)), int(glow_radius))
            surface.blit(glow_surf, (self.x - glow_radius, self.y - glow_radius), special_flags=pygame.BLEND_ADD)


# --- Objekte erzeugen ---
insects = [Insect(random.choice(INSECT_TYPES)) for _ in range(NUM_INSECTS)]
light_spot = LightSpot()

# --- Hauptschleife ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

    for insect in insects:
        insect.update()
    light_spot.update()

    screen.fill(BG_COLOR)
    light_spot.draw(screen)
    for insect in insects:
        insect.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
