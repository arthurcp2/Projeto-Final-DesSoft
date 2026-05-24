import pygame
import sys
import math
import os

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1V1 OLYMPICS")

# ── Sprite sheets ───────────────────────────────────────────────
_SPRITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Spritesheets")

def _load_frames(fname, fw=32, fh=32):
    sheet = pygame.image.load(os.path.join(_SPRITE_DIR, fname)).convert_alpha()
    return [sheet.subsurface((i*fw, 0, fw, fh)) for i in range(sheet.get_width() // fw)]

RUN_FRAMES = [_load_frames("RunPlayer1.png"),_load_frames("RunPlayer2.png")]
JUMP_FRAMES = [_load_frames("JumpPlayer1.png"),_load_frames("JumpPlayer2.png")]
JAVELIN_THROW_FRAMES = [ _load_frames("JavelinPlayer1.png", 40, 34), _load_frames("JavelinPlayer2.png", 40, 34)]
JAVELIN_FRAMES      = _load_frames("Javelin.png", 40, 34)

WIN_SPRITES   = [_load_frames("WinPlayer1.png",16, 32), _load_frames("WinPlayer2.png",   16, 32)]
LOSE_SPRITES  = [_load_frames("LosePlayer1.png",  14, 28), _load_frames("LosePlayer2.png",  16, 29)]
DRAW_SPRITES  = [_load_frames("DrawPlayer1.png",  12, 32), _load_frames("DrawPlayer2.png",  15, 32)]
MEDAL_SPRITES = [_load_frames("MedalPlayer1.png", 16, 32), _load_frames("MedalPlayer2.png", 16, 32)]
# ───────────────────────────────────────────────────────────────

clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (220, 50,  50)
BLUE       = (50,  100, 220)
GREEN      = (50,  180, 50)
YELLOW     = (240, 200, 0)
ORANGE     = (240, 140, 0)
GRAY       = (150, 150, 150)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY  = (80,  80,  80)
SKY        = (85,  160, 215)
SAND       = (210, 180, 120)
TRACK      = (180, 120, 60)
GOLD       = (255, 215, 0)
SILVER     = (192, 192, 192)

_FONT_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Font", "nintendo-nes-font.ttf")
font_big    = pygame.font.Font(_FONT_PATH, 32)
font_med    = pygame.font.Font(_FONT_PATH, 20)
font_small  = pygame.font.Font(_FONT_PATH, 14)
font_tiny   = pygame.font.Font(_FONT_PATH, 10)


# Music
_MUSIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Music", "thememusic.mp3")
pygame.mixer.music.load(_MUSIC_PATH)
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)

# Marcador de pontos

scores = [0, 0]          # tabela de pontuacao
event_results = []       # resultado do evento


def draw_text_center(surf, text, font, color, y):
    s = font.render(text, True, color)
    surf.blit(s, (WIDTH // 2 - s.get_width() // 2, y))

def draw_text(surf, text, font, color, x, y):
    surf.blit(font.render(text, True, color), (x, y))

def draw_sprite(surf, frames, idx, cx, ground_y, scale=2):
    """Draw spritesheet frame centered at cx, feet at ground_y."""
    frame = frames[int(idx) % len(frames)]
    sw = frame.get_width() * scale
    sh = frame.get_height() * scale
    scaled = pygame.transform.scale(frame, (sw, sh))
    surf.blit(scaled, (int(cx) - sw // 2, int(ground_y) - sh))

def draw_athlete(surf, x, y, color, frame): #Feito com ajuda do Claude Code
    """Simple stick-figure athlete. frame 0-3 for running animation."""
    # corpo
    pygame.draw.line(surf, color, (x, y - 30), (x, y - 10), 3)
    # cabeca
    pygame.draw.circle(surf, color, (x, y - 38), 8)
    # animacao das pernas
    leg_angles = [(-20, 20), (-10, 10), (20, -20), (10, -10)]
    la, ra = leg_angles[frame % 4]
    lx = x + int(math.sin(math.radians(la)) * 20)
    ly = y + int(math.cos(math.radians(la)) * 20) - 10
    rx = x + int(math.sin(math.radians(ra)) * 20)
    ry = y + int(math.cos(math.radians(ra)) * 20) - 10
    pygame.draw.line(surf, color, (x, y - 10), (lx, ly), 3)
    pygame.draw.line(surf, color, (x, y - 10), (rx, ry), 3)
    # animacao dos bracos
    arm_angles = [(30, -30), (15, -15), (-30, 30), (-15, 15)]
    aa, ab = arm_angles[frame % 4]
    ax1 = x + int(math.sin(math.radians(aa)) * 18)
    ay1 = y - 30 + int(math.cos(math.radians(aa)) * 18) - 10
    ax2 = x + int(math.sin(math.radians(ab)) * 18)
    ay2 = y - 30 + int(math.cos(math.radians(ab)) * 18) - 10
    pygame.draw.line(surf, color, (x, y - 28), (ax1, ay1), 3)
    pygame.draw.line(surf, color, (x, y - 28), (ax2, ay2), 3)

def draw_athlete_standing(surf, x, y, color):
    pygame.draw.circle(surf, color, (x, y - 38), 8)
    pygame.draw.line(surf, color, (x, y - 30), (x, y - 10), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x - 10, y + 10), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x + 10, y + 10), 3)
    pygame.draw.line(surf, color, (x, y - 28), (x - 14, y - 14), 3)
    pygame.draw.line(surf, color, (x, y - 28), (x + 14, y - 14), 3)

def draw_athlete_jumping(surf, x, y, color):
    pygame.draw.circle(surf, color, (x, y - 38), 8)
    pygame.draw.line(surf, color, (x, y - 30), (x, y - 10), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x - 15, y + 5), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x + 15, y + 5), 3)
    pygame.draw.line(surf, color, (x, y - 28), (x - 18, y - 38), 3)
    pygame.draw.line(surf, color, (x, y - 28), (x + 18, y - 38), 3)

def draw_athlete_throw(surf, x, y, color, angle_deg): #Feito com ajuda do Claude Code
    """Athlete throwing: arm raised at angle."""
    pygame.draw.circle(surf, color, (x, y - 38), 8)
    pygame.draw.line(surf, color, (x, y - 30), (x, y - 10), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x - 10, y + 12), 3)
    pygame.draw.line(surf, color, (x, y - 10), (x + 10, y + 12), 3)
    # animacao do braco de jogar algo
    rad = math.radians(angle_deg)
    arm_end = (x + int(math.cos(rad) * 22), int(y - 28 - math.sin(rad) * 22))
    pygame.draw.line(surf, color, (x, y - 28), arm_end, 3)
    # dardo
    jav_end = (arm_end[0] + int(math.cos(rad) * 28), arm_end[1] - int(math.sin(rad) * 28))
    pygame.draw.line(surf, ORANGE, arm_end, jav_end, 3)


def draw_outcome_sprite(surf, frames, cx, ground_y, scale=3, t=0):
    frame = frames[(t // 15) % len(frames)]
    sw = frame.get_width() * scale
    sh = frame.get_height() * scale
    surf.blit(pygame.transform.scale(frame, (sw, sh)), (cx - sw // 2, ground_y - sh))


