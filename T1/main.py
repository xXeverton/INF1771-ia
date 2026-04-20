# Ponto de entrada principal do programa.

from map.constants import ARQUIVO_MAPA
from map.map_core import MapaAang
from entities.agent import AgenteAvatar
from gui.renderer import VisualizadorPygame


def main():
    """
    Inicializa o sistema, carrega o mapa, instancia o agente e inicia a interface gráfica.
    """
    print("Inicializando sistema...")
    mapa = MapaAang(ARQUIVO_MAPA)
    
    print("Criando agente...")
    agente = AgenteAvatar(mapa)
    
    print("Calculando rotas e estratégias...")
    caminho_completo, log_jornada = agente.resolver_jornada_completa()

    if caminho_completo and log_jornada:
        print("Abrindo interface...")
        gui = VisualizadorPygame(mapa, caminho_completo, log_jornada)
        gui.iniciar_loop()
    else:
        print("Falha ao calcular a jornada.")


if __name__ == "__main__":
    main()