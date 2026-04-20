"""
Módulo de otimização da alocação de equipe utilizando Algoritmo Genético.
"""

import random
import time

# Parâmetros do Algoritmo Genético
AG_POPULACAO  = 20 # Número de indivíduos na população
AG_GERACOES = 200 # Número máximo de gerações
AG_ELITE = 3 # Quantos melhores sobrevivem intactos (elitismo)
AG_TAXA_CROSSOVER = 0.85 # Probabilidade de aplicar crossover (vs. cópia)
AG_TAXA_MUTACAO = 0.40 # Probabilidade de aplicar mutação no filho
AG_TAXA_MUTACAO_GENE = 0.35 # Probabilidade de mutar cada personagem na mutação
AG_K_TORNEIO = 3 # Tamanho do torneio de seleção
AG_SEED = 42 # Semente aleatória (garante reprodutibilidade)
AG_PARADA_ESTAGNACAO = 60 # Para após N gerações sem melhoria


def _cromossomo_para_alocacao(cromossomo, etapas_batalha):
    """
    Converte representação por personagem para representação por etapa.
    :param cromossomo: Cromossomo por personagem.
    :param etapas_batalha: Dicionário de etapas.
    :return: Alocação por etapa.
    """
    alocacao = {e: [] for e in etapas_batalha}
    for personagem, etapas in cromossomo.items():
        for etapa in etapas:
            alocacao[etapa].append(personagem)
    return alocacao


def _calcular_fitness(cromossomo, etapas_batalha, config_equipe):
    """
    Calcula o fitness de um cromossomo.
    :param cromossomo: Cromossomo.
    :param etapas_batalha: Dicionário de etapas.
    :param config_equipe: Configuração da equipe.
    :return: Valor de fitness.
    """
    alocacao = _cromossomo_para_alocacao(cromossomo, etapas_batalha)
    total = 0.0
    for etapa, equipe in alocacao.items():
        agilidade = sum(config_equipe[p]["agilidade"] for p in equipe)
        if agilidade == 0:
            return float('inf')
        total += etapas_batalha[etapa] / agilidade
    return total


def _gerar_individuo_aleatorio(etapas_batalha, config_equipe, pers_por_agilidade, seed=None):
    """
    Gera um indivíduo inicial via benefício marginal.
    :param etapas_batalha: Dicionário de etapas.
    :param config_equipe: Configuração da equipe.
    :param pers_por_agilidade: Personagens ordenados por agilidade.
    :param seed: Semente aleatória.
    :return: Cromossomo gerado.
    """
    if seed is not None:
        random.seed(seed)

    pers = sorted(
        pers_por_agilidade,
        key=lambda k: config_equipe[k]["agilidade"] + random.uniform(-0.3, 0.3),
        reverse=True
    )
    energia = {p: config_equipe[p]["energia"] for p in pers}
    alocacao = {e: [] for e in etapas_batalha}

    # Fase 1: 1 personagem por etapa
    for etapa in sorted(
        etapas_batalha,
        key=lambda e: etapas_batalha[e] + random.uniform(-20, 20),
        reverse=True
    ):
        for p in pers:
            if energia[p] > 0:
                alocacao[etapa].append(p)
                energia[p] -= 1
                break

    # Fase 2: distribui energia restante por benefício marginal
    while True:
        melhor_beneficio, melhor_etapa, melhor_p = 0, None, None
        for etapa, dif in etapas_batalha.items():
            agilidade_atual = sum(config_equipe[p]["agilidade"] for p in alocacao[etapa])
            tempo_atual = dif / agilidade_atual
            for p in pers:
                if energia[p] > 0 and p not in alocacao[etapa]:
                    agilidade_novo = agilidade_atual + config_equipe[p]["agilidade"]
                    beneficio = tempo_atual - dif / agilidade_novo
                    if beneficio > melhor_beneficio:
                        melhor_beneficio = beneficio
                        melhor_etapa = etapa
                        melhor_p = p
        if not melhor_etapa:
            break
        alocacao[melhor_etapa].append(melhor_p)
        energia[melhor_p] -= 1

    cromossomo = {p: [] for p in config_equipe}
    for etapa, equipe in alocacao.items():
        for p in equipe:
            cromossomo[p].append(etapa)
    return cromossomo


