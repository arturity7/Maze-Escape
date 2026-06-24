"""
╔═══════════════════════════════════════════════════════════════════╗
║                     MAZE-ESCAPE  ·  jogo.py                       ║
╠═══════════════════════════════════════════════════════════════════╣
║  ESTRUTURA DO ARQUIVO                                             ║
║                                                                   ║
║  1. IMPORTS & INIT          linha ~30                             ║
║  2. CONSTANTES & CONFIG     linha ~60                             ║
║  3. SPRITESHEET             linha ~110   get_frame(), build_frames║
║  4. CLASSE Jogador          linha ~180   update(), draw()         ║
║  5. CLASSE Inimigo          linha ~310   persegue por 4s          ║
║  6. CLASSE Onda             linha ~390   eco-localização          ║
║  7. MAPA & PAREDES          linha ~450   segmentos de linha       ║
║  8. TELA DE START           linha ~510   menu principal           ║
║  9. TELA DE COMANDOS        linha ~620   tutorial pré-jogo        ║
║  10. LOOP PRINCIPAL         linha ~680   gameplay                 ║
╚═══════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════
# 1. IMPORTS & INIT
# ═══════════════════════════════════════════════════════════════════
import pygame, os, random, math
from sys import exit

pygame.init()
pygame.mixer.init()

# ═══════════════════════════════════════════════════════════════════
# 2. CONSTANTES & CONFIG
# ═══════════════════════════════════════════════════════════════════
WIDTH, HEIGHT = 1200, 600
FPS    = 60
TITULO = "Maze Escape"
TILE   = 50

C_BG        = (8,  8,  14)
C_WALL_HI   = (200, 240, 255)
C_WALL_LO   = (60, 120, 180)
C_EXIT      = (0, 255, 120)
C_HUD       = (80, 200, 255)
C_MENU_BG   = (5, 5, 20)
C_ACCENT    = (0, 180, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITULO)
clock  = pygame.time.Clock()
fullscreen = False

# ───── Fontes ─────────────────────────────────────────────────────
pygame.font.init()
FONT_BIG   = pygame.font.SysFont("monospace", 48, bold=True)
FONT_MED   = pygame.font.SysFont("monospace", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("monospace", 16)
FONT_TINY  = pygame.font.SysFont("monospace", 13)

# ───── Áudio ──────────────────────────────────────────────────────
_base = os.path.dirname(os.path.abspath(__file__))

def _load_music(path):
    try:
        pygame.mixer.music.load(path)
        return True
    except:
        return False

_load_music(os.path.join(_base, "../assets/sons/soundtrack.mp3"))
volume_music = 0.15
pygame.mixer.music.set_volume(volume_music)
pygame.mixer.music.play(-1, fade_ms=3000)

sons_eco: list[pygame.mixer.Sound] = []
_pasta_eco = os.path.join(_base, "../assets/sons/eco-loc")
try:
    for _f in os.listdir(_pasta_eco):
        if _f.endswith(".ogg"):
            _s = pygame.mixer.Sound(os.path.join(_pasta_eco, _f))
            _s.set_volume(0.3)
            sons_eco.append(_s)
except:
    pass

BACKGROUND = None

# ═══════════════════════════════════════════════════════════════════
# 3. SPRITESHEET
# ═══════════════════════════════════════════════════════════════════
ASSETS = os.path.join(_base, "..", "assets", "imagens", "spritesheets")

P1_PATH    = os.path.join(ASSETS, "spritesheet.png")
P2_PATH    = os.path.join(ASSETS, "spritesheet2.png")
ENEMY_PATH = os.path.join(ASSETS, "../snorlax.png")

enemy_sheet = pygame.image.load(ENEMY_PATH).convert_alpha()

def build_enemy_frames(sheet, scale=40):
    """
    Spritesheet 3×4: 4 linhas (down, left, right, up), 3 colunas por linha.
    """
    frames = {}
    dirs = ["down", "left", "right", "up"]
    cell_w = sheet.get_width()  // 3
    cell_h = sheet.get_height() // 4

    for row, direction in enumerate(dirs):
        frames[direction] = []
        for col in range(3):
            src   = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
            frame = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), src)
            frame = pygame.transform.scale(frame, (scale, scale))
            frames[direction].append(frame)

    return frames

ENEMY_FRAMES = build_enemy_frames(enemy_sheet)

sheet1 = pygame.image.load(P1_PATH).convert_alpha()
sheet2 = pygame.image.load(P2_PATH).convert_alpha()

def get_frame(sheet, col, row, scale=40):
    cell_w = sheet.get_width()  // 4
    cell_h = sheet.get_height() // 4
    src    = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
    frame  = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), src)
    return pygame.transform.scale(frame, (scale, scale))

def build_frames(sheet, scale=40):
    return {
        "down":  {"walk": [get_frame(sheet, c, 0, scale) for c in range(4)],
                  "run":  [get_frame(sheet, c, 0, scale) for c in range(4)]},
        "left":  {"walk": [get_frame(sheet, c, 1, scale) for c in range(4)],
                  "run":  [get_frame(sheet, c, 1, scale) for c in range(4)]},
        "right": {"walk": [get_frame(sheet, c, 2, scale) for c in range(4)],
                  "run":  [get_frame(sheet, c, 2, scale) for c in range(4)]},
        "up":    {"walk": [get_frame(sheet, c, 3, scale) for c in range(4)],
                  "run":  [get_frame(sheet, c, 3, scale) for c in range(4)]},
    }

P1_FRAMES = build_frames(sheet1, 40)
P2_FRAMES = build_frames(sheet2, 40)

# ═══════════════════════════════════════════════════════════════════
# 4. CLASSE Jogador
# ═══════════════════════════════════════════════════════════════════
class Jogador:
    SPEED_WALK   = 3
    SPEED_RUN    = 5
    SPEED_SPRINT = 8
    SPRINT_DUR   = 400
    SPRINT_CD    = 2000

    def __init__(self, x, y, frames, controls, glow_color=(100, 180, 255)):
        self.rect      = pygame.Rect(x, y, 30, 30)
        self.direction = "down"
        self.frames    = frames
        self.controls  = controls
        self.glow      = glow_color

        self.anim_t   = 0
        self.anim_f   = 0
        self.mode     = "walk"

        self.sprinting    = False
        self.sprint_start = -9999
        self.sprint_last  = -9999
        self.trail: list  = []

        self.active = True

    def update(self, dt: int, paredes: list) -> str:
        keys  = pygame.key.get_pressed()
        c     = self.controls
        agora = pygame.time.get_ticks()

        if keys[c["sprint"]]:
            if agora - self.sprint_last >= self.SPRINT_CD:
                self.sprinting    = True
                self.sprint_start = agora
                self.sprint_last  = agora

        if self.sprinting:
            if agora - self.sprint_start >= self.SPRINT_DUR:
                self.sprinting = False
            else:
                if random.random() < 0.35:
                    self.trail.append({
                        "x": self.rect.centerx + random.randint(-3, 3),
                        "y": self.rect.centery + random.randint(-3, 3),
                        "a": 180,
                        "r": random.randint(3, 7),
                    })

        for p in self.trail[:]:
            p["a"] -= 14
            if p["a"] <= 0:
                self.trail.remove(p)

        if self.sprinting:
            speed     = self.SPEED_SPRINT
            self.mode = "run"
        elif keys[c["run"]]:
            speed     = self.SPEED_RUN
            self.mode = "run"
        else:
            speed     = self.SPEED_WALK
            self.mode = "walk"

        dx, dy = 0, 0
        if keys[c["up"]]:    dy -= speed; self.direction = "up"
        if keys[c["down"]]:  dy += speed; self.direction = "down"
        if keys[c["left"]]:  dx -= speed; self.direction = "left"
        if keys[c["right"]]: dx += speed; self.direction = "right"
        moved = dx != 0 or dy != 0

        old_x = self.rect.x
        self.rect.x += dx
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = old_x
                break

        old_y = self.rect.y
        self.rect.y += dy
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.y = old_y
                break

        if moved:
            self.anim_t += dt
            if self.anim_t >= 120:
                self.anim_t = 0
                flist       = self.frames[self.direction][self.mode]
                self.anim_f = (self.anim_f + 1) % len(flist)
        else:
            self.anim_f = 0

        return self.mode

    def draw(self, surf: pygame.Surface, cam: tuple, brightness: float = 1.0):
        agora  = pygame.time.get_ticks()
        sx     = self.rect.x - cam[0]
        sy     = self.rect.y - cam[1]
        glow_r, glow_g, glow_b = self.glow

        for p in self.trail:
            a = int(p["a"] * brightness)
            r = p["r"]
            glow_surf = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (glow_r, glow_g, glow_b, a),
                               (r*2, r*2), r*2)
            surf.blit(glow_surf, (p["x"] - cam[0] - r*2, p["y"] - cam[1] - r*2))

        flist = self.frames[self.direction][self.mode]
        frame = flist[min(self.anim_f, len(flist)-1)]

        if self.sprinting and (agora // 55) % 2 == 0:
            bright = frame.copy()
            b_int  = int(120 * brightness)
            bright.fill((b_int, b_int, b_int, 0),
                        special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(bright, (sx - 5, sy - 5))
        else:
            surf.blit(frame, (sx - 5, sy - 5))


# ═══════════════════════════════════════════════════════════════════
# 5. CLASSE Inimigo
#
#  · Fica parado até ser "ouvido" (onda de eco ou sprint do jogador)
#  · Ao ouvir: persegue o jogador mais próximo por 4 segundos
#  · O timer NÃO acumula — cada novo aviso reseta para 4 s
#  · Colisão com jogador = game over (hitkill)
#  · Spritesheet 3×4: linhas = down/left/right/up, colunas = 3 frames
# ═══════════════════════════════════════════════════════════════════
class Inimigo:
    SPEED     = 1.2
    AGRO_TIME = 2000   # ms de perseguição

    def __init__(self, x, y):
        self.vis = 0
        self.rect      = pygame.Rect(x, y, 32, 32)
        self.frames    = ENEMY_FRAMES
        self.direction = "down"
        self.anim_frame = 0
        self.anim_timer = 0
        self.agro_until = 0   # timestamp até onde persegue
        self.alvo       = None

    # ── Ativa / reseta o timer de perseguição ──────────────────────
    def ouvir(self, jogador):
        """
        Chamado quando a onda toca o inimigo OU quando um jogador
        usa sprint próximo. Sempre reseta o timer para 4 s — não acumula.
        """
        agora = pygame.time.get_ticks()
        self.agro_until = agora + self.AGRO_TIME
        self.alvo = jogador
        self.vis = 255
    def ativo(self) -> bool:
        return pygame.time.get_ticks() < self.agro_until

    # ── Atualização por frame ───────────────────────────────────────
    def update(self, dt: int, paredes: list, jogadores: list):
        if not self.ativo():
            # parado — apenas anima idle (frame 0)
            self.anim_frame = 0
            return

        ativos = [j for j in jogadores if j.active]
        if not ativos:
            return

        # Se o alvo saiu de jogo, troca para o mais próximo
        if self.alvo not in ativos:
            self.alvo = min(ativos,
                            key=lambda j: math.dist(self.rect.center,
                                                    j.rect.center))

        dx = self.alvo.rect.centerx - self.rect.centerx
        dy = self.alvo.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        vx   = dx / dist * self.SPEED
        vy   = dy / dist * self.SPEED

        # Direção visual
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        # Movimento com colisão de parede
        old_x = self.rect.x
        self.rect.x += vx
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = old_x
                break

        old_y = self.rect.y
        self.rect.y += vy
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.y = old_y
                break

        # Animação
        self.anim_timer += dt
        if self.anim_timer >= 120:
            self.anim_timer  = 0
            self.anim_frame  = (self.anim_frame + 1) % 3

        # Hitkill
        for j in ativos:
            if self.rect.colliderect(j.rect):
                print("GAME OVER — inimigo alcançou o jogador!")
                pygame.quit()
                exit()

    def draw(self, surf: pygame.Surface, cam: tuple, idx: int):
        if idx in enemy_vis:
            alpha = enemy_vis[idx]
        else:
            alpha = 0  # invisível total
        frame = self.frames[self.direction][self.anim_frame].copy()
        frame.set_alpha(alpha)
        surf.blit(frame, (self.rect.x - cam[0], self.rect.y - cam[1]))


# ═══════════════════════════════════════════════════════════════════
# 6. CLASSE Onda (eco-localização)
# ═══════════════════════════════════════════════════════════════════
class Onda:
    SPEED  = 5
    MAX_R  = 200
    PART_N = 3

    def __init__(self, cx, cy):
        self.cx    = cx
        self.cy    = cy
        self.r     = 0
        self.ativa = True
        self.parts: list = []

    def update(self):
        self.r += self.SPEED
        if self.r >= self.MAX_R:
            self.ativa = False

        if self.ativa:
            for _ in range(self.PART_N):
                ang = random.uniform(0, math.tau)
                self.parts.append({
                    "x":    self.cx + math.cos(ang) * self.r,
                    "y":    self.cy + math.sin(ang) * self.r,
                    "vx":   math.cos(ang) * random.uniform(0.3, 1.8),
                    "vy":   math.sin(ang) * random.uniform(0.3, 1.8),
                    "life": random.randint(10, 25),
                    "sz":   random.uniform(1.2, 3.5),
                })

        for p in self.parts[:]:
            p["x"]    += p["vx"]
            p["y"]    += p["vy"]
            p["life"] -= 2
            if p["life"] <= 0:
                self.parts.remove(p)

    def reveal(self, wall_vis: dict, segs_enum: list):
        global exit_vis

        for idx, (p1, p2) in segs_enum:
            mx = (p1[0] + p2[0]) * 0.5
            my = (p1[1] + p2[1]) * 0.5
            d  = math.dist((self.cx, self.cy), (mx, my))
            if d > 200:
                continue
            if abs(d - self.r) < 8:
                wall_vis[idx] = 200


    def reveal_inimigo(self, wall_vis: dict, segs_enum: list, inimigos: list):
        for i, inimigo in enumerate(inimigos):
            inimigo.draw(screen, cam, i)
            if abs(d - self.r) < 15:
                enemy_vis[i] = 255

        ex = EXIT_RECT.centerx
        ey = EXIT_RECT.centery
        d_exit = math.dist((self.cx, self.cy), (ex, ey))
        if abs(d_exit - self.r) < 15:
            exit_vis = 255

    def tocar_inimigos(self, inimigos: list, jogadores: list):
        """
        Verifica se a frente da onda toca algum inimigo.
        Se sim, chama inimigo.ouvir() com o jogador mais próximo do inimigo.
        """
        ativos = [j for j in jogadores if j.active]
        if not ativos:
            return

        for inimigo in inimigos:
            d = math.dist((self.cx, self.cy), inimigo.rect.center)
            if abs(d - self.r) < 6:          # tolerância de toque
                alvo = min(ativos,
                           key=lambda j: math.dist(inimigo.rect.center,
                                                   j.rect.center))
                inimigo.ouvir(alvo)

    def draw(self, surf: pygame.Surface, cam: tuple, brightness: float = 1.0):
        if not self.ativa and not self.parts:
            return
        cx_s = self.cx - cam[0]
        cy_s = self.cy - cam[1]

        if self.ativa:
            fade = 1.0 - self.r / self.MAX_R
            a    = int(120 * fade * brightness)
            d    = self.r * 2 + 4
            ring = pygame.Surface((int(d), int(d)), pygame.SRCALPHA)
            pygame.draw.circle(ring, (80, 210, 255, a),
                               (int(self.r+2), int(self.r+2)),
                               int(self.r), 2)
            surf.blit(ring, (int(cx_s - self.r - 2), int(cy_s - self.r - 2)))

        for p in self.parts:
            px_s = int(p["x"] - cam[0])
            py_s = int(p["y"] - cam[1])
            a    = max(0, int(220 * p["life"] / 70 * brightness))
            sz   = max(1, int(p["sz"]))
            gs   = pygame.Surface((sz*4, sz*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (100, 230, 255, a), (sz*2, sz*2), sz*2)
            pygame.draw.circle(gs, (220, 255, 255, min(255, a+60)),
                               (sz*2, sz*2), sz)
            surf.blit(gs, (px_s - sz*2, py_s - sz*2))


# ═══════════════════════════════════════════════════════════════════
# 7. MAPA & PAREDES
# ═══════════════════════════════════════════════════════════════════
MAPA_LINHAS = [
    "1111111111111111111111111111",
    "1S00011111100000001110001111",
    "1S11011000001111100001000111",
    "1011011011101100001101110011",
    "1010000011100110111101110111",
    "1010111011110110001000000111",
    "1000100000010111000011011111",
    "1110111111110000111110000001",
    "1000000000000010000001110101",
    "1011111111001011111101000101",
    "1010000001010101000100010101",
    "1010110111010001010111110101",
    "1010100111010111010111110101",
    "1000101100000001010100000111",
    "1110101101101100010110111111",
    "1110001101100111110000011111",
    "1110101101101100110111000001",
    "1110000001001110110111001111",
    "1101110110101100000000011011",
    "1100110000101110111110110011",
    "1101001110101110011100000111",
    "1100000000101100011110111001",
    "1101111110001101111110000011",
    "1111111111111111111111111111",
]

mapa      = [list(ln) for ln in MAPA_LINHAS]
MAPA_ROWS = len(mapa)
MAPA_COLS = len(mapa[0])
MAPA_PX_W = MAPA_COLS * TILE
MAPA_PX_H = MAPA_ROWS * TILE

EXIT_TILE_X = MAPA_COLS - 2
EXIT_TILE_Y = MAPA_ROWS - 2
mapa[EXIT_TILE_Y][EXIT_TILE_X] = "0"
EXIT_RECT = pygame.Rect(EXIT_TILE_X * TILE, EXIT_TILE_Y * TILE, TILE, TILE)

paredes = [
    pygame.Rect(x * TILE, y * TILE, TILE, TILE)
    for y, linha in enumerate(mapa)
    for x, t in enumerate(linha)
    if t == "1"
]

def _gerar_segmentos(mapa):
    segs = []
    for y, linha in enumerate(mapa):
        for x, t in enumerate(linha):
            if t == "1":
                tx, ty = x * TILE, y * TILE
                segs += [
                    ((tx,      ty),      (tx+TILE, ty)),
                    ((tx,      ty+TILE), (tx+TILE, ty+TILE)),
                    ((tx,      ty),      (tx,      ty+TILE)),
                    ((tx+TILE, ty),      (tx+TILE, ty+TILE)),
                ]
    return segs

wall_segments = _gerar_segmentos(mapa)
wall_segs_e   = list(enumerate(wall_segments))
wall_vis: dict = {}
exit_vis = 0
enemy_vis = {}  # id(inimigo) -> alpha

def _spawns_start_zone():
    return [
        (x*TILE + TILE//2 - 15, y*TILE + TILE//2 - 15)
        for y, ln in enumerate(mapa)
        for x, t in enumerate(ln)
        if t == "S"
    ]

def _spawn_start(excluir=(), min_dist=120):
    cands = _spawns_start_zone()
    random.shuffle(cands)
    for c in cands:
        if all(math.dist(c, e) >= min_dist for e in excluir):
            return c
    return cands[0] if cands else (TILE, TILE)


# ═══════════════════════════════════════════════════════════════════
# 8. TELA DE START
# ═══════════════════════════════════════════════════════════════════
def _draw_slider(surf, x, y, w, val, label, mx, my):
    pygame.draw.rect(surf, (30,50,70), (x, y-4, w, 8), border_radius=4)
    fill_w = int(w * val)
    pygame.draw.rect(surf, C_ACCENT, (x, y-4, fill_w, 8), border_radius=4)
    tx    = x + fill_w
    hover = abs(mx - tx) < 12 and abs(my - y) < 12
    pygame.draw.circle(surf, (255,255,255) if hover else (180,220,255),
                       (tx, y), 9 if hover else 7)
    lbl = FONT_SMALL.render(label, True, (120,180,220))
    surf.blit(lbl, (x, y - 26))

def _toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

def tela_start():
    vol = volume_music
    bri = 1.0
    dragging = None

    SL_X      = WIDTH//2 - 150
    SL_W      = 300
    SL_VOL_Y  = HEIGHT//2 + 20
    SL_BRI_Y  = HEIGHT//2 + 80
    PLAY_R    = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 150, 180, 48)

    stars = [{"x": random.randint(0, WIDTH),
              "y": random.randint(0, HEIGHT),
              "r": random.uniform(0.5, 2),
              "sp": random.uniform(0.2, 0.8)} for _ in range(80)]
    title_anim = 0.0

    while True:
        dt = clock.tick(FPS)
        title_anim += dt * 0.002
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                _toggle_fullscreen()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    if PLAY_R.collidepoint(mx, my):
                        pygame.mixer.music.set_volume(vol)
                        return vol, bri
                    if SL_X <= mx <= SL_X + SL_W:
                        if abs(my - SL_VOL_Y) < 14:
                            dragging = "vol"
                        if abs(my - SL_BRI_Y) < 14:
                            dragging = "bri"
            if ev.type == pygame.MOUSEBUTTONUP:
                dragging = None
            if ev.type == pygame.MOUSEMOTION and dragging:
                t = max(0.0, min(1.0, (mx - SL_X) / SL_W))
                if dragging == "vol":
                    vol = t
                    pygame.mixer.music.set_volume(vol)
                if dragging == "bri":
                    bri = t

        screen.fill(C_MENU_BG)

        for st in stars:
            st["y"] += st["sp"]
            if st["y"] > HEIGHT:
                st["y"] = 0; st["x"] = random.randint(0, WIDTH)
            a = int(120 + 80 * math.sin(title_anim + st["x"] * 0.1))
            pygame.draw.circle(screen, (a//2, a, 255),
                               (int(st["x"]), int(st["y"])), int(st["r"]))

        pulse  = 0.85 + 0.15 * math.sin(title_anim * 2)
        t_surf = FONT_BIG.render("MAZE ESCAPE", True, C_ACCENT)
        t_surf = pygame.transform.scale(t_surf,
                     (int(t_surf.get_width() * pulse),
                      int(t_surf.get_height() * pulse)))
        screen.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 110)))

        sub = FONT_SMALL.render("eco-localização · labirinto · fuga",
                                True, (80,140,180))
        screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 - 55)))

        _draw_slider(screen, SL_X, SL_VOL_Y, SL_W, vol,
                     f"VOLUME  {int(vol*100):3d}%", mx, my)
        _draw_slider(screen, SL_X, SL_BRI_Y, SL_W, bri,
                     f"BRILHO  {int(bri*100):3d}%", mx, my)

        hover   = PLAY_R.collidepoint(mx, my)
        col_btn = (0, 210, 100) if hover else (0, 160, 80)
        pygame.draw.rect(screen, col_btn, PLAY_R, border_radius=8)
        pygame.draw.rect(screen, (0, 255, 120), PLAY_R, 2, border_radius=8)
        lbl = FONT_MED.render("▶  JOGAR", True,
                              (0,0,0) if hover else (200,255,200))
        screen.blit(lbl, lbl.get_rect(center=PLAY_R.center))

        hint = FONT_TINY.render("F11 = tela cheia   |   ESC = sair",
                                True, (50,70,90))
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 20)))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════════
# 9. TELA DE COMANDOS
# ═══════════════════════════════════════════════════════════════════
COMANDOS = [
    ("── JOGADOR 1 ──", ""),
    ("W A S D",         "Mover"),
    ("Shift esq.",      "Correr (velocidade maior)"),
    ("Q",               "Sprint + brilho  (cooldown 2 s)"),
    ("E",               "Emitir eco-localização"),
    ("",                ""),
    ("── JOGADOR 2 ──", ""),
    ("↑ ↓ ← →",        "Mover"),
    ("Shift dir.",      "Correr"),
    ("0 (numpad)",      "Sprint + brilho"),
    ("Enter numpad",    "Emitir eco-localização"),
    ("",                ""),
    ("── GERAL ──",    ""),
    ("9",               "Adicionar Jogador 2"),
    ("F11",             "Tela cheia"),
    ("- / =",           "Diminuir / aumentar volume"),
    ("",                ""),
    ("🏁  Chegue à SAÍDA (borda verde) para vencer!", ""),
]

def tela_comandos():
    anim = 0.0
    while True:
        dt    = clock.tick(FPS)
        anim += dt * 0.001

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

        screen.fill(C_MENU_BG)

        t = FONT_MED.render("CONTROLES", True, C_ACCENT)
        screen.blit(t, t.get_rect(center=(WIDTH//2, 38)))
        pygame.draw.line(screen, (0,80,120), (WIDTH//4, 60), (WIDTH*3//4, 60), 1)

        y_off  = 80
        line_h = 24
        half   = len(COMANDOS) // 2 + 1

        for i, (key, desc) in enumerate(COMANDOS):
            col_x = 80 if i < half else WIDTH//2 + 40
            row_y = y_off + (i % half) * line_h

            if desc == "":
                if key:
                    surf = FONT_SMALL.render(key, True, (0, 200, 180))
                    screen.blit(surf, (col_x, row_y))
                continue

            k_surf = FONT_SMALL.render(key,  True, (220, 220, 100))
            d_surf = FONT_SMALL.render(desc, True, (160, 190, 210))
            screen.blit(k_surf, (col_x, row_y))
            screen.blit(d_surf, (col_x + 180, row_y))

        if int(anim * 2) % 2 == 0:
            hint = FONT_SMALL.render("Pressione ENTER ou clique para começar",
                                     True, (80, 160, 80))
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 28)))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════════
# INÍCIO — menus e criação de objetos
# ═══════════════════════════════════════════════════════════════════
volume_music, brightness = tela_start()
tela_comandos()

p1_pos = _spawn_start()
p2_pos = _spawn_start(excluir=[p1_pos])
if p2_pos == p1_pos:
    cands  = _spawns_start_zone()
    p2_pos = next((c for c in cands if c != p1_pos), p1_pos)

p1 = Jogador(
    p1_pos[0], p1_pos[1],
    frames   = P1_FRAMES,
    controls = {
        "up":     pygame.K_w,
        "down":   pygame.K_s,
        "left":   pygame.K_a,
        "right":  pygame.K_d,
        "run":    pygame.K_LSHIFT,
        "sprint": pygame.K_q,
    },
    glow_color=(100, 180, 255),
)

p2 = Jogador(
    p2_pos[0], p2_pos[1],
    frames   = P2_FRAMES,
    controls = {
        "up":     pygame.K_UP,
        "down":   pygame.K_DOWN,
        "left":   pygame.K_LEFT,
        "right":  pygame.K_RIGHT,
        "run":    pygame.K_RSHIFT,
        "sprint": pygame.K_KP0,
    },
    glow_color=(80, 255, 100),
)
p2.active = False

jogadores = [p1, p2]

# ── Spawn de inimigos em células livres ───────────────────────────
inimigos: list[Inimigo] = []
for _ in range(6):
    while True:
        x    = random.randint(1, MAPA_COLS - 2) * TILE
        y    = random.randint(1, MAPA_ROWS - 2) * TILE
        test = pygame.Rect(x, y, 32, 32)
        if not any(test.colliderect(p) for p in paredes):
            break
    inimigos.append(Inimigo(x, y))

ondas: list[Onda] = []
ECO_CD   = 1500
eco_last = {p1: -9999, p2: -9999}

show_vol  = False
vol_timer = 0

SPRINT_ALERT_DIST = 200   # raio em px: sprint acorda inimigos nessa distância

def _camera(jogadores, sw, sh):
    ativos = [j for j in jogadores if j.active]
    cx = sum(j.rect.centerx for j in ativos) / len(ativos)
    cy = sum(j.rect.centery for j in ativos) / len(ativos)
    return (
        max(0, min(cx - sw//2, MAPA_PX_W - sw)),
        max(0, min(cy - sh//2, MAPA_PX_H - sh)),
    )

cam        = (0, 0)
ganhou     = False
win_timer  = 0
win_player = 0


# ═══════════════════════════════════════════════════════════════════
# 10. LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
while True:
    dt    = clock.tick(FPS)
    agora = pygame.time.get_ticks()
    sw, sh = screen.get_size()

    # ── Eventos ───────────────────────────────────────────────────
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); exit()

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_F11:
                _toggle_fullscreen()

            if ev.key == pygame.K_MINUS:
                volume_music = max(0.0, volume_music - 0.05)
                pygame.mixer.music.set_volume(volume_music)
                show_vol = True; vol_timer = agora
            if ev.key == pygame.K_EQUALS:
                volume_music = min(1.0, volume_music + 0.05)
                pygame.mixer.music.set_volume(volume_music)
                show_vol = True; vol_timer = agora

            if ev.key == pygame.K_9 and not p2.active:
                p2.active = True
                npos = _spawn_start(excluir=[(p1.rect.x, p1.rect.y)])
                p2.rect.topleft = npos

            # Eco P1
            if ev.key == pygame.K_e and p1.active:
                if agora - eco_last[p1] >= ECO_CD:
                    eco_last[p1] = agora
                    ondas.append(Onda(p1.rect.centerx, p1.rect.centery))
                    if sons_eco:
                        random.choice(sons_eco).play()

            # Eco P2
            if ev.key == pygame.K_KP_ENTER and p2.active:
                if agora - eco_last[p2] >= ECO_CD:
                    eco_last[p2] = agora
                    ondas.append(Onda(p2.rect.centerx, p2.rect.centery))
                    if sons_eco:
                        random.choice(sons_eco).play()

            if ganhou and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                import subprocess, sys
                subprocess.Popen([sys.executable] + sys.argv)
                pygame.quit(); exit()

    # ── Lógica ────────────────────────────────────────────────────
    if not ganhou:
        p1.update(dt, paredes)
        if p2.active:
            p2.update(dt, paredes)

        # Sprint acorda inimigos próximos
        for jogador in [p for p in jogadores if p.active]:
            if jogador.sprinting:
                for inimigo in inimigos:
                    d = math.dist(jogador.rect.center, inimigo.rect.center)
                    if d <= SPRINT_ALERT_DIST:
                        inimigo.ouvir(jogador)

        # Ondas: atualização + reveal de paredes + toque em inimigos
        for o in ondas[:]:
            o.update()
            o.reveal(wall_vis, wall_segs_e)
            o.tocar_inimigos(inimigos, jogadores)
            if not o.ativa and not o.parts:
                ondas.remove(o)

        # Fade das paredes
        for idx in list(wall_vis):
            wall_vis[idx] -= 2
            if wall_vis[idx] <= 0:
                del wall_vis[idx]
        if exit_vis > 0:
            exit_vis -= 2

    for i in list(enemy_vis):
        enemy_vis[i] -= 4
        if enemy_vis[i] <= 0:
            del enemy_vis[i]

        # Atualiza inimigos
        for inimigo in inimigos:
            inimigo.update(dt, paredes, jogadores)

        # Checa vitória
        for i, j in enumerate(jogadores, 1):
            if j.active and j.rect.colliderect(EXIT_RECT):
                ganhou     = True
                win_player = i
                win_timer  = agora
                break
    cam = _camera(jogadores, sw, sh)
    # ── Renderização ──────────────────────────────────────────────
    if BACKGROUND:
        screen.blit(BACKGROUND, (0, 0))
    else:
        screen.fill(C_BG)

    # Ondas
    for o in ondas:
        o.draw(screen, cam, brightness)

    # Saída
    if exit_vis > 0:
        ex_s  = (EXIT_RECT.x - cam[0], EXIT_RECT.y - cam[1])
        pulse = 0.5 + 0.5 * math.sin(agora * 0.003)
        alpha = int(exit_vis * pulse)

        exit_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        exit_surf.fill((0, 255, 100, alpha))
        screen.blit(exit_surf, ex_s)
        pygame.draw.rect(screen, (0, 255, 100, alpha),
                         pygame.Rect(ex_s[0], ex_s[1], TILE, TILE), 2)
        lbl = FONT_TINY.render("SAÍDA", True, (0, 255, 100))
        lbl.set_alpha(alpha)
        screen.blit(lbl, (ex_s[0] + TILE//2 - lbl.get_width()//2,
                           ex_s[1] + TILE//2 - lbl.get_height()//2))

    # Paredes reveladas
    for idx, (pt1, pt2) in wall_segs_e:
        if idx not in wall_vis:
            continue
        a   = wall_vis[idx]
        t   = a / 200.0 * brightness
        r   = int(C_WALL_LO[0] + (C_WALL_HI[0] - C_WALL_LO[0]) * t)
        g   = int(C_WALL_LO[1] + (C_WALL_HI[1] - C_WALL_LO[1]) * t)
        b   = int(C_WALL_LO[2] + (C_WALL_HI[2] - C_WALL_LO[2]) * t)
        sx1 = pt1[0] - cam[0]
        sy1 = pt1[1] - cam[1]
        sx2 = pt2[0] - cam[0]
        sy2 = pt2[1] - cam[1]
        pygame.draw.line(screen, (r, g, b), (sx1, sy1), (sx2, sy2), 2)
        pygame.draw.line(screen, (200, 240, 255), (sx1, sy1), (sx2, sy2), 1)

    # Inimigos
    for i, inimigo in enumerate(inimigos):
        inimigo.draw(screen, cam, i)

    # Jogadores
    p1.draw(screen, cam, brightness)
    if p2.active:
        p2.draw(screen, cam, brightness)

    # HUD volume
    if show_vol:
        if agora - vol_timer > 2500:
            show_vol = False
        else:
            pygame.draw.rect(screen, (30,50,70), (16,16,204,10), border_radius=5)
            pygame.draw.rect(screen, C_ACCENT,
                             (16,16,int(volume_music*200)+4,10), border_radius=5)
            v_lbl = FONT_TINY.render(f"VOL {int(volume_music*100)}%",
                                     True, (180,220,255))
            screen.blit(v_lbl, (224, 12))

    # HUD eco P1
    if p1.active:
        cd_left  = max(0, ECO_CD - (agora - eco_last[p1]))
        bw       = 70
        pygame.draw.rect(screen, (20,40,60), (16, sh-26, bw, 8), border_radius=4)
        ready_w  = int(bw * (1 - cd_left / ECO_CD))
        pygame.draw.rect(screen, C_HUD, (16, sh-26, ready_w, 8), border_radius=4)
        eco_txt  = FONT_TINY.render("ECO [E]" + (" ✓" if cd_left == 0 else ""),
                                    True, C_HUD)
        screen.blit(eco_txt, (16, sh-44))

    # Dica P2
    if not p2.active:
        d = FONT_TINY.render("[9] Adicionar Jogador 2", True, (50,80,100))
        screen.blit(d, d.get_rect(center=(sw//2, sh-16)))

    # Tela de vitória
    if ganhou:
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))
        w1 = FONT_BIG.render(f"JOGADOR {win_player} SAIU!", True, C_EXIT)
        w2 = FONT_MED.render("Você escapou do labirinto", True, (180,255,200))
        w3 = FONT_SMALL.render("ENTER ou ESPAÇO para jogar de novo",
                               True, (80,160,80))
        screen.blit(w1, w1.get_rect(center=(sw//2, sh//2 - 60)))
        screen.blit(w2, w2.get_rect(center=(sw//2, sh//2)))
        screen.blit(w3, w3.get_rect(center=(sw//2, sh//2 + 60)))

    pygame.display.flip()