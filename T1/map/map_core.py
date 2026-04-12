"""
Aqui fica a classe responsável por ler o mapa, achar vizinhos e desenhar no terminal.
"""

from map.constants import CUSTOS_TERRENO

class MapaAang:
    """Carrega, armazena e exibe o mapa do mundo de Avatar."""

    def __init__(self, caminho_arquivo):
        self.matriz = []
        self.checkpoints = {}
        self.custos_terreno = CUSTOS_TERRENO
        self.carregar_mapa(caminho_arquivo)

    def carregar_mapa(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                for y, linha in enumerate(arquivo):
                    linha_matriz = []
                    for x, char in enumerate(linha.strip()):
                        if char in self.custos_terreno:
                            linha_matriz.append(char)
                        else:
                            self.checkpoints[char] = (x, y)
                            linha_matriz.append('.')   # Checkpoints ficam sobre terreno plano
                    self.matriz.append(linha_matriz)

            altura = len(self.matriz)
            largura = len(self.matriz[0]) if altura > 0 else 0
            print(f"Mapa carregado: {largura}x{altura} (largura x altura).")
            print(f"Total de checkpoints registrados: {len(self.checkpoints)}")

        except FileNotFoundError:
            print(f"ERRO CRÍTICO: Arquivo '{caminho_arquivo}' não encontrado.")

    def obter_custo(self, x, y):
        return self.custos_terreno[self.matriz[y][x]]

    def obter_ordem_checkpoints(self):
        return sorted(self.checkpoints.keys())

    def vizinhos_validos(self, x, y):
        altura = len(self.matriz)
        largura = len(self.matriz[0]) if altura > 0 else 0
        vizinhos = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura:
                vizinhos.append((nx, ny))
        return vizinhos

    def exibir_mapa(self, caminho=None):
        matriz_visual = [linha[:] for linha in self.matriz]

        if caminho:
            for x, y in caminho:
                matriz_visual[y][x] = '█'

        for checkpoint, (x, y) in self.checkpoints.items():
            matriz_visual[y][x] = checkpoint

        print("\n=== MAPA DO AVATAR ===")
        for linha in matriz_visual:
            print("".join(linha))
        print("======================\n")