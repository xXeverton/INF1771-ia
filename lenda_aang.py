import heapq

# =====================================================================
# CONFIGURAÇÕES EDITÁVEIS (enunciado exige que sejam fáceis de mudar)
# =====================================================================

# Custos de cada tipo de terreno (em minutos)
CUSTOS_TERRENO = {
    '.': 1,    # Plano
    'R': 5,    # Rochoso
    'F': 10,   # Floresta
    'A': 15,   # Água
    'M': 200   # Montanhoso
}

# Dificuldade de cada etapa (checkpoint '0' é a aldeia de partida, sem batalha)
DIFICULDADES = {
    '0': 0,                                                            # Partida (sem batalha)
    '1': 10,  '2': 20,  '3': 30,  '4': 40,  '5': 50,
    '6': 60,  '7': 70,  '8': 80,  '9': 90,
    'B': 100, 'C': 110, 'D': 120, 'E': 130, 'G': 140,
    'H': 150, 'I': 160, 'J': 170, 'K': 180, 'L': 190,
    'N': 200, 'O': 210, 'P': 220, 'Q': 230, 'S': 240,
    'T': 250, 'U': 260, 'V': 270, 'W': 280, 'X': 290,
    'Y': 300, 'Z': 310                                                 # Última batalha
}

# Agilidade de cada personagem (influencia o tempo das etapas)
EQUIPE_CONFIG = {
    "Aang":   {"energia": 8, "agilidade": 1.8},
    "Zukko":  {"energia": 8, "agilidade": 1.6},
    "Toph":   {"energia": 8, "agilidade": 1.6},
    "Katara": {"energia": 8, "agilidade": 1.6},
    "Sokka":  {"energia": 8, "agilidade": 1.4},
    "Appa":   {"energia": 8, "agilidade": 0.9},
    "Momo":   {"energia": 8, "agilidade": 0.7}
}

# Arquivo do mapa
ARQUIVO_MAPA = "MAPA_LENDA-AANG.txt"


# =====================================================================
# 1. ESTRUTURA DO NÓ (ESTADO DA BUSCA)
# =====================================================================
class No:
    """Representa um estado na busca A*, com posição, custos e ponteiro para o pai."""
    def __init__(self, x, y, custo_g=0, heuristica_h=0, pai=None):
        self.x = x
        self.y = y
        self.g = custo_g        # Custo real acumulado da origem até este nó
        self.h = heuristica_h   # Estimativa heurística até o destino
        self.f = custo_g + heuristica_h  # Custo total estimado (f = g + h)
        self.pai = pai          # Ponteiro para reconstrução do caminho

    def __lt__(self, outro):
        return self.f < outro.f


# =====================================================================
# 2. GERENCIAMENTO DO AMBIENTE (MAPA)
# =====================================================================
class MapaAang:
    """Carrega, armazena e exibe o mapa do mundo de Avatar."""

    def __init__(self, caminho_arquivo):
        self.matriz = []
        self.checkpoints = {}
        self.custos_terreno = CUSTOS_TERRENO
        self.carregar_mapa(caminho_arquivo)

    def carregar_mapa(self, caminho_arquivo):
        """Lê o arquivo .txt e separa terrenos de checkpoints."""
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                for y, linha in enumerate(arquivo):
                    linha_matriz = []
                    for x, char in enumerate(linha.strip()):
                        if char in self.custos_terreno:
                            linha_matriz.append(char)
                        else:
                            # Qualquer caractere fora dos terrenos é um checkpoint
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
        """Retorna o custo em minutos para pisar na célula (x, y)."""
        return self.custos_terreno[self.matriz[y][x]]

    def obter_ordem_checkpoints(self):
        """Retorna a lista de checkpoints na ordem correta da jornada (sort ASCII)."""
        return sorted(self.checkpoints.keys())

    def vizinhos_validos(self, x, y):
        """Retorna vizinhos acessíveis (4 direções: cima, baixo, esq, dir)."""
        altura = len(self.matriz)
        largura = len(self.matriz[0]) if altura > 0 else 0
        vizinhos = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura:
                vizinhos.append((nx, ny))
        return vizinhos

    def exibir_mapa(self, caminho=None):
        """Imprime o mapa no terminal, desenhando o rastro do agente se fornecido."""
        matriz_visual = [linha[:] for linha in self.matriz]

        # Marca as células do caminho com o símbolo de rastro
        if caminho:
            for x, y in caminho:
                matriz_visual[y][x] = '█'

        # Reposiciona os checkpoints por cima do rastro (para não serem apagados)
        for checkpoint, (x, y) in self.checkpoints.items():
            matriz_visual[y][x] = checkpoint

        print("\n=== MAPA DO AVATAR ===")
        for linha in matriz_visual:
            print("".join(linha))
        print("======================\n")


