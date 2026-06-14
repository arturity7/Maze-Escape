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
║  5. CLASSE Morcego          linha ~310   inimigo invisível        ║
║  6. CLASSE Onda             linha ~370   eco-localização          ║
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
TILE   = 64          

C_BG        = (8,  8,  14)   # Fundo do jogo (escuro)
C_WALL_HI   = (200, 240, 255) # Linha de parede iluminada (branco-azul)
C_WALL_LO   = (60, 120, 180)  # Linha de parede apagando
C_EXIT      = (0, 255, 120)   # Cor da saída
C_HUD       = (80, 200, 255)  # Texto HUD
C_MENU_BG   = (5, 5, 20)      # Fundo do menu
C_ACCENT    = (0, 180, 255)   # Destaque azul-ciano

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
_base = os.path.dirname(__file__)

def _load_music(path):
    try:
        pygame.mixer.music.load(path)
        return True
    except:
        return False

_load_music(os.path.join(_base, "../assets/sons/soundtrack.mp3"))
volume_music = 0.15         # 0.0 – 1.0  (controlado pelo menu)
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

# ── Sons de morcego (deixados em aberto) ──────────────────────────
# SOM_BAT_FLAP    = pygame.mixer.Sound("assets/sons/bat_flap.ogg")
# SOM_BAT_SCREECH = pygame.mixer.Sound("assets/sons/bat_screech.ogg")
# SOM_BAT_FLAP.set_volume(0.15)
# SOM_BAT_SCREECH.set_volume(0.2)

# ── Background (deixado em aberto) ────────────────────────────────
# BACKGROUND = pygame.image.load("assets/imagens/background.png").convert()
# BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))
BACKGROUND = None   # <- substitua None pela variável acima

# ═══════════════════════════════════════════════════════════════════
# 3. SPRITESHEET
#
#  Layout confirmado (cada célula = 128 × 256 px):
#
#  ROW walk  (y=88):
#   DOWN  idle/walk : cols 0, 1
#   UP    idle/walk : cols 2, 3
#   LEFT  walk      : cols 9, 10, 11, 12
#   RIGHT walk      : cols 16, 17, 18, 19
#
#  ROW run   (y=344):
#   DOWN  run       : cols 5, 6
#   UP    run       : cols 0, 1   (row run)
#   LEFT  run       : cols 11, 12, 13, 14
#   RIGHT run       : cols 16, 17, 18, 19
# ═══════════════════════════════════════════════════════════════════
_SPRITE_PATH = os.path.join(_base, "../assets/imagens/spritesheet.bmp")
_sheet = pygame.image.load(_SPRITE_PATH).convert_alpha()

CELL_W = 128   # largura de cada frame no spritesheet
CELL_H = 256   # altura de cada frame no spritesheet

Y_WALK = 88    # y da linha de caminhada
Y_RUN  = 344   # y da linha de corrida

def get_frame(col: int, row_y: int, scale: int = 40) -> pygame.Surface:
    """
    Recorta um único frame da spritesheet e o escala.
    col   : coluna (0-21, cada uma tem 128px)
    row_y : posição y da linha no spritesheet (Y_WALK ou Y_RUN)
    scale : tamanho final em pixels (quadrado)
    """
    src = pygame.Rect(col * CELL_W, row_y, CELL_W, CELL_H)
    buf = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
    buf.blit(_sheet, (0, 0), src)
    return pygame.transform.scale(buf, (scale, scale))

def build_frames(y_walk: int, y_run: int, scale: int = 40) -> dict:
    """
    Constrói dicionário de frames para as 4 direções × 2 modos.
    Retorna: { "down": {"walk": [...], "run": [...]}, ... }
    """
    return {
        "down":  {
            "walk": [get_frame(c, y_walk, scale) for c in [0, 1]],
            "run":  [get_frame(c, y_run,  scale) for c in [5, 6]],
        },
        "up":    {
            "walk": [get_frame(c, y_walk, scale) for c in [2, 3]],
            "run":  [get_frame(c, y_run,  scale) for c in [0, 1]],
        },
        "left":  {
            "walk": [get_frame(c, y_walk, scale) for c in [9, 10, 11, 12]],
            "run":  [get_frame(c, y_run,  scale) for c in [11, 12, 13, 14]],
        },
        "right": {
            "walk": [get_frame(c, y_walk, scale) for c in [16, 17, 18, 19]],
            "run":  [get_frame(c, y_run,  scale) for c in [16, 17, 18, 19]],
        },
    }

