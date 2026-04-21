# Documentação do Módulo de Mapa (map_core.py e constants.py)

## 📋 Visão Geral

O módulo de mapa gerencia toda a estrutura do mundo de Avatar:
- **map_core.py**: Classe que carrega e manipula o mapa
- **constants.py**: Definições de custos, dificuldades e equipe

### Objetivo Principal
Representar o mapa como uma matriz 2D onde cada célula tem um tipo de terreno com custo associado, e armazenar pontos de interesse (checkpoints).

---

## 📁 Arquivo: constants.py

### 1. Custos de Terreno

```python
CUSTOS_TERRENO = {
    '.': 1,    # Plano      → rápido de cruzar
    'R': 5,    # Rochoso    → 5x mais lento
    'F': 10,   # Floresta   → 10x mais lento
    'A': 15,   # Água       → 15x mais lento
    'M': 200   # Montanhoso → praticamente impraticável
}
```

**O que significam os números?**
- Cada número representa minutos gastos ao cruzar 1 célula daquele terreno
- **Plano (.)**: 1 minuto/célula → terreno mais eficiente
- **Montanhoso (M)**: 200 minutos/célula → praticamente intransponível

**Exemplo na Prática:**
```
Caminho: [Plano(1) → Rochoso(5) → Floresta(10)]
Tempo total: 1 + 5 + 10 = 16 minutos
```

---

### 2. Dificuldades das Etapas (Batalhas)

```python
DIFICULDADES = {
    '0': 0,                                    # Aldeia (sem batalha)
    '1': 10, '2': 20, ..., '9': 90,           # Checkpoints 1-9
    'B': 100, 'C': 110, ..., 'Z': 310         # Checkpoints B-Z
}
```

**Interpretação:**
- Cada checkpoint representa uma **etapa de batalha**
- O número é a **dificuldade** (custo base em pontos)
- Checkpoint '0' é a aldeia inicial sem batalha

**Progressão de Dificuldades:**
```
Etapa '0': 0      (início, sem luta)
Etapa '1': 10     (fácil)
Etapa '5': 50     (moderada)
Etapa 'Z': 310    (extremamente difícil)
```

**Como É Usado:**
```
O algoritmo de alocação usa estas dificuldades para determinar
quantos personagens são necessários em cada etapa.

Etapa com dificuldade 100:
- Com 1 personagem ágil (agilidade=2.0): 100/2.0 = 50 minutos
- Com 2 personagens ágeis (agilidade=4.0): 100/4.0 = 25 minutos
```

---

### 3. Configuração da Equipe

```python
CONFIG_EQUIPE = {
    "Aang":   {"energia": 8, "agilidade": 1.8},  # Mais ágil
    "Zukko":  {"energia": 8, "agilidade": 1.6},
    "Toph":   {"energia": 8, "agilidade": 1.6},
    "Katara": {"energia": 8, "agilidade": 1.6},
    "Sokka":  {"energia": 8, "agilidade": 1.4},
    "Appa":   {"energia": 8, "agilidade": 0.9},   # Menos ágil
    "Momo":   {"energia": 8, "agilidade": 0.7}
}
```

**Energia:**
- Máximo de etapas que o personagem pode participar
- Todos começam com 8 (pode participar de até 8 etapas)

**Agilidade:**
- Velocidade de combate do personagem
- Quanto maior, mais rápido completa uma etapa
- Aang é o mais ágil (1.8), Momo o menos (0.7)

**Exemplo:**
```
Etapa com dificuldade 100

Com Aang (agilidade 1.8): tempo = 100/1.8 ≈ 55.6 minutos
Com Momo (agilidade 0.7): tempo = 100/0.7 ≈ 142.9 minutos

Aang é ~2.5x mais rápido que Momo!
```

---

### 4. Caminho do Arquivo Mapa

```python
ARQUIVO_MAPA = "data/mapa.txt"
```

Caminho relativo para o arquivo de dados do mapa.

---

## 🗺️ Arquivo: map_core.py

### Classe `MapaAang`

**Propósito:** Carregar e gerenciar a estrutura do mapa.

---

## 🔧 Método: `__init__(caminho_arquivo)`

**Propósito:** Inicializar o mapa.

**Processo:**
1. Cria matrizes vazias
2. Carrega o arquivo do mapa
3. Processa cada caractere

**Exemplo:**
```python
mapa = MapaAang("data/mapa.txt")
# Resultado:
# - mapa.matriz: lista 2D de caracteres
# - mapa.checkpoints: dict com posição de cada checkpoint
# - mapa.custos_terreno: referência aos custos (de constants.py)
```

---

## 🔧 Método: `carregar_mapa(caminho_arquivo)`

**Propósito:** Ler arquivo e processar mapa.

