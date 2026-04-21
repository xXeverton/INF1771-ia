# Documentação do Algoritmo A* (astar.py)

## 📋 Visão Geral

O módulo `astar.py` implementa o **algoritmo A\* (A-Star)**, um algoritmo de busca em grafos que encontra o **caminho mais curto** de um ponto inicial a um destino em um mapa.

### Objetivo Principal
Encontrar a rota ótima (menor custo) entre dois pontos em um grid, considerando:
- **Terrenos com custos variáveis** (água, floresta, montanha = mais caros)
- **Heurística de Manhattan** para guiar a busca
- **Garantia de otimalidade** (caminho encontrado é o melhor possível)

---

## 🧭 Conceitos Fundamentais

### Fórmula do A*
```
f(n) = g(n) + h(n)

Onde:
  f(n) = Custo total estimado do caminho
  g(n) = Custo REAL do ponto inicial até o nó n
  h(n) = Custo ESTIMADO do nó n até o destino (heurística)
```

### Por Que A* é Melhor que Dijkstra?
- **Dijkstra**: Explora em todas as direções (menos eficiente)
- **A\***: Usa heurística para guiar a busca na direção do alvo

```
Dijkstra explora assim:     A* explora assim:
         ╭───╮                    ↗
        ╱     ╲                  ╱
      ◯       ◯              ◯  ★  ◯
        ╲     ╱               ↖
         ╰───╯
```

---

## 🔧 Classes e Funções

### 1. Classe `No`

**Propósito:** Representa um nó (célula) no mapa durante a busca.

**Atributos:**
```python
class No:
    x              # Coordenada X do nó
    y              # Coordenada Y do nó
    g              # Custo real do início até este nó
    h              # Custo estimado (heurística) daqui até destino
    f              # f = g + h (custo total estimado)
    pai            # Referência ao nó anterior no caminho
```

**Exemplo:**
```python
# Nó na posição (3, 5)
# Veio do início com custo 15
# Estima 8 até o destino
no = No(x=3, y=5, custo_g=15, heuristica_h=8)
# f automaticamente = 15 + 8 = 23
```

**Método Especial `__lt__` (less than):**
```python
def __lt__(self, outro):
    return self.f < outro.f
```
- Usado para comparar nós na fila de prioridade
- Garante que nó com MENOR f tem MAIOR prioridade
- Permite que `heapq` ordene automaticamente

**Exemplo:**
```python
no1 = No(1, 1, g=5, h=10)  # f = 15
no2 = No(2, 2, g=3, h=15)  # f = 18

no1 < no2  # True (15 < 18)
# no1 tem prioridade maior (será processado primeiro)
```

---

### 2. Função `distancia_manhattan(x1, y1, x2, y2)`

**Propósito:** Calcular a heurística H.

**O Que é Distância de Manhattan?**

Distância entre dois pontos em movimento ortogonal (cima, baixo, esquerda, direita):
```
Fórmula: |x1 - x2| + |y1 - y2|

Exemplo:
  Ponto A: (1, 1)
  Ponto B: (4, 5)
  
  Distância = |1 - 4| + |1 - 5|
            = |−3| + |−4|
            = 3 + 4
            = 7 passos
```

**Visualização:**
```
  0 1 2 3 4
0 . . . . .
1 A → → → .
2 . ↓ . . .
3 . ↓ . . .
4 . ↓ . . .
5 . . . . B

Caminho: direita 3 passos + baixo 4 passos = 7 passos
```

**Por Que Manhattan e não Euclidiana?**
- Mapas tipo grade permitem só 4 direções (N, S, L, O)
- Manhattan reflete o movimento real
- Euclidiana seria incorreta para grid

---

### 3. Função `executar_a_estrela(mapa, inicio, destino)`

**Propósito:** Orquestradora do algoritmo A*.

**Entrada:**
```python
mapa = MiniMapa(...)      # Objeto com método vizinhos_validos() e obter_custo()
inicio = (x1, y1)         # Tupla com coordenadas iniciais
destino = (x2, y2)        # Tupla com coordenadas finais
```

**Saída:**
```python
caminho = [(x1, y1), (x2, y2), ..., (xn, yn)]  # Lista de coordenadas
custo = 45.3                                    # Custo total do caminho
# Retorna ([], float('inf')) se não encontrar caminho
```

---

## 📊 Fluxo do Algoritmo Passo a Passo

```
┌─ INICIALIZAÇÃO
│  ├─ Cria fila de prioridade (heap vazio)
│  ├─ Cria dicionário de custos g
│  ├─ Calcula heurística h para nó inicial
│  ├─ Cria nó inicial
│  ├─ Adiciona nó inicial à fila
│  └─ Define custo_g[inicio] = 0
│
├─ LOOP ENQUANTO FILA NÃO ESTIVER VAZIA
│  ├─ POP: Remove nó com MENOR f da fila
│  │  └─ (heapq garante ser o melhor)
│  │
│  ├─ VERIFICAÇÃO DE META
│  │  └─ Se nó_atual == destino:
│  │     ├─ Reconstrói caminho voltando pelos pais
│  │     ├─ Reverte lista (estava de trás para frente)
│  │     └─ RETORNA (caminho, custo_total)
│  │
│  ├─ EXPLORAÇÃO DE VIZINHOS
│  │  └─ Para cada vizinho válido:
│  │     ├─ Calcula novo_custo_g = g_atual + custo_terreno
│  │     │
│  │     ├─ SE é novo OU custo_g melhor:
│  │     │  ├─ Atualiza custos_g[vizinho]
│  │     │  ├─ Calcula nova heurística h
│  │     │  ├─ Cria novo nó com pai = nó_atual
│  │     │  └─ Adiciona à fila (será ordenado por f)
│  │     │
│  │     └─ SENÃO: ignora (já foi explorado com custo melhor)
│  │
│  └─ Próxima iteração
│
└─ SE FILA ESVAZIAR: Sem caminho possível
   └─ RETORNA ([], infinito)
```

