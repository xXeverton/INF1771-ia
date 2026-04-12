"""
Este arquivo será totalmente neutro. 
Ele não precisa saber quem é o Aang, apenas recebe um mapa, uma origem e um destino, e devolve o caminho.
"""

import heapq

class No:
    """Representa um estado na busca A*, com posição, custos e ponteiro para o pai."""
    def __init__(self, x, y, custo_g=0, heuristica_h=0, pai=None):
        self.x = x
        self.y = y
        self.g = custo_g
        self.h = heuristica_h
        self.f = custo_g + heuristica_h
        self.pai = pai

    def __lt__(self, outro):
        return self.f < outro.f

def distancia_manhattan(x1, y1, x2, y2):
    """Heurística admissível: distância de Manhattan entre dois pontos."""
    return abs(x1 - x2) + abs(y1 - y2)

def executar_a_estrela(mapa, inicio, destino):
    """
    Algoritmo A* para encontrar o caminho de menor custo entre dois pontos.
    """
    fila_prioridade = []
    custos_g = {}

    h_inicial = distancia_manhattan(inicio[0], inicio[1], destino[0], destino[1])
    no_inicial = No(inicio[0], inicio[1], custo_g=0, heuristica_h=h_inicial)
    
    heapq.heappush(fila_prioridade, no_inicial)
    custos_g[inicio] = 0

    while fila_prioridade:
        no_atual = heapq.heappop(fila_prioridade)
        coord_atual = (no_atual.x, no_atual.y)

        # Chegamos ao destino
        if coord_atual == destino:
            caminho = []
            custo_trajeto = no_atual.g
            while no_atual is not None:
                caminho.append((no_atual.x, no_atual.y))
                no_atual = no_atual.pai
            caminho.reverse()
            return caminho, custo_trajeto

        # Expande os vizinhos válidos consultando o mapa
        for nx, ny in mapa.vizinhos_validos(no_atual.x, no_atual.y):
            coord_vizinho = (nx, ny)
            custo_terreno = mapa.obter_custo(nx, ny)
            novo_custo_g = no_atual.g + custo_terreno

            if coord_vizinho not in custos_g or novo_custo_g < custos_g[coord_vizinho]:
                custos_g[coord_vizinho] = novo_custo_g
                novo_h = distancia_manhattan(nx, ny, destino[0], destino[1])
                novo_no = No(nx, ny, custo_g=novo_custo_g, heuristica_h=novo_h, pai=no_atual)
                heapq.heappush(fila_prioridade, novo_no)

    # Destino inalcançável
    return [], float('inf')