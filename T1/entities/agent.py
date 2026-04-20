# Este arquivo define a classe AgenteAvatar, responsável por orquestrar a jornada.

from map.constants import CONFIG_EQUIPE, DIFICULDADES
from algorithms.astar import executar_a_estrela
from algorithms.allocation import otimizar_alocacao_equipe

class AgenteAvatar:
    """
    Agente que orquestra a jornada do Avatar.
    """

    def __init__(self, mapa):
        """
        Inicializa o agente.
        :param mapa: Objeto mapa.
        """
        self.mapa = mapa
        self.equipe = CONFIG_EQUIPE
        self.dificuldades = DIFICULDADES

    def resolver_jornada_completa(self):
        """
        Orquestra a jornada resolvendo os problemas 1 e 2.
        :return: Tupla com caminho completo e log da jornada.
        """
        ordem_etapas = self.mapa.obter_ordem_checkpoints()
        
        print("Planejando estratégia de batalhas...")
        
        alocacao_equipe, energia_final = otimizar_alocacao_equipe(self.dificuldades, self.equipe)

        tempo_viagens = 0.0
        tempo_batalhas = 0.0
        caminho_completo = []
        log_jornada = []

        print("\n" + "="*70)
        print(" JORNADA DO AVATAR ".center(70, "="))
        print("="*70)
        print(f"\n{'Etapa':<10} {'Equipe Alocada':<35} {'Viagem':>8} {'Batalha':>8} {'Total':>8}")
        print("-" * 70)

        for i in range(len(ordem_etapas) - 1):
            chave_origem = ordem_etapas[i]
            chave_destino = ordem_etapas[i + 1]

            coord_origem = self.mapa.checkpoints[chave_origem]
            coord_destino = self.mapa.checkpoints[chave_destino]

            caminho_trecho, tempo_viagem = executar_a_estrela(self.mapa, coord_origem, coord_destino)

            if not caminho_trecho:
                print(f"ERRO: Caminho bloqueado entre '{chave_origem}' e '{chave_destino}'.")
                return [], []

            tempo_batalha = 0.0
            equipe_luta = []

            if chave_destino in alocacao_equipe:
                equipe_luta = alocacao_equipe[chave_destino]
                dificuldade_etapa = self.dificuldades[chave_destino]
                soma_agilidade = sum(self.equipe[p]["agilidade"] for p in equipe_luta)
                tempo_batalha = dificuldade_etapa / soma_agilidade if soma_agilidade > 0 else float('inf')

            tempo_viagens += tempo_viagem
            tempo_batalhas += tempo_batalha
            tempo_total = tempo_viagens + tempo_batalhas

            equipe_str = ", ".join(equipe_luta) if equipe_luta else "—"
            
            dados_trecho = {
                "trecho": f"{chave_origem} -> {chave_destino}",
                "equipe": equipe_str,
                "delta_astar": tempo_viagem,
                "delta_comb": tempo_batalha,
                "astar": tempo_viagens,
                "comb": tempo_batalhas
            }
            log_jornada.append(dados_trecho)
            
            linha_log = f"[{chave_origem}->{chave_destino}] {equipe_str:<35} {tempo_viagens:>8.1f} {tempo_batalhas:>8.1f} {tempo_total:>8.1f}"
            print(linha_log)

            caminho_completo.extend(caminho_trecho[:-1])

        caminho_completo.append(self.mapa.checkpoints[ordem_etapas[-1]])

        print("="*70)
        print(" JORNADA CONCLUÍDA ".center(70, "="))
        print(f"  Tempo de deslocamento (A*):  {tempo_viagens:.2f} min")
        print(f"  Tempo de batalhas:           {tempo_batalhas:.2f} min")
        print(f"  TEMPO TOTAL:                 {tempo_viagens + tempo_batalhas:.2f} min")
        print("="*70)

        return caminho_completo, log_jornada