# from map.constants import ARQUIVO_MAPA
# from map.map_core import MapaAang
# from entities.agent import AgenteAvatar

# def main():
#     print("1. Inicializando o Sistema...")
    
#     # 1. Instancia o ambiente
#     mapa = MapaAang(ARQUIVO_MAPA)
    
#     # 2. Instancia o agente inteligente no ambiente
#     agente = AgenteAvatar(mapa)
    
#     # 3. Dá a ordem de execução
#     agente.resolver_jornada_completa()

# if __name__ == "__main__":
#     main()


# main.py

from map.constants import ARQUIVO_MAPA
from map.map_core import MapaAang
from entities.agent import AgenteAvatar
from gui.renderer import VisualizadorPygame # Importa a nossa nova GUI!

def main():
    print("1. Inicializando o Sistema e Carregando o Mapa...")
    mapa = MapaAang(ARQUIVO_MAPA)
    
    print("2. Instanciando a Inteligência Artificial do Agente Avatar...")
    agente = AgenteAvatar(mapa)
    
    print("3. Calculando rotas ótimas e estratégias de alocação...")
    # ATENÇÃO: Modificamos o agente para retornar dados em vez de só printar!
    # caminho_completo: Lista de tuplas (x, y) com a rota percorrida
    # log_jornada: Lista de strings com os textos para a tabela do Pygame
    caminho_completo, log_jornada = agente.resolver_jornada_completa()

    if caminho_completo and log_jornada:
        print("4. Abrindo Interface Gráfica Pygame...")
        # Inicializa a GUI passando o mapa, a rota e os textos
        gui = VisualizadorPygame(mapa, caminho_completo, log_jornada)
        gui.iniciar_loop()
    else:
        print("Falha ao calcular a jornada. Interface não será aberta.")

if __name__ == "__main__":
    main()