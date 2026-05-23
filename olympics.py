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