def _busca_local_completa(cromossomo_entrada, etapas_batalha, config_equipe):
    """
    Hill Climbing completo com swap e move.
    :param cromossomo_entrada: Cromossomo inicial.
    :param etapas_batalha: Dicionário de etapas.
    :param config_equipe: Configuração da equipe.
    :return: Cromossomo otimizado e seu fitness.
    """
    cromossomo = {p: list(v) for p, v in cromossomo_entrada.items()}
    fitness = _calcular_fitness(cromossomo, etapas_batalha, config_equipe)
    personagens = list(config_equipe.keys())

    while True:
        melhorou = False

        # Operação SWAP
        for i, p1 in enumerate(personagens):
            for p2 in personagens[i + 1:]:
                for e1 in list(cromossomo[p1]):
                    for e2 in list(cromossomo[p2]):
                        if e1 == e2 or e2 in cromossomo[p1] or e1 in cromossomo[p2]:
                            continue

                        cromossomo[p1] = [e2 if e == e1 else e for e in cromossomo[p1]]
                        cromossomo[p2] = [e1 if e == e2 else e for e in cromossomo[p2]]

                        novo_fitness = _calcular_fitness(cromossomo, etapas_batalha, config_equipe)
                        if novo_fitness < fitness - 1e-9:
                            fitness = novo_fitness
                            melhorou = True
                            break
                        cromossomo[p1] = [e1 if e == e2 else e for e in cromossomo[p1]]
                        cromossomo[p2] = [e2 if e == e1 else e for e in cromossomo[p2]]
                    if melhorou:
                        break
                if melhorou:
                    break
            if melhorou:
                break
        if melhorou:
            continue

        # Operação MOVE
        for p in personagens:
            alocacao_atual = _cromossomo_para_alocacao(cromossomo, etapas_batalha)
            for e1 in list(cromossomo[p]):
                if len(alocacao_atual[e1]) <= 1:
                    continue
                for e2 in etapas_batalha:
                    if e2 in cromossomo[p]:
                        continue

                    cromossomo[p] = [e2 if e == e1 else e for e in cromossomo[p]]
                    novo_fitness = _calcular_fitness(cromossomo, etapas_batalha, config_equipe)
                    if novo_fitness < fitness - 1e-9:
                        fitness = novo_fitness
                        melhorou = True
                        break
                    cromossomo[p] = [e1 if e == e2 else e for e in cromossomo[p]]
                if melhorou:
                    break
            if melhorou:
                break

        if not melhorou:
            break

    return cromossomo, fitness


def _crossover(pai1, pai2, etapas_batalha, config_equipe, pers_por_agilidade):
    """
    Crossover de ponto de corte nas etapas.
    :param pai1: Cromossomo do primeiro pai.
    :param pai2: Cromossomo do segundo pai.
    :param etapas_batalha: Dicionário de etapas.
    :param config_equipe: Configuração da equipe.
    :param pers_por_agilidade: Personagens ordenados.
    :return: Cromossomo filho.
    """
    etapas = list(etapas_batalha.keys())
    ponto = random.randint(1, len(etapas) - 1)

    aloc1 = _cromossomo_para_alocacao(pai1, etapas_batalha)
    aloc2 = _cromossomo_para_alocacao(pai2, etapas_batalha)

    alocacao_filho = {
        e: list(aloc1[e]) if i < ponto else list(aloc2[e])
        for i, e in enumerate(etapas)
    }

    # Reparo de energia
    uso = {p: 0 for p in config_equipe}
    for equipe in alocacao_filho.values():
        for p in equipe:
            uso[p] += 1

    etapas_por_dif = sorted(etapas, key=lambda e: etapas_batalha[e])
    for p in config_equipe:
        while uso[p] > config_equipe[p]["energia"]:
            removido = False
            for e in etapas_por_dif:
                if p in alocacao_filho[e] and len(alocacao_filho[e]) > 1:
                    alocacao_filho[e] = [x for x in alocacao_filho[e] if x != p]
                    uso[p] -= 1
                    removido = True
                    break
            if not removido:
                for e in etapas_por_dif:
                    if p in alocacao_filho[e]:
                        alocacao_filho[e] = [x for x in alocacao_filho[e] if x != p]
                        uso[p] -= 1
                        if not alocacao_filho[e]:
                            substitutos = [pp for pp in pers_por_agilidade
                                         if uso[pp] < config_equipe[pp]["energia"]]
                            if substitutos:
                                alocacao_filho[e].append(substitutos[0])
                                uso[substitutos[0]] += 1
                        break

    # Distribui energia restante
    while True:
        melhor_beneficio, melhor_etapa, melhor_p = 0, None, None
        for e, dif in etapas_batalha.items():
            agilidade_atual = sum(config_equipe[p]["agilidade"] for p in alocacao_filho[e])
            if agilidade_atual == 0:
                continue
            tempo_atual = dif / agilidade_atual
            for p in pers_por_agilidade:
                if uso[p] < config_equipe[p]["energia"] and p not in alocacao_filho[e]:
                    agilidade_novo = agilidade_atual + config_equipe[p]["agilidade"]
                    beneficio = tempo_atual - dif / agilidade_novo
                    if beneficio > melhor_beneficio:
                        melhor_beneficio = beneficio
                        melhor_etapa = e
                        melhor_p = p
        if not melhor_etapa:
            break
        alocacao_filho[melhor_etapa].append(melhor_p)
        uso[melhor_p] += 1

    cromossomo = {p: [] for p in config_equipe}
    for e, equipe in alocacao_filho.items():
        for p in equipe:
            cromossomo[p].append(e)
    return cromossomo


