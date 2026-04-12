meu_projeto/
│
├── assets/              # imagens .png aqui
│   ├── tiles/           # Imagens de grama, montanha, água, etc.
│   └── sprites/         # Imagens dos personagens (Aang, Katara...)
│
├── gui/                 # Tudo relacionado ao Pygame
│   ├── __init__.py
│   └── renderer.py      # Classe responsável por abrir a janela e desenhar
│
├── map/                 # Tudo relacionado ao ambiente
│   ├── __init__.py
│   ├── map_core.py      # Leitura e impressão do mapa
│   └── constants.py     # Custos e dicionários
│
├── algorithms/          # Puramente matemática e IA
│   ├── __init__.py
│   ├── astar.py         # Busca do Caminho e Heurística (Problema 1)
│   └── allocation.py    # Busca Gulosa de Benefício Marginal (Problema 2)
│
├── entities/            # Os "atores" do nosso sistema
│   ├── __init__.py
│   └── agent.py         # Classe AgenteAvatar (Orquestra a viagem e as batalhas)
│
├── data/
│   └── mapa.txt         
│
└── main.py              