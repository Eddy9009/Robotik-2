# -*- coding: utf-8 -*-
"""
Nao Interactive Platformer
Vollständig mit Menü, Gegnern, animierten Blöcken, fortlaufendem Level und NAO-Reaktionen
"""

import pygame, sys, time, random

# NAOqi-Module nur importieren, wenn verfügbar
try:
    from naoqi import ALProxy
    nao_available = True
except ImportError:
    nao_available = False

# ================== KONFIGURATION ==================
NAO_IP = "192.168.13.188"  # IP-Adresse deines NAO-Roboters
NAO_PORT = 9559

# ================== NAO VERBINDUNG ==================
nao_connected = False
if nao_available:
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

# ================== PYGAME SETUP ==================
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nao Interactive Platformer")
font = pygame.font.SysFont("Arial", 40)

# ================== FARBEN ==================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# ================== BILDER LADEN ==================
bg = pygame.image.load("img/background.png")

# Verschiedene Blockbilder für fortlaufendes Level
block_imgs = [
    pygame.image.load("img/block1.png"),
    pygame.image.load("img/block2.png"),
    pygame.image.load("img/block3.png")
]

# NAO Bilder
nao_stand = pygame.image.load("img/nao_stand.png")
nao_walk_imgs = [pygame.image.load("img/nao_walk1.png"),
                 pygame.image.load("img/nao_walk2.png")]

# Gegner Bilder
enemy_imgs = [pygame.image.load("img/enemy1.png"),
              pygame.image.load("img/enemy2.png")]

# ================== SOUNDS ==================
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
land_sound = pygame.mixer.Sound("sounds/land.wav")
applause_sound = pygame.mixer.Sound("sounds/applause.wav")
fall_sound = pygame.mixer.Sound("sounds/fall.wav")

# ================== NAO-FUNKTIONEN ==================
def nao_say(text):
    """NAO spricht Text"""
    if nao_connected:
        animSpeech.say(text)

def nao_jump():
    """NAO reagiert auf Sprung"""
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0x0000FF, 0.3)
        nao_say("\\style=excited\\ Hüpfen! \\pau=400\\ Los geht’s!")
        motion.setAngles(["HeadPitch","RShoulderRoll"], [-0.3, -0.2], 0.3)
    jump_sound.play()

def nao_land():
    """NAO reagiert auf Landung"""
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0x00FF00, 0.3)
        nao_say("\\style=joyful\\ Gut gelandet!")
        motion.setAngles("HeadPitch", 0.1, 0.2)
    land_sound.play()

def nao_fall():
    """NAO reagiert auf Fallen"""
    if nao_connected:
        leds.fadeRGB("FaceLeds", 0xFF0000, 0.3)
        nao_say("\\style=fearful\\ Aaaah, ich falle!")
        motion.setAngles("HeadPitch", 0.4, 0.3)
        memory.raiseEvent("NaoGame/FallEvent", 1)
    fall_sound.play()

def nao_applaud():
    """NAO applaudiert"""
    if nao_connected:
        nao_say("\\style=joyful\\ Bravo!")
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

# ================== FALL- EVENT ==================
def on_fall_event(value):
    nao_say("\\style=sad\\ Oh nein, das tat weh!")

if nao_connected:
    fall_sub = memory.subscriber("NaoGame/FallEvent")
    fall_sub.signal.connect(on_fall_event)

# ================== SPIELKLASSEN ==================
class NaoPlayer(pygame.sprite.Sprite):
    """Hauptspielerklasse"""
    def __init__(self, x, y):
        super(NaoPlayer, self).__init__()
        self.images = nao_walk_imgs
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

        # Bewegung
        self.rect.x += dx
        self.rect.y += self.vel_y

        # Kollisionen
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y >= 0:
                self.rect.bottom = plat.top
                self.vel_y = 0
                self.on_ground = True
                nao_land()

    def animate(self):
        self.frame += 1
        if self.frame >= 10:
            self.frame = 0
        self.image = self.images[self.frame // 5]

class Enemy(pygame.sprite.Sprite):
    """Gegner mit Animation"""
    def __init__(self, x, y, images):
        super(Enemy, self).__init__()
        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.frame = 0
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        self.frame += 1
        if self.frame >= 10:
            self.frame = 0
        self.image = self.images[self.frame // 5]

# ================== PLATTFORMEN ==================
platforms = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(200, 450, 200, 20),
    pygame.Rect(500, 350, 200, 20),
]

# ================== SPRITE-GRUPPEN ==================
player = NaoPlayer(100, 400)
enemies = pygame.sprite.Group(
    Enemy(300, 410, enemy_imgs)
)
all_sprites = pygame.sprite.Group(player)
all_sprites.add(enemies)

# ================== SPIELVARIABLEN ==================
clock = pygame.time.Clock()
fall_timer = 0
level_done = False

# ================== MENÜ ==================
def draw_menu(selected):
    """Zeichnet das Start-/Stop-Menü"""
    win.fill(BLACK)
    title = font.render("Nao Game", True, YELLOW)
    win.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    start_color = BLUE if selected == "start" else WHITE
    stop_color = BLUE if selected == "stop" else WHITE

    start_text = font.render("Start Game", True, start_color)
    stop_text = font.render("Quit Game", True, stop_color)

    win.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 250))
    win.blit(stop_text, (WIDTH//2 - stop_text.get_width()//2, 350))
    pygame.display.update()

def menu_loop():
    """Start-/Stop-Menü mit Auswahl"""
    selected = "start"
    while True:
        draw_menu(selected)
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

# ================== STARTE MENÜ ==================
menu_loop()

# ================== SPIELLOOP ==================
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

    # Fallen erkennen
    if player.vel_y > 6 and not player.on_ground:
        fall_timer += 1
        if fall_timer == 20:
            nao_fall()
    else:
        fall_timer = 0

    # Levelabschluss (rechte Seite)
    if player.rect.x > WIDTH - 60 and not level_done:
        level_done = True
        nao_applaud()

    # Zeichnen
    win.blit(bg, (0, 0))
    for i, plat in enumerate(platforms):
        win.blit(block_imgs[i % len(block_imgs)], (plat.x, plat.y))
    all_sprites.draw(win)
    pygame.display.update()