**Processo Passo-a-Passo:**

```
1. Abre arquivo linha por linha
   
2. Para cada linha (y = número da linha):
   
   3. Para cada caractere (x = coluna):
      
      a) Se caractere está em CUSTOS_TERRENO:
         └─ Adiciona à matriz (ex: '.', 'R', 'F')
      
      b) Se NÃO está em CUSTOS_TERRENO:
         ├─ Trata como checkpoint (ex: '1', 'B', 'Z')
         ├─ Armazena em checkpoints: {char: (x, y)}
         └─ Substitui por '.' na matriz (terreno padrão)
   
4. Imprime estatísticas (tamanho, quantidade de checkpoints)
```

**Exemplo com Arquivo:**
```
Arquivo data/mapa.txt:
  . . 1 . .
  R . . . 2
  . F . . .
  . . . M .

Processamento:
  y=0: ['.', '.', '1', '.', '.']
       └─ Detecta '1' → checkpoints['1'] = (2, 0), coloca '.'
       
  y=1: ['R', '.', '.', '.', '2']
       └─ Detecta '2' → checkpoints['2'] = (4, 1), coloca '.'
  
  Resultado:
  matriz[0]: ['.', '.', '.', '.', '.']
  matriz[1]: ['R', '.', '.', '.', '.']
  checkpoints: {'1': (2, 0), '2': (4, 1)}
```

---

## 🔧 Método: `obter_custo(x, y)`

**Propósito:** Retornar o custo do terreno em uma coordenada.

**Processo:**
```
1. Acessa matriz[y][x] (obtém tipo de terreno)
2. Busca custo em CUSTOS_TERRENO[tipo]
3. Retorna o valor numérico
```

**Exemplo:**
```python
mapa.obter_custo(0, 1)  # Posição (0, 1)
# matriz[1][0] = 'R' (rochoso)
# CUSTOS_TERRENO['R'] = 5
# Retorna 5
```

**Usado por:** Algoritmo A* para calcular custo de movimento

---

## 🔧 Método: `vizinhos_validos(x, y)`

**Propósito:** Encontrar todas as células adjacentes válidas.

**Processo:**
```
1. Define 4 direções ortogonais:
   [(0, -1),  # Cima (norte)
    (0,  1),  # Baixo (sul)
    (-1, 0),  # Esquerda (oeste)
    (1,  0)]  # Direita (leste)

2. Para cada direção:
   ├─ Calcula nova posição: (nx, ny) = (x+dx, y+dy)
   ├─ Verifica se dentro dos limites do mapa:
   │  └─ 0 ≤ nx < largura E 0 ≤ ny < altura
   └─ Se válido: adiciona à lista de vizinhos

3. Retorna lista de vizinhos válidos
```

**Exemplo Prático:**
```
Mapa 5x5:
    0 1 2 3 4
  0 . . . . .
  1 . X . . .
  2 . . . . .
  3 . . . . .
  4 . . . . .

vizinhos_validos(1, 1):
  Cima:    (1, 0) ✓
  Baixo:   (1, 2) ✓
  Esquerda: (0, 1) ✓
  Direita: (2, 1) ✓
  
Retorna: [(1, 0), (1, 2), (0, 1), (2, 1)]

vizinhos_validos(0, 0) [canto]:
  Cima:    (0, -1) ✗ (fora do mapa)
  Baixo:   (0, 1) ✓
  Esquerda: (-1, 0) ✗ (fora do mapa)
  Direita: (1, 0) ✓
  
Retorna: [(0, 1), (1, 0)] (apenas 2 vizinhos)
```

**Usado por:** Algoritmo A* para explorar o mapa

---

## 🔧 Método: `obter_ordem_checkpoints()`

**Propósito:** Retornar checkpoints em ordem alfabética.

**Processo:**
```
1. Obtém todas as chaves do dicionário checkpoints
2. Ordena alfabeticamente
3. Retorna lista ordenada
```

**Exemplo:**
```python
checkpoints = {'Z': (10, 20), '1': (5, 5), 'B': (15, 10)}
obter_ordem_checkpoints()
# Retorna: ['1', 'B', 'Z'] (ordem alfabética)
```

**Usado por:** Sistema de missões para definir ordem de visitação

---

## 📊 Fluxo Completo de Carregamento

```
main.py
  ↓
mapa = MapaAang("data/mapa.txt")
  ├─ __init__()
  │  └─ carregar_mapa()
  │     ├─ Lê arquivo linha a linha
  │     ├─ Preenche matriz[][] com tipos de terreno
  │     ├─ Popula dicionário checkpoints
  │     └─ Imprime: "Mapa carregado: 20x15"
  │        "Checkpoints encontrados: 26"
  │
  ├─ Agora mapa está pronto para ser usado
  │
  ├─ a_star.py chama:
  │  ├─ mapa.vizinhos_validos(x, y)
  │  └─ mapa.obter_custo(x, y)
  │
  └─ allocation.py lê:
     └─ mapa.checkpoints (para saber dificuldades)
```

