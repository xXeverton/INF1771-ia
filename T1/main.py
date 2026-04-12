from map.constants import ARQUIVO_MAPA
from map.map_core import MapaAang
from entities.agent import AgenteAvatar

def main():
    print("1. Inicializando o Sistema...")
    
    # 1. Instancia o ambiente
    mapa = MapaAang(ARQUIVO_MAPA)
    
    # 2. Instancia o agente inteligente no ambiente
    agente = AgenteAvatar(mapa)
    
    # 3. Dá a ordem de execução
    agente.resolver_jornada_completa()

if __name__ == "__main__":
    main()