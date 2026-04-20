# Este arquivo implementa a interface gráfica usando Pygame para visualizar o mapa e a jornada.

"""
Visualizador Pygame - Avatar: The Last Airbender Theme
INF1771 · Layout em Cards com Assets Reais do Jogo GBA

Assets utilizados (pasta assets/):
  Miscellaneous-Font-and-Options.png   → Fonte pixel-art do jogo (letras A-Z, a-z)
  Miscellaneous-Portraits-of-Aang.png  → Retrato do Aang no card de status (crop)
  Miscellaneous-Introduction.png       → Background de montanha + logo Avatar no painel
  sprites/Playable-Characters-Avatar-Aang.png → Sprite do Aang caminhando no mapa
  Momo.png                             → Momo no header do painel
"""

import pygame
import sys
import os
import math

os.environ['SDL_AUDIODRIVER'] = 'dummy'

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
PANEL_W  = 390
FPS      = 60
STEP_MS  = 25

# Paleta extraída das telas do jogo GBA
BG           = (8,  12, 18)       # Azul-noite profundo (fundo do mapa)
PANEL_BG     = (10, 14, 20)       # Painel lateral
CARD_BG      = (16, 20, 30)       # Fundo dos cards
CARD_BORDER  = (210, 110, 20)     # Laranja-fogo (cor dominante do jogo)
HEADER_BG    = (14, 10,  4)       # Quase preto com toque quente

# Elementos
C_AIR        = (125, 205, 255)    # Azul ar - Aang
C_AIR_DIM    = (50, 110, 170)
C_FIRE       = (245, 125, 25)     # Laranja fogo
C_FIRE_DIM   = (160, 60,  8)
C_WATER_ELEM = (45, 150, 210)
C_EARTH      = (80, 170, 70)
C_GOLD       = (255, 210, 45)     # Dourado do logo Avatar

# Terrenos
C_PLAIN      = (72, 120, 58)
C_ROCK       = (100, 94, 78)
C_FOREST     = (35, 92, 35)
C_WATER      = (28, 70, 145)
C_MOUNT      = (120, 88, 55)
C_CHECKPOINT = (210, 112, 15)

# UI
C_WHITE      = (230, 236, 246)
C_GRAY       = (100, 115, 135)
C_DARK       = (22,  28,  40)
C_ROW_EVEN   = (14,  18,  28)
C_ROW_ODD    = (20,  25,  37)
C_ROW_SEL    = (22,  45,  18)

STAT_COLORS = {
    "total": C_WHITE,
    "astar": C_AIR,
    "comb" : C_FIRE,
}

TERRAIN_LEGEND = [
    ("Plano",      C_PLAIN),
    ("Rochoso",    C_ROCK),
    ("Floresta",   C_FOREST),
    ("Água",       C_WATER),
    ("Montanha",   C_MOUNT),
    ("Checkpoint", C_CHECKPOINT),
]


