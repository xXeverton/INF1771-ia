"""
Este arquivo passa a ser uma biblioteca de matemática pura. 
Ele não sabe o que é o "Avatar" ou um "mapa", apenas recebe variáveis e devolve a melhor distribuição
usando a Busca Gulosa.
"""

def tempo_etapa(dificuldade, agilidade_total):
    """Calcula o tempo gasto numa etapa com base na agilidade somada."""
    if agilidade_total > 0:
        return dificuldade / agilidade_total
    return float('inf')

def otimizar_alocacao_equipa(dificuldades_etapas, configuracao_equipa):
    """
    Algoritmo guloso de benefício marginal para resolver o Problema 2.
    Distribui os personagens pelas etapas de forma a minimizar o tempo total.
    
    :param dificuldades_etapas: Dicionário { 'etapa': dificuldade }
    :param configuracao_equipa: Dicionário { 'Nome': {'energia': int, 'agilidade': float} }
    :return: (alocacao_final, energias_restantes)
    """
    # Filtra apenas as etapas que têm batalha (dificuldade > 0)
    etapas_batalha = {e: d for e, d in dificuldades_etapas.items() if d > 0}
    
    # Copia a energia atual para não alterar o dicionário original
    energia_disponivel = {nome: cfg["energia"] for nome, cfg in configuracao_equipa.items()}
    
    # Inicializa a alocação (lista vazia de personagens para cada etapa)
    alocacao = {etapa: [] for etapa in etapas_batalha}

    # Ordena os personagens dos mais rápidos para os mais lentos
    personagens_por_agilidade = sorted(
        configuracao_equipa.keys(),
        key=lambda k: configuracao_equipa[k]["agilidade"],
        reverse=True
    )

    # FASE 1: Garantir que cada etapa (das mais difíceis para as mais fáceis) 
    # recebe pelo menos o personagem mais rápido disponível.
    for etapa, _ in sorted(etapas_batalha.items(), key=lambda x: x[1], reverse=True):
        for p in personagens_por_agilidade:
            if energia_disponivel[p] > 0:
                alocacao[etapa].append(p)
                energia_disponivel[p] -= 1
                break

    # FASE 2: Distribuição Gulosa do benefício marginal.
    # Avalia onde o próximo ponto de energia causará a maior redução de tempo.
    while True:
        melhor_beneficio = 0.0
        melhor_etapa = None
        melhor_personagem = None

        for etapa, dif in etapas_batalha.items():
            agilidade_atual = sum(configuracao_equipa[p]["agilidade"] for p in alocacao[etapa])
            t_atual = tempo_etapa(dif, agilidade_atual)
            
            for p in personagens_por_agilidade:
                # Se o personagem tem energia e ainda não está nesta etapa
                if energia_disponivel[p] > 0 and p not in alocacao[etapa]:
                    agilidade_simulada = agilidade_atual + configuracao_equipa[p]["agilidade"]
                    t_simulado = tempo_etapa(dif, agilidade_simulada)
                    
                    beneficio = t_atual - t_simulado
                    
                    if beneficio > melhor_beneficio:
                        melhor_beneficio = beneficio
                        melhor_etapa = etapa
                        melhor_personagem = p

        # Critério de paragem: se não houver mais nenhum movimento que traga benefício
        if melhor_etapa is None:
            break

        # Aplica a melhor jogada encontrada
        alocacao[melhor_etapa].append(melhor_personagem)
        energia_disponivel[melhor_personagem] -= 1

    return alocacao, energia_disponivel