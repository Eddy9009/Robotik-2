# -*- coding: utf-8 -*-
import pygame, sys, time, random
from naoqi import ALProxy

# === KONFIGURATION ===
NAO_IP = "192.168.13.188"
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

# === BILDER LADEN ===
bg = pygame.image.load("img/background.png")
block_imgs = [
    pygame.image.load("img/block1.png"),
    pygame.image.load("img/block2.png")
]
nao_stand = pygame.image.load("img/nao_stand.png")
nao_walk1 = pygame.image.load("img/nao_walk1.png")
nao_walk2 = pygame.image.load("img/nao_walk2.png")

enemy_imgs = [
    pygame.image.load("img/enemy1.png"),
    pygame.image.load("img/enemy2.png")
]

# === SOUNDS LADEN ===
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
land_sound = pygame.mixer.Sound("sounds/land.wav")
applause_sound = pygame.mixer.Sound("sounds/applause.wav")
fall_sound = pygame.mixer.Sound("sounds/fall.wav")

# === NAO-REAKTIONEN ===
def nao_say(text):
    if nao_connected:
        animSpeech.say(text)

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

# === FALL-EVENT ===
def on_fall_event(value):
    nao_say("\\style=sad\\ Oh nein, das tat weh!")

if nao_connected:
    fall_subscriber = memory.subscriber("NaoGame/FallEvent")
    fall_subscriber.signal.connect(on_fall_event)

# === SPIELKLASSEN ===
class NaoPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(NaoPlayer, self).__init__()
        self.images = [nao_walk1, nao_walk2]
        self.image = nao_stand
        self.rect = self.image.get_rect(topleft=(x, y))
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

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            nao_jump()

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.rect.y += self.vel_y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect) and self.vel_y >= 0:
                self.rect.bottom = plat.rect.top
                self.vel_y = 0
                self.on_ground = True
                nao_land()

    def animate(self):
        self.frame += 1
        if self.frame >= 10:
            self.frame = 0
        self.image = self.images[self.frame // 5]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super(Enemy, self).__init__()
        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frame = 0
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 2
        self.frame += 1
        if self.frame >= 20:
            self.frame = 0
        self.image = self.images[self.frame // 10]

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, range_x, speed):
        super(MovingPlatform, self).__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.image.fill((100,100,255))
        self.start_x = x
        self.range_x = range_x
        self.speed = speed
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x < self.start_x or self.rect.x > self.start_x + self.range_x:
            self.direction *= -1

# === LEVELS ===
levels = [
    {
        "platforms": [
            MovingPlatform(0, HEIGHT - 40, WIDTH, 40, 0, 0),
            MovingPlatform(200, 450, 200, 20, 100, 2),
            MovingPlatform(500, 350, 200, 20, 150, 3)
        ],
        "enemies": [
            Enemy(300, 310, enemy_imgs)
        ]
    },
    {
        "platforms": [
            MovingPlatform(0, HEIGHT - 40, WIDTH, 40, 0, 0),
            MovingPlatform(150, 400, 150, 20, 100, 2),
            MovingPlatform(400, 300, 200, 20, 200, 3),
            MovingPlatform(650, 200, 100, 20, 50, 1)
        ],
        "enemies": [
            Enemy(200, 360, enemy_imgs),
            Enemy(500, 260, enemy_imgs)
        ]
    }
]

# === SPIELSETUP ===
player = NaoPlayer(100, 400)
current_level = 0
platforms = pygame.sprite.Group(levels[current_level]["platforms"])
enemies = pygame.sprite.Group(levels[current_level]["enemies"])
all_sprites = pygame.sprite.Group(player, *platforms, *enemies)

clock = pygame.time.Clock()
fall_timer = 0
level_done = False

# === START-/STOP-MENÜ ===
def menu_loop():
    selected = "start"
    font = pygame.font.SysFont(None, 60)
    while True:
        win.fill(WHITE)
        start_text = font.render("START", True, BLUE if selected=="start" else BROWN)
        stop_text = font.render("STOP", True, BLUE if selected=="stop" else BROWN)
        win.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 - 50))
        win.blit(stop_text, (WIDTH//2 - stop_text.get_width()//2, HEIGHT//2 + 50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    selected = "stop" if selected == "start" else "start"
                elif event.key == pygame.K_RETURN:
                    if selected == "start":
                        if nao_connected:
                            nao_say("\\style=excited\\ Lass uns spielen!")
                        return
                    else:
                        if nao_connected:
                            nao_say("\\style=neutral\\ Auf Wiedersehen!")
                        pygame.quit()
                        sys.exit()

menu_loop()

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

    # Update Sprites
    player.update(keys, platforms)
    enemies.update()
    platforms.update()

    # Fallen erkennen
    if player.vel_y > 6 and not player.on_ground:
        fall_timer += 1
        if fall_timer == 20:
            nao_fall()
    else:
        fall_timer = 0

    # Levelabschluss
    if player.rect.x > WIDTH - 60:
        current_level += 1
        if current_level < len(levels):
            # Level laden
            platforms.empty()
            enemies.empty()
            level_data = levels[current_level]
            platforms.add(*level_data["platforms"])
            enemies.add(*level_data["enemies"])
            all_sprites.add(*level_data["platforms"])
            all_sprites.add(*level_data["enemies"])
            player.rect.topleft = (50, HEIGHT - 100)
            nao_applaud()
        else:
            nao_say("\\style=joyful\\ Herzlichen Glückwunsch, alle Level geschafft!")
            pygame.quit()
            sys.exit()

    # Zeichnen
    win.blit(bg, (0,0))
    for plat in platforms:
        win.blit(plat.image, plat.rect.topleft)
    all_sprites.draw(win)
    pygame.display.update()
