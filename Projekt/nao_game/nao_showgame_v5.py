# -*- coding: utf-8 -*-
import pygame, sys, time, random

# ===== NAO SDK =====
try:
    from naoqi import ALProxy
except:
    ALProxy = None  # NAO SDK nicht verfügbar

NAO_IP = "192.168.13.188"
NAO_PORT = 9559
nao_connected = False

if ALProxy is not None:
    try:
        motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
        leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
        animSpeech = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)
        memory = ALProxy("ALMemory", NAO_IP, NAO_PORT)
        nao_connected = True
        print("NAO verbunden!")
    except Exception as e:
        print("NAO nicht verbunden:", e)

# ===== PYGAME SETUP =====
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nao Side-Scroller")

# ===== FARBEN =====
WHITE = (255,255,255)
BLUE = (0,100,255)
RED = (255,0,0)
GREEN = (0,255,0)

# ===== BILDER =====
bg = pygame.image.load("img/background.png")
block_imgs = [pygame.image.load("img/block1.png"),
              pygame.image.load("img/block2.png")]
nao_stand = pygame.image.load("img/nao_stand.png")
nao_walk1 = pygame.image.load("img/nao_walk1.png")
nao_walk2 = pygame.image.load("img/nao_walk2.png")
enemy_imgs = [pygame.image.load("img/enemy1.png"),
              pygame.image.load("img/enemy2.png")]

# ===== SOUNDS =====
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
land_sound = pygame.mixer.Sound("sounds/land.wav")
applause_sound = pygame.mixer.Sound("sounds/applause.wav")
fall_sound = pygame.mixer.Sound("sounds/fall.wav")

# ===== NAO REAKTIONEN =====
def nao_say(style_text):
    if nao_connected:
        animSpeech.say(style_text)

def nao_jump(): 
    jump_sound.play()
    if nao_connected:
        nao_say("\\style=excited\\ Hüpfen!")

def nao_land():
    land_sound.play()
    if nao_connected:
        nao_say("\\style=joyful\\ Gut gelandet!")

def nao_fall():
    fall_sound.play()
    if nao_connected:
        nao_say("\\style=fearful\\ Aaaah, ich falle!")

def nao_applaud():
    applause_sound.play()
    if nao_connected:
        nao_say("\\style=joyful\\ Bravo!")

# ===== SPIELKLASSEN =====
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
            nao_jump()

        # Schwerkraft
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.rect.y += self.vel_y

        # Kollision
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

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, img, movable=False, range_x=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.movable = movable
        self.start_x = x
        self.range_x = range_x
        self.direction = 1

    def update(self):
        if self.movable:
            self.rect.x += self.direction * 2
            if self.rect.x > self.start_x + self.range_x or self.rect.x < self.start_x:
                self.direction *= -1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = enemy_imgs
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.frame = 0
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        self.animate()

    def animate(self):
        self.frame += 1
        if self.frame >= 20:
            self.frame = 0
        self.image = self.images[self.frame // 10]

# ===== FORTLAUFENDES LEVEL =====
def create_level(start_x):
    level_platforms = []
    level_enemies = []

    for i in range(10):
        x = start_x + i * 250
        y = random.randint(300, 500)
        img = random.choice(block_imgs)
        movable = random.choice([True, False])
        range_x = random.randint(100, 300) if movable else 0
        level_platforms.append(Platform(x, y, img, movable, range_x))

        if random.random() > 0.6:  # 40% Chance Gegner
            level_enemies.append(Enemy(x + 50, y - 40))

    return level_platforms, level_enemies

# ===== ERSTES LEVEL =====
platforms, enemies = create_level(0)
player = NaoPlayer(100, 400)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
for p in platforms:
    all_sprites.add(p)
for e in enemies:
    all_sprites.add(e)

scroll_x = 0
clock = pygame.time.Clock()
menu = True
level_end_x = 2500
level_done = False
fall_timer = 0

# ===== SPIELLOOP =====
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if menu:
                if event.key == pygame.K_s:
                    menu = False
                    nao_say("\\style=excited\\ Das Spiel beginnt!")
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            else:
                if event.key == pygame.K_p:
                    nao_applaud()
                elif event.key == pygame.K_f:
                    nao_fall()

    if menu:
        win.fill(BLUE)
        font = pygame.font.SysFont(None, 50)
        text1 = font.render("NAO SIDE-SCROLLER", True, WHITE)
        text2 = font.render("S: Start   Q: Quit", True, WHITE)
        win.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 50))
        win.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 10))
        pygame.display.update()
        continue

    # Update Spieler und Level
    player.update(keys, platforms)
    for p in platforms:
        p.update()
    for e in enemies:
        e.update()

    # Spieler fällt
    if player.vel_y > 6 and not player.on_ground:
        fall_timer += 1
        if fall_timer == 20:
            nao_fall()
    else:
        fall_timer = 0

    # Levelabschluss
    if player.rect.x - scroll_x > level_end_x and not level_done:
        level_done = True
        nao_applaud()
        # Neues Level laden
        new_platforms, new_enemies = create_level(level_end_x)
        platforms.extend(new_platforms)
        enemies.extend(new_enemies)
        for p in new_platforms:
            all_sprites.add(p)
        for e in new_enemies:
            all_sprites.add(e)
        level_end_x += 2500
        level_done = False

    # Side-Scrolling
    if player.rect.x - scroll_x > WIDTH//2:
        scroll_x = player.rect.x - WIDTH//2

    # Zeichnen
    win.blit(bg, (-scroll_x, 0))
    for p in platforms:
        win.blit(p.image, (p.rect.x - scroll_x, p.rect.y))
    for e in enemies:
        win.blit(e.image, (e.rect.x - scroll_x, e.rect.y))
    win.blit(player.image, (player.rect.x - scroll_x, player.rect.y))

    pygame.display.update()