---

## 🔍 Exemplo Prático Detalhado

**Cenário:**
```
Mapa 5x5, começar em (0,0), ir a (4,4)

Custos de terreno:
  . = 1 (plano)
  R = 3 (rochoso)
  F = 5 (floresta)
  A = 10 (água)

Mapa:
    0 1 2 3 4
  0 S . . . .
  1 . R R . .
  2 . . F . .
  3 . . . . .
  4 . . . . D
```

**Iteração 1:**
```
Fila: vazia
Custo g: {}

Criar nó inicial:
  No(x=0, y=0, g=0, h=manhattan(0,0,4,4)=8)
  f = 0 + 8 = 8

Fila: [No(0,0,f=8)]
Custo g: {(0,0): 0}
```

**Iteração 2:**
```
POP: No(0,0,f=8)  ← menor f

Vizinhos válidos: [(0,1), (1,0)]

Vizinho (0,1):
  novo_g = 0 + custo(0,1) = 0 + 1 = 1
  novo_h = manhattan(0,1,4,4) = |0-4| + |1-4| = 4 + 3 = 7
  novo_f = 1 + 7 = 8
  → PUSH: No(0,1, g=1, h=7, f=8, pai=No(0,0))

Vizinho (1,0):
  novo_g = 0 + 1 = 1
  novo_h = manhattan(1,0,4,4) = 3 + 4 = 7
  novo_f = 1 + 7 = 8
  → PUSH: No(1,0, g=1, h=7, f=8, pai=No(0,0))

Custo g: {(0,0): 0, (0,1): 1, (1,0): 1}
Fila: [No(0,1,f=8), No(1,0,f=8)]
```

**... (mais iterações) ...**

**Iteração Final:**
```
POP: No(4,4)
DESTINO ENCONTRADO!

Reconstrói caminho:
  No(4,4) ← pai No(3,4) ← pai No(3,3) ← ... ← No(0,0)

Caminho: [(0,0), (0,1), (1,2), (2,2), (3,3), (4,4)]
Custo total: g(4,4) = 20

RETORNA: (caminho, 20)
```

---

## 💾 Estrutura de Dados - Fila de Prioridade

O `heapq` do Python implementa **Min-Heap**:

```python
fila_prioridade = []
heapq.heappush(fila, No(0,0,f=8))
heapq.heappush(fila, No(1,0,f=8))
heapq.heappush(fila, No(2,0,f=5))   ← Menor, sai primeiro
heapq.heappush(fila, No(3,0,f=10))

no = heapq.heappop(fila)  # Retorna No(2,0,f=5)
```

---

## ✅ Características Importantes

| Aspecto | Detalhes |
|---------|----------|
| **Otimalidade** | Garante encontrar caminho mais curto |
| **Completude** | Encontra solução se existir |
| **Complexidade** | O(b^d) onde b=branching, d=profundidade |
| **Heurística** | Manhattan (admissível e consistente) |
| **Admissibilidade** | h nunca superestima o custo real |
| **Consistência** | h(n) ≤ custo(n→n') + h(n') |

---

## 🚫 Casos Onde Retorna Sem Solução

```python
# Se não houver caminho válido
return [], float('inf')
```

**Exemplos:**
- Destino cercado por água/montanha intransponível
- Coordenadas inválidas
- Mapa completamente bloqueado

---

## 📈 Comparação: A* vs Dijkstra

| Algoritmo | Heurística | Velocidade | Nós Visitados | Otimalidade |
|-----------|-----------|-----------|-------------|------------|
| Dijkstra | Não | Lenta | Muitos | Ótima |
| A* | Sim | Rápida | Poucos | Ótima |
| BFS | Não | Média | Médio | Só se custo=1 |

**Exemplo visual (20 nós no grid):**
```
Dijkstra visita:    A* visita:
      ◯ ◯ ◯ ◯        ◯ ◯ ◯
    ◯ ◯ ◯ ◯ ◯        ◯ ★ ◯
  ◯ ◯ ◯ ◯ ◯ ◯      ◯ ◯ ◯
    ◯ ◯ ◯ ◯ ◯
      ◯ ◯ ◯

Dijkstra: ~80 nós    A*: ~30 nós
```

---

## 🎓 Aprendizados-Chave

1. **A* é busca informada** - usa conhecimento (heurística) sobre o destino
2. **Fila de prioridade é crítica** - permite selecionar nó mais promissor
3. **Rastreamento de pais** - permite reconstruir caminho completo
4. **Dicionário de custos** - evita reprocessar nós com custos piores
5. **Heurística deve ser admissível** - nunca superestimar ou A* não garante otimalidade

---

## 🔗 Integração com o Projeto

```
main.py
   ↓
mapa.py (carrega grid do arquivo)
   ↓
astar.py (encontra caminho no grid)
   ↓
gui/renderer.py (visualiza caminho na tela)
```

**Entrada do usuário:** inicio (0,0) → destino (10,10)
**Saída do A\*:** Caminho ótimo com custo mínimo
**Visualização:** Rastro amarelo no mapa
