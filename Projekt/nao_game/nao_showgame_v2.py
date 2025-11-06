# -*- coding: utf-8 -*-
import pygame, sys, time, random
from naoqi import ALProxy

# === KONFIGURATION ===
NAO_IP = "192.168.13.188"  # NAO IP-Adresse
NAO_PORT = 9559

# === NAO VERBINDUNG ===
nao_connected = False
try:
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    animSpeech = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)
    audio = ALProxy("ALAudioPlayer", NAO_IP, NAO_PORT)
    memory = ALProxy("ALMemory", NAO_IP, NAO_PORT)
    nao_connected = True
    print("NAO verbunden!")
except Exception as e:
    print("NAO nicht verbunden:", e)

# === PYGAME SETUP ===
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nao Interactive Platformer")

# === FARBEN ===
WHITE = (255,255,255)
BLUE = (0,100,255)
BROWN = (139,69,19)
RED = (255,0,0)
GREEN = (0,255,0)

# === BILDER LADEN ===
bg = pygame.image.load("img/background.png")
block_img = pygame.image.load("img/block.png")
nao_stand = pygame.image.load("img/nao_stand.png")
nao_walk1 = pygame.image.load("img/nao_walk1.png")
nao_walk2 = pygame.image.load("img/nao_walk2.png")

# === SOUNDS LADEN ===
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
land_sound = pygame.mixer.Sound("sounds/land.wav")
applause_sound = pygame.mixer.Sound("sounds/applause.wav")
fall_sound = pygame.mixer.Sound("sounds/fall.wav")

# === NAO-REAKTIONEN ===
def nao_say(style_text):
    if nao_connected:
        animSpeech.say(style_text)

def nao_jump():
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0x0000FF, 0.3)
        nao_say("\\style=excited\\ Hüpfen! \\pau=400\\ Los geht’s!")
        motion.setAngles(["HeadPitch","RShoulderRoll"], [-0.3, -0.2], 0.3)
    jump_sound.play()

def nao_land():
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0x00FF00, 0.3)
        nao_say("\\style=joyful\\ Geschafft! \\pau=200\\ Gut gelandet!")
        motion.setAngles("HeadPitch", 0.1, 0.2)
    land_sound.play()

def nao_fall():
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0xFF0000, 0.3)
        nao_say("\\style=fearful\\ Aaaah, ich falle!")
        motion.setAngles("HeadPitch", 0.4, 0.3)
        memory.raiseEvent("NaoGame/FallEvent", 1)
    fall_sound.play()

def nao_applaud():
    if nao_connected:
        nao_say("\\style=joyful\\ Super gemacht! \\pau=400\\ Bravo!")
        leds.fadeRGB("FaceLeds", 0xFFFF00, 0.5)
        try:
            motion.setAngles(["LShoulderPitch","RShoulderPitch"], [0.4,0.4], 0.3)
            for i in range(2):
                motion.setAngles(["LElbowRoll","RElbowRoll"], [-1.0,1.0], 0.5)
                time.sleep(0.2)
                motion.setAngles(["LElbowRoll","RElbowRoll"], [-0.3,0.3], 0.5)
            motion.setAngles(["LShoulderPitch","RShoulderPitch"], [1.2,1.2], 0.3)
        except:
            pass
        leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.5)
    applause_sound.play()

# === PUBLIKUMSREAKTIONEN ===
def nao_cheer():
    nao_say("\\style=joyful\\ Jaa! Weiter so!")
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0x00FF00, 0.5)

def nao_boo():
    nao_say("\\style=sad\\ Oh nein, das war nichts...")
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0xFF0000, 0.5)

# === EXTERNER EVENT-LISTENER ===
def on_fall_event(value):
    nao_say("\\style=sad\\ Oh nein, das tat weh!")

if nao_connected:
    fall_subscriber = memory.subscriber("NaoGame/FallEvent")
    fall_subscriber.signal.connect(on_fall_event)

# === SPIELKLASSEN ===
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

    def update(self, keys, platforms, moving_platforms_group):
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
            nao_jump()

        # Schwerkraft
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.rect.y += self.vel_y

        # Begrenzungen
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        # Standard-Plattformkollision
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y >= 0:
                self.rect.bottom = plat.top
                self.vel_y = 0
                self.on_ground = True
                nao_land()

        # Bewegliche Plattformkollision
        for plat in moving_platforms_group:
            if self.rect.colliderect(plat.rect) and self.vel_y >= 0:
                self.rect.bottom = plat.rect.top
                self.vel_y = 0
                self.on_ground = True
                # Spieler bewegt sich mit Plattform
                self.rect.x += plat.move_x
                self.rect.y += plat.move_y
                nao_land()

    def animate(self):
        self.frame += 1
        if self.frame >= 10:
            self.frame = 0
        self.image = self.images[self.frame // 5]

# === GEGENER-KLASSE ===
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, range_x=100, speed=2):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.start_x = x
        self.range_x = range_x
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if abs(self.rect.x - self.start_x) > self.range_x:
            self.speed *= -1

# === BEWEGLICHE PLATTFORM ===
class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, move_x=0, move_y=2, range_y=80):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_y = y
        self.move_x = move_x
        self.move_y = move_y
        self.range_y = range_y

    def update(self):
        self.rect.y += self.move_y
        if abs(self.rect.y - self.start_y) > self.range_y:
            self.move_y *= -1

# === PLATTFORMEN ===
platforms = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(200, 450, 200, 20),
    pygame.Rect(500, 350, 200, 20),
]

moving_platforms = pygame.sprite.Group(
    MovingPlatform(350, 250, 120, 20, move_y=2, range_y=60)
)

enemies = pygame.sprite.Group(
    Enemy(400, HEIGHT - 80, range_x=120),
    Enemy(600, 330, range_x=100)
)

# === SPIELSETUP ===
player = NaoPlayer(100, 400)
all_sprites = pygame.sprite.Group(player)
clock = pygame.time.Clock()
fall_timer = 0
level_done = False

# === SPIELLOOP ===
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if nao_connected:
                nao_say("\\style=neutral\\ Bis bald, Spieler!")
                leds.fadeRGB("FaceLeds", 0x000000, 0.5)
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Cheer
                nao_cheer()
            elif event.key == pygame.K_b:  # Boo
                nao_boo()

    player.update(keys, platforms, moving_platforms)
    moving_platforms.update()
    enemies.update()

    # Fallen erkennen
    if player.vel_y > 6 and not player.on_ground:
        fall_timer += 1
        if fall_timer == 20:
            nao_fall()
    else:
        fall_timer = 0

    # Gegner-Kollision
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            player.rect.topleft = (100, 400)
            player.vel_y = 0
            nao_fall()

    # Levelabschluss (rechte Seite)
    if player.rect.x > WIDTH - 60 and not level_done:
        level_done = True
        nao_applaud()

    # Zeichnen
    win.blit(bg, (0, 0))
    for plat in platforms:
        win.blit(block_img, (plat.x, plat.y))
    moving_platforms.draw(win)
    enemies.draw(win)
    all_sprites.draw(win)
    pygame.display.update()
