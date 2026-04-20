"""
Constantes do jogo: custos de terreno, dificuldades das etapas e configuração da equipe.
"""

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
    '0': 0,                                                            
    '1': 10,  '2': 20,  '3': 30,  '4': 40,  '5': 50,
    '6': 60,  '7': 70,  '8': 80,  '9': 90,
    'B': 100, 'C': 110, 'D': 120, 'E': 130, 'G': 140,
    'H': 150, 'I': 160, 'J': 170, 'K': 180, 'L': 190,
    'N': 200, 'O': 210, 'P': 220, 'Q': 230, 'S': 240,
    'T': 250, 'U': 260, 'V': 270, 'W': 280, 'X': 290,
    'Y': 300, 'Z': 310                                                 
}

# Configuração da equipe (energia e agilidade)
CONFIG_EQUIPE = {
    "Aang":   {"energia": 8, "agilidade": 1.8},
    "Zukko":  {"energia": 8, "agilidade": 1.6},
    "Toph":   {"energia": 8, "agilidade": 1.6},
    "Katara": {"energia": 8, "agilidade": 1.6},
    "Sokka":  {"energia": 8, "agilidade": 1.4},
    "Appa":   {"energia": 8, "agilidade": 0.9},
    "Momo":   {"energia": 8, "agilidade": 0.7}
}

# Caminho para o arquivo do mapa (apontando para a pasta data)
ARQUIVO_MAPA = "data/mapa.txt"