P1_FRAMES = build_frames(Y_WALK, Y_RUN, scale=40)

def _tint(frames: dict, rgba_add: tuple) -> dict:
    """Aplica tinte aditivo sobre todos os frames de um dicionário."""
    result = {}
    for d, modes in frames.items():
        result[d] = {}
        for m, lst in modes.items():
            tinted = []
            for s in lst:
                ts = s.copy()
                overlay = pygame.Surface(ts.get_size(), pygame.SRCALPHA)
                overlay.fill(rgba_add)
                ts.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                tinted.append(ts)
            result[d][m] = tinted
    return result

P2_FRAMES = _tint(build_frames(Y_WALK, Y_RUN, scale=40), (0, 60, 0, 0))

# Frames do morcego (visíveis apenas em debug/eco)
# Bat brown row: y ≈ 1040, CELL=128 -> cols 0,1,2
BAT_FRAMES = [get_frame(c, 1040, scale=28) for c in [0, 1, 2]]

# ═══════════════════════════════════════════════════════════════════
# 4. CLASSE Jogador
#
#  Responsabilidades:
#  · Movimento com WASD / setas
#  · Colisão com paredes (eixo X separado do Y)
#  · Três velocidades: walk / run (Shift) / sprint (Q ou 0)
#  · Sprint: dura 400 ms, tem cooldown de 2 s, deixa rastro luminoso
#    e faz o sprite piscar (blink)
#  · Animação por direção + modo (walk/run)
# ═══════════════════════════════════════════════════════════════════
class Jogador:
    SPEED_WALK   = 3
    SPEED_RUN    = 5
    SPEED_SPRINT = 8
    SPRINT_DUR   = 400     # ms que o sprint dura
    SPRINT_CD    = 2000    # ms de cooldown após sprint

    def __init__(self, x, y, frames, controls, glow_color=(100, 180, 255)):
        self.rect      = pygame.Rect(x, y, 30, 30)
        self.direction = "down"
        self.frames    = frames
        self.controls  = controls
        self.glow      = glow_color

        self.anim_t    = 0       # acumulador de tempo (ms)
        self.anim_f    = 0       # índice do frame atual
        self.mode      = "walk"  # "walk" ou "run"

        self.sprinting     = False
        self.sprint_start  = -9999
        self.sprint_last   = -9999
        self.trail: list   = []  # partículas do rastro

        self.active = True

    def update(self, dt: int, paredes: list) -> str:
        """
        Chama a cada frame. Retorna o modo atual ("walk"/"run").
        dt      : delta-time em ms
        paredes : lista de pygame.Rect das paredes
        """
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
                # Gera partículas do rastro
                if random.random() < 0.35:
                    self.trail.append({
                        "x":    self.rect.centerx + random.randint(-3, 3),
                        "y":    self.rect.centery + random.randint(-3, 3),
                        "a":    180,    # alpha inicial
                        "r":    random.randint(3, 7),  # raio
                    })

        for p in self.trail[:]:
            p["a"] -= 14
            if p["a"] <= 0:
                self.trail.remove(p)

        if self.sprinting:
            speed = self.SPEED_SPRINT
            self.mode = "run"
        elif keys[c["run"]]:
            speed = self.SPEED_RUN
            self.mode = "run"
        else:
            speed = self.SPEED_WALK
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

        # Só avança o frame quando está se movendo
        if moved:
            self.anim_t += dt
            if self.anim_t >= 120:   # troca de frame a cada 120 ms
                self.anim_t = 0
                flist = self.frames[self.direction][self.mode]
                self.anim_f = (self.anim_f + 1) % len(flist)
        else:
            self.anim_f = 0          # volta ao frame parado

        return self.mode

    def draw(self, surf: pygame.Surface, cam: tuple, brightness: float = 1.0):
        """
        Desenha rastro + sprite na posição de tela.
        cam        : (cam_x, cam_y) offset da câmera
        brightness : 0.0–1.0 (ajustado pelo slider do menu)
        """
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
            surf.blit(glow_surf,
                      (p["x"] - cam[0] - r*2, p["y"] - cam[1] - r*2))

        flist  = self.frames[self.direction][self.mode]
        frame  = flist[min(self.anim_f, len(flist)-1)]

        if self.sprinting and (agora // 55) % 2 == 0:
            bright = frame.copy()
            b_int  = int(120 * brightness)
            bright.fill((b_int, b_int, b_int, 0),
                        special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(bright, (sx - 5, sy - 5))
        else:
            surf.blit(frame, (sx - 5, sy - 5))


# ═══════════════════════════════════════════════════════════════════
# 5. CLASSE Morcego
#
#  · Invisível durante o jogo (self.visible = False por design)
#  · Patrulha o labirinto e persegue o jogador se estiver próximo
#  · Anima frames mesmo invisível (pronto para debug ou se quiser
#    revelar com eco no futuro)
#  · Slots de som comentados – adicione os caminhos quando tiver
#    os arquivos de áudio
# ═══════════════════════════════════════════════════════════════════
class Morcego:
    SPEED         = 1.1
    DETECT_RANGE  = 280   # px – raio de detecção do jogador
    SOUND_CD_MIN  = 1500  # ms mínimos entre sons
    SOUND_CD_MAX  = 4500  # ms máximos entre sons

    def __init__(self, x, y):
        self.rect      = pygame.Rect(x, y, 24, 24)
        self.vx        = random.choice([-1, 1]) * self.SPEED
        self.vy        = random.choice([-1, 1]) * self.SPEED
        self.anim_t    = 0
        self.anim_f    = 0
        self.snd_timer = pygame.time.get_ticks() + random.randint(
            self.SOUND_CD_MIN, self.SOUND_CD_MAX)

    def update(self, dt: int, paredes: list, jogadores: list):
        """Move o morcego; persegue jogadores próximos."""
        # ── IA: perseguição ───────────────────────────────────────
        ativos = [j for j in jogadores if j.active]
        if ativos:
            alvo = min(ativos, key=lambda j: math.dist(
                self.rect.center, j.rect.center))
            dist = math.dist(self.rect.center, alvo.rect.center)
            if dist < self.DETECT_RANGE:
                dx = alvo.rect.centerx - self.rect.centerx
                dy = alvo.rect.centery - self.rect.centery
                n  = max(dist, 0.1)
                self.vx = dx / n * self.SPEED
                self.vy = dy / n * self.SPEED

        # ── Movimento com colisão ──────────────────────────────────
        old_x = self.rect.x
        self.rect.x += self.vx
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = old_x
                self.vx = -self.vx
                break

        old_y = self.rect.y
        self.rect.y += self.vy
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.y = old_y
                self.vy = -self.vy
                break

        # ── Animação ───────────────────────────────────────────────
        self.anim_t += dt
        if self.anim_t >= 100:
            self.anim_t = 0
            self.anim_f = (self.anim_f + 1) % len(BAT_FRAMES)

        # ── Som (descomente quando tiver os arquivos) ──────────────
        # agora = pygame.time.get_ticks()
        # if agora >= self.snd_timer:
        #     SOM_BAT_FLAP.play()
        #     self.snd_timer = agora + random.randint(
        #         self.SOUND_CD_MIN, self.SOUND_CD_MAX)


# ═══════════════════════════════════════════════════════════════════
# 6. CLASSE Onda (eco-localização)
#
#  · Emitida ao pressionar E (P1) ou Enter-numpad (P2)
#  · Expande como anel com partículas nas bordas
#  · Ao tocar em segmentos de parede, registra-os em wall_visibility
#    com alpha=200 (eles vão apagando a ~1.5 pts/frame)
#  · Radius máximo reduzido para 220 px (era 350)
# ═══════════════════════════════════════════════════════════════════
class Onda:
    SPEED   = 5
    MAX_R   = 150    # ← radius máximo
    PART_N  = 3      # partículas por frame

    def __init__(self, cx, cy):
        self.cx   = cx
        self.cy   = cy
        self.r    = 0
        self.ativa = True
        self.parts: list = []

    def update(self):
        """Avança o radius e gera/atualiza partículas."""
        self.r += self.SPEED
        if self.r >= self.MAX_R:
            self.ativa = False

        for _ in range(self.PART_N):
            ang = random.uniform(0, math.tau)
            self.parts.append({
                "x":  self.cx + math.cos(ang) * self.r,
                "y":  self.cy + math.sin(ang) * self.r,
                "vx": math.cos(ang) * random.uniform(0.3, 1.8),
                "vy": math.sin(ang) * random.uniform(0.3, 1.8),
                "life": random.randint(25, 70),
                "sz":  random.uniform(1.2, 3.5),
            })

        for p in self.parts[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 2
            if p["life"] <= 0:
                self.parts.remove(p)

    def reveal(self, wall_vis, segs_enum):
        for idx, (p1, p2) in segs_enum:

            mx = (p1[0] + p2[0]) * 0.5
            my = (p1[1] + p2[1]) * 0.5

            d = math.dist((self.cx, self.cy), (mx, my))

            if d > 220:
                continue

            if abs(d - self.r) < 8:
                wall_vis[idx] = 200

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
            surf.blit(ring, (int(cx_s - self.r - 2),
                             int(cy_s - self.r - 2)))

        for p in self.parts:
            px_s = int(p["x"] - cam[0])
            py_s = int(p["y"] - cam[1])
            a    = max(0, int(220 * p["life"] / 70 * brightness))
            sz   = max(1, int(p["sz"]))
            gs   = pygame.Surface((sz*4, sz*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (100, 230, 255, a),
                               (sz*2, sz*2), sz*2)
            pygame.draw.circle(gs, (220, 255, 255, min(255, a+60)),
                               (sz*2, sz*2), sz)
            surf.blit(gs, (px_s - sz*2, py_s - sz*2))


# ═══════════════════════════════════════════════════════════════════
# 7. MAPA & PAREDES
#
#  Mapa 19×19 – '1' = parede, '0' = caminho
#  As paredes NÃO são blocos: são segmentos de linha (bordas das
#  células '1') armazenados em wall_segments.
#  wall_visibility mapeia  idx -> alpha  para o efeito de eco.
# ═══════════════════════════════════════════════════════════════════
MAPA_LINHAS = [
    "1111111111111111111",
    "1000000100000010001",
    "1011101110111011101",
    "1010001000001010001",
    "1010111011101110111",
    "1000100010000000001",
    "1110101110101011011",
    "1000100000101010001",
    "1011011101101010111",
    "1000000001001000001",
    "1101110101001110101",
    "1001000101000010101",
    "1011011101111010001",
    "1010000001000011101",
    "1010111011011010001",
    "1000001010000010001",
    "1011101110111011011",
    "1000000000000000001",
    "1111111111111111111",
]
mapa       = [list(ln) for ln in MAPA_LINHAS]
MAPA_ROWS  = len(mapa)
MAPA_COLS  = len(mapa[0])
MAPA_PX_W  = MAPA_COLS * TILE
MAPA_PX_H  = MAPA_ROWS * TILE


# A saída fica na última célula livre antes da borda direita, na penúltima linha
EXIT_TILE_X = MAPA_COLS - 2   # coluna 17
EXIT_TILE_Y = MAPA_ROWS - 2   # linha 17
mapa[EXIT_TILE_Y][EXIT_TILE_X] = "0"   # garante que é caminho
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
                    ((tx, ty), (tx+TILE, ty)),
                    ((tx, ty+TILE), (tx+TILE, ty+TILE)),
                    ((tx, ty), (tx, ty+TILE)),
                    ((tx+TILE, ty), (tx+TILE, ty+TILE)),
                ]
    return segs

wall_segments = _gerar_segmentos(mapa)
wall_segs_e   = list(enumerate(wall_segments))  
wall_vis: dict = {}   


def _spawns_livres():
    return [
        (x*TILE + TILE//2 - 15, y*TILE + TILE//2 - 15)
        for y, ln in enumerate(mapa)
        for x, t in enumerate(ln)
        if t == "0" and (x, y) != (EXIT_TILE_X, EXIT_TILE_Y)
    ]

def _spawn_longe(excluir=(), min_dist=120):
    cands = _spawns_livres()
    random.shuffle(cands)
    for c in cands:
        if all(math.dist(c, e) >= min_dist for e in excluir):
            return c
    return cands[0]


# ═══════════════════════════════════════════════════════════════════
# 8. TELA DE START
#
#  Apresenta: título, slider de volume, slider de brilho, botão PLAY
#  Retorna (volume_music, brightness) quando o usuário clica em PLAY.
# ═══════════════════════════════════════════════════════════════════
def tela_start():
    """
    Menu principal com sliders de volume e brilho.
    Retorna (vol: float, bri: float).
    """
    vol = volume_music
    bri = 1.0      # brilho: 0.0 – 1.0
    dragging = None   # "vol" | "bri"

    SL_X    = WIDTH//2 - 150   # x do início dos sliders
    SL_W    = 300               # largura dos sliders
    SL_VOL_Y = HEIGHT//2 + 20
    SL_BRI_Y = HEIGHT//2 + 80
    PLAY_R  = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 150, 180, 48)


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
                    # Clicar nos sliders
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


        pulse = 0.85 + 0.15 * math.sin(title_anim * 2)
        t_surf = FONT_BIG.render("MAZE ESCAPE", True, C_ACCENT)
        t_surf = pygame.transform.scale(t_surf,
                     (int(t_surf.get_width() * pulse),
                      int(t_surf.get_height() * pulse)))
        screen.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 110)))

        sub = FONT_SMALL.render("eco-localização · labirinto · fuga", True, (80,140,180))
        screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 - 55)))


        _draw_slider(screen, SL_X, SL_VOL_Y, SL_W, vol,
                     f"VOLUME  {int(vol*100):3d}%", mx, my)


        _draw_slider(screen, SL_X, SL_BRI_Y, SL_W, bri,
                     f"BRILHO  {int(bri*100):3d}%", mx, my)


        hover = PLAY_R.collidepoint(mx, my)
        col_btn = (0, 210, 100) if hover else (0, 160, 80)
        pygame.draw.rect(screen, col_btn, PLAY_R, border_radius=8)
        pygame.draw.rect(screen, (0, 255, 120), PLAY_R, 2, border_radius=8)
        lbl = FONT_MED.render("▶  JOGAR", True, (0,0,0) if hover else (200,255,200))
        screen.blit(lbl, lbl.get_rect(center=PLAY_R.center))

        hint = FONT_TINY.render("F11 = tela cheia   |   ESC = sair", True, (50,70,90))
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 20)))

        pygame.display.flip()


