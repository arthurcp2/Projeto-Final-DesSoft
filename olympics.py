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

#  Tela de Inicio

def start_screen(): #Feito com ajuda do ClaudeCode
    cx = WIDTH // 2
    _h, _v = 58, 34   # horizontal and vertical spacing between ring centres
    rings = [
        (cx - _h,      165, RED),
        (cx,           165, WHITE),
        (cx + _h,      165, BLUE),
        (cx - _h // 2, 165 + _v, YELLOW),
        (cx + _h // 2, 165 + _v, GREEN),
    ]

    dev_panel = False
    t = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_t:
                    dev_panel = not dev_panel
                elif e.key == pygame.K_RETURN:
                    return "all"
                elif dev_panel:
                    if e.key == pygame.K_1: return "event1"
                    if e.key == pygame.K_2: return "event2"
                    if e.key == pygame.K_3: return "event3"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                btn = pygame.Rect(cx - 120, 450, 240, 56)
                if btn.collidepoint(mx, my):
                    return "all"

        screen.fill(SKY)
        # chao
        pygame.draw.rect(screen, GREEN, (0, 500, WIDTH, 100))
        pygame.draw.rect(screen, TRACK, (0, 500, WIDTH, 20))

        # sprites de vitoria nos lados
        for i in range(2):
            draw_outcome_sprite(screen, WIN_SPRITES[i], 80 if i == 0 else WIDTH - 80, 500, scale=6, t=t)

        # Olympic rings
        for rx, ry, rc in rings:
            pygame.draw.circle(screen, rc, (rx, ry), 36, 7)

        draw_text_center(screen, "1V1 OLYMPICS", font_big, BLACK, 20)
        draw_text_center(screen, "THREE EVENTS - BEST OF 3", font_small, DARK_GRAY, 68)

        events_info = [
            ("1", "100M SPRINT",    "PRESS KEY = SPEED"),
            ("2", "LONG JUMP",      "RUN + JUMP"),
            ("3", "JAVELIN THROW",  "ANGLE + POWER"),
        ]
        for i, (num, name, desc) in enumerate(events_info):
            bx = 160 + i * 240
            pygame.draw.rect(screen, WHITE, (bx, 252, 200, 72), border_radius=12)
            pygame.draw.rect(screen, DARK_GRAY, (bx, 252, 200, 72), 2, border_radius=12)
            draw_text(screen, num + ". " + name, font_tiny, BLACK, bx + 10, 264)
            draw_text(screen, desc, font_tiny, GRAY, bx + 10, 292)

        # Botao de iniciar
        _btn_label = "PRESS TO START"
        _btn_tw, _btn_th = font_med.size(_btn_label)
        _btn_w = _btn_tw + 40
        _btn_h = _btn_th + 24
        btn = pygame.Rect(cx - _btn_w // 2, 345, _btn_w, _btn_h)
        pygame.draw.rect(screen, GOLD, btn, border_radius=14)
        pygame.draw.rect(screen, BLACK, btn, 2, border_radius=14)
        draw_text_center(screen, _btn_label, font_med, BLACK, btn.y + (btn.height - _btn_th) // 2)

        # legenda de controles
        draw_text_center(screen, "P1 PRESS A   P2 PRESS L", font_tiny, DARK_GRAY, 512)
        draw_text_center(screen, "PRESS T FOR DEV PANEL", font_tiny, GRAY, 530)

        # Developer panel overlay
        if dev_panel:
            pw, ph = 300, 150
            px, py = cx - pw // 2, 180
            panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
            panel.fill((20, 20, 20, 210))
            screen.blit(panel, (px, py))
            pygame.draw.rect(screen, YELLOW, (px, py, pw, ph), 2, border_radius=8)
            draw_text_center(screen, "DEV PANEL  -  PRESS T TO CLOSE", font_tiny, YELLOW, py + 10)
            draw_text_center(screen, "PRESS 1  100M SPRINT",           font_small, WHITE,  py + 42)
            draw_text_center(screen, "PRESS 2  LONG JUMP",             font_small, WHITE,  py + 74)
            draw_text_center(screen, "PRESS 3  JAVELIN THROW",         font_small, WHITE,  py + 106)

        t += 1
        pygame.display.flip()
        clock.tick(FPS)


def _show_event_result(event_name, v1, v2, winner, unit, scores=None): #Feito com ajuda do ClaudeCode
    """Generic result screen. Returns winner index (0 or 1)."""
    names = ["PLAYER 1", "PLAYER 2"]
    wname = names[winner]
    outcome_sprites = [WIN_SPRITES[0] if winner == 0 else LOSE_SPRITES[0],
                       WIN_SPRITES[1] if winner == 1 else LOSE_SPRITES[1]]

    start = pygame.time.get_ticks()
    t = 0
    while pygame.time.get_ticks() - start < 3500:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if pygame.time.get_ticks() - start >= 1000:
                    return winner

        screen.fill(SKY)
        pygame.draw.rect(screen, GREEN, (0, 480, WIDTH, 120))
        pygame.draw.rect(screen, TRACK, (0, 480, WIDTH, 20))

        draw_outcome_sprite(screen, outcome_sprites[0], 80,          480, scale=6, t=t)
        draw_outcome_sprite(screen, outcome_sprites[1], WIDTH - 80,  480, scale=6, t=t)

        draw_text_center(screen, event_name + " - RESULT", font_med, BLACK, 22)

        for i, (v, color, name) in enumerate([(v1, RED, "PLAYER 1"), (v2, BLUE, "PLAYER 2")]):
            bx = 150 + i * 400
            pygame.draw.rect(screen, color, (bx, 78, 280, 104), border_radius=16)
            draw_text(screen, name, font_med, WHITE, bx + 20, 93)
            val_str = "DNF" if (v >= 9000 or v < 0) else f"{v:.2f} {unit}"
            draw_text(screen, val_str, font_big, WHITE, bx + 20, 128)

        draw_text_center(screen, f"{wname} WINS!", font_big, GOLD, 205)

        if scores is not None:
            pygame.draw.line(screen, LIGHT_GRAY, (150, 252), (850, 252), 1)
            draw_text_center(screen, "SCORE", font_small, DARK_GRAY, 260)
            for i, clr in enumerate([RED, BLUE]):
                bx = 300 + i * 220
                pygame.draw.rect(screen, clr, (bx, 285, 180, 80), border_radius=12)
                nm = font_tiny.render(names[i], True, WHITE)
                screen.blit(nm, (bx + 90 - nm.get_width() // 2, 295))
                sc = font_big.render(str(scores[i]), True, WHITE)
                screen.blit(sc, (bx + 90 - sc.get_width() // 2, 318))

        draw_text_center(screen, "NEXT EVENT IN 3S... OR PRESS ANY KEY", font_tiny, DARK_GRAY, 443)

        pygame.display.flip()
        clock.tick(FPS)
        t += 1

    return winner

