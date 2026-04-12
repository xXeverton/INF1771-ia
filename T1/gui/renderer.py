# gui/renderer.py

import pygame
import sys
import os

# --- SILENCIA OS ERROS DE ÁUDIO (ALSA) NO LINUX ---
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Constantes de Interface
TAMANHO_TILE = 24  # Um tamanho excelente para pixel art GBA
LARGURA_TELA = 1200 # Tela cheia para o mapa
ALTURA_TELA = 800

# Cores
COR_DESTAQUE = (255, 153, 51)
COR_RASTRO = (255, 255, 0, 150)

class VisualizadorPygame:
    def __init__(self, mapa, caminho_calculado, log_jornada):
        pygame.init()
        pygame.display.set_caption("A Lenda de Aang - IA (Trabalho 1)")
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        self.clock = pygame.time.Clock()
        
        self.fonte_cabecalho = pygame.font.SysFont("Arial", 13, bold=True)

        self.mapa = mapa
        self.caminho = caminho_calculado
        self.log_jornada = log_jornada # Guardamos caso queira imprimir no terminal no futuro
        
        self.tiles = {}
        self.carregar_assets()

        # === SETUP DO MAPA GIGANTE ===
        self.linhas_mapa = len(self.mapa.matriz)
        self.cols_mapa = len(self.mapa.matriz[0]) if self.linhas_mapa > 0 else 1
        
        # Cria uma superfície gigante que caberá todo o mapa
        self.map_surface = pygame.Surface((self.cols_mapa * TAMANHO_TILE, self.linhas_mapa * TAMANHO_TILE))
        self.desenhar_mapa_estatico()

        # Variáveis de Animação
        self.passo_caminho = 0  # Índice de onde o Aang está no array de coordenadas

    def carregar_assets(self):
        """Carrega e ajusta os assets para 24x24 pixels."""
        try:
            self.tiles['A'] = pygame.transform.scale(pygame.image.load('assets/water.png'), (TAMANHO_TILE, TAMANHO_TILE))
            self.tiles['R'] = pygame.transform.scale(pygame.image.load('assets/rock.png'), (TAMANHO_TILE, TAMANHO_TILE))
            self.tiles['F'] = pygame.transform.scale(pygame.image.load('assets/treetop.png'), (TAMANHO_TILE, TAMANHO_TILE))
            self.tiles['M'] = pygame.transform.scale(pygame.image.load('assets/trunk.png'), (TAMANHO_TILE, TAMANHO_TILE))
            # Futuramente o Aang: self.img_aang = pygame.image.load('assets/Playable-Characters-Avatar-Aang.png')
        except FileNotFoundError:
            pass 

    def desenhar_mapa_estatico(self):
        """Pinta o mapa uma única vez na superfície gigante."""
        self.map_surface.fill((10, 10, 15))
        cores = {
            '.': (80, 140, 80),  'R': (100, 100, 100), 'F': (34, 100, 34),
            'A': (50, 80, 180),  'M': (101, 67, 33)
        }
        
        for y, linha in enumerate(self.mapa.matriz):
            for x, char in enumerate(linha):
                rect = pygame.Rect(x * TAMANHO_TILE, y * TAMANHO_TILE, TAMANHO_TILE, TAMANHO_TILE)
                
                # É um checkpoint?
                is_checkpoint = False
                chave_check = ""
                for k, coord in self.mapa.checkpoints.items():
                    if coord == (x, y):
                        is_checkpoint = True
                        chave_check = k
                        break

                if is_checkpoint:
                    pygame.draw.rect(self.map_surface, COR_DESTAQUE, rect)
                    texto = self.fonte_cabecalho.render(chave_check, True, (0,0,0))
                    self.map_surface.blit(texto, (x * TAMANHO_TILE + 6, y * TAMANHO_TILE + 4))
                else:
                    if char in self.tiles:
                        self.map_surface.blit(self.tiles[char], rect)
                    else:
                        pygame.draw.rect(self.map_surface, cores.get(char, (0,0,0)), rect)

    def render_camera_e_agente(self):
        """Sistema de Câmera: Enquadra o pedaço do mapa onde o agente está usando a tela inteira."""
        if not self.caminho: return
        
        # Pega a posição atual do Agente
        ax, ay = self.caminho[self.passo_caminho]

        # Câmera tenta centralizar no agente (agora baseada na LARGURA_TELA inteira)
        cam_x = (ax * TAMANHO_TILE) - (LARGURA_TELA // 2)
        cam_y = (ay * TAMANHO_TILE) - (ALTURA_TELA // 2)

        # Não deixa a câmera sair das bordas do mapa
        cam_x = max(0, min(cam_x, self.map_surface.get_width() - LARGURA_TELA))
        cam_y = max(0, min(cam_y, self.map_surface.get_height() - ALTURA_TELA))

        # 1. Pinta a visão da Câmera na Tela Inteira
        self.tela.blit(self.map_surface, (0, 0), (cam_x, cam_y, LARGURA_TELA, ALTURA_TELA))

        # 2. Desenha o rastro amarelo por onde ele já passou
        s_rastro = pygame.Surface((TAMANHO_TILE, TAMANHO_TILE), pygame.SRCALPHA)
        s_rastro.fill((255, 255, 0, 80)) # Amarelo transparente
        
        for i in range(self.passo_caminho):
            cx, cy = self.caminho[i]
            rx = (cx * TAMANHO_TILE) - cam_x
            ry = (cy * TAMANHO_TILE) - cam_y
            # Só desenha se estiver dentro da câmera
            if -TAMANHO_TILE <= rx <= LARGURA_TELA and -TAMANHO_TILE <= ry <= ALTURA_TELA:
                self.tela.blit(s_rastro, (rx, ry))

        # 3. Desenha o Avatar (Por enquanto um quadrado vermelho)
        rx = (ax * TAMANHO_TILE) - cam_x
        ry = (ay * TAMANHO_TILE) - cam_y
        pygame.draw.rect(self.tela, (255, 50, 50), (rx, ry, TAMANHO_TILE, TAMANHO_TILE))

    def atualizar_simulacao(self):
        """Avança o Agente no mapa."""
        if self.passo_caminho < len(self.caminho) - 1:
            self.passo_caminho += 1 # O Aang dá 1 passo

    def iniciar_loop(self):
        # A velocidade do jogo: atualiza a cada 30ms
        pygame.time.set_timer(pygame.USEREVENT, 30) 
        
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.USEREVENT:
                    self.atualizar_simulacao()

            self.tela.fill((0, 0, 0))
            
            # Chama apenas o render da câmera em tela cheia
            self.render_camera_e_agente()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()