---

## 🗺️ Formato do Arquivo Mapa

**Arquivo: data/mapa.txt**

```
. . . 1 . . . . .
. R R . . 2 . . .
. . F . . . . 3 .
. . . . . . . . .
4 . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
```

**Legenda:**
- `.` = Plano (custo 1)
- `R` = Rochoso (custo 5)
- `F` = Floresta (custo 10)
- `A` = Água (custo 15)
- `M` = Montanhoso (custo 200)
- `0-9, A-Z` = Checkpoints (etapas de batalha)

**Requisitos:**
- Cada linha deve ter o mesmo número de caracteres
- Checkpoints são detectados automaticamente
- Arquivo deve estar em UTF-8

---

## 🎯 Interação com Outros Módulos

### Conexão com A* (astar.py)
```python
# A* precisa saber:
# 1. Vizinhos válidos de uma posição
vizinhos = mapa.vizinhos_validos(10, 15)

# 2. Custo de movimento para cada vizinho
for nx, ny in vizinhos:
    custo = mapa.obter_custo(nx, ny)
```

### Conexão com Alocação (allocation.py)
```python
# Alocação precisa saber:
# 1. Checkpoints disponíveis
checkpoints = mapa.checkpoints  # {'1': (2,0), 'B': (15,10), ...}

# 2. Dificuldades de cada checkpoint
from map.constants import DIFICULDADES
dificuldade_etapa1 = DIFICULDADES['1']  # 10
```

### Conexão com GUI (gui/renderer.py)
```python
# Renderer precisa saber:
# 1. Tamanho do mapa
altura = len(mapa.matriz)
largura = len(mapa.matriz[0])

# 2. Tipo de terreno de cada célula
for y in range(altura):
    for x in range(largura):
        tipo_terreno = mapa.matriz[y][x]
        cor = mapear_terreno_para_cor(tipo_terreno)
```

---

## 💾 Estruturas de Dados Utilizadas

| Estrutura | Tipo | Exemplo |
|-----------|------|---------|
| `matriz` | `list[list[str]]` | `[['.','.','R'], ['F','.','.'], ...]` |
| `checkpoints` | `dict[str, tuple]` | `{'1': (2,0), 'B': (15,10), ...}` |
| `custos_terreno` | `dict[str, int]` | `{'.': 1, 'R': 5, 'F': 10, ...}` |

---

## 🐛 Tratamento de Erros

```python
except FileNotFoundError:
    print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
```

Se o arquivo não existir, o programa imprime mensagem de erro mas continua rodando com mapa vazio.

---

## 📈 Complexidade

| Operação | Complexidade | Notas |
|----------|-------------|-------|
| Carregar mapa | O(L × C) | L=linhas, C=colunas |
| obter_custo() | O(1) | Acesso direto |
| vizinhos_validos() | O(1) | Sempre 4 vizinhos máximo |
| obter_ordem_checkpoints() | O(n log n) | n = número de checkpoints |

---

## 📚 Exemplos de Uso

```python
from map.map_core import MapaAang
from map.constants import CONFIG_EQUIPE, DIFICULDADES

# Carregar mapa
mapa = MapaAang("data/mapa.txt")
# Output: Mapa carregado: 50x40
#         Checkpoints encontrados: 26

# Usar em A*
from algorithms.astar import executar_a_estrela
caminho, custo = executar_a_estrela(mapa, (0,0), (49, 39))

# Usar em Alocação
from algorithms.allocation import otimizar_alocacao_equipe
dificuldades = {cp: DIFICULDADES[cp] for cp in mapa.checkpoints}
alocacao, energia = otimizar_alocacao_equipe(dificuldades, CONFIG_EQUIPE)

# Visualizar em GUI
from gui.renderer import VisualizadorPygame
viz = VisualizadorPygame(mapa, caminho, [])
viz.iniciar_loop()
```

---

## 🎓 Conceitos-Chave

| Termo | Significado |
|------|------------|
| **Matriz** | Representação 2D do mapa (grid) |
| **Checkpoint** | Ponto de interesse/etapa de batalha |
| **Custo** | Tempo para cruzar uma célula |
| **Vizinhos** | Células adjacentes (4-conectado, sem diagonais) |
| **Agilidade** | Velocidade do personagem em combate |
| **Energia** | Quantas etapas um personagem pode participar |
| **Dificuldade** | Nível de desafio de uma etapa |
