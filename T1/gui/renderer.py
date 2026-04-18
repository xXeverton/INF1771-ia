# gui/renderer.py
"""
Visualizador Pygame completo para "Avatar Path".
Com suporte a janela redimensionável e Câmera Livre (Pan & Zoom).
"""

import pygame
import sys
import os

os.environ['SDL_AUDIODRIVER'] = 'dummy'

# ─────────────────────────────────────────────
#  CONSTANTES DE LAYOUT E CORES
# ─────────────────────────────────────────────
LEGEND_H    = 50          
PANEL_W     = 370         
FPS         = 60
STEP_MS     = 25          

BG          = (18, 20, 24)
PANEL_BG    = (24, 27, 32)
PANEL_BORDER= (40, 45, 55)

C_PLAIN     = (120, 160, 100)
C_ROCK      = (130, 125, 115)
C_FOREST    = ( 55, 120,  55)
C_WATER     = ( 55,  95, 175)
C_MOUNT     = (160, 120,  75)
C_CHECKPOINT= (220, 130,  40)

C_WHITE     = (230, 235, 242)
C_GRAY      = (130, 140, 155)
C_DARK_GRAY = ( 55,  60,  70)
C_ACCENT    = ( 80, 185, 255)     
C_GREEN     = ( 60, 200, 120)
C_ORANGE    = (255, 153,  51)     
C_YELLOW    = (255, 230,  60)     
C_BTN_ACT   = ( 80, 185, 255)
C_BTN_IDLE  = ( 40,  45,  55)
C_BTN_TXT   = (230, 235, 242)
C_ROW_EVEN  = ( 30,  33,  40)
C_ROW_ODD   = ( 36,  40,  48)
C_ROW_SEL   = ( 45,  80, 120)

STAT_COLORS = {
    "total": (230, 235, 242),
    "astar": ( 80, 185, 255),
    "comb" : (255, 153,  51),
}

TERRAIN_LEGEND = [
    ("Plano",    C_PLAIN),
    ("Rochoso",  C_ROCK),
    ("Floresta", C_FOREST),
    ("Água",     C_WATER),
    ("Montanha", C_MOUNT),
    ("Checkpoint",C_CHECKPOINT),
]

C_PANEL_BORDER = PANEL_BORDER

# ─────────────────────────────────────────────
#  HELPERS DE DESENHO
# ─────────────────────────────────────────────
def draw_text(surf, text, font, color, x, y, align="left"):
    img = font.render(text, True, color)
    if align == "center":
        x -= img.get_width() // 2
    elif align == "right":
        x -= img.get_width()
    surf.blit(img, (x, y))
    return img.get_width()

