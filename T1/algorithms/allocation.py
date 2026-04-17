""" verificar comentario
Este arquivo passa a ser uma biblioteca de matemática pura. 
Ele não sabe o que é o "Avatar" ou um "mapa", apenas recebe variáveis e devolve a melhor distribuição
usando a Busca Gulosa.
"""

"""
Módulo de otimização da alocação de equipe — Problema 2.

Este arquivo é uma biblioteca de matemática pura: não sabe o que é "Avatar"
ou "mapa". Recebe dicionários de dificuldades e configurações de personagens
e devolve a melhor distribuição via Algoritmo Genético.

Estrutura do Algoritmo Genético implementado
(baseado nos slides Aula 05 e Aula 06 — INF1771):

  Representação do cromossomo:
    cromo[personagem] = [lista de etapas onde o personagem participa]

    Vantagem sobre a representação por etapa: a restrição de energia por
    personagem é respeitada por construção — a lista de cada personagem
    nunca tem mais elementos do que sua energia máxima.

  Operadores:
    - Seleção por torneio
    - Crossover de ponto de corte nas etapas (1-point crossover)
    - Mutação por troca de etapa
    - Hill Climbing como busca local lamarckiana (AG memético)
    - Elitismo

  Critério de parada:
    - Número máximo de gerações atingido, ou
    - N gerações consecutivas sem melhoria (estagnação)
"""

import random
import time

# ──────────────────────────────────────────────────────────────────────────────
# PARÂMETROS DO ALGORITMO GENÉTICO
# Todos aqui para serem facilmente editáveis conforme exige o enunciado.
# ──────────────────────────────────────────────────────────────────────────────

AG_POPULACAO          = 20    # Número de indivíduos na população
AG_GERACOES           = 200   # Número máximo de gerações
AG_ELITE              = 3     # Quantos melhores sobrevivem intactos (elitismo)
AG_TAXA_CROSS         = 0.85  # Probabilidade de aplicar crossover (vs. cópia)
AG_TAXA_MUT           = 0.40  # Probabilidade de aplicar mutação no filho
AG_TAXA_MUT_GENE      = 0.35  # Probabilidade de mutar cada personagem na mutação
AG_K_TORNEIO          = 3     # Tamanho do torneio de seleção
AG_SEED               = 42    # Semente aleatória (garante reprodutibilidade)
AG_PARADA_ESTAGNACAO  = 80    # Para após N gerações sem melhoria


# ──────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES PURAS
# ──────────────────────────────────────────────────────────────────────────────

def _tempo_etapa(dificuldade, agilidade_total):
    """
    Calcula o tempo gasto em uma etapa.
    Fórmula do enunciado: Tempo = Dificuldade / Soma(Agilidade)
    """
    if agilidade_total > 0:
        return dificuldade / agilidade_total
    return float('inf')


def _cromo_para_aloc(cromo, etapas_batalha):
    """
    Converte a representação por personagem para a representação por etapa.

    Entrada:  cromo = { 'Aang': ['Z', 'Y', ...], 'Zukko': ['X', ...], ... }
    Saída:    aloc  = { 'Z': ['Aang', ...], 'Y': ['Aang', ...], ... }
    """
    aloc = {e: [] for e in etapas_batalha}
    for personagem, etapas in cromo.items():
        for etapa in etapas:
            aloc[etapa].append(personagem)
    return aloc


def _fitness(cromo, etapas_batalha, configuracao_equipa):
    """
    Função de avaliação (fitness) de um cromossomo.

    Calcula o tempo total de batalhas de uma solução.
    Quanto MENOR o valor, MELHOR o indivíduo.

    Retorna float('inf') se alguma etapa ficar sem personagem (inválido).
    """
    aloc = _cromo_para_aloc(cromo, etapas_batalha)
    total = 0.0
    for etapa, equipa in aloc.items():
        ag = sum(configuracao_equipa[p]["agilidade"] for p in equipa)
        if ag == 0:
            return float('inf')  # solução inválida
        total += etapas_batalha[etapa] / ag
    return total


