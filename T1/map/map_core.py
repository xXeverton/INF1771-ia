# Este arquivo define a classe MapaAang, responsável por gerenciar o mapa do jogo.

"""
Carrega, armazena e exibe o mapa do mundo de Avatar.
"""

from map.constants import CUSTOS_TERRENO

class MapaAang:
    """
    Carrega, armazena e exibe o mapa do mundo de Avatar.
    """

    def __init__(self, caminho_arquivo):
        """
        Inicializa o mapa carregando do arquivo.
        :param caminho_arquivo: Caminho para o arquivo do mapa.
        """
        self.matriz = []
        self.checkpoints = {}
        self.custos_terreno = CUSTOS_TERRENO
        self.carregar_mapa(caminho_arquivo)

    def carregar_mapa(self, caminho_arquivo):
        """
        Carrega o mapa do arquivo.
        :param caminho_arquivo: Caminho para o arquivo.
        """
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                for y, linha in enumerate(arquivo):
                    linha_matriz = []
                    for x, char in enumerate(linha.strip()):
                        if char in self.custos_terreno:
                            linha_matriz.append(char)
                        else:
                            self.checkpoints[char] = (x, y)
                            linha_matriz.append('.')
                    self.matriz.append(linha_matriz)

            altura = len(self.matriz)
            largura = len(self.matriz[0]) if altura > 0 else 0
            print(f"Mapa carregado: {largura}x{altura}")
            print(f"Checkpoints encontrados: {len(self.checkpoints)}")

        except FileNotFoundError:
            print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")

    def obter_custo(self, x, y):
        """
        Obtém o custo do terreno na posição.
        :param x: Coordenada x.
        :param y: Coordenada y.
        :return: Custo do terreno.
        """
        return self.custos_terreno[self.matriz[y][x]]

    def obter_ordem_checkpoints(self):
        """
        Obtém a ordem alfabética dos checkpoints.
        :return: Lista ordenada de checkpoints.
        """
        return sorted(self.checkpoints.keys())

    def vizinhos_validos(self, x, y):
        """
        Obtém os vizinhos válidos da posição.
        :param x: Coordenada x.
        :param y: Coordenada y.
        :return: Lista de tuplas (nx, ny).
        """
        altura = len(self.matriz)
        largura = len(self.matriz[0]) if altura > 0 else 0
        vizinhos = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura:
                vizinhos.append((nx, ny))
        return vizinhos