# ─────────────────────────────────────────────
#  PIXEL FONT  (extraída de Miscellaneous-Font-and-Options.png)
# ─────────────────────────────────────────────
class AvatarPixelFont:
    """
    Recorta as letras da sprite-sheet de fonte do jogo GBA.
    """

    # Ajuste estes valores conforme a imagem real:
    TILE_W  = 14   # largura de cada caractere na sprite-sheet
    TILE_H  = 14   # altura de cada caractere
    COLS    =  9   # quantos chars por linha na sheet

    # Mapeamento: char → (col, row) na grid da imagem
    _MAP: dict[str, tuple[int, int]] = {}

    def __init__(self, sheet: pygame.Surface):
        """
        Inicializa a fonte com a sprite-sheet.
        :param sheet: Superfície da sprite-sheet.
        """
        self.sheet = sheet
        self._build_map()
        self._cache: dict[tuple, pygame.Surface] = {}

    def _build_map(self):
        """Constrói o mapeamento char → posição na grid."""
        # Maiúsculas A-Z  (26 chars, dispostos em 3 linhas de 9)
        for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            self._MAP[ch] = (i % self.COLS, i // self.COLS)

        # Minúsculas a-z (linha 3 em diante na sheet)
        row_offset = math.ceil(26 / self.COLS)   # linha onde as minúsculas começam
        for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
            self._MAP[ch] = (i % self.COLS, row_offset + i // self.COLS)

    def get_char(self, ch: str, color_key=(0, 0, 255)) -> pygame.Surface | None:
        """
        Retorna a superfície recortada de um caractere.
        :param ch: Caractere.
        :param color_key: Chave de cor para transparência.
        :return: Superfície do caractere ou None.
        """
        if ch not in self._MAP:
            return None
        pos = self._MAP[ch]
        key = (ch, color_key)
        if key not in self._cache:
            x = pos[0] * self.TILE_W
            y = pos[1] * self.TILE_H
            surf = pygame.Surface((self.TILE_W, self.TILE_H), pygame.SRCALPHA)
            surf.blit(self.sheet, (0, 0), (x, y, self.TILE_W, self.TILE_H))
            # Remove fundo azul da sprite-sheet
            surf.set_colorkey(color_key)
            self._cache[key] = surf
        return self._cache[key]

    def render(self, text: str, scale: float = 1.0) -> pygame.Surface:
        """
        Renderiza uma string usando os glifos da font sheet.
        :param text: Texto a renderizar.
        :param scale: Escala.
        :return: Superfície renderizada.
        """
        chars = [self.get_char(c) for c in text]
        chars = [c for c in chars if c is not None]
        if not chars:
            return pygame.Surface((0, 0))

        tw = int(self.TILE_W * scale)
        th = int(self.TILE_H * scale)
        total_w = tw * len(chars)
        surf = pygame.Surface((total_w, th), pygame.SRCALPHA)
        for i, ch_surf in enumerate(chars):
            scaled = pygame.transform.scale(ch_surf, (tw, th)) if scale != 1.0 else ch_surf
            surf.blit(scaled, (i * tw, 0))
        return surf


# ─────────────────────────────────────────────
#  HELPERS DE DESENHO
# ─────────────────────────────────────────────
def draw_text(surf, text, font, color, x, y, align="left"):
    """
    Desenha texto na superfície.
    :param surf: Superfície.
    :param text: Texto.
    :param font: Fonte.
    :param color: Cor.
    :param x: Posição x.
    :param y: Posição y.
    :param align: Alinhamento.
    """
    img = font.render(str(text), True, color)
    if align == "center": x -= img.get_width() // 2
    elif align == "right": x -= img.get_width()
    surf.blit(img, (x, y))


def draw_text_shadow(surf, text, font, color, x, y, align="left"):
    """
    Desenha texto com sombra.
    :param surf: Superfície.
    :param text: Texto.
    :param font: Fonte.
    :param color: Cor.
    :param x: Posição x.
    :param y: Posição y.
    :param align: Alinhamento.
    """
    shadow = font.render(str(text), True, (0, 0, 0))
    img    = font.render(str(text), True, color)
    if align == "center":
        x -= img.get_width() // 2
    elif align == "right":
        x -= img.get_width()
    surf.blit(shadow, (x + 1, y + 1))
    surf.blit(img,    (x,     y))


def blit_pixel_text(surf, px_font: AvatarPixelFont | None,
                    fallback_font, text: str, color,
                    x, y, scale=1.0, align="left"):
    """
    Tenta usar a pixel-font do jogo; cai para font SDL se não disponível.
    :param surf: Superfície.
    :param px_font: Fonte pixel.
    :param fallback_font: Fonte fallback.
    :param text: Texto.
    :param color: Cor.
    :param x: Posição x.
    :param y: Posição y.
    :param scale: Escala.
    :param align: Alinhamento.
    """
    if px_font is not None:
        img = px_font.render(text.upper(), scale)
        if img.get_width() > 0:
            # Coloriza: multiplica pixel-a-pixel pela cor desejada
            colored = img.copy()
            colored.fill((*color, 0), special_flags=pygame.BLEND_RGBA_MULT)
            colored.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            # Simplificado: apenas blit com tint
            img.fill((*color, 255), special_flags=pygame.BLEND_RGB_MULT)
            if align == "center": x -= img.get_width() // 2
            elif align == "right": x -= img.get_width()
            surf.blit(img, (x, y))
            return
    draw_text_shadow(surf, text, fallback_font, color, x, y, align)


def draw_button(surf, rect, label, font, active=False, hover=False):
    """
    Desenha um botão.
    :param surf: Superfície.
    :param rect: Retângulo.
    :param label: Rótulo.
    :param font: Fonte.
    :param active: Se ativo.
    :param hover: Se hover.
    """
    if active:
        bg, border = C_FIRE, C_GOLD
    elif hover:
        bg, border = (38, 48, 62), C_FIRE
    else:
        bg, border = (20, 26, 38), (48, 58, 76)

    pygame.draw.rect(surf, bg, rect, border_radius=4)
    pygame.draw.rect(surf, border, rect, 1, border_radius=4)
    # Brilho superior (estilo GBA)
    pygame.draw.rect(surf, (255, 220, 140) if active else (55, 65, 85),
                     (rect.x + 3, rect.y + 2, rect.w - 6, 1))
    txt_c = (12, 8, 0) if active else C_WHITE
    draw_text(surf, label, font, txt_c,
              rect.x + rect.w // 2, rect.y + rect.h // 2 - font.get_height() // 2,
              "center")


# ─────────────────────────────────────────────
#  CLASSE PRINCIPAL
# ─────────────────────────────────────────────
class VisualizadorPygame:
    """
    Classe para visualizar a jornada usando Pygame.
    """

    def __init__(self, mapa, caminho_calculado, log_jornada):
        """
        Inicializa o visualizador.
        :param mapa: Objeto mapa.
        :param caminho_calculado: Lista de caminho.
        :param log_jornada: Lista de log da jornada.
        """
        pygame.init()
        pygame.display.set_caption("Avatar Path · INF1771")
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.clock  = pygame.time.Clock()

        self.mapa    = mapa
        self.caminho = caminho_calculado
        self.trechos = log_jornada

        self.cam_x, self.cam_y = 0, 0
        self.TILE        = 10
        self.is_dragging = False
        self.last_mouse  = (0, 0)
        self.anim_tick   = 0

        self._load_assets()

        # Fontes SDL (fallback e para números/dados)
        self.f_title    = pygame.font.SysFont("Impact", 19)
        self.f_sub      = pygame.font.SysFont("Arial",  10)
        self.f_stat_v   = pygame.font.SysFont("Impact", 21)
        self.f_stat_l   = pygame.font.SysFont("Arial",  10)
        self.f_btn      = pygame.font.SysFont("Arial",  11, bold=True)
        self.f_card_h   = pygame.font.SysFont("Arial",  11, bold=True)
        self.f_legend   = pygame.font.SysFont("Arial",  10)
        self.f_table_h  = pygame.font.SysFont("Arial",  11, bold=True)
        self.f_table    = pygame.font.SysFont("Arial",  11)
        self.f_cp       = pygame.font.SysFont("Arial",   8, bold=True)
        self.f_badge    = pygame.font.SysFont("Arial",   9, bold=True)

        self.passo        = 0
        self.playing      = False
        self.concluido    = False
        self.table_scroll = 0

        pygame.time.set_timer(pygame.USEREVENT + 1, STEP_MS)
        self._update_layout()
        self._center_map()

    # ── Carregamento de Assets ────────────────
    def _load_assets(self):
        self.assets = {}

        # Inicializa a pixel-font se a sheet carregou
        if self.assets.get("font_sheet"):
            self.px_font = AvatarPixelFont(self.assets["font_sheet"])
        else:
            self.px_font = None

        # ── Pré-processa o background de montanha ──
        # Extrai o painel de fundo de montanha da intro (canto superior direito)
        self.bg_mountain = None
        intro = self.assets.get("intro")
        if intro:
            iw, ih = intro.get_size()
            # O background de montanha ocupa aprox. a coluna direita da intro sheet
            # (ajuste as coordenadas conforme o layout real)
            crop_rect = pygame.Rect(int(iw * 0.72), 0, int(iw * 0.28), ih // 2)
            self.bg_mountain = pygame.Surface((crop_rect.w, crop_rect.h), pygame.SRCALPHA)
            self.bg_mountain.blit(intro, (0, 0), crop_rect)

        # ── Logo "Avatar: The Last Airbender" ──
        # Extrai o logo da tela de título (linha 2, col 2 da intro sheet)
        self.logo_avatar = None
        if intro:
            iw, ih = intro.get_size()
            # Linha 2 = rows 1/3 a 2/3 da height; coluna central
            logo_rect = pygame.Rect(int(iw * 0.34), int(ih * 0.34),
                                    int(iw * 0.35), int(ih * 0.16))
            self.logo_avatar = pygame.Surface((logo_rect.w, logo_rect.h), pygame.SRCALPHA)
            self.logo_avatar.blit(intro, (0, 0), logo_rect)

        # ── Retrato do Aang (primeiro da sheet de portraits) ──
        self.portrait_aang = None
        portrait_sheet = self.assets.get("aang_portrait")
        if portrait_sheet:
            pw, ph = portrait_sheet.get_size()
            # Primeiro retrato: canto superior esquerdo, approx 1/4 da largura
            port_rect = pygame.Rect(0, 0, pw // 4, ph // 6)
            self.portrait_aang = pygame.Surface((port_rect.w, port_rect.h), pygame.SRCALPHA)
            self.portrait_aang.blit(portrait_sheet, (0, 0), port_rect)
            self.portrait_aang.set_colorkey((0, 0, 255))  # remove fundo azul

    # ── Layout ───────────────────────────────
    def _update_layout(self):
        self.WIN_W, self.WIN_H = self.screen.get_size()
        self.MAP_W = max(400, self.WIN_W - PANEL_W)
        self.MAP_H = self.WIN_H

        x0    = self.MAP_W + 14
        btn_w = (PANEL_W - 32) // 4

        self.btn_play  = pygame.Rect(x0,                    262, btn_w - 2, 26)
        self.btn_pause = pygame.Rect(x0 +   btn_w,          262, btn_w - 2, 26)
        self.btn_adv   = pygame.Rect(x0 + 2*btn_w,          262, btn_w - 2, 26)
        self.btn_reset = pygame.Rect(x0 + 3*btn_w,          262, btn_w - 2, 26)

    def _center_map(self):
        rows = len(self.mapa.matriz)
        cols = len(self.mapa.matriz[0]) if rows else 1
        self.TILE  = max(2, min(self.MAP_W // cols, self.MAP_H // rows))
        self.cam_x = -(self.MAP_W - cols * self.TILE) // 2
        self.cam_y = -(self.MAP_H - rows * self.TILE) // 2
        self._build_static_map()

    def _zoom(self, direction, mx, my):
        if mx >= self.MAP_W: return
        old = self.TILE
        self.TILE = max(2, min(self.TILE + direction * max(1, self.TILE // 5), 40))
        if old != self.TILE:
            self.cam_x = int(((mx + self.cam_x) / old) * self.TILE - mx)
            self.cam_y = int(((my + self.cam_y) / old) * self.TILE - my)
            self._build_static_map()

    def _build_static_map(self):
        rows = len(self.mapa.matriz)
        cols = len(self.mapa.matriz[0])
        self.map_surf = pygame.Surface((cols * self.TILE, rows * self.TILE))
        cmap = {'.': C_PLAIN, 'R': C_ROCK, 'F': C_FOREST, 'A': C_WATER, 'M': C_MOUNT}

        for y, linha in enumerate(self.mapa.matriz):
            for x, ch in enumerate(linha):
                col = cmap.get(ch, C_PLAIN)
                pygame.draw.rect(self.map_surf, col,
                                 (x * self.TILE, y * self.TILE, self.TILE, self.TILE))
                if self.TILE >= 6:
                    darker = tuple(max(0, c - 20) for c in col)
                    pygame.draw.rect(self.map_surf, darker,
                                     (x * self.TILE, y * self.TILE, self.TILE, self.TILE), 1)

        for k, (cx, cy) in self.mapa.checkpoints.items():
            pygame.draw.rect(self.map_surf, C_CHECKPOINT,
                             (cx * self.TILE, cy * self.TILE, self.TILE, self.TILE))
            if self.TILE > 8:
                lbl = self.f_cp.render(k, True, (20, 8, 0))
                self.map_surf.blit(lbl, (
                    cx * self.TILE + (self.TILE - lbl.get_width()) // 2,
                    cy * self.TILE + (self.TILE - lbl.get_height()) // 2))

    # ── Área do Mapa ─────────────────────────
    def _draw_map_area(self):
        clip = pygame.Rect(0, 0, self.MAP_W, self.MAP_H)
        self.screen.set_clip(clip)
        self.screen.fill(BG)

        # Background de montanha (intro) no canto superior esquerdo do mapa
        if self.bg_mountain:
            bw = min(self.MAP_W, self.bg_mountain.get_width())
            bh = min(self.MAP_H // 3, self.bg_mountain.get_height())
            scaled_bg = pygame.transform.smoothscale(self.bg_mountain, (bw, bh))
            scaled_bg.set_alpha(40)  # bem transparente, só ambienta
            self.screen.blit(scaled_bg, (0, 0))

        self.screen.blit(self.map_surf, (-self.cam_x, -self.cam_y))

        if self.caminho:
            # Rastro de fogo
            for i in range(self.passo):
                tx, ty = self.caminho[i]
                age = self.passo - i
                r = min(255, 180 + age)
                g = max(0, 90 - age * 4)
                pygame.draw.rect(self.screen, (r, g, 10),
                    (tx * self.TILE - self.cam_x + 1,
                     ty * self.TILE - self.cam_y + 1,
                     self.TILE - 2, self.TILE - 2))

            # Agente Aang
            ax, ay = self.caminho[min(self.passo, len(self.caminho) - 1)]
            cx = ax * self.TILE + self.TILE // 2 - self.cam_x
            cy = ay * self.TILE + self.TILE // 2 - self.cam_y

            # Aura de ar pulsante
            pulse = abs(math.sin(self.anim_tick * 0.07)) * 5
            pygame.draw.circle(self.screen, C_AIR_DIM,
                               (cx, cy), int(self.TILE * 0.95 + pulse), 1)
            pygame.draw.circle(self.screen, C_AIR,
                               (cx, cy), int(self.TILE * 0.65 + pulse * 0.5), 1)

            aang_sprite = self.assets.get("aang_sprite")
            if aang_sprite:
                # Usa a primeira pose de caminhada (canto superior esquerdo da sheet)
                # A sheet tem múltiplos frames — pega o primeiro (aprox 24x32 px)
                sw, sh = aang_sprite.get_size()
                frame_w = sw // 8   # estimativa de colunas na sheet
                frame_h = sh // 12  # estimativa de linhas
                frame_rect = pygame.Rect(0, 0, frame_w, frame_h)

                frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame_surf.blit(aang_sprite, (0, 0), frame_rect)
                frame_surf.set_colorkey((255, 255, 255))  # fundo branco

                tamanho = max(self.TILE * 2, 24)
                scaled  = pygame.transform.smoothscale(frame_surf, (tamanho, tamanho))
                self.screen.blit(scaled, scaled.get_rect(center=(cx, cy)))
            else:
                pygame.draw.circle(self.screen, C_GOLD, (cx, cy), max(3, self.TILE // 2))

        # Borda divisória lateral
        pygame.draw.line(self.screen, C_FIRE_DIM, (self.MAP_W - 2, 0), (self.MAP_W - 2, self.MAP_H), 2)
        pygame.draw.line(self.screen, C_FIRE,     (self.MAP_W - 1, 0), (self.MAP_W - 1, self.MAP_H), 1)
        self.screen.set_clip(None)

    # ── Card base ────────────────────────────
    def _draw_card(self, x, y, w, h, title="", title_color=None):
        if title_color is None:
            title_color = C_FIRE
        pygame.draw.rect(self.screen, CARD_BG, (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, CARD_BORDER, (x, y, w, h), 1, border_radius=5)
        if title:
            pygame.draw.rect(self.screen, HEADER_BG,
                             (x, y, w, 26),
                             border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.line(self.screen, CARD_BORDER, (x + 6, y + 26), (x + w - 6, y + 26), 1)
            # Usa pixel-font para o título se disponível
            blit_pixel_text(self.screen, self.px_font, self.f_card_h,
                            title, title_color, x + 12, y + 7)

    # ── Painel ───────────────────────────────
    def _draw_panel(self, mx, my):
        px, pw, ph = self.MAP_W, PANEL_W, self.WIN_H
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, pw, ph))

        cx   = px + 12
        cw   = pw - 24
        py   = 8

        # ── HEADER com logo Avatar e Momo ────
        hh = 74
        pygame.draw.rect(self.screen, HEADER_BG, (cx, py, cw, hh), border_radius=6)
        pygame.draw.rect(self.screen, C_FIRE,    (cx, py, cw, hh), 1, border_radius=6)
        # Linha de brilho dourado topo
        pygame.draw.rect(self.screen, C_GOLD, (cx + 2, py + 1, cw - 4, 2), border_radius=4)

        # Logo Avatar (cropped da intro sheet) — ocupa a parte esquerda/central
        logo = self.logo_avatar
        if logo:
            lw = min(cw - 60, 200)
            lh = int(logo.get_height() * (lw / logo.get_width()))
            lh = min(lh, hh - 10)
            scaled_logo = pygame.transform.smoothscale(logo, (lw, lh))
            scaled_logo.set_colorkey((0, 128, 0))  # remove fundo verde da sheet
            self.screen.blit(scaled_logo, (cx + 8, py + (hh - lh) // 2))
        else:
            # Fallback: texto com pixel-font
            blit_pixel_text(self.screen, self.px_font, self.f_title,
                            "AVATAR PATH", C_FIRE, cx + 10, py + 12, scale=1.1)
            draw_text(self.screen, "INF1771 · Busca de Caminhos",
                      self.f_sub, C_AIR_DIM, cx + 10, py + 48)

        # Momo no canto direito do header
        momo = self.assets.get("momo")
        if momo:
            mh = hh - 8
            mw = int(momo.get_width() * (mh / momo.get_height()))
            scaled_momo = pygame.transform.smoothscale(momo, (mw, mh))
            self.screen.blit(scaled_momo, (cx + cw - mw - 4, py + 4))

        py += hh + 7

        # ── CARD 1: Status + Retrato do Aang ─
        hc1 = 66
        self._draw_card(cx, py, cw, hc1, "ESTADO DA MISSAO")

        # Retrato do Aang no card de status
        portrait = self.portrait_aang
        portrait_w = 0
        if portrait:
            ph_scaled = hc1 - 14
            pw_scaled = int(portrait.get_width() * (ph_scaled / portrait.get_height()))
            scaled_p  = pygame.transform.smoothscale(portrait, (pw_scaled, ph_scaled))
            self.screen.blit(scaled_p, (cx + cw - pw_scaled - 8, py + 7))
            portrait_w = pw_scaled + 12

        # Texto de status
        if self.concluido:
            status_txt, cor = "Destino Alcancado!", C_EARTH
        elif self.playing:
            status_txt, cor = "Simulacao Ativa...", C_AIR
        else:
            status_txt, cor = "Em Pausa", C_GRAY

        blit_pixel_text(self.screen, self.px_font, self.f_stat_v,
                        status_txt, cor, cx + 12, py + 30, scale=0.95)

        idx = -1
        if self.trechos and self.caminho:
            idx = min(int((self.passo / max(1, len(self.caminho) - 1)) * len(self.trechos)),
                      len(self.trechos) - 1)
        row = self.trechos[idx] if idx >= 0 else {"astar": 0, "comb": 0}
        py += hc1 + 6

        # ── CARD 2: Métricas ─────────────────
        hc2 = 88
        self._draw_card(cx, py, cw, hc2, "METRICAS DO CUSTO A*", C_AIR)
        stats = [
            ("Total",   f"{row.get('astar',0)+row.get('comb',0):.1f}", STAT_COLORS["total"]),
            ("Viagem",  f"{row.get('astar',0):.1f}",                   STAT_COLORS["astar"]),
            ("Batalha", f"{row.get('comb',0):.1f}",                    STAT_COLORS["comb"]),
        ]
        sw = (cw - 30) // 3
        for i, (lbl, val, col) in enumerate(stats):
            bx = cx + 10 + i * (sw + 5)
            by = py + 30
            pygame.draw.rect(self.screen, (10, 14, 22), (bx, by, sw, 48), border_radius=4)
            pygame.draw.rect(self.screen, (38, 48, 65), (bx, by, sw, 48), 1, border_radius=4)
            draw_text(self.screen, lbl, self.f_stat_l, C_GRAY, bx + sw // 2, by + 6, "center")
            draw_text(self.screen, val, self.f_stat_v, col,    bx + sw // 2, by + 22, "center")
        py += hc2 + 6

        # ── CARD 3: Controles ────────────────
        hc3 = 100
        self._draw_card(cx, py, cw, hc3, "CONTROLES DE NAVEGACAO")

        draw_button(self.screen, self.btn_play,  "PLAY",   self.f_btn,
                    active=self.playing,
                    hover=self.btn_play.collidepoint(mx, my))
        draw_button(self.screen, self.btn_pause, "PAUSA",  self.f_btn,
                    active=not self.playing and not self.concluido,
                    hover=self.btn_pause.collidepoint(mx, my))
        draw_button(self.screen, self.btn_adv,   "STEP",   self.f_btn,
                    hover=self.btn_adv.collidepoint(mx, my))
        draw_button(self.screen, self.btn_reset, "RESET",  self.f_btn,
                    hover=self.btn_reset.collidepoint(mx, my))

        # Barra de progresso
        prog  = (self.passo / max(1, len(self.caminho) - 1)) if self.caminho else 0
        bar_y = py + 70
        bar_x = cx + 10
        bar_w = cw - 20
        pygame.draw.rect(self.screen, (18, 22, 32), (bar_x, bar_y, bar_w, 8), border_radius=4)
        pygame.draw.rect(self.screen, (38, 48, 65), (bar_x, bar_y, bar_w, 8), 1, border_radius=4)
        fill = int(bar_w * prog)
        if fill > 2:
            pygame.draw.rect(self.screen, C_FIRE, (bar_x, bar_y, fill, 8), border_radius=4)
            # Chama na ponta
            pygame.draw.circle(self.screen, C_GOLD, (bar_x + fill, bar_y + 4), 4)
        draw_text(self.screen, f"{int(prog*100)}%", self.f_badge, C_GRAY,
                  cx + cw - 10, bar_y - 1, "right")
        py += hc3 + 6

        # ── CARD 4: Legenda ──────────────────
        hc4 = 82
        self._draw_card(cx, py, cw, hc4, "LEGENDA DO MAPA", C_EARTH)
        lx = cx + 10
        ly = py + 30
        for i, (nome, cor) in enumerate(TERRAIN_LEGEND):
            ex = lx + (i % 3) * (cw // 3)
            ey = ly + (i // 3) * 22
            pygame.draw.rect(self.screen, cor, (ex, ey, 11, 11), border_radius=2)
            pygame.draw.rect(self.screen, (180, 180, 180), (ex, ey, 11, 11), 1, border_radius=2)
            draw_text(self.screen, nome, self.f_legend, C_WHITE, ex + 15, ey + 1)
        py += hc4 + 6

        # ── CARD 5: Tabela de Rota ───────────
        hc5 = ph - py - 10
        self._draw_card(cx, py, cw, hc5, "DETALHES DA ROTA", C_WATER_ELEM)

        cols_x = [cx + 10, cx + 80, cx + 136, cx + 192]
        ty     = py + 30

        # Cabeçalho da tabela
        pygame.draw.rect(self.screen, (14, 20, 34),
                         (cx + 6, ty - 2, cw - 12, 18), border_radius=3)
        for i, h in enumerate(["Trecho", "A*", "Luta", "Equipa"]):
            draw_text(self.screen, h, self.f_table_h, C_AIR, cols_x[i], ty)
        ty += 20
        pygame.draw.line(self.screen, CARD_BORDER,
                         (cx + 6, ty - 2), (cx + cw - 6, ty - 2), 1)

        table_clip = pygame.Rect(cx + 4, ty, cw - 8, hc5 - 52)
        self.screen.set_clip(table_clip)
        for i, r in enumerate(self.trechos):
            iy  = ty + (i - self.table_scroll) * 22
            sel = (i == idx)
            bg_r= (20, 42, 16) if sel else (C_ROW_EVEN if i % 2 == 0 else C_ROW_ODD)
            pygame.draw.rect(self.screen, bg_r,
                             (cx + 6, iy, cw - 12, 20), border_radius=3)
            if sel:
                pygame.draw.rect(self.screen, C_EARTH,
                                 (cx + 6, iy, cw - 12, 20), 1, border_radius=3)
                draw_text(self.screen, "►", self.f_badge, C_FIRE, cx + 6, iy + 5)
            draw_text(self.screen, str(r.get("trecho",     "")),      self.f_table, C_WHITE,  cols_x[0], iy + 4)
            draw_text(self.screen, f"{r.get('delta_astar', 0):.1f}",  self.f_table, C_AIR,    cols_x[1], iy + 4)
            draw_text(self.screen, f"{r.get('delta_comb',  0):.1f}",  self.f_table, C_FIRE,   cols_x[2], iy + 4)
            draw_text(self.screen, str(r.get("equipe",     "")),       self.f_table, C_GRAY,   cols_x[3], iy + 4)
        self.screen.set_clip(None)

    # ── Loop ─────────────────────────────────
    def iniciar_loop(self):
        """
        Inicia o loop principal da interface gráfica.
        """
        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            self.anim_tick += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._update_layout()
                    self._center_map()
                elif event.type == pygame.USEREVENT + 1 and self.playing and not self.concluido:
                    self.passo += 1
                    if self.passo >= len(self.caminho) - 1:
                        self.playing, self.concluido = False, True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if mx < self.MAP_W:
                            self.is_dragging = True
                            self.last_mouse  = event.pos
                        elif self.btn_play.collidepoint(mx, my):
                            if self.concluido:
                                self.passo, self.concluido = 0, False
                            self.playing = True
                        elif self.btn_pause.collidepoint(mx, my):
                            self.playing = False
                        elif self.btn_adv.collidepoint(mx, my):
                            self.passo = min(self.passo + 1, len(self.caminho) - 1)
                        elif self.btn_reset.collidepoint(mx, my):
                            self.passo, self.playing, self.concluido = 0, False, False
                    elif event.button == 3:
                        self._center_map()
                    elif event.button == 4:
                        self._zoom(1, mx, my)
                    elif event.button == 5:
                        self._zoom(-1, mx, my)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging = False
                elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                    self.cam_x -= event.pos[0] - self.last_mouse[0]
                    self.cam_y -= event.pos[1] - self.last_mouse[1]
                    self.last_mouse = event.pos
                elif event.type == pygame.MOUSEWHEEL and mx > self.MAP_W:
                    self.table_scroll = max(0, self.table_scroll - event.y)

            self.screen.fill(BG)
            self._draw_map_area()
            self._draw_panel(mx, my)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()