def _mutacao(cromossomo_entrada, etapas_batalha, config_equipe):
    """
    Mutação por troca de etapa.
    :param cromossomo_entrada: Cromossomo.
    :param etapas_batalha: Dicionário de etapas.
    :param config_equipe: Configuração da equipe.
    :return: Cromossomo mutado.
    """
    cromossomo = {p: list(v) for p, v in cromossomo_entrada.items()}
    alocacao_atual = _cromossomo_para_alocacao(cromossomo, etapas_batalha)

    for p in config_equipe:
        if random.random() > AG_TAXA_MUTACAO_GENE:
            continue

        saida = [e for e in cromossomo[p] if len(alocacao_atual[e]) > 1]
        entrada = [e for e in etapas_batalha if e not in cromossomo[p]]

        if not saida or not entrada:
            continue

        e_sai = random.choice(saida)
        e_entra = random.choice(entrada)

        cromossomo[p] = [e_entra if e == e_sai else e for e in cromossomo[p]]
        alocacao_atual = _cromossomo_para_alocacao(cromossomo, etapas_batalha)

    return cromossomo


def _torneio(fitness_valores, k):
    """
    Seleção por torneio.
    :param fitness_valores: Lista de fitness.
    :param k: Tamanho do torneio.
    :return: Índice do vencedor.
    """
    candidatos = random.sample(range(len(fitness_valores)), min(k, len(fitness_valores)))
    return min(candidatos, key=lambda i: fitness_valores[i])


def otimizar_alocacao_equipe(dificuldades_etapas, config_equipe, verbose=True):
    """
    Algoritmo Genético para otimizar alocação de equipe.
    :param dificuldades_etapas: Dicionário de dificuldades.
    :param config_equipe: Configuração da equipe.
    :param verbose: Se True, imprime progresso.
    :return: Tupla com alocação final e energias restantes.
    """
    random.seed(AG_SEED)
    tempo_inicio = time.time()

    etapas_batalha = {e: d for e, d in dificuldades_etapas.items() if d > 0}

    pers_por_agilidade = sorted(
        config_equipe.keys(),
        key=lambda k: config_equipe[k]["agilidade"],
        reverse=True
    )

    if verbose:
        print(f"Gerando {AG_POPULACAO} indivíduos iniciais...")

    populacao = []
    for i in range(AG_POPULACAO):
        ind = _gerar_individuo_aleatorio(
            etapas_batalha, config_equipe, pers_por_agilidade,
            seed=AG_SEED + i * 7
        )
        ind_hc, tf = _busca_local_completa(ind, etapas_batalha, config_equipe)
        populacao.append((tf, ind_hc))

    populacao.sort(key=lambda x: x[0])
    melhor_tempo = populacao[0][0]
    melhor_solucao = {p: list(v) for p, v in populacao[0][1].items()}

    if verbose:
        print(f"Melhor (inicial): {melhor_tempo:.4f} min ({time.time() - tempo_inicio:.1f}s)")

    sem_melhora = 0

    for geracao in range(AG_GERACOES):
        fitness_valores = [t for t, _ in populacao]
        nova_populacao = list(populacao[:AG_ELITE])

        while len(nova_populacao) < AG_POPULACAO:
            i1 = _torneio(fitness_valores, AG_K_TORNEIO)
            i2 = _torneio(fitness_valores, AG_K_TORNEIO)
            while i2 == i1:
                i2 = _torneio(fitness_valores, AG_K_TORNEIO)

            if random.random() < AG_TAXA_CROSSOVER:
                filho = _crossover(populacao[i1][1], populacao[i2][1],
                                 etapas_batalha, config_equipe, pers_por_agilidade)
            else:
                filho = {p: list(v) for p, v in populacao[i1][1].items()}

            if random.random() < AG_TAXA_MUTACAO:
                filho = _mutacao(filho, etapas_batalha, config_equipe)

            filho_hc, tf = _busca_local_completa(filho, etapas_batalha, config_equipe)
            nova_populacao.append((tf, filho_hc))

        nova_populacao.sort(key=lambda x: x[0])
        populacao = nova_populacao[:AG_POPULACAO]

        if populacao[0][0] < melhor_tempo - 1e-9:
            melhor_tempo = populacao[0][0]
            melhor_solucao = {p: list(v) for p, v in populacao[0][1].items()}
            sem_melhora = 0
            if verbose:
                print(f"Gen {geracao:3d}: {melhor_tempo:.4f} min ({time.time() - tempo_inicio:.1f}s)")
        else:
            sem_melhora += 1

        if sem_melhora >= AG_PARADA_ESTAGNACAO:
            if verbose:
                print(f"Parada por estagnação na geração {geracao}.")
            break

    if verbose:
        print(f"Concluído: {melhor_tempo:.4f} min (CPU: {time.time() - tempo_inicio:.1f}s)")

    alocacao_final = _cromossomo_para_alocacao(melhor_solucao, etapas_batalha)

    uso_por_pessoa = {p: len(melhor_solucao[p]) for p in config_equipe}
    energias_restantes = {
        p: config_equipe[p]["energia"] - uso_por_pessoa[p]
        for p in config_equipe
    }

    return alocacao_final, energias_restantes