# =====================================================================
# 3. MOTOR DO ALGORITMO A* E GESTÃO DA EQUIPE
# =====================================================================
class AgenteAvatar:
    """Agente inteligente que executa o A* e otimiza a alocação da equipe."""

    def __init__(self, mapa):
        self.mapa = mapa
        # Cópia profunda das configurações para não alterar o dicionário global
        self.equipe = {
            nome: {"energia": cfg["energia"], "agilidade": cfg["agilidade"]}
            for nome, cfg in EQUIPE_CONFIG.items()
        }

    # ------------------------------------------------------------------
    # PROBLEMA 1: BUSCA A* (encontrar o melhor caminho entre dois pontos)
    # ------------------------------------------------------------------
    def distancia_manhattan(self, x1, y1, x2, y2):
        """Heurística admissível: distância de Manhattan entre dois pontos.
        Nunca superestima o custo real (custo mínimo por passo = 1).
        """
        return abs(x1 - x2) + abs(y1 - y2)

    def executar_a_estrela(self, inicio, destino):
        """
        Algoritmo A* para encontrar o caminho de menor custo entre dois pontos.

        Parâmetros:
            inicio  : tupla (x, y) da coordenada de partida
            destino : tupla (x, y) da coordenada de chegada

        Retorna:
            caminho      : lista de tuplas [(x,y), ...] da origem ao destino
            custo_trajeto: custo total em minutos do caminho encontrado
        """
        fila_prioridade = []
        # custos_g guarda o menor custo real conhecido para cada coordenada
        custos_g = {}

        h_inicial = self.distancia_manhattan(inicio[0], inicio[1], destino[0], destino[1])
        no_inicial = No(inicio[0], inicio[1], custo_g=0, heuristica_h=h_inicial)
        heapq.heappush(fila_prioridade, no_inicial)
        custos_g[inicio] = 0

        while fila_prioridade:
            no_atual = heapq.heappop(fila_prioridade)
            coord_atual = (no_atual.x, no_atual.y)

            # Chegamos ao destino: reconstrói e retorna o caminho
            if coord_atual == destino:
                caminho = []
                custo_trajeto = no_atual.g
                while no_atual is not None:
                    caminho.append((no_atual.x, no_atual.y))
                    no_atual = no_atual.pai
                caminho.reverse()
                return caminho, custo_trajeto

            # Expande os vizinhos válidos
            for nx, ny in self.mapa.vizinhos_validos(no_atual.x, no_atual.y):
                coord_vizinho = (nx, ny)
                custo_terreno = self.mapa.obter_custo(nx, ny)
                novo_custo_g = no_atual.g + custo_terreno

                # Só processa se encontrou um caminho mais barato para este vizinho
                if coord_vizinho not in custos_g or novo_custo_g < custos_g[coord_vizinho]:
                    custos_g[coord_vizinho] = novo_custo_g
                    novo_h = self.distancia_manhattan(nx, ny, destino[0], destino[1])
                    novo_no = No(nx, ny, custo_g=novo_custo_g, heuristica_h=novo_h, pai=no_atual)
                    heapq.heappush(fila_prioridade, novo_no)

        # Destino inalcançável (não deve ocorrer neste mapa)
        return [], float('inf')

    def testar_rota(self, chave_origem, chave_destino):
        """Método auxiliar para testar o A* entre dois checkpoints específicos."""
        if chave_origem not in self.mapa.checkpoints or chave_destino not in self.mapa.checkpoints:
            print(f"ERRO: Checkpoints '{chave_origem}' ou '{chave_destino}' não encontrados.")
            return

        inicio = self.mapa.checkpoints[chave_origem]
        destino = self.mapa.checkpoints[chave_destino]
        print(f"\nTestando rota: '{chave_origem}' {inicio} -> '{chave_destino}' {destino}")

        caminho, custo = self.executar_a_estrela(inicio, destino)

        if caminho:
            print(f"[SUCESSO] Rota encontrada!")
            print(f"  > Passos: {len(caminho)}")
            print(f"  > Custo de deslocamento: {custo} minutos")
            self.mapa.exibir_mapa(caminho)
        else:
            print(f"[FALHA] Nenhum caminho encontrado entre '{chave_origem}' e '{chave_destino}'.")

    # ------------------------------------------------------------------
    # PROBLEMA 2: ALOCAÇÃO DA EQUIPE (busca local gulosa por benefício marginal)
    # ------------------------------------------------------------------
    def _tempo_etapa(self, dificuldade, equipa):
        """Calcula o tempo de uma etapa dado o grupo de personagens alocado."""
        soma_agilidade = sum(self.equipe[p]["agilidade"] for p in equipa)
        return dificuldade / soma_agilidade if soma_agilidade > 0 else float('inf')

    def planear_equipa_beneficio_marginal(self):
        """
        Algoritmo guloso de benefício marginal para alocação da equipe.

        Estratégia em duas fases:
          Fase 1 — Garante ao menos 1 personagem por etapa (os mais ágeis
                   são alocados primeiro nas etapas mais difíceis).
          Fase 2 — Distribui a energia restante iterativamente: a cada passo,
                   adiciona o personagem que mais reduz o tempo total da jornada,
                   respeitando sempre o limite de energia de cada um.

        Isso respeita a restrição de energia (máx 8 usos por personagem) e
        produz uma solução bem melhor que o sistema de vagas fixas.
        """
        # Filtra apenas etapas com batalha (dificuldade > 0)
        etapas_com_batalha = {e: d for e, d in DIFICULDADES.items() if d > 0}

        energia = {p: info["energia"] for p, info in self.equipe.items()}
        equipa_por_etapa = {etapa: [] for etapa in etapas_com_batalha}

        # Personagens em ordem decrescente de agilidade
        personagens_por_ag = sorted(
            self.equipe.keys(),
            key=lambda k: self.equipe[k]["agilidade"],
            reverse=True
        )

        # --- FASE 1: garantir 1 personagem por etapa ---
        # Etapas ordenadas da mais difícil para a mais fácil
        for etapa, _ in sorted(etapas_com_batalha.items(), key=lambda x: x[1], reverse=True):
            for p in personagens_por_ag:
                if energia[p] > 0:
                    equipa_por_etapa[etapa].append(p)
                    energia[p] -= 1
                    break

        # --- FASE 2: distribuir energia restante por benefício marginal ---
        # Enquanto houver energia disponível, adiciona o personagem que
        # causa a maior redução no tempo total da jornada
        while True:
            melhor_beneficio = 0.0
            melhor_etapa = None
            melhor_personagem = None

            for etapa, dif in etapas_com_batalha.items():
                t_atual = self._tempo_etapa(dif, equipa_por_etapa[etapa])

                for p in personagens_por_ag:
                    # Só pode adicionar se: tem energia E ainda não está nesta etapa
                    if energia[p] > 0 and p not in equipa_por_etapa[etapa]:
                        t_novo = self._tempo_etapa(dif, equipa_por_etapa[etapa] + [p])
                        beneficio = t_atual - t_novo

                        if beneficio > melhor_beneficio:
                            melhor_beneficio = beneficio
                            melhor_etapa = etapa
                            melhor_personagem = p

            # Para quando não há mais melhoria possível ou energia esgotou
            if melhor_etapa is None:
                break

            equipa_por_etapa[melhor_etapa].append(melhor_personagem)
            energia[melhor_personagem] -= 1

        return equipa_por_etapa, etapas_com_batalha, energia

    # ------------------------------------------------------------------
    # ORQUESTRADOR DA JORNADA COMPLETA
    # ------------------------------------------------------------------
    def resolver_jornada_completa(self):
        """
        Orquestra a jornada completa:
          1. Planeja a alocação da equipe (Problema 2)
          2. Executa o A* entre cada par de checkpoints consecutivos (Problema 1)
          3. Exibe o custo acumulado após cada etapa (requisito do enunciado)
          4. Desenha o percurso completo no mapa ao final
        """
        ordem_etapas = self.mapa.obter_ordem_checkpoints()
        alocacao_equipa, dificuldades, energia_final = self.planear_equipa_beneficio_marginal()

        # Acumuladores
        tempo_soma_viagens  = 0.0
        tempo_soma_batalhas = 0.0
        tempo_total_jornada = 0.0
        caminho_completo    = []

        print("\n" + "="*65)
        print(" INICIANDO A GRANDE JORNADA DO AVATAR ".center(65, "="))
        print("="*65)
        print(f"\n{'Etapa':<12} {'Equipe':<38} {'Viagem':>8} {'Batalha':>8} {'Total':>8}")
        print("-"*65)

        for i in range(len(ordem_etapas) - 1):
            chave_origem  = ordem_etapas[i]
            chave_destino = ordem_etapas[i + 1]

            coord_origem  = self.mapa.checkpoints[chave_origem]
            coord_destino = self.mapa.checkpoints[chave_destino]

            # --- PROBLEMA 1: A* para encontrar o melhor caminho ---
            caminho_trecho, tempo_viagem = self.executar_a_estrela(coord_origem, coord_destino)

            if not caminho_trecho:
                print(f"ERRO: Caminho bloqueado entre '{chave_origem}' e '{chave_destino}'.")
                return

            # --- PROBLEMA 2: Tempo da batalha na etapa de destino ---
            tempo_batalha  = 0.0
            soma_agilidade = 0.0
            dificuldade    = 0
            equipa         = []

            if chave_destino in alocacao_equipa:
                equipa         = alocacao_equipa[chave_destino]
                dificuldade    = dificuldades[chave_destino]
                soma_agilidade = sum(self.equipe[p]["agilidade"] for p in equipa)
                tempo_batalha  = dificuldade / soma_agilidade

            # --- Atualiza acumuladores ---
            tempo_soma_viagens  += tempo_viagem
            tempo_soma_batalhas += tempo_batalha
            tempo_total_jornada  = tempo_soma_viagens + tempo_soma_batalhas

            # --- Exibição do custo acumulado por etapa (requisito do enunciado) ---
            equipa_str = ", ".join(equipa) if equipa else "—"
            print(f"[{chave_origem}->{chave_destino}]  {equipa_str:<38} {tempo_soma_viagens:>7.1f}  {tempo_soma_batalhas:>7.1f}  {tempo_total_jornada:>7.1f}")

            # Acumula o caminho (sem o último ponto para evitar duplicar o início do próximo)
            caminho_completo.extend(caminho_trecho[:-1])

        # Adiciona o último checkpoint (destino final)
        caminho_completo.append(self.mapa.checkpoints[ordem_etapas[-1]])

        # --- Resumo final ---
        print("="*65)
        print(" JORNADA CONCLUÍDA COM SUCESSO! ".center(65, "="))
        print(f"  Busca acumulada (A*):        {tempo_soma_viagens:.2f} min")
        print(f"  Combinatória acumulada:      {tempo_soma_batalhas:.2f} min")
        print(f"  TOTAL GERAL:                 {tempo_total_jornada:.2f} min")
        print("="*65)

        # Verifica se a restrição de energia foi respeitada
        print("\n--- Energia restante por personagem ---")
        for p, e in energia_final.items():
            status = "OK" if e >= 0 else "VIOLAÇÃO!"
            print(f"  {p:<8}: {e} pontos restantes  [{status}]")

        print("\nDesenhando o percurso completo no mapa...")
        self.mapa.exibir_mapa(caminho_completo)


# =====================================================================
# 4. EXECUÇÃO PRINCIPAL
# =====================================================================
def main():
    print("1. Carregando ambiente...")
    mapa = MapaAang(ARQUIVO_MAPA)

    agente = AgenteAvatar(mapa)

    # Para testar uma rota específica, descomente a linha abaixo:
    # agente.testar_rota('0', '1')

    # Executa a simulação completa da jornada
    agente.resolver_jornada_completa()


if __name__ == "__main__":
    main()