def _draw_slider(surf, x, y, w, val, label, mx, my):
    """Desenha um slider horizontal estilizado."""
    pygame.draw.rect(surf, (30,50,70), (x, y-4, w, 8), border_radius=4)
    fill_w = int(w * val)
    pygame.draw.rect(surf, C_ACCENT, (x, y-4, fill_w, 8), border_radius=4)
    tx = x + fill_w
    hover = abs(mx - tx) < 12 and abs(my - y) < 12
    pygame.draw.circle(surf, (255,255,255) if hover else (180,220,255),
                       (tx, y), 9 if hover else 7)
    lbl = FONT_SMALL.render(label, True, (120,180,220))
    surf.blit(lbl, (x, y - 26))


def _toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))


# ═══════════════════════════════════════════════════════════════════
# 9. TELA DE COMANDOS
#
#  Exibida após clicar em PLAY, antes do gameplay começar.
#  Lista todos os controles de P1 e P2.
#  Pressionar ENTER / SPACE / clique inicia o jogo.
# ═══════════════════════════════════════════════════════════════════
COMANDOS = [
    # (ícone, descrição)
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
    ("── GERAL ──", ""),
    ("9",               "Adicionar Jogador 2"),
    ("F11",             "Tela cheia"),
    ("- / =",           "Diminuir / aumentar volume"),
    ("",                ""),
    ("🏁  Chegue à SAÍDA (borda verde) para vencer!", ""),
]

