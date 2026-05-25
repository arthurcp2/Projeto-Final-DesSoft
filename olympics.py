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

def draw_athlete(surf, x, y, color, frame):
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

def draw_athlete_throw(surf, x, y, color, angle_deg):
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

def start_screen():
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


def _show_event_result(event_name, v1, v2, winner, unit, scores=None):
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


#  Tela final

def final_screen(scores, event_results):
    overall = 0 if scores[0] > scores[1] else (1 if scores[1] > scores[0] else -1)
    names = ["PLAYER 1", "PLAYER 2"]
    colors = [RED, BLUE]
    event_names = ["100M SPRINT", "LONG JUMP", "JAVELIN THROW"]

    if overall == -1:
        end_sprites = [DRAW_SPRITES[0], DRAW_SPRITES[1]]
    else:
        end_sprites = [MEDAL_SPRITES[0] if overall == 0 else LOSE_SPRITES[0],
                       MEDAL_SPRITES[1] if overall == 1 else LOSE_SPRITES[1]]

    t = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(SKY)
        pygame.draw.rect(screen, GREEN, (0, 500, WIDTH, 100))
        pygame.draw.rect(screen, TRACK, (0, 500, WIDTH, 20))

        draw_text_center(screen, "FINAL RESULTS", font_big, BLACK, 20)

        # caixa de pontos
        for i in range(2):
            bx = 100 + i * 500
            pygame.draw.rect(screen, colors[i], (bx, 82, 260, 90), border_radius=16)
            draw_text(screen, names[i], font_med, WHITE, bx + 15, 92)
            draw_text(screen, f"{scores[i]} WINS", font_big, WHITE, bx + 15, 132)

        # Tela do vencedor
        if overall == -1:
            draw_text_center(screen, "TIE!", font_big, GOLD, 196)
        else:
            draw_text_center(screen, f"CHAMPION: {names[overall]}!", font_big, GOLD, 196)

        # Tabela de resultados
        tx, tw = 175, 650
        pygame.draw.rect(screen, WHITE, (tx, 252, tw, 120), border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, (tx, 252, tw, 120), 2, border_radius=10)
        draw_text(screen, "EVENT",    font_tiny, DARK_GRAY, tx + 12,  260)
        draw_text(screen, "PLAYER 1", font_tiny, RED,       tx + 220, 260)
        draw_text(screen, "PLAYER 2", font_tiny, BLUE,      tx + 360, 260)
        draw_text(screen, "WINNER",   font_tiny, DARK_GRAY, tx + 510, 260)
        pygame.draw.line(screen, DARK_GRAY, (tx, 278), (tx + tw, 278), 1)

        for i, (p1v, p2v, wstr, unit) in enumerate(event_results):
            y = 290 + i * 26
            draw_text(screen, event_names[i], font_tiny, BLACK,     tx + 12,  y)
            p1s = "DNF" if (p1v >= 9000 or p1v < 0) else f"{p1v:.2f}{unit}"
            p2s = "DNF" if (p2v >= 9000 or p2v < 0) else f"{p2v:.2f}{unit}"
            draw_text(screen, p1s,           font_tiny, RED,        tx + 220, y)
            draw_text(screen, p2s,           font_tiny, BLUE,       tx + 360, y)
            draw_text(screen, wstr,          font_tiny, DARK_GRAY,  tx + 510, y)

        draw_text_center(screen, "PRESS R TO PLAY AGAIN   ESC TO QUIT", font_small, DARK_GRAY, 388)


        draw_outcome_sprite(screen, end_sprites[0], 80,         500, scale=6, t=t)
        draw_outcome_sprite(screen, end_sprites[1], WIDTH - 80, 500, scale=6, t=t)
        t += 1

        pygame.display.flip()
        clock.tick(FPS)


