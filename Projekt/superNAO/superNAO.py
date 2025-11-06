# -*- coding: utf-8 -*-
import pygame, sys, time
from naoqi import ALProxy

# --- NAO-Verbindung ---
NAO_IP = "192.168.1.100"   # <- IP deines Roboters eintragen
NAO_PORT = 9559

try:
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
    nao_connected = True
    print("NAO connected")
except Exception as e:
    print("Konnte NAO nicht verbinden:", e)
    nao_connected = False

# --- Spiel Initialisierung ---
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NAO Platformer")

WHITE = (255,255,255)
BROWN = (139,69,19)
BLUE = (0,100,255)

# --- Bilder ---
bg = pygame.image.load("img/background.png")
block_img = pygame.image.load("img/block.png")
nao_stand = pygame.image.load("img/nao_stand.png")
nao_walk1 = pygame.image.load("img/nao_walk1.png")
nao_walk2 = pygame.image.load("img/nao_walk2.png")

# --- Spielerklasse ---
class NaoPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [nao_walk1, nao_walk2]
        self.image = nao_stand
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.vel_y = 0
        self.jump_power = -15
        self.on_ground = False
        self.frame = 0

    def update(self, keys, platforms):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
            self.animate()
        elif keys[pygame.K_RIGHT]:
            dx = 5
            self.animate()
        else:
            self.image = nao_stand

        # Sprung
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            if nao_connected:
                tts.say("Hüpfen!")
                motion.angleInterpolationWithSpeed("HeadPitch", -0.3, 0.2)

        # Schwerkraft
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.rect.y += self.vel_y

        # Kollision
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y >= 0:
                self.rect.bottom = plat.top
                self.vel_y = 0
                self.on_ground = True
                if nao_connected:
                    motion.angleInterpolationWithSpeed("HeadPitch", 0.1, 0.2)

    def animate(self):
        self.frame += 1
        if self.frame >= 10:
            self.frame = 0
        self.image = self.images[self.frame // 5]

# --- Plattformen ---
platforms = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(200, 450, 200, 20),
    pygame.Rect(500, 350, 200, 20),
]

# --- Nao-Spieler ---
player = NaoPlayer(100, 400)
all_sprites = pygame.sprite.Group(player)

clock = pygame.time.Clock()
falling_timer = 0

# --- Hauptloop ---
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if nao_connected:
                tts.say("Bis bald!")
            pygame.quit()
            sys.exit()

    prev_y = player.rect.y
    player.update(keys, platforms)

    # Erkennen, ob Spieler fällt
    if player.vel_y > 5 and not player.on_ground:
        falling_timer += 1
        if falling_timer == 20 and nao_connected:
            tts.say("Achtung, ich falle!")
    else:
        falling_timer = 0

    # Zeichnen
    win.blit(bg, (0, 0))
    for plat in platforms:
        win.blit(block_img, (plat.x, plat.y))
    all_sprites.draw(win)
    pygame.display.update()