def tela_comandos():
    """Exibe os comandos. Retorna quando o usuário confirmar."""
    anim = 0.0
    while True:
        dt   = clock.tick(FPS)
        anim += dt * 0.001

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if getattr(ev, "key", 0) in (pygame.K_RETURN, pygame.K_SPACE,
                                              0) or ev.type == pygame.MOUSEBUTTONDOWN:
                    return

        screen.fill(C_MENU_BG)

        t = FONT_MED.render("CONTROLES", True, C_ACCENT)
        screen.blit(t, t.get_rect(center=(WIDTH//2, 38)))
        pygame.draw.line(screen, (0,80,120), (WIDTH//4, 60), (WIDTH*3//4, 60), 1)

        col_w = WIDTH // 2 - 40
        y_off = 80
        line_h = 24
        for i, (key, desc) in enumerate(COMANDOS):
            col_x = 80 if i <= len(COMANDOS)//2 else WIDTH//2 + 40
            row_y = y_off + (i % (len(COMANDOS)//2 + 1)) * line_h

            if desc == "":
                if key:
                    surf = FONT_SMALL.render(key, True, (0, 200, 180))
                    screen.blit(surf, (col_x, row_y))
                continue

            k_surf = FONT_SMALL.render(key, True, (220, 220, 100))
            d_surf = FONT_SMALL.render(desc, True, (160, 190, 210))
            screen.blit(k_surf, (col_x, row_y))
            screen.blit(d_surf, (col_x + 180, row_y))

        if int(anim * 2) % 2 == 0:
            hint = FONT_SMALL.render("Pressione ENTER ou clique para começar",
                                     True, (80, 160, 80))
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 28)))

        pygame.display.flip()

volume_music, brightness = tela_start()
tela_comandos()

p1_pos = _spawn_longe()
p2_pos = _spawn_longe(excluir=[p1_pos])

p1 = Jogador(p1_pos[0], p1_pos[1],
    frames   = P1_FRAMES,
    controls = {
        "up":     pygame.K_w,
        "down":   pygame.K_s,
        "left":   pygame.K_a,
        "right":  pygame.K_d,
        "run":    pygame.K_LSHIFT,
        "sprint": pygame.K_q,
    },
    glow_color = (100, 180, 255),
)

p2 = Jogador(p2_pos[0], p2_pos[1],
    frames   = P2_FRAMES,
    controls = {
        "up":     pygame.K_UP,
        "down":   pygame.K_DOWN,
        "left":   pygame.K_LEFT,
        "right":  pygame.K_RIGHT,
        "run":    pygame.K_RSHIFT,
        "sprint": pygame.K_KP0,
    },
    glow_color = (80, 255, 100),
)
p2.active = False

jogadores = [p1, p2]

morcegos = []
for _ in range(5):
    pos = _spawn_longe(excluir=[p1_pos, p2_pos])
    morcegos.append(Morcego(pos[0], pos[1]))

ondas: list[Onda] = []
ECO_CD   = 1500   
eco_last = {p1: -9999, p2: -9999}

show_vol  = False
vol_timer = 0

def _camera(jogadores, sw, sh):
    """Centraliza entre os jogadores ativos."""
    ativos = [j for j in jogadores if j.active]
    cx = sum(j.rect.centerx for j in ativos) / len(ativos)
    cy = sum(j.rect.centery for j in ativos) / len(ativos)
    return (
        max(0, min(cx - sw//2, MAPA_PX_W - sw)),
        max(0, min(cy - sh//2, MAPA_PX_H - sh)),
    )

cam = (0, 0)

ganhou     = False
win_timer  = 0
win_player = 0   # 1 ou 2

while True:
    dt    = clock.tick(FPS)
    agora = pygame.time.get_ticks()
    sw, sh = screen.get_size()

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
                npos = _spawn_longe(excluir=[(p1.rect.x, p1.rect.y)])
                p2.rect.topleft = npos

            if ev.key == pygame.K_e and p1.active:
                if agora - eco_last[p1] >= ECO_CD:
                    eco_last[p1] = agora
                    ondas.append(Onda(p1.rect.centerx, p1.rect.centery))
                    if sons_eco:
                        random.choice(sons_eco).play()

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

    if not ganhou:
        mode_p1 = p1.update(dt, paredes)
        mode_p2 = p2.update(dt, paredes) if p2.active else "walk"

        for m in morcegos:
            m.update(dt, paredes, jogadores)

        # Ondas
        for o in ondas[:]:
            o.update()
            o.reveal(wall_vis, wall_segs_e)
            if not o.ativa and not o.parts:
                ondas.remove(o)

        # Fade das paredes
        for idx in list(wall_vis):
            wall_vis[idx] -= 2
            if wall_vis[idx] <= 0:
                del wall_vis[idx]

        cam = _camera(jogadores, sw, sh)

        for i, j in enumerate(jogadores, 1):
            if j.active and j.rect.colliderect(EXIT_RECT):
                ganhou    = True
                win_player = i
                win_timer  = agora
                break

    if BACKGROUND:
        screen.blit(BACKGROUND, (0, 0))
    else:
        screen.fill(C_BG)

    for o in ondas:
        o.draw(screen, cam, brightness)

    ex_s = (EXIT_RECT.x - cam[0], EXIT_RECT.y - cam[1])
    pulse = 0.5 + 0.5 * math.sin(agora * 0.003)
    exit_alpha = int(60 + 80 * pulse)
    exit_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    exit_surf.fill((0, 255, 100, exit_alpha))
    screen.blit(exit_surf, ex_s)
    pygame.draw.rect(screen, C_EXIT,
                     pygame.Rect(ex_s[0], ex_s[1], TILE, TILE), 2)
    ex_lbl = FONT_TINY.render("SAÍDA", True, C_EXIT)
    screen.blit(ex_lbl, (ex_s[0] + TILE//2 - ex_lbl.get_width()//2,
                          ex_s[1] + TILE//2 - ex_lbl.get_height()//2))

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
        pygame.draw.line(screen, (200, 240, 255),
                         (sx1, sy1), (sx2, sy2), 1)

    p1.draw(screen, cam, brightness)
    if p2.active:
        p2.draw(screen, cam, brightness)

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

    if p1.active:
        cd_left = max(0, ECO_CD - (agora - eco_last[p1]))
        bw = 70
        pygame.draw.rect(screen, (20,40,60), (16, sh-26, bw, 8), border_radius=4)
        ready_w = int(bw * (1 - cd_left/ECO_CD))
        pygame.draw.rect(screen, C_HUD, (16, sh-26, ready_w, 8), border_radius=4)
        eco_txt = FONT_TINY.render("ECO [E]" + (" ✓" if cd_left==0 else ""),
                                   True, C_HUD)
        screen.blit(eco_txt, (16, sh-44))

    if not p2.active:
        d = FONT_TINY.render("[9] Adicionar Jogador 2", True, (50,80,100))
        screen.blit(d, d.get_rect(center=(sw//2, sh-16)))

    if ganhou:
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        w1 = FONT_BIG.render(f"JOGADOR {win_player} SAIU!", True, C_EXIT)
        w2 = FONT_MED.render("Você escapou do labirinto", True, (180,255,200))
        w3 = FONT_SMALL.render("ENTER ou ESPAÇO para jogar de novo", True,
                                (80,160,80))
        screen.blit(w1, w1.get_rect(center=(sw//2, sh//2 - 60)))
        screen.blit(w2, w2.get_rect(center=(sw//2, sh//2)))
        screen.blit(w3, w3.get_rect(center=(sw//2, sh//2 + 60)))

    pygame.display.flip()