"""
Módulo do Agente Avatar — orquestrador da jornada completa.

Este é o "gestor": conhece o ambiente (MapaAang), sabe andar (astar.py)
e pede ajuda para organizar a equipe (allocation.py).
Sua responsabilidade é juntar tudo e imprimir o diário de bordo.
"""

from map.constants import EQUIPE_CONFIG, DIFICULDADES
from algorithms.astar import executar_a_estrela
from algorithms.allocation import otimizar_alocacao_equipa


class AgenteAvatar:
    """
    O agente inteligente que orquestra a viagem.
    Ele analisa o mapa, calcula as rotas (Problema 1 — A*)
    e gerencia a equipe em cada checkpoint (Problema 2 — AG).
    """

    def __init__(self, mapa):
        self.mapa         = mapa
        self.equipa       = EQUIPE_CONFIG
        self.dificuldades = DIFICULDADES

    def resolver_jornada_completa(self):
        """
        Orquestra a jornada completa em duas fases:

          Fase 1 — Problema 2 (QUEM luta ONDE):
            Chama o Algoritmo Genético para encontrar a melhor alocação
            de personagens por etapa, minimizando o tempo total de batalhas.

          Fase 2 — Problema 1 (COMO chegar lá):
            Para cada par de checkpoints consecutivos, executa o A*
            para encontrar o caminho de menor custo no mapa.

          Ao final, exibe o resumo completo e desenha o percurso no mapa.
        """

        # Identifica os checkpoints na ordem correta da jornada (sort ASCII)
        ordem_etapas = self.mapa.obter_ordem_checkpoints()

        # ── FASE 1: Algoritmo Genético (Problema 2) ───────────────────────
        print("\n" + "=" * 70)
        print(" ALGORITMO GENÉTICO — PLANEJANDO ALOCAÇÃO DA EQUIPE ".center(70, "="))
        print("=" * 70)

        # verbose=True ativa o log de progresso do AG (gerações e melhorias)
        alocacao_equipa, energia_final = otimizar_alocacao_equipa(
            self.dificuldades, self.equipa, verbose=True
        )

        # Exibe a alocação por etapa em ordem decrescente de dificuldade
        etapas_batalha = {e: d for e, d in self.dificuldades.items() if d > 0}
        print(f"\n  {'Etapa':<6} {'Dif':>6}  {'Equipe alocada':<42}  {'Tempo (min)':>11}")
        print("  " + "-" * 70)
        for etapa in sorted(etapas_batalha, key=lambda e: etapas_batalha[e], reverse=True):
            equipa = alocacao_equipa.get(etapa, [])
            ag     = sum(self.equipa[p]["agilidade"] for p in equipa)
            t_e    = etapas_batalha[etapa] / ag if ag > 0 else 0
            print(f"  {etapa:<6} {etapas_batalha[etapa]:>6}  {', '.join(equipa):<42}  {t_e:>10.2f}")

        # Verifica e exibe a energia restante de cada personagem
        print(f"\n  Energia restante por personagem:")
        for p, e in energia_final.items():
            status = "OK" if e >= 0 else "VIOLAÇÃO DE ENERGIA!"
            print(f"    {p:<8}: {e} ponto(s) restante(s)  [{status}]")

        # ── FASE 2: A* sequencial (Problema 1) ───────────────────────────
        print("\n" + "=" * 70)
        print(" A* — INICIANDO A GRANDE JORNADA DO AVATAR ".center(70, "="))
        print("=" * 70)
        print(f"\n  {'Etapa':<12} {'Equipe':<35}  {'Viagem':>8}  {'Batalha':>8}  {'Total':>8}")
        print("  " + "-" * 75)

        tempo_soma_viagens  = 0.0
        tempo_soma_batalhas = 0.0
        caminho_completo    = []

        for i in range(len(ordem_etapas) - 1):
            chave_origem  = ordem_etapas[i]
            chave_destino = ordem_etapas[i + 1]

            coord_origem  = self.mapa.checkpoints[chave_origem]
            coord_destino = self.mapa.checkpoints[chave_destino]

            # ── A*: encontra o melhor caminho entre os dois checkpoints ──
            caminho_trecho, tempo_viagem = executar_a_estrela(
                self.mapa, coord_origem, coord_destino
            )

            if not caminho_trecho:
                print(f"  ERRO: Caminho bloqueado entre '{chave_origem}' e '{chave_destino}'.")
                return

            # ── Calcula o tempo de batalha no checkpoint de destino ──────
            tempo_batalha = 0.0
            equipa_luta   = []

            if chave_destino in alocacao_equipa:
                equipa_luta       = alocacao_equipa[chave_destino]
                dificuldade_etapa = self.dificuldades[chave_destino]
                soma_agilidade    = sum(self.equipa[p]["agilidade"] for p in equipa_luta)
                tempo_batalha     = dificuldade_etapa / soma_agilidade

            # ── Acumuladores ──────────────────────────────────────────────
            tempo_soma_viagens  += tempo_viagem
            tempo_soma_batalhas += tempo_batalha
            tempo_total_jornada  = tempo_soma_viagens + tempo_soma_batalhas

            # ── Exibição do custo acumulado por etapa ────────────────────
            equipa_str = ", ".join(equipa_luta) if equipa_luta else "—"
            print(f"  [{chave_origem}->{chave_destino}]  "
                  f"{equipa_str:<35}  "
                  f"{tempo_soma_viagens:>7.1f}  "
                  f"{tempo_soma_batalhas:>7.1f}  "
                  f"{tempo_total_jornada:>7.1f}")

            # Acumula o caminho (remove o último ponto para não duplicar)
            caminho_completo.extend(caminho_trecho[:-1])

        # Adiciona o checkpoint final ao percurso
        caminho_completo.append(self.mapa.checkpoints[ordem_etapas[-1]])

        # ── RESUMO FINAL ──────────────────────────────────────────────────
        tempo_total_jornada = tempo_soma_viagens + tempo_soma_batalhas
        print("\n" + "=" * 70)
        print(" JORNADA CONCLUÍDA COM SUCESSO! ".center(70, "="))
        print(f"  Busca A* acumulada (viagens):        {tempo_soma_viagens:.2f} min")
        print(f"  Combinatória AG (batalhas):           {tempo_soma_batalhas:.2f} min")
        print(f"  TOTAL GERAL DA JORNADA:               {tempo_total_jornada:.2f} min")
        print("=" * 70)

        # ── MAPA FINAL ────────────────────────────────────────────────────
        print("\nDesenhando percurso completo no mapa...")
        self.mapa.exibir_mapa(caminho_completo)