# ──────────────────────────────────────────────────────────────────────────────
# GERAÇÃO DA POPULAÇÃO INICIAL
# ──────────────────────────────────────────────────────────────────────────────

def _individuo_aleatorio(etapas_batalha, configuracao_equipa,
                         pers_por_ag, seed=None):
    """
    Gera um indivíduo inicial via benefício marginal com perturbação aleatória.

    Por que não gerar aleatoriamente do zero?
    Porque o espaço de soluções válidas é enorme e soluções completamente
    aleatórias têm fitness muito ruim. Começar perto de boas soluções
    acelera muito a convergência do AG.

    Estratégia:
      Fase 1 — Garante 1 personagem por etapa (mais difíceis primeiro),
               com perturbação aleatória na ordem para gerar diversidade.
      Fase 2 — Distribui a energia restante por benefício marginal
               (adiciona onde a redução de tempo é maior).
    """
    if seed is not None:
        random.seed(seed)

    # Embaralha ligeiramente a ordem dos personagens e etapas
    # para criar diversidade entre os indivíduos da população
    pers = sorted(
        pers_por_ag,
        key=lambda k: configuracao_equipa[k]["agilidade"] + random.uniform(-0.3, 0.3),
        reverse=True
    )
    energia = {p: configuracao_equipa[p]["energia"] for p in pers}
    aloc    = {e: [] for e in etapas_batalha}

    # Fase 1: 1 personagem por etapa, das mais difíceis para as mais fáceis
    for etapa in sorted(
        etapas_batalha,
        key=lambda e: etapas_batalha[e] + random.uniform(-20, 20),
        reverse=True
    ):
        for p in pers:
            if energia[p] > 0:
                aloc[etapa].append(p)
                energia[p] -= 1
                break

    # Fase 2: distribui energia restante por benefício marginal
    while True:
        melhor_beneficio, melhor_etapa, melhor_p = 0, None, None
        for etapa, dif in etapas_batalha.items():
            ag_atual = sum(configuracao_equipa[p]["agilidade"] for p in aloc[etapa])
            t_atual  = dif / ag_atual
            for p in pers:
                if energia[p] > 0 and p not in aloc[etapa]:
                    ag_novo = ag_atual + configuracao_equipa[p]["agilidade"]
                    b = t_atual - dif / ag_novo
                    if b > melhor_beneficio:
                        melhor_beneficio = b
                        melhor_etapa     = etapa
                        melhor_p         = p
        if not melhor_etapa:
            break
        aloc[melhor_etapa].append(melhor_p)
        energia[melhor_p] -= 1

    # Converte alocação por etapa → cromossomo por personagem
    cromo = {p: [] for p in configuracao_equipa}
    for etapa, equipa in aloc.items():
        for p in equipa:
            cromo[p].append(etapa)
    return cromo


# ──────────────────────────────────────────────────────────────────────────────
# BUSCA LOCAL (HILL CLIMBING) — operador lamarckiano
# ──────────────────────────────────────────────────────────────────────────────