def main_game():
    global scores, event_results
    scores = [0, 0]
    event_results = []

    # Evento 1
    pygame.mixer.music.set_volume(0.3)
    w, v1, v2 = event_sprint_v2()
    scores[w] += 1
    event_results.append((v1, v2, f"P{w+1}", "s"))
    pygame.mixer.music.set_volume(1.0)
    _show_event_result("100M SPRINT", v1, v2, w, "s", scores)

    # Evento 2
    pygame.mixer.music.set_volume(0.3)
    w, v1, v2 = event_long_jump_v2()
    scores[w] += 1
    event_results.append((v1, v2, f"P{w+1}", "m"))
    pygame.mixer.music.set_volume(1.0)
    _show_event_result("LONG JUMP", v1, v2, w, "m", scores)

    # Evento 3
    pygame.mixer.music.set_volume(0.3)
    w, v1, v2 = event_javelin_v2()
    scores[w] += 1
    event_results.append((v1, v2, f"P{w+1}", "m"))
    pygame.mixer.music.set_volume(1.0)
    _show_event_result("JAVELIN THROW", v1, v2, w, "m", scores)

    return final_screen(scores, event_results)



def event_sprint_v2():
    RACE_DIST = 100.0
    pos   = [0.0, 0.0]
    vel   = [0.0, 0.0]
    frame = [0, 0]
    frame_timer = [0.0, 0.0]
    finished = [False, False]
    finish_time = [None, None]
    time_start = None

    TRACK_Y = 290
    TRACK_H = 90
    LANE_Y  = [TRACK_Y + 30, TRACK_Y + 65]

    finish_x = WIDTH - 100
    for cd in range(3, 0, -1):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        screen.fill(SKY)
        pygame.draw.rect(screen, GREEN, (0, TRACK_Y + TRACK_H, WIDTH, HEIGHT - TRACK_Y - TRACK_H))
        pygame.draw.rect(screen, TRACK, (0, TRACK_Y, WIDTH, TRACK_H))
        pygame.draw.line(screen, WHITE, (0, TRACK_Y + TRACK_H // 2),
                         (WIDTH, TRACK_Y + TRACK_H // 2), 1)
        for yy in range(TRACK_Y, TRACK_Y + TRACK_H, 10):
            c = WHITE if (yy // 10) % 2 == 0 else BLACK
            pygame.draw.rect(screen, c, (finish_x, yy, 15, 10))
        for i in range(2):
            draw_sprite(screen, RUN_FRAMES[i], 0, 80, LANE_Y[i], scale=2)
        draw_text_center(screen, "100M SPRINT", font_big, BLACK, 60)
        draw_text_center(screen, "P1 PRESS A   P2 PRESS L   FAST!", font_small, WHITE, 150)
        draw_text_center(screen, str(cd), font_big, YELLOW, 220)
        pygame.display.flip()
        pygame.time.wait(1000)

    screen.fill(SKY)
    pygame.draw.rect(screen, GREEN, (0, TRACK_Y + TRACK_H, WIDTH, HEIGHT - TRACK_Y - TRACK_H))
    pygame.draw.rect(screen, TRACK, (0, TRACK_Y, WIDTH, TRACK_H))
    pygame.draw.line(screen, WHITE, (0, TRACK_Y + TRACK_H // 2),
                     (WIDTH, TRACK_Y + TRACK_H // 2), 1)
    for yy in range(TRACK_Y, TRACK_Y + TRACK_H, 10):
        c = WHITE if (yy // 10) % 2 == 0 else BLACK
        pygame.draw.rect(screen, c, (finish_x, yy, 15, 10))
    for i in range(2):
        draw_sprite(screen, RUN_FRAMES[i], 0, 80, LANE_Y[i], scale=2)
    draw_text_center(screen, "GO!", font_big, RED, 220)
    pygame.display.flip()
    pygame.time.wait(600)

    time_start = pygame.time.get_ticks()
    first_finish_at = None
    DNF_TIMEOUT = 4.0
    last_press  = [0, 0]   #Tempo em milissegundos da última tecla pressionada 
    FAST_IV   = 0.10       # intervalo que fornece impulso máximo
    SLOW_IV   = 0.55       # intervalo que fornece impulso minimo
    MAX_BOOST = 4.0
    MIN_BOOST = 0.2
    DECAY     = 3.0        #desaceleracao da velocidade vel -= DECAY * vel * dt

    while True:
        dt = clock.tick(FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a and not finished[0]:
                    now = pygame.time.get_ticks()
                    iv  = min((now - last_press[0]) / 1000.0, SLOW_IV)
                    t   = (iv - FAST_IV) / (SLOW_IV - FAST_IV)
                    vel[0] = min(vel[0] + MAX_BOOST * (1 - t) + MIN_BOOST * t, 13.0)
                    last_press[0] = now
                if e.key == pygame.K_l and not finished[1]:
                    now = pygame.time.get_ticks()
                    iv  = min((now - last_press[1]) / 1000.0, SLOW_IV)
                    t   = (iv - FAST_IV) / (SLOW_IV - FAST_IV)
                    vel[1] = min(vel[1] + MAX_BOOST * (1 - t) + MIN_BOOST * t, 13.0)
                    last_press[1] = now

        for i in range(2):
            if not finished[i]:
                vel[i] = max(0, vel[i] - DECAY * vel[i] * dt)
                pos[i] += vel[i] * dt
                if pos[i] >= RACE_DIST:
                    pos[i] = RACE_DIST
                    finished[i] = True
                    finish_time[i] = (pygame.time.get_ticks() - time_start) / 1000.0
                frame_timer[i] += vel[i] * dt
                if frame_timer[i] > 0.12:
                    frame[i] += 1
                    frame_timer[i] = 0

        if any(finished) and not all(finished) and first_finish_at is None:
            first_finish_at = pygame.time.get_ticks()
        if all(finished):
            break
        if first_finish_at is not None:
            if (pygame.time.get_ticks() - first_finish_at) / 1000.0 >= DNF_TIMEOUT:
                break

        screen.fill(SKY)
        pygame.draw.rect(screen, GREEN, (0, TRACK_Y + TRACK_H, WIDTH, HEIGHT - TRACK_Y - TRACK_H))
        pygame.draw.rect(screen, TRACK, (0, TRACK_Y, WIDTH, TRACK_H))
        pygame.draw.line(screen, WHITE, (0, TRACK_Y + TRACK_H // 2),
                         (WIDTH, TRACK_Y + TRACK_H // 2), 1)
        finish_x = WIDTH - 100
        for yy in range(TRACK_Y, TRACK_Y + TRACK_H, 10):
            c = WHITE if (yy // 10) % 2 == 0 else BLACK
            pygame.draw.rect(screen, c, (finish_x, yy, 15, 10))

        draw_text_center(screen, "100M SPRINT", font_big, BLACK, 20)
        draw_text_center(screen, "P1 PRESS A   P2 PRESS L   FAST!", font_tiny, WHITE, 75)

        for i, (clr, lbl) in enumerate([(RED, "P1"), (BLUE, "P2")]):
            ax = int(80 + (pos[i] / RACE_DIST) * (finish_x - 90))
            ay = LANE_Y[i]
            draw_sprite(screen, RUN_FRAMES[i], frame[i], ax, ay, scale=2)
            _lw = font_tiny.size(lbl)[0]
            draw_text(screen, lbl, font_tiny, clr, ax - _lw // 2 + 4, ay - 80)

            bar_y = TRACK_Y + TRACK_H + 15 + i * 30
            pygame.draw.rect(screen, LIGHT_GRAY, (80, bar_y, WIDTH - 160, 20), border_radius=4)
            fv = int((pos[i] / RACE_DIST) * (WIDTH - 160))
            pygame.draw.rect(screen, clr, (80, bar_y, fv, 20), border_radius=4)
            draw_text(screen, f"{lbl}: {pos[i]:.1f}", font_tiny, clr, 10, bar_y + 2)

        if first_finish_at is not None and not all(finished):
            remaining = max(0.0, DNF_TIMEOUT - (pygame.time.get_ticks() - first_finish_at) / 1000.0)
            draw_text_center(screen, f"DNF IN {remaining:.1f}S", font_med, ORANGE, 130)

        pygame.display.flip()

    # caso acabe em empate
    t0 = finish_time[0] if finish_time[0] is not None else 9999.0
    t1 = finish_time[1] if finish_time[1] is not None else 9999.0
    winner = 0 if t0 <= t1 else 1
    return winner, t0, t1


def event_long_jump_v2():
    CAM_TARGET_X = 300
    RUNWAY       = 600.0
    FOUL_LINE    = RUNWAY + 70  # linha de penalidade

    while True:  # caso os dois atletas recebam penalidade eles tentarao novamente
        results = []

        for player_idx in range(2):
            color    = RED if player_idx == 0 else BLUE
            label    = "PLAYER 1" if player_idx == 0 else "PLAYER 2"
            run_key  = pygame.K_a if player_idx == 0 else pygame.K_l
            jump_key = pygame.K_SPACE if player_idx == 0 else pygame.K_RETURN
            rk_name  = "A" if player_idx == 0 else "L"
            jk_name  = "SPACE" if player_idx == 0 else "ENTER"

            for cd in range(3, 0, -1):
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                screen.fill(SKY)
                cd_bnd = int(RUNWAY + 82)
                pygame.draw.rect(screen, SAND, (0, 390, WIDTH, 210))
                pygame.draw.rect(screen, GREEN, (0, 420, min(cd_bnd, WIDTH), 180))
                pygame.draw.rect(screen, TRACK, (0, 390, min(cd_bnd, WIDTH), 35))
                pygame.draw.rect(screen, WHITE, (int(FOUL_LINE), 390, 12, 35))
                draw_sprite(screen, RUN_FRAMES[player_idx], 0, 80, 390, scale=2)
                draw_text_center(screen, "LONG JUMP", font_big, BLACK, 40)
                draw_text_center(screen, f"{label} - GET READY!", font_med, color, 120)
                draw_text_center(screen, f"PRESS {rk_name} TO RUN   {jk_name} TO JUMP", font_small, DARK_GRAY, 190)
                draw_text_center(screen, str(cd), font_big, YELLOW, 280)
                pygame.display.flip()
                pygame.time.wait(1000)

            vel      = 0.0
            pos_x    = 0.0
            frame    = 0
            ft       = 0.0
            jumped   = False
            pre_jump = False   # Delay do pulo
            pre_jump_vel = 0.0
            foul     = False
            jvx      = 0.0
            jvy      = 0.0
            ax       = 80.0
            ay       = 390.0
            in_air   = False
            distance = 0.0
            jsx      = 0.0
            GY       = 390.0
            started         = False
            cam_x           = 0.0
            jump_frame      = 0
            jump_timer      = 0.0
            last_press_time = 0    # tempo da ultima tecla pressionada
            FAST_IV   = 0.10
            SLOW_IV   = 0.55
            MAX_BOOST = 4.0
            MIN_BOOST = 0.2
            DECAY     = 3.0

            while True:
                dt = clock.tick(FPS) / 1000.0
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == run_key and not jumped:
                            now = pygame.time.get_ticks()
                            iv  = min((now - last_press_time) / 1000.0, SLOW_IV)
                            t   = (iv - FAST_IV) / (SLOW_IV - FAST_IV)
                            vel = min(vel + MAX_BOOST * (1 - t) + MIN_BOOST * t, 11.0)
                            last_press_time = now
                            started = True
                        if e.key == jump_key and not jumped and started:
                            jumped = True
                            jsx = ax
                            if jsx >= FOUL_LINE:
                                foul = True
                                distance = -1.0
                            else:
                                pre_jump = True
                                pre_jump_vel = vel
                                jump_frame = 0
                                jump_timer = 0.0

                if not jumped:
                    vel = max(0, vel - DECAY * vel * dt)
                    ax = min(80.0 + pos_x, RUNWAY + 80)
                    pos_x += vel * dt * 40
                    ft += vel * dt
                    if ft > 0.12: frame += 1; ft = 0
                    if ax >= RUNWAY + 80:
                        ax = RUNWAY + 80
                elif pre_jump:
                    # Continue se movendo na velocidade de um pulo enquanto os quadros de animação inicial são reproduzidos.
                    ax += pre_jump_vel * dt * 40
                    if ax >= FOUL_LINE:
                        pre_jump = False
                        foul = True
                        distance = -1.0
                    else:
                        jump_timer += dt
                        if jump_timer > 0.09:
                            jump_frame += 1
                            jump_timer = 0.0
                            if jump_frame >= 4:
                                pre_jump = False
                                in_air = True
                                jvx = pre_jump_vel
                                jvy = -9.5 - pre_jump_vel * 0.35
                elif in_air:
                    jvy += 18.0 * dt
                    ax  += jvx * dt * 55
                    ay  += jvy * 55 * dt
                    jump_timer += dt
                    if jump_timer > 0.09:
                        jump_frame = min(jump_frame + 1, len(JUMP_FRAMES[player_idx]) - 2)
                        jump_timer = 0.0
                    if ay >= GY:
                        ay = GY; in_air = False
                        jump_frame = len(JUMP_FRAMES[player_idx]) - 1
                        distance = max(0.0, (ax - FOUL_LINE) * 0.01)

                if in_air or pre_jump or not jumped:
                    cam_x = max(0.0, ax - CAM_TARGET_X)

                bnd = int(RUNWAY + 82 - cam_x)
                screen.fill(SKY)
                pygame.draw.rect(screen, SAND, (0, 390, WIDTH, 210))
                if bnd > 0:
                    pygame.draw.rect(screen, GREEN, (0, 420, min(bnd, WIDTH), 180))
                    pygame.draw.rect(screen, TRACK, (0, 390, min(bnd, WIDTH), 35))

                # linha de falta muda de cor
                tb_sx = int(FOUL_LINE - cam_x)
                if -15 < tb_sx < WIDTH:
                    board_color = RED if foul else WHITE
                    pygame.draw.rect(screen, board_color, (tb_sx, 390, 12, 35))

                for m in range(0, 13):  # 0m a 12m, 100px por metro
                    wrx = int(FOUL_LINE + m * 100)
                    srx = wrx - int(cam_x)
                    if 0 <= srx < WIDTH:
                        pygame.draw.line(screen, DARK_GRAY, (srx, 408), (srx, 425), 2)
                        draw_text(screen, f"{m}m", font_tiny, DARK_GRAY, srx - 8, 427)

                draw_text_center(screen, "LONG JUMP", font_big, BLACK, 20)
                draw_text_center(screen, f"{label}: PRESS {rk_name} TO RUN  {jk_name} TO JUMP",
                                 font_tiny, color, 80)
                pygame.draw.rect(screen, LIGHT_GRAY, (80, 130, 300, 22), border_radius=4)
                fv2 = int((vel / 11.0) * 300)
                pygame.draw.rect(screen, color, (80, 130, fv2, 22), border_radius=4)
                draw_text(screen, f"SPEED: {vel:.1f}", font_tiny, BLACK, 80, 108)

                asx = int(ax - cam_x)
                if foul:
                    draw_sprite(screen, RUN_FRAMES[player_idx], 0, asx, int(ay), scale=2)
                    draw_text_center(screen, "FOUL! DISQUALIFIED", font_med, RED, 300)
                elif pre_jump or in_air:
                    draw_sprite(screen, JUMP_FRAMES[player_idx], jump_frame, asx, int(ay), scale=2)
                elif jumped:
                    draw_sprite(screen, JUMP_FRAMES[player_idx], len(JUMP_FRAMES[player_idx]) - 1,
                                asx, int(ay) + 14, scale=2)
                    foul_sx = int(FOUL_LINE - cam_x)
                    land_sx = int(ax - cam_x)
                    pygame.draw.line(screen, GOLD, (foul_sx, 390), (land_sx, 390), 4)
                    draw_text(screen, f"{distance:.2f}M!", font_med, GOLD, asx - 30, int(ay) - 80)
                else:
                    draw_sprite(screen, RUN_FRAMES[player_idx], frame, asx, int(ay), scale=2)

                if (not in_air and not pre_jump and jumped) or foul:
                    draw_text_center(screen, "PRESS ANY KEY TO CONTINUE",
                                     font_tiny, DARK_GRAY, 530)
                    pygame.display.flip()
                    w2 = True
                    while w2:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if e.type == pygame.KEYDOWN: w2 = False
                    break

                pygame.display.flip()

            results.append(distance)

        # Mensagem de repeticao
        if results[0] < 0 and results[1] < 0:
            t_start = pygame.time.get_ticks()
            anim_t = 0
            while pygame.time.get_ticks() - t_start < 2500:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN: break
                screen.fill(SKY)
                pygame.draw.rect(screen, GREEN, (0, 480, WIDTH, 120))
                pygame.draw.rect(screen, TRACK, (0, 480, WIDTH, 20))
                draw_outcome_sprite(screen, DRAW_SPRITES[0], 80,         480, scale=4, t=anim_t)
                draw_outcome_sprite(screen, DRAW_SPRITES[1], WIDTH - 80, 480, scale=4, t=anim_t)
                draw_text_center(screen, "BOTH DISQUALIFIED!", font_med, RED, 230)
                draw_text_center(screen, "RETRYING EVENT...", font_small, DARK_GRAY, 300)
                pygame.display.flip()
                clock.tick(FPS)
                anim_t += 1
            continue

        if results[0] < 0:
            winner = 1
        elif results[1] < 0:
            winner = 0
        else:
            winner = 0 if results[0] >= results[1] else 1
        break

    return winner, results[0], results[1]


def _javelin_frame(angle_deg):
    """Map flight angle (degrees, positive = upward) to Javelin spritesheet frame."""
    if angle_deg >= 52.5: return 0   # 60° +
    if angle_deg >= 37.5: return 1   # 45° +
    if angle_deg >= 25.0: return 2   # 30° +
    if angle_deg >= 10.0: return 3   # 20° +
    if angle_deg >= -10.0: return 4  # 0° 
    if angle_deg >= -25.0: return 5  # 20° -
    if angle_deg >= -37.5: return 6  # 30° -
    if angle_deg >= -52.5: return 7  # 45° -
    return 8                          # 60° -


def event_javelin_v2():
    results = []
    CAM_TARGET_JX = int(WIDTH * 0.35)

    for player_idx in range(2):
        color      = RED if player_idx == 0 else BLUE
        label      = "PLAYER 1" if player_idx == 0 else "PLAYER 2"
        action_key = pygame.K_a if player_idx == 0 else pygame.K_l
        key_name   = "A" if player_idx == 0 else "L"

        AX = 130
        AY = 460          # chao
        THROW_LINE = 400  # linha de lancamento
        n_frames = len(JAVELIN_THROW_FRAMES[player_idx])  # ultimo frame = lancamento

        for cd in range(3, 0, -1):
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            screen.fill(SKY)
            if THROW_LINE > 0:
                pygame.draw.rect(screen, TRACK, (0, AY, min(THROW_LINE, WIDTH), HEIGHT - AY))
            if THROW_LINE < WIDTH:
                pygame.draw.rect(screen, GREEN, (THROW_LINE, AY, WIDTH - THROW_LINE, HEIGHT - AY))
            pygame.draw.line(screen, WHITE, (THROW_LINE, AY - 20), (THROW_LINE, AY + 10), 3)
            draw_text(screen, "LINE", font_tiny, WHITE, THROW_LINE - 14, AY - 36)
            draw_sprite(screen, JAVELIN_THROW_FRAMES[player_idx], 0, AX, AY, scale=2)
            draw_text_center(screen, "JAVELIN THROW", font_big, BLACK, 30)
            draw_text_center(screen, f"{label} - GET READY!", font_med, color, 110)
            draw_text_center(screen, f"PRESS {key_name} FOR SPEED THEN ANGLE", font_small, DARK_GRAY, 185)
            draw_text_center(screen, str(cd), font_big, YELLOW, 280)
            pygame.display.flip()
            pygame.time.wait(1000)

        speed        = 0.0
        speed_dir    = 1
        speed_osc    = 130.0
        locked_speed = 0.0
        angle        = 45.0
        angle_dir    = 1
        angle_speed  = 110.0
        locked_angle = 0.0
        # velocidade → movimento → angulo → pose de lancamento → voo
        phase        = "speed"

        run_frame        = 0
        run_timer        = 0.0
        walk_frames_done = 0     # contagem de frames do movimento
        throw_pose_timer = 0.0
        ax_world         = float(AX)   

        jx = jy = jvx = jvy = 0.0
        distance    = 0.0
        flight_done = False
        cam_x       = 0.0

        while True:
            dt = clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == action_key:
                    if phase == "speed":
                        locked_speed = speed
                        phase = "walk"
                        run_frame = 0
                        run_timer = 0.0
                        walk_frames_done = 0
                    elif phase == "angle":
                        locked_angle = angle
                        phase = "throw_pose"
                        throw_pose_timer = 0.0

            if phase == "speed":
                speed += speed_dir * speed_osc * dt
                if speed >= 100: speed = 100; speed_dir = -1
                elif speed <= 0: speed = 0;   speed_dir = 1
            elif phase == "walk":
                ax_world = min(ax_world + (30 + locked_speed / 100.0 * 120) * dt,
                               THROW_LINE - 30)
                run_timer += dt
                if run_timer > 0.10:
                    run_timer = 0.0
                    run_frame = (run_frame + 1) % (n_frames - 1)
                    walk_frames_done += 1
                    if walk_frames_done >= n_frames - 1:
                        phase = "angle"
            elif phase == "angle":
                angle += angle_dir * angle_speed * dt
                if angle >= 78: angle = 78; angle_dir = -1
                elif angle <= 12: angle = 12; angle_dir = 1
                run_frame = n_frames - 2   # paralizar na ultima frame
            elif phase == "throw_pose":
                run_frame = n_frames - 1
                throw_pose_timer += dt
                if throw_pose_timer >= 0.4:
                    phase = "flight"
                    sp  = 6 + locked_speed / 100.0 * 16
                    rad = math.radians(locked_angle)
                    jx  = float(ax_world + 50)
                    jy  = float(AY - 55)
                    jvx = math.cos(rad) * sp
                    jvy = -math.sin(rad) * sp
            elif phase == "flight" and not flight_done:
                jvx *= (1 - 0.35 * dt)
                jvy += 11.0 * dt
                jx  += jvx * 30 * dt
                jy  += jvy * 30 * dt
                if jy >= AY - 22:
                    jy = AY - 22; flight_done = True
                    raw = (jx - THROW_LINE) * 0.07
                    distance = raw if raw > 0 else -1.0

            if phase == "flight" and not flight_done:
                cam_x = max(0.0, jx - CAM_TARGET_JX)
            elif phase != "flight":
                cam_x = 0.0

            screen.fill(SKY)
            te_sx = int(THROW_LINE - cam_x)

            #  track 
            if te_sx > 0:
                pygame.draw.rect(screen, TRACK, (0, AY, min(te_sx, WIDTH), HEIGHT - AY))

            # setor de queda(da vara)
            gs = max(0, te_sx)
            if gs < WIDTH:
                pygame.draw.rect(screen, GREEN, (gs, AY, WIDTH - gs, HEIGHT - AY))

            # linha de lancamento
            if 0 <= te_sx <= WIDTH:
                pygame.draw.line(screen, WHITE, (te_sx, AY - 20), (te_sx, AY + 10), 3)
                draw_text(screen, "LINE", font_tiny, WHITE, te_sx - 14, AY - 36)

            # Distancia do lancamento
            for m in range(0, 90, 10):
                world_rx  = THROW_LINE + int(m / 0.07)
                screen_rx = int(world_rx - cam_x)
                if 0 <= screen_rx < WIDTH:
                    pygame.draw.line(screen, DARK_GRAY, (screen_rx, AY), (screen_rx, AY + 14), 2)
                    draw_text(screen, f"{m}m", font_tiny, DARK_GRAY, screen_rx - 8, AY + 16)

            draw_text_center(screen, "JAVELIN THROW", font_big, BLACK, 20)
            _phase_hint = {
                "speed":      f"PRESS {key_name} TO LOCK SPEED",
                "walk":       "RUNNING...",
                "angle":      f"PRESS {key_name} TO LOCK ANGLE",
                "throw_pose": "THROWING!",
                "flight":     "JAVELIN IN FLIGHT!",
            }.get(phase, "")
            draw_text_center(screen, f"{label}  -  {_phase_hint}", font_small, color, 78)

            ax_sx = int(ax_world - cam_x)
            draw_sprite(screen, JAVELIN_THROW_FRAMES[player_idx], run_frame, ax_sx, AY, scale=2)

            bx, by, bw, bh = 60, 310, 340, 32
            ds = locked_speed if phase != "speed" else speed

            if phase == "speed":
                pygame.draw.rect(screen, LIGHT_GRAY, (bx, by, bw, bh), border_radius=6)
                fc = GREEN if ds < 60 else YELLOW if ds < 85 else RED
                pygame.draw.rect(screen, fc, (bx, by, int(ds / 100 * bw), bh), border_radius=6)
                pygame.draw.rect(screen, BLACK, (bx, by, bw, bh), 2, border_radius=6)
                draw_text(screen, f"SPEED: {ds:.0f}", font_small, BLACK, bx, by - 28)
                draw_text(screen, "PRESS TO LOCK SPEED!", font_small, DARK_GRAY, bx, by + 40)
            elif phase == "angle":
                draw_text(screen, f"SPEED: {ds:.0f}", font_small, BLACK, bx, by - 54)
                af = int((angle - 12) / (78 - 12) * bw)
                pygame.draw.rect(screen, LIGHT_GRAY, (bx, by, bw, bh), border_radius=6)
                pygame.draw.rect(screen, RED, (bx, by, af, bh), border_radius=6)
                pygame.draw.rect(screen, BLACK, (bx, by, bw, bh), 2, border_radius=6)
                draw_text(screen, f"ANGLE: {angle:.0f}", font_small, BLACK, bx, by - 28)
                draw_text(screen, "PRESS TO LOCK ANGLE!", font_small, DARK_GRAY, bx, by + 40)
                rad2 = math.radians(angle)
                ae   = (ax_sx + int(math.cos(rad2) * 60), AY - 40 - int(math.sin(rad2) * 60))
                pygame.draw.line(screen, RED, (ax_sx, AY - 40), ae, 3)
                pygame.draw.polygon(screen, RED, [
                    ae,
                    (ae[0] - int(math.cos(rad2 - 0.4) * 12), ae[1] + int(math.sin(rad2 - 0.4) * 12)),
                    (ae[0] - int(math.cos(rad2 + 0.4) * 12), ae[1] + int(math.sin(rad2 + 0.4) * 12)),
                ])
            elif phase in ("throw_pose", "flight"):
                draw_text(screen, f"SPEED: {ds:.0f}", font_small, BLACK, bx, by - 28)
                draw_text(screen, f"ANGLE: {locked_angle:.0f}", font_small, BLACK, bx, by + 8)

            if phase == "flight":
                jx_sx   = int(jx - cam_x)
                ang_now = math.degrees(math.atan2(-jvy, jvx))
                jframe  = _javelin_frame(ang_now if not flight_done else -90)
                jf_surf = JAVELIN_FRAMES[jframe]
                jfw     = jf_surf.get_width() * 2
                jfh     = jf_surf.get_height() * 2
                screen.blit(pygame.transform.scale(jf_surf, (jfw, jfh)),
                            (jx_sx - jfw // 2, int(jy) - jfh // 2))
                if flight_done:
                    draw_text(screen, f"{distance:.2f}M!", font_med, GOLD,
                              jx_sx - 25, int(jy) - 55)

            if flight_done:
                draw_text_center(screen, "PRESS ANY KEY TO CONTINUE",
                                 font_tiny, DARK_GRAY, 555)
                pygame.display.flip()
                wt = True
                while wt:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if e.type == pygame.KEYDOWN: wt = False
                break

            pygame.display.flip()

        results.append(distance)

    if results[0] < 0 and results[1] < 0:
        winner = 0  # ambos DNF — P1 vence por desempate padrão
    elif results[0] < 0:
        
        winner = 1
    elif results[1] < 0:
        winner = 0
    else:
        winner = 0 if results[0] >= results[1] else 1
    return winner, results[0], results[1]


if __name__ == "__main__":
    _DEV_EVENTS = {
        "event1": (event_sprint_v2,    "100M SPRINT",   "s"),
        "event2": (event_long_jump_v2, "LONG JUMP",     "m"),
        "event3": (event_javelin_v2,   "JAVELIN THROW", "m"),
    }
    while True:
        action = start_screen()
        if action in _DEV_EVENTS:
            fn, name, unit = _DEV_EVENTS[action]
            w, v1, v2 = fn()
            _show_event_result(name, v1, v2, w, unit)
            # loop para a tela de inicio
        else:
            result = main_game()
            if result != "restart":
                break
    pygame.quit()
    sys.exit()
