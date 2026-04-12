T1/
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