def draw_button(surf, rect, label, font, active=False, hover=False):
    bg = C_BTN_ACT if active else (C_DARK_GRAY if hover else C_BTN_IDLE)
    pygame.draw.rect(surf, bg, rect, border_radius=6)
    pygame.draw.rect(surf, C_PANEL_BORDER if not active else C_ACCENT, rect, 1, border_radius=6)
    tw = font.render(label, True, C_BTN_TXT).get_width()
    draw_text(surf, label, font, C_BTN_TXT, rect[0] + rect[2]//2 - tw//2, rect[1] + rect[3]//2 - font.get_height()//2)


# ─────────────────────────────────────────────
#  CLASSE PRINCIPAL
# ─────────────────────────────────────────────
class VisualizadorPygame:
    def __init__(self, mapa, caminho_calculado, log_jornada):
        pygame.init()
        pygame.display.set_caption("Avatar Path  ·  Planejador de Jornada")

        # 1. JANELA REDIMENSIONÁVEL COM BOTÕES DO SISTEMA OPERACIONAL
        flags = pygame.RESIZABLE | getattr(pygame, 'WINDOWMAXIMIZED', 0)
        self.screen = pygame.display.set_mode((1280, 720), flags)
        self.clock  = pygame.time.Clock()

        # Dados Core
        self.mapa = mapa
        self.caminho = caminho_calculado
        self.log_jornada = log_jornada
        self.trechos = self._parse_log(log_jornada)

        # Variáveis de Câmera Livre (Pan & Zoom)
        self.cam_x = 0
        self.cam_y = 0
        self.TILE = 10
        self.is_dragging = False
        self.last_mouse = (0, 0)

        # Fontes
        self.f_title   = pygame.font.SysFont("Arial", 18, bold=True)
        self.f_sub     = pygame.font.SysFont("Arial", 10)
        self.f_stat_v  = pygame.font.SysFont("Arial", 20, bold=True)
        self.f_stat_l  = pygame.font.SysFont("Arial", 10)
        self.f_btn     = pygame.font.SysFont("Arial", 12, bold=True)
        self.f_detail  = pygame.font.SysFont("Arial", 11)
        self.f_detail_b= pygame.font.SysFont("Arial", 11, bold=True)
        self.f_legend  = pygame.font.SysFont("Arial", 10)
        self.f_table_h = pygame.font.SysFont("Arial", 11, bold=True)
        self.f_table   = pygame.font.SysFont("Arial", 11)
        self.f_cp      = pygame.font.SysFont("Arial",  8, bold=True)

        # Controle de Animação
        self.passo = 0
        self.playing = False
        self.concluido = False
        self.table_scroll = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, STEP_MS)

        # Inicializa o layout
        self.map_surf = None
        self._update_layout()
        self._center_map()

    def _update_layout(self):
        """Atualiza a geometria quando a janela muda de tamanho."""
        self.WIN_W, self.WIN_H = self.screen.get_size()
        self.MAP_W = max(400, self.WIN_W - PANEL_W)
        self.MAP_H = max(300, self.WIN_H - LEGEND_H)

        x0 = self.MAP_W + 14
        btn_w = (PANEL_W - 28 - 10) // 2
        
        # Posicionamento fixo dos botões baseado no layout vertical
        self.btn_play  = pygame.Rect(x0,            162, btn_w, 32)
        self.btn_pause = pygame.Rect(x0 + btn_w+10, 162, btn_w, 32)
        self.btn_adv   = pygame.Rect(x0,            204, btn_w, 32)
        self.btn_reset = pygame.Rect(x0 + btn_w+10, 204, btn_w, 32)

    def _center_map(self):
        """Ajusta o TILE e a Câmera para mostrar o mapa inteiro centralizado."""
        rows = len(self.mapa.matriz)
        cols = len(self.mapa.matriz[0]) if rows else 1
        
        tile_w = self.MAP_W // cols
        tile_h = self.MAP_H // rows
        self.TILE = max(2, min(tile_w, tile_h))
        
        self.cam_x = -(self.MAP_W - (cols * self.TILE)) // 2
        self.cam_y = -(self.MAP_H - (rows * self.TILE)) // 2
        self._build_static_map()

    def _zoom(self, direction, mx, my):
        """Controla o zoom aproximando/afastando onde o mouse está apontando."""
        if mx >= self.MAP_W or my >= self.MAP_H: return

        old_tile = self.TILE
        # Quanto mais zoom, mais rápido ele aumenta
        step = max(1, self.TILE // 5)
        self.TILE += direction * step
        self.TILE = max(2, min(self.TILE, 40)) # Limites seguros de zoom

        if old_tile != self.TILE:
            # Matemática para manter o pixel sob o mouse no mesmo lugar
            map_x = (mx + self.cam_x) / old_tile
            map_y = (my + self.cam_y) / old_tile
            self.cam_x = int(map_x * self.TILE - mx)
            self.cam_y = int(map_y * self.TILE - my)
            self._build_static_map()

    def _build_static_map(self):
        """Desenha a imagem do mapa. Só é chamada se o zoom mudar."""
        rows = len(self.mapa.matriz)
        cols = len(self.mapa.matriz[0]) if rows else 1
        
        self.map_surf = pygame.Surface((cols * self.TILE, rows * self.TILE))
        self.map_surf.fill((15, 18, 25))
        
        color_map = {'.': C_PLAIN, 'R': C_ROCK, 'F': C_FOREST, 'A': C_WATER, 'M': C_MOUNT}
        
        for y, linha in enumerate(self.mapa.matriz):
            for x, ch in enumerate(linha):
                col = color_map.get(ch, C_PLAIN)
                noise = ((x * 3 + y * 7) % 9) - 4
                col = (
                    max(0, min(255, col[0] + noise)),
                    max(0, min(255, col[1] + noise)),
                    max(0, min(255, col[2] + noise)),
                )
                pygame.draw.rect(self.map_surf, col, (x * self.TILE, y * self.TILE, self.TILE, self.TILE))

        for k, (cx, cy) in self.mapa.checkpoints.items():
            r = pygame.Rect(cx * self.TILE, cy * self.TILE, self.TILE, self.TILE)
            pygame.draw.rect(self.map_surf, C_CHECKPOINT, r)
            # Não desenha a letra se o tile for muito pequeno
            if self.TILE > 6:
                lbl = self.f_cp.render(k, True, (0, 0, 0))
                self.map_surf.blit(lbl, (cx * self.TILE + self.TILE//2 - lbl.get_width()//2, cy * self.TILE + self.TILE//2 - lbl.get_height()//2))

    def _draw_map_area(self):
        # Evita que elementos vazem do limite do mapa
        self.screen.set_clip(pygame.Rect(0, 0, self.MAP_W, self.MAP_H))
        
        # Fundo escuro atrás do mapa
        pygame.draw.rect(self.screen, BG, (0, 0, self.MAP_W, self.MAP_H))

        if not self.caminho:
            self.screen.blit(self.map_surf, (-self.cam_x, -self.cam_y))
            self.screen.set_clip(None)
            return

        ax, ay = self.caminho[min(self.passo, len(self.caminho)-1)]
        self.screen.blit(self.map_surf, (-self.cam_x, -self.cam_y))

        # Rastro
        trail_surf = pygame.Surface((self.TILE, self.TILE), pygame.SRCALPHA)
        trail_surf.fill((255, 80, 80, 60))
        for i in range(self.passo):
            tx, ty = self.caminho[i]
            # Otimização: só desenha se estiver dentro da tela
            rx = tx * self.TILE - self.cam_x
            ry = ty * self.TILE - self.cam_y
            if -self.TILE <= rx <= self.MAP_W and -self.TILE <= ry <= self.MAP_H:
                self.screen.blit(trail_surf, (rx, ry))

        # Caminho Futuro e Percorrido (Linhas)
        def calc_pts(lista_pontos):
            return [(cx * self.TILE + self.TILE//2 - self.cam_x, cy * self.TILE + self.TILE//2 - self.cam_y) for cx, cy in lista_pontos]

        if self.passo < len(self.caminho) - 1:
            pts = calc_pts(self.caminho[self.passo:])
            if len(pts) > 1: pygame.draw.lines(self.screen, (200, 80, 80, 180), False, pts, max(1, self.TILE//4))

        if self.passo > 0:
            pts_done = calc_pts(self.caminho[:self.passo+1])
            if len(pts_done) > 1: pygame.draw.lines(self.screen, (220, 70, 70), False, pts_done, max(1, self.TILE//4))

        # Agente
        rx = ax * self.TILE - self.cam_x
        ry = ay * self.TILE - self.cam_y
        raio = max(3, self.TILE // 2)
        pygame.draw.circle(self.screen, C_YELLOW, (rx + self.TILE//2, ry + self.TILE//2), raio)
        pygame.draw.circle(self.screen, (0, 0, 0), (rx + self.TILE//2, ry + self.TILE//2), raio, max(1, raio//4))

        self.screen.set_clip(None)

    # ... (O RESTANTE DA CLASSE É O PAINEL DE INFORMAÇÕES) ...
    def _parse_log(self, log):
        rows = []
        for linha in log:
            try:
                bracket_end = linha.index(']')
                trecho_str  = linha[1:bracket_end]        
                resto       = linha[bracket_end+1:].split()
                nums = []
                equipe_parts = []
                for tok in resto:
                    try:
                        nums.append(float(tok))
                    except ValueError:
                        equipe_parts.append(tok)
                equipe = " ".join(equipe_parts).strip().rstrip(',').strip()
                if not equipe: equipe = "—"
                astar_v = nums[0] if len(nums) > 0 else 0.0
                comb_v  = nums[1] if len(nums) > 1 else 0.0
                rows.append({"trecho": trecho_str, "astar": astar_v, "comb": comb_v, "equipe": equipe})
            except Exception: pass
        prev_a, prev_c = 0.0, 0.0
        for r in rows:
            r["delta_astar"] = r["astar"] - prev_a
            r["delta_comb"]  = r["comb"]  - prev_c
            prev_a, prev_c = r["astar"], r["comb"]
        return rows

    def _draw_legend(self):
        y0 = self.MAP_H
        pygame.draw.rect(self.screen, (20, 23, 30), (0, y0, self.MAP_W, LEGEND_H))
        pygame.draw.line(self.screen, PANEL_BORDER, (0, y0), (self.MAP_W, y0), 1)
        item_w = self.MAP_W // len(TERRAIN_LEGEND)
        for i, (label, color) in enumerate(TERRAIN_LEGEND):
            x = i * item_w + 16
            cy = y0 + LEGEND_H // 2 - 6
            pygame.draw.rect(self.screen, color, (x, cy, 14, 14), border_radius=2)
            draw_text(self.screen, label, self.f_legend, C_GRAY, x + 18, cy + 1)

    def _draw_panel(self, mx, my):
        px = self.MAP_W
        pw = PANEL_W
        ph = self.WIN_H

        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, pw, ph))
        pygame.draw.line(self.screen, PANEL_BORDER, (px, 0), (px, ph), 1)

        x0 = px + 14
        y  = 14

        draw_text(self.screen, "Avatar Path", self.f_title, C_WHITE, x0, y)
        y += 22
        draw_text(self.screen, "A* no mapa  ·  Algoritmo Guloso nas equipes", self.f_sub, C_GRAY, x0, y)
        y += 20
        pygame.draw.line(self.screen, PANEL_BORDER, (x0, y), (px + pw - 14, y), 1)
        y += 12

        total_v, astar_v, comb_v = self._current_stats()
        stat_labels = [("Total", f"{total_v:.2f}", STAT_COLORS["total"]),
                       ("A*",    f"{astar_v:.2f}", STAT_COLORS["astar"]),
                       ("Comb.", f"{comb_v:.2f}",  STAT_COLORS["comb"])]
        sw = (pw - 28) // 3
        for i, (lbl, val, col) in enumerate(stat_labels):
            sx = x0 + i * (sw + 5)
            box = pygame.Rect(sx, y, sw, 54)
            pygame.draw.rect(self.screen, C_ROW_EVEN, box, border_radius=6)
            pygame.draw.rect(self.screen, PANEL_BORDER, box, 1, border_radius=6)
            draw_text(self.screen, lbl,  self.f_stat_l, C_GRAY, sx + sw//2, y + 6, "center")
            draw_text(self.screen, val,  self.f_stat_v, col,    sx + sw//2, y + 22, "center")
        y += 66

        pygame.draw.line(self.screen, PANEL_BORDER, (x0, y), (px + pw - 14, y), 1)
        y += 10

        draw_text(self.screen, "Controles (Mouse Direito para Centrar Mapa)", self.f_detail_b, C_GRAY, x0, y)
        
        # Botões
        hover_play  = self.btn_play.collidepoint(mx, my)
        hover_pause = self.btn_pause.collidepoint(mx, my)
        hover_adv   = self.btn_adv.collidepoint(mx, my)
        hover_reset = self.btn_reset.collidepoint(mx, my)

        draw_button(self.screen, self.btn_play,  "Reproduzir", self.f_btn, active=self.playing, hover=hover_play)
        draw_button(self.screen, self.btn_pause, "Pausar",     self.f_btn, active=not self.playing and not self.concluido, hover=hover_pause)
        draw_button(self.screen, self.btn_adv,   "Avançar",    self.f_btn, hover=hover_adv)
        draw_button(self.screen, self.btn_reset, "Reiniciar",  self.f_btn, hover=hover_reset)

        y = self.btn_adv.bottom + 12
        pygame.draw.line(self.screen, PANEL_BORDER, (x0, y), (px + pw - 14, y), 1)
        y += 10

        draw_text(self.screen, "Detalhes", self.f_detail_b, C_GRAY, x0, y)
        y += 18

        details = self._build_details()
        col_label_w = 110
        for lbl, val in details:
            draw_text(self.screen, lbl, self.f_detail, C_GRAY, x0, y)
            draw_text(self.screen, val, self.f_detail, C_WHITE, x0 + col_label_w, y)
            y += 16

        y += 6
        pygame.draw.line(self.screen, PANEL_BORDER, (x0, y), (px + pw - 14, y), 1)
        y += 10

        draw_text(self.screen, "Trechos Planejados", self.f_detail_b, C_GRAY, x0, y)
        y += 18

        table_x  = [x0, x0+52, x0+130, x0+210, x0+270]
        t_headers = ["Trecho", "A*", "Comb.", "Equipe"]
        for i, h in enumerate(t_headers):
            draw_text(self.screen, h, self.f_table_h, C_GRAY, table_x[i], y)
        y += 16
        pygame.draw.line(self.screen, PANEL_BORDER, (x0, y), (px + pw - 14, y), 1)
        y += 3

        row_h    = 20
        table_area_h = self.WIN_H - y - 8
        max_visible  = table_area_h // row_h
        cur_trecho_idx = self._current_trecho_index()

        if cur_trecho_idx >= 0:
            if cur_trecho_idx < self.table_scroll:
                self.table_scroll = cur_trecho_idx
            elif cur_trecho_idx >= self.table_scroll + max_visible:
                self.table_scroll = cur_trecho_idx - max_visible + 1

        clip_rect = pygame.Rect(x0, y, pw - 16, table_area_h)
        self.screen.set_clip(clip_rect)

        for i, row in enumerate(self.trechos):
            iy = y + (i - self.table_scroll) * row_h
            if iy < y or iy > y + table_area_h: continue
            is_active = (i == cur_trecho_idx)
            bg = C_ROW_SEL if is_active else (C_ROW_EVEN if i % 2 == 0 else C_ROW_ODD)
            pygame.draw.rect(self.screen, bg, (x0, iy, pw - 16, row_h))
            col_txt = C_WHITE if is_active else C_GRAY

            draw_text(self.screen, row["trecho"], self.f_table, col_txt, table_x[0], iy + 3)
            draw_text(self.screen, f"{row['delta_astar']:.2f}", self.f_table, C_ACCENT,  table_x[1], iy + 3)
            draw_text(self.screen, f"{row['delta_comb']:.2f}",  self.f_table, C_ORANGE,  table_x[2], iy + 3)

            eq = row["equipe"]
            max_eq_w = pw - 16 - (table_x[3] - x0) - 4
            if self.f_table.render(eq, True, col_txt).get_width() > max_eq_w:
                while eq and self.f_table.render(eq + "…", True, col_txt).get_width() > max_eq_w:
                    eq = eq[:-1]
                eq += "…"
            draw_text(self.screen, eq, self.f_table, col_txt, table_x[3], iy + 3)

        self.screen.set_clip(None)

    def _current_stats(self):
        idx = self._current_trecho_index()
        if idx < 0 or not self.trechos: return 0.0, 0.0, 0.0
        row = self.trechos[idx]
        return row["astar"] + row["comb"], row["astar"], row["comb"]

    def _current_trecho_index(self):
        if not self.caminho or not self.trechos: return -1
        progress = self.passo / max(1, len(self.caminho) - 1)
        idx = int(progress * len(self.trechos))
        return min(idx, len(self.trechos) - 1)

    def _build_details(self):
        cx, cy = self.caminho[min(self.passo, len(self.caminho)-1)] if self.caminho else (0,0)
        idx    = self._current_trecho_index()
        trecho = self.trechos[idx]["trecho"] if idx >= 0 else "—"
        equipe = self.trechos[idx]["equipe"] if idx >= 0 else "—"
        status = "Jornada concluída." if self.concluido else ("A viajar…" if self.playing else "Pausado.")
        tf = len(self.caminho)
        return [
            ("Status:", status), ("Posição:", f"linha {cy}, coluna {cx}"),
            ("Progresso:", f"frame {self.passo}/{tf-1} | passo {self.passo}/{tf-1}"),
            ("Nós exp.:", str(max(0, self.passo * 2))),
            ("Trecho:", trecho), ("Equipe:", equipe),
        ]

    # ─────────────────────────────────────────
    #  LOOP PRINCIPAL DE EVENTOS
    # ─────────────────────────────────────────
    def iniciar_loop(self):
        running = True
        while running:
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Lida com redimensionamento da janela
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._update_layout()
                    self._center_map()

                elif event.type == pygame.USEREVENT + 1:
                    if self.playing and not self.concluido:
                        self.passo += 1
                        if self.passo >= len(self.caminho) - 1:
                            self.passo, self.playing, self.concluido = len(self.caminho) - 1, False, True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Clique Esquerdo
                        # Se clicou na área do mapa, inicia o arraste (pan)
                        if mx < self.MAP_W and my < self.MAP_H:
                            self.is_dragging = True
                            self.last_mouse = event.pos
                        else:
                            # Se clicou no painel, checa os botões
                            if self.btn_play.collidepoint(mx, my):
                                if self.concluido: self.passo, self.concluido = 0, False
                                self.playing = True
                            elif self.btn_pause.collidepoint(mx, my): self.playing = False
                            elif self.btn_adv.collidepoint(mx, my):
                                self.playing = False
                                if self.passo < len(self.caminho) - 1: self.passo += 1
                            elif self.btn_reset.collidepoint(mx, my):
                                self.passo, self.playing, self.concluido, self.table_scroll = 0, False, False, 0
                    elif event.button == 3: # Clique Direito reseta o zoom/posição
                        self._center_map()
                    elif event.button == 4: # Scroll Up (Zoom In)
                        self._zoom(1, mx, my)
                    elif event.button == 5: # Scroll Down (Zoom Out)
                        self._zoom(-1, mx, my)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    # Lida com o arraste da câmera
                    if self.is_dragging and mx < self.MAP_W and my < self.MAP_H:
                        dx = event.pos[0] - self.last_mouse[0]
                        dy = event.pos[1] - self.last_mouse[1]
                        self.cam_x -= dx
                        self.cam_y -= dy
                        self.last_mouse = event.pos

                elif event.type == pygame.MOUSEWHEEL:
                    # Se rolar o scroll sobre o painel direito, desce a tabela
                    if mx > self.MAP_W:
                        self.table_scroll = max(0, self.table_scroll - event.y)

            self.screen.fill(BG)
            self._draw_map_area()
            self._draw_legend()
            self._draw_panel(mx, my)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()