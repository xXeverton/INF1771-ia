"""
Este é o gestor. O Agente conhece o ambiente (map.py), sabe andar (astar.py) e pede ajuda
para organizar a equipa (allocation.py). A responsabilidade dele é juntar tudo e enviar os 
dados estruturados para o diário de bordo e interface gráfica.
"""

from map.constants import EQUIPE_CONFIG, DIFICULDADES
from algorithms.astar import executar_a_estrela
from algorithms.allocation import otimizar_alocacao_equipa

class AgenteAvatar:
    """
    O Agente que orquestra a viagem. Ele analisa o mapa, 
    calcula as rotas e gere a equipa em cada checkpoint.
    """

    def __init__(self, mapa):
        self.mapa = mapa
        self.equipa = EQUIPE_CONFIG
        self.dificuldades = DIFICULDADES

    def resolver_jornada_completa(self):
        """Orquestra a jornada resolvendo o Problema 1 e 2 sequencialmente."""
        
        # 1. Identificar as etapas pela ordem alfabética definida no mapa
        ordem_etapas = self.mapa.obter_ordem_checkpoints()
        
        # 2. Resolver o Problema 2 (Quem luta onde)
        print("A planear a estratégia de batalhas...")
        
        # O allocation.py agora usa a nossa nova classe internamente
        alocacao_equipa, energia_final = otimizar_alocacao_equipa(self.dificuldades, self.equipa)

        # Variáveis para acumular o tempo e os dados para a interface gráfica
        tempo_soma_viagens = 0.0
        tempo_soma_batalhas = 0.0
        caminho_completo = []
        log_jornada = []  # Lista de dicionários estruturados para o Pygame

        print("\n" + "="*70)
        print(" INICIANDO A GRANDE JORNADA DO AVATAR ".center(70, "="))
        print("="*70)
        print(f"\n{'Etapa':<10} {'Equipa Alocada':<35} {'Viagem':>8} {'Batalha':>8} {'Total':>8}")
        print("-" * 70)

        # 3. Resolver o Problema 1 (Andar de A para B)
        for i in range(len(ordem_etapas) - 1):
            chave_origem = ordem_etapas[i]
            chave_destino = ordem_etapas[i + 1]

            coord_origem = self.mapa.checkpoints[chave_origem]
            coord_destino = self.mapa.checkpoints[chave_destino]

            # Encontra o caminho via A*
            caminho_trecho, tempo_viagem = executar_a_estrela(self.mapa, coord_origem, coord_destino)

            if not caminho_trecho:
                print(f"ERRO CRÍTICO: Caminho bloqueado entre '{chave_origem}' e '{chave_destino}'.")
                return [], [] # Retorna listas vazias em caso de erro

            # Calcula o tempo de batalha se houver uma luta neste destino
            tempo_batalha = 0.0
            equipa_luta = []

            if chave_destino in alocacao_equipa:
                equipa_luta = alocacao_equipa[chave_destino]
                dificuldade_etapa = self.dificuldades[chave_destino]
                soma_agilidade = sum(self.equipa[p]["agilidade"] for p in equipa_luta)
                tempo_batalha = dificuldade_etapa / soma_agilidade if soma_agilidade > 0 else float('inf')

            # Acumuladores
            tempo_soma_viagens += tempo_viagem
            tempo_soma_batalhas += tempo_batalha
            tempo_total_jornada = tempo_soma_viagens + tempo_soma_batalhas

            # Formatação da Equipe
            equipa_str = ", ".join(equipa_luta) if equipa_luta else "—"
            
            # --- INTEGRAÇÃO COM PYGAME (NOVO FORMATO ESTRUTURADO) ---
            # Em vez de passar string e forçar o renderer a fazer split, passamos os dados puros.
            dados_trecho = {
                "trecho": f"{chave_origem} -> {chave_destino}",
                "equipe": equipa_str,
                "delta_astar": tempo_viagem,
                "delta_comb": tempo_batalha,
                "astar": tempo_soma_viagens,
                "comb": tempo_soma_batalhas
            }
            log_jornada.append(dados_trecho)
            
            # --- OUTPUT DO TERMINAL (Visual Clássico Mantido) ---
            linha_log = f"[{chave_origem}->{chave_destino}] {equipa_str:<35} {tempo_soma_viagens:>8.1f} {tempo_soma_batalhas:>8.1f} {tempo_total_jornada:>8.1f}"
            print(linha_log)

            # Adiciona o caminho ao rasto geral (ignorando o último passo para não duplicar)
            caminho_completo.extend(caminho_trecho[:-1])

        # Adiciona o ponto final ao caminho
        caminho_completo.append(self.mapa.checkpoints[ordem_etapas[-1]])

        # Resumo Final
        print("="*70)
        print(" JORNADA CONCLUÍDA COM SUCESSO! ".center(70, "="))
        print(f"  Tempo Total de Deslocamento (A*):    {tempo_soma_viagens:.2f} minutos")
        print(f"  Tempo Total de Batalhas (Otimizado): {tempo_soma_batalhas:.2f} minutos")
        print(f"  CUSTO GLOBAL DA JORNADA:             {tempo_total_jornada:.2f} minutos")
        print("="*70)

        # Desenhar no terminal o rasto (duplo feedback visual)
        print("\nA processar rasto do mapa no console...")
        self.mapa.exibir_mapa(caminho_completo)

        # Retorna o caminho para a animação e a lista de dicionários para o painel de status
        return caminho_completo, log_jornada