def _hc_completo(cromo_in, etapas_batalha, configuracao_equipa):
    """
    Hill Climbing completo: itera swap e move até não haver mais melhoria.

    Por que usar HC dentro do AG (AG memético / lamarckiano)?
    O crossover e a mutação produzem filhos que ainda estão "longe" do ótimo
    local. Aplicar HC em cada filho garante que a população seja sempre
    composta por ótimos locais, o que acelera muito a convergência.

    Operações:
      SWAP — Troca a etapa de p1 pela etapa de p2 (e vice-versa).
             Preserva a energia de ambos por construção.
             Ex: p1 estava em [Z, Y] e p2 em [X, W]
                 → p1 fica em [X, Y] e p2 em [Z, W]

      MOVE — Remove p de uma etapa e o coloca em outra onde ele não está.
             Só é válido se a etapa de saída tiver mais de 1 personagem
             (para não deixar nenhuma etapa vazia).
    """
    cromo = {p: list(v) for p, v in cromo_in.items()}
    t     = _fitness(cromo, etapas_batalha, configuracao_equipa)
    pers  = list(configuracao_equipa.keys())

    while True:
        melhorou = False

        # ── Operação SWAP ────────────────────────────────────────────────
        for i, p1 in enumerate(pers):
            for p2 in pers[i + 1:]:
                for e1 in list(cromo[p1]):
                    for e2 in list(cromo[p2]):
                        # Só faz sentido trocar etapas diferentes
                        # que ainda não estejam no conjunto do outro
                        if e1 == e2 or e2 in cromo[p1] or e1 in cromo[p2]:
                            continue

                        # Aplica o swap
                        cromo[p1] = [e2 if e == e1 else e for e in cromo[p1]]
                        cromo[p2] = [e1 if e == e2 else e for e in cromo[p2]]

                        tn = _fitness(cromo, etapas_batalha, configuracao_equipa)
                        if tn < t - 1e-9:
                            # Melhoria encontrada: aceita e reinicia
                            t = tn
                            melhorou = True
                            break
                        # Sem melhoria: desfaz o swap
                        cromo[p1] = [e1 if e == e2 else e for e in cromo[p1]]
                        cromo[p2] = [e2 if e == e1 else e for e in cromo[p2]]
                    if melhorou: break
                if melhorou: break
            if melhorou: break
        if melhorou:
            continue  # reinicia o loop externo

        # ── Operação MOVE ────────────────────────────────────────────────
        for p in pers:
            # Reconstrói alocação por etapa para checar cobertura
            aloc_cur = _cromo_para_aloc(cromo, etapas_batalha)
            for e1 in list(cromo[p]):
                # Só sai se a etapa não ficar vazia
                if len(aloc_cur[e1]) <= 1:
                    continue
                for e2 in etapas_batalha:
                    # Só entra em etapa onde ainda não está
                    if e2 in cromo[p]:
                        continue

                    # Aplica o move
                    cromo[p] = [e2 if e == e1 else e for e in cromo[p]]

                    tn = _fitness(cromo, etapas_batalha, configuracao_equipa)
                    if tn < t - 1e-9:
                        t = tn
                        melhorou = True
                        break
                    # Sem melhoria: desfaz
                    cromo[p] = [e1 if e == e2 else e for e in cromo[p]]
                if melhorou: break
            if melhorou: break

        # Nenhuma operação melhorou: ótimo local atingido
        if not melhorou:
            break

    return cromo, t


# ──────────────────────────────────────────────────────────────────────────────
# OPERADORES GENÉTICOS
# ──────────────────────────────────────────────────────────────────────────────

def _crossover(pai1, pai2, etapas_batalha, configuracao_equipa, pers_por_ag):
    """
    Crossover de ponto de corte nas etapas (1-point crossover).

    Como funciona:
      1. Sorteia um ponto de corte aleatório na lista de etapas.
      2. O filho herda as equipes do pai1 para as etapas antes do corte
         e as equipes do pai2 para as etapas após o corte.

    Por que corte nas ETAPAS e não nos personagens?
    O crossover por personagem (cada personagem herda sua lista de um pai)
    gerava filhos onde algumas etapas ficavam sem cobertura, pois dois pais
    podiam ter alocações completamente distintas. O corte nas etapas garante
    que toda etapa sempre tem ao menos os personagens de um dos pais.

    Após o crossover:
      3. Remove excessos de energia (personagens que aparecem mais vezes
         do que seu limite permite), removendo das etapas mais fáceis.
      4. Distribui energia restante por benefício marginal.
    """
    etapas = list(etapas_batalha.keys())
    ponto  = random.randint(1, len(etapas) - 1)

    # Constrói alocações por etapa de cada pai
    aloc1 = _cromo_para_aloc(pai1, etapas_batalha)
    aloc2 = _cromo_para_aloc(pai2, etapas_batalha)

    # Filho herda metade de cada pai
    filho_aloc = {
        e: list(aloc1[e]) if i < ponto else list(aloc2[e])
        for i, e in enumerate(etapas)
    }

    # ── Reparo de energia ────────────────────────────────────────────────
    # Conta quantas vezes cada personagem aparece no filho
    uso = {p: 0 for p in configuracao_equipa}
    for equipa in filho_aloc.values():
        for p in equipa:
            uso[p] += 1

    # Remove excessos das etapas mais FÁCEIS (preserva as difíceis)
    etapas_por_dif = sorted(etapas, key=lambda e: etapas_batalha[e])
    for p in configuracao_equipa:
        while uso[p] > configuracao_equipa[p]["energia"]:
            removido = False
            # Tenta remover de etapa com mais de 1 personagem
            for e in etapas_por_dif:
                if p in filho_aloc[e] and len(filho_aloc[e]) > 1:
                    filho_aloc[e] = [x for x in filho_aloc[e] if x != p]
                    uso[p] -= 1
                    removido = True
                    break
            if not removido:
                # Força remoção mesmo que a etapa fique temporariamente vazia
                for e in etapas_por_dif:
                    if p in filho_aloc[e]:
                        filho_aloc[e] = [x for x in filho_aloc[e] if x != p]
                        uso[p] -= 1
                        # Repõe com o personagem mais ágil que ainda tem energia
                        if not filho_aloc[e]:
                            subs = [pp for pp in pers_por_ag
                                    if uso[pp] < configuracao_equipa[pp]["energia"]]
                            if subs:
                                filho_aloc[e].append(subs[0])
                                uso[subs[0]] += 1
                        break

    # ── Distribui energia restante por benefício marginal ────────────────
    while True:
        melhor_beneficio, melhor_etapa, melhor_p = 0, None, None
        for e, dif in etapas_batalha.items():
            ag_atual = sum(configuracao_equipa[p]["agilidade"] for p in filho_aloc[e])
            if ag_atual == 0:
                continue
            t_atual = dif / ag_atual
            for p in pers_por_ag:
                if uso[p] < configuracao_equipa[p]["energia"] and p not in filho_aloc[e]:
                    ag_novo = ag_atual + configuracao_equipa[p]["agilidade"]
                    b = t_atual - dif / ag_novo
                    if b > melhor_beneficio:
                        melhor_beneficio = b
                        melhor_etapa     = e
                        melhor_p         = p
        if not melhor_etapa:
            break
        filho_aloc[melhor_etapa].append(melhor_p)
        uso[melhor_p] += 1

    # Converte de volta para cromossomo por personagem
    cromo = {p: [] for p in configuracao_equipa}
    for e, equipa in filho_aloc.items():
        for p in equipa:
            cromo[p].append(e)
    return cromo


def _mutacao(cromo_in, etapas_batalha, configuracao_equipa):
    """
    Mutação por troca de etapa.

    Para cada personagem (com probabilidade AG_TAXA_MUT_GENE):
      - Escolhe aleatoriamente uma etapa de saída (onde ele participa
        e a etapa não ficaria vazia sem ele).
      - Escolhe aleatoriamente uma etapa de entrada (onde ele ainda
        não está).
      - Faz a troca.

    A energia por personagem é preservada (é uma troca, não adição).
    A cobertura das etapas é preservada (só sai de etapas com > 1 person.).

    Por que mutar desta forma?
    Mutações aleatórias demais destroem boas soluções. Esta abordagem
    garante que a solução continua válida após a mutação, sem precisar
    de reparo.
    """
    cromo    = {p: list(v) for p, v in cromo_in.items()}
    aloc_cur = _cromo_para_aloc(cromo, etapas_batalha)

    for p in configuracao_equipa:
        # Cada personagem muta com probabilidade AG_TAXA_MUT_GENE
        if random.random() > AG_TAXA_MUT_GENE:
            continue

        # Etapas de onde p pode sair sem deixar a etapa vazia
        saida  = [e for e in cromo[p] if len(aloc_cur[e]) > 1]
        # Etapas para onde p pode entrar (onde ainda não está)
        entrada = [e for e in etapas_batalha if e not in cromo[p]]

        if not saida or not entrada:
            continue  # mutação não aplicável para este personagem

        e_sai   = random.choice(saida)
        e_entra = random.choice(entrada)

        # Aplica a troca
        cromo[p] = [e_entra if e == e_sai else e for e in cromo[p]]
        # Atualiza o mapa de cobertura para o próximo personagem
        aloc_cur = _cromo_para_aloc(cromo, etapas_batalha)

    return cromo


def _torneio(fitnesses, k):
    """
    Seleção por torneio.

    Sorteia k candidatos aleatórios da população e retorna o índice
    do melhor (menor fitness).

    Por que torneio e não roleta?
    A roleta pode ser dominada por um único indivíduo muito bom,
    reduzindo a diversidade. O torneio mantém mais pressão seletiva
    controlada pelo parâmetro k.
    """
    candidatos = random.sample(range(len(fitnesses)), min(k, len(fitnesses)))
    return min(candidatos, key=lambda i: fitnesses[i])


# ──────────────────────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL — PONTO DE ENTRADA DO MÓDULO
# ──────────────────────────────────────────────────────────────────────────────

def otimizar_alocacao_equipa(dificuldades_etapas, configuracao_equipa,
                              verbose=False):
    """
    Algoritmo Genético para resolver o Problema 2 (alocação de equipe).

    Esta é a única função pública deste módulo.
    Recebe os dados do problema e devolve a melhor alocação encontrada.

    Fluxo completo (conforme Aula 05 e Aula 06 — INF1771):

      ┌─ INICIALIZAÇÃO ────────────────────────────────────────────────────┐
      │  Gera AG_POPULACAO indivíduos via benefício marginal perturbado.   │
      │  Aplica HC completo em cada um (population seeding).               │
      │  Isso garante que toda a população inicial seja composta por        │
      │  ótimos locais de alta qualidade.                                   │
      └────────────────────────────────────────────────────────────────────┘
      ┌─ LOOP DE EVOLUÇÃO (por geração) ───────────────────────────────────┐
      │  1. ELITISMO    — Os AG_ELITE melhores passam intactos.            │
      │  2. SELEÇÃO     — Torneio de tamanho AG_K_TORNEIO.                 │
      │  3. CROSSOVER   — Ponto de corte nas etapas (prob AG_TAXA_CROSS).  │
      │  4. MUTAÇÃO     — Troca de etapa por personagem (prob AG_TAXA_MUT).│
      │  5. BUSCA LOCAL — HC completo no filho (operador lamarckiano).      │
      └────────────────────────────────────────────────────────────────────┘
      ┌─ CRITÉRIO DE PARADA ───────────────────────────────────────────────┐
      │  AG_GERACOES atingido  OU  AG_PARADA_ESTAGNACAO sem melhoria.      │
      └────────────────────────────────────────────────────────────────────┘

    Parâmetros:
        dificuldades_etapas : dict { 'etapa': dificuldade }
        configuracao_equipa : dict { 'Nome': {'energia': int, 'agilidade': float} }
        verbose             : bool — imprime progresso se True

    Retorna:
        alocacao_final    : dict { 'etapa': [personagens] }
        energias_restantes: dict { 'personagem': energia_restante }
    """
    random.seed(AG_SEED)
    t0 = time.time()

    # Filtra apenas etapas com batalha (dificuldade > 0)
    # O checkpoint '0' (aldeia de partida) não tem batalha
    etapas_batalha = {e: d for e, d in dificuldades_etapas.items() if d > 0}

    # Pré-computa lista de personagens ordenada por agilidade
    # (usada em vários operadores para priorizar os mais eficientes)
    pers_por_ag = sorted(
        configuracao_equipa.keys(),
        key=lambda k: configuracao_equipa[k]["agilidade"],
        reverse=True
    )

    # ── INICIALIZAÇÃO DA POPULAÇÃO ────────────────────────────────────────
    if verbose:
        print(f"\n  [AG] Gerando {AG_POPULACAO} indivíduos iniciais...", flush=True)

    populacao = []
    for i in range(AG_POPULACAO):
        # Cada indivíduo usa uma seed diferente para garantir diversidade
        ind = _individuo_aleatorio(
            etapas_batalha, configuracao_equipa, pers_por_ag,
            seed=AG_SEED + i * 7
        )
        # Aplica HC completo: toda a população inicial vira ótimos locais
        ind_hc, tf = _hc_completo(ind, etapas_batalha, configuracao_equipa)
        populacao.append((tf, ind_hc))

    # Ordena do melhor para o pior
    populacao.sort(key=lambda x: x[0])
    melhor_t   = populacao[0][0]
    melhor_sol = {p: list(v) for p, v in populacao[0][1].items()}

    if verbose:
        print(f"  [AG] Pop. inicial — melhor: {melhor_t:.4f} min  "
              f"({time.time()-t0:.1f}s)", flush=True)

    # ── LOOP DE EVOLUÇÃO ──────────────────────────────────────────────────
    sem_melhora = 0

    for gen in range(AG_GERACOES):
        fitnesses = [t for t, _ in populacao]

        # Começa nova população com os AG_ELITE melhores intactos (elitismo)
        # O elitismo garante que o melhor resultado nunca regride
        nova_pop = list(populacao[:AG_ELITE])

        # Preenche o restante da população com filhos
        while len(nova_pop) < AG_POPULACAO:

            # ── Seleção por torneio ──────────────────────────────────────
            i1 = _torneio(fitnesses, AG_K_TORNEIO)
            i2 = _torneio(fitnesses, AG_K_TORNEIO)
            while i2 == i1:  # garante dois pais distintos
                i2 = _torneio(fitnesses, AG_K_TORNEIO)

            # ── Crossover ────────────────────────────────────────────────
            if random.random() < AG_TAXA_CROSS:
                # Cria filho combinando material genético dos dois pais
                filho = _crossover(
                    populacao[i1][1], populacao[i2][1],
                    etapas_batalha, configuracao_equipa, pers_por_ag
                )
            else:
                # Sem crossover: filho é cópia do pai1 (reprodução assexuada)
                filho = {p: list(v) for p, v in populacao[i1][1].items()}

            # ── Mutação ──────────────────────────────────────────────────
            if random.random() < AG_TAXA_MUT:
                # Aplica perturbação aleatória para manter diversidade
                # e evitar convergência prematura
                filho = _mutacao(filho, etapas_batalha, configuracao_equipa)

            # ── Busca local lamarckiana ───────────────────────────────────
            # O HC "educa" o filho: encontra o ótimo local a partir dele.
            # Isso é o que torna este AG memético — combina evolução global
            # do AG com refinamento local do HC.
            filho_hc, tf = _hc_completo(filho, etapas_batalha, configuracao_equipa)
            nova_pop.append((tf, filho_hc))

        # Ordena e trunca: mantém apenas os AG_POPULACAO melhores
        nova_pop.sort(key=lambda x: x[0])
        populacao = nova_pop[:AG_POPULACAO]

        # ── Atualiza melhor global ───────────────────────────────────────
        if populacao[0][0] < melhor_t - 1e-9:
            melhor_t    = populacao[0][0]
            melhor_sol  = {p: list(v) for p, v in populacao[0][1].items()}
            sem_melhora = 0
            if verbose:
                print(f"  [AG] Gen {gen:3d}: novo melhor = {melhor_t:.4f} min  "
                      f"({time.time()-t0:.1f}s)", flush=True)
        else:
            sem_melhora += 1

        # ── Critério de parada por estagnação ────────────────────────────
        if sem_melhora >= AG_PARADA_ESTAGNACAO:
            if verbose:
                print(f"  [AG] Parada por estagnação na geração {gen}.", flush=True)
            break

    if verbose:
        print(f"  [AG] Concluído — melhor: {melhor_t:.4f} min  "
              f"(CPU: {time.time()-t0:.1f}s)", flush=True)

    # ── CONVERTE RESULTADO PARA O FORMATO DE SAÍDA ────────────────────────
    # Volta para { etapa: [personagens] } que é o formato esperado pelo agente
    alocacao_final = _cromo_para_aloc(melhor_sol, etapas_batalha)

    # Calcula energia restante por personagem
    uso_por_pessoa = {p: len(melhor_sol[p]) for p in configuracao_equipa}
    energias_restantes = {
        p: configuracao_equipa[p]["energia"] - uso_por_pessoa[p]
        for p in configuracao_equipa
    }

    return alocacao_final, energias_restantes