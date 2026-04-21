# 2026-1-t1-lenda-de-aang-botavasco

---

### Nomes: Everton Pereira Militão - 2320462; José Carlos de Sampaio Neto - 2320465

**Link**: [Apresentação do Trabalho](https://drive.google.com/file/d/14iPBOqz6aslw32X0seOAKdN0RAp-hIOC/view?usp=sharing)

## Organização dos Trabalhos

```
T1/
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
│   └── allocation.py    # Algoritmo Genético + Busca Local (Hill Climbing)
│
├── entities/            # Os "atores" do nosso sistema
│   ├── __init__.py
│   └── agent.py         # Classe AgenteAvatar (Orquestra a viagem e as batalhas)
│
├── data/
│   └── mapa.txt         
│
└── main.py        
```

Como rodar o projeto?

## No Windows:
Abra o terminal na pasta raiz do projeto.

Crie o ambiente virtual:

```Bash
python -m venv venv
```

### Ative o ambiente:

```Bash
.\venv\Scripts\activate
```

## No Linux/macOS (e WSL):

Abra o terminal na pasta raiz do projeto.

### Crie o ambiente virtual:

```Bash
python3 -m venv venv
Ative o ambiente:
```

```Bash
source venv/bin/activate
```

### Instalação de Dependências
```Bash
pip install -r requirements.txt
```

Todas as variáveis de ajuste estão centralizadas no arquivo map/constants.py (ou constants.py)

### Ajuste de Custos de Terreno
Você pode modificar o custo de deslocamento para cada tipo de terreno no dicionário CUSTOS_TERRENO

### Agilidade e Energia da Equipe
No dicionário CONFIG_EQUIPE, é possível alterar a agilidade de cada personagem e sua capacidade de energia (limite de 8 etapas).
+1

### Alteração de Mapas
O sistema suporta a leitura de mapas configuráveis via arquivos de texto.

Como mudar o mapa:

Arquivo de Texto: Coloque o novo arquivo .txt na pasta data/.

Atualização do Caminho: No arquivo map/constants.py (ou diretamente no main.py), altere a constante ARQUIVO_MAPA para apontar para o novo arquivo:

```Python
ARQUIVO_MAPA = "data/novo_mapa.txt"
```
---

## 🚀 Execução
Para iniciar a simulação com a interface gráfica e a inteligência artificial ativa, execute:
```
Bash
python main.py
``` 
O programa calculará as rotas ótimas via A* e a alocação de equipe via Algoritmo Genético, exibindo o custo total no console e a animação no Pygame.