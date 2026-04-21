# Documentação do Orquestrador (main.py e agent.py)

## 📋 Visão Geral

Estes dois arquivos formam o **orquestrador** do sistema:
- **main.py**: Ponto de entrada do programa
- **agent.py**: Classe que coordena toda a lógica de resolução

### Objetivo Principal
Integrar todos os módulos (mapa, A*, alocação, GUI) em um fluxo único que resolve completamente a jornada do Avatar.

---

## 🚀 Arquivo: main.py

### Função `main()`

**Propósito:** Inicializar e executar o programa completo.

**Fluxo Passo-a-Passo:**

```
1. Carrega mapa
   ├─ Lê arquivo data/mapa.txt
   ├─ Processa terrenos e checkpoints
   └─ Prepara estruturas de dados

2. Cria agente
   ├─ Passa mapa como parâmetro
   └─ Inicializa contexto de resolução

3. Resolve jornada
   ├─ Calcula caminho via A*
   ├─ Otimiza alocação via Algoritmo Genético
   ├─ Compila dados de cada etapa
   └─ Retorna caminho completo e logs

4. Se resolução bem-sucedida:
   ├─ Inicia Pygame
   ├─ Cria visualizador
   ├─ Passa dados da jornada
   └─ Abre interface interativa

5. Se falhar:
   ├─ Imprime mensagem de erro
   └─ Encerra programa
```

**Código:**
```python
def main():
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
```

### Point: `if __name__ == "__main__"`

**Significado:**
```python
if __name__ == "__main__":
    main()
```

- Executa `main()` apenas quando script é rodado diretamente
- Não executa se importado por outro módulo
- Padrão Python para entry points

---

## 🎯 Arquivo: agent.py

### Classe `AgenteAvatar`

**Propósito:** Orquestrar a resolução completa da jornada.

**Responsabilidades:**
1. Carregar configuração da equipe
2. Coordenar cálculos de rota (A*)
3. Coordenar otimização (Algoritmo Genético)
4. Integrar resultados em log estruturado
5. Exibir relatório ao usuário

---

## 🔧 Método: `__init__(mapa)`

**Propósito:** Inicializar o agente com contexto.

**Processo:**
```python
def __init__(self, mapa):
    self.mapa = mapa                    # Referência ao mapa
    self.equipe = CONFIG_EQUIPE         # Config dos personagens
    self.dificuldades = DIFICULDADES    # Dificuldades das etapas
```

**Armazenado:**
- Mapa para calcular rotas
- Equipe e dificuldades para otimização

---

## 🔧 Método: `resolver_jornada_completa()`

**Propósito:** Resolver completamente a jornada de Avatar.

Este é o método-chave que **integra A* e Algoritmo Genético**.

### Passo 1: Obter Ordem de Checkpoints

```python
ordem_etapas = self.mapa.obter_ordem_checkpoints()
# Exemplo retorno: ['0', '1', '2', 'B', 'Z']
```

Obtém checkpoints em ordem alfabética (é a ordem de visitação).

### Passo 2: Otimizar Alocação de Equipe

```python
alocacao_equipe, energia_final = otimizar_alocacao_equipe(
    self.dificuldades,  # {'1': 10, '2': 20, ...}
    self.equipe         # {"Aang": {...}, "Katara": {...}, ...}
)
```

**Retorno:**
```python
alocacao_equipe = {
    '1': ['Aang', 'Katara'],      # Etapa 1: quem vai lutar
    '2': ['Sokka', 'Toph'],
    'B': ['Aang', 'Zukko', 'Toph'],
    'Z': ['Aang', 'Katara', 'Zukko', 'Toph']  # Etapa final
}
```

---

### Passo 3: Processar Cada Etapa

Loop através de todos os checkpoints adjacentes:

```python
for i in range(len(ordem_etapas) - 1):
    chave_origem = ordem_etapas[i]      # Ex: '1'
    chave_destino = ordem_etapas[i+1]   # Ex: '2'
```

---

#### 3a. Calcular Caminho via A*

```python
coord_origem = self.mapa.checkpoints[chave_origem]   # (10, 15)
coord_destino = self.mapa.checkpoints[chave_destino] # (25, 30)

caminho_trecho, tempo_viagem = executar_a_estrela(
    self.mapa, 
    coord_origem, 
    coord_destino
)
```

**Retorno:**
```python
caminho_trecho = [(10,15), (11,15), (12,15), ..., (25,30)]
tempo_viagem = 45.3  # minutos
```

---

#### 3b. Calcular Custo de Batalha

```python
if chave_destino in alocacao_equipe:
    equipe_luta = alocacao_equipe[chave_destino]  # ['Aang', 'Katara']
    dificuldade_etapa = self.dificuldades[chave_destino]  # 50
    
    # Soma agilidade de todos personagens da equipe
    soma_agilidade = sum(
        self.equipe[p]["agilidade"] 
        for p in equipe_luta
    )
    # Exemplo: Aang(1.8) + Katara(1.6) = 3.4
    
    # Tempo = dificuldade / agilidade total
    tempo_batalha = dificuldade_etapa / soma_agilidade
    # 50 / 3.4 ≈ 14.7 minutos
```

---

#### 3c. Compilar Dados do Trecho

```python
dados_trecho = {
    "trecho": f"{chave_origem} -> {chave_destino}",
    "equipe": "Aang, Katara",
    "delta_astar": tempo_viagem,      # Custo deste trecho
    "delta_comb": tempo_batalha,      # Custo desta batalha
    "astar": tempo_viagens,           # Acumulado
    "comb": tempo_batalhas            # Acumulado
}
log_jornada.append(dados_trecho)
```

---

### Passo 4: Compilar Caminho Completo

```python
# Concatena todos os trechos (removendo sobreposição do final)
caminho_completo.extend(caminho_trecho[:-1])

# Adiciona último checkpoint
caminho_completo.append(self.mapa.checkpoints[ordem_etapas[-1]])
```

**Resultado:**
```python
caminho_completo = [
    (0, 0),           # Checkpoint 0
    (5, 2), (6, 2),   # Caminho A*: 0→1
    (7, 3), (8, 5),   # ...
    (10, 15),         # Checkpoint 1
    (12, 16),         # Caminho A*: 1→2
    ...
    (100, 100)        # Checkpoint final
]
```

---

### Passo 5: Exibir Relatório

```
======================================================================
                         JORNADA DO AVATAR
======================================================================

Etapa       Equipe Alocada           Viagem   Batalha    Total
----------------------------------------------------------------------
[0->1] Aang, Katara                   45.3      14.7     60.0
[1->2] Sokka, Toph                    38.2      16.3     54.5
[2->B] Aang, Zukko, Toph              52.1      29.4     81.5
[B->Z] Aang, Katara, Zukko, Toph     145.6      65.2    210.8
======================================================================
                        JORNADA CONCLUÍDA
  Tempo de deslocamento (A*):  281.20 min
  Tempo de batalhas:           125.60 min
  TEMPO TOTAL:                 406.80 min
======================================================================
```

---

## 📊 Fluxo Completo do Sistema

```
main.py::main()
  ↓
1. Carregar Mapa
  MapaAang("data/mapa.txt")
  └─ Matriz + Checkpoints
  ↓
2. Criar Agente
  AgenteAvatar(mapa)
  └─ Contexto de resolução
  ↓
3. Resolver Jornada
  agente.resolver_jornada_completa()
  ├─ Obter ordem: ['0', '1', '2', 'B', 'Z']
  │
  ├─ Otimizar alocação (Algoritmo Genético)
  │  └─ allocation.otimizar_alocacao_equipe()
  │     Retorna: alocacao_equipe
  │
  ├─ Para cada etapa:
  │  ├─ Calcular rota (A*)
  │  │  └─ astar.executar_a_estrela()
  │  │     Retorna: caminho_trecho, tempo_viagem
  │  │
  │  ├─ Calcular batalha
  │  │  ├─ Equipe = alocacao_equipe[etapa]
  │  │  ├─ Dificuldade = DIFICULDADES[etapa]
  │  │  ├─ Agilidade_total = Σ agilidade
  │  │  └─ Tempo = dificuldade / agilidade_total
  │  │
  │  └─ Compilar dados do trecho
  │
  ├─ Compilar caminho completo
  ├─ Imprimir relatório
  └─ Retornar (caminho_completo, log_jornada)
  ↓
4. Se sucesso:
  Criar GUI
  VisualizadorPygame(mapa, caminho, log)
  └─ gui.iniciar_loop()
  ↓
5. Interface Interativa
  Usuário pode:
  - Ver o caminho no mapa
  - Play/Pause animação
  - Ver metrics em tempo real
  - Visualizar tabela de etapas
```

---

## 📐 Estrutura do Log

Cada entrada do log corresponde a um trecho (etapa para etapa):

```python
log_jornada = [
    {
        "trecho": "0 -> 1",
        "equipe": "Aang, Katara",
        "delta_astar": 45.3,      # Tempo A* deste trecho
        "delta_comb": 14.7,       # Tempo batalha deste trecho
        "astar": 45.3,            # Acumulado A*
        "comb": 14.7              # Acumulado batalha
    },
    {
        "trecho": "1 -> 2",
        "equipe": "Sokka, Toph",
        "delta_astar": 38.2,
        "delta_comb": 16.3,
        "astar": 83.5,            # 45.3 + 38.2
        "comb": 31.0              # 14.7 + 16.3
    },
    # ... mais trechos
]
```

### Campos:
- **trecho**: Identificação do trecho (checkpoint origem → destino)
- **equipe**: Nomes dos personagens que lutam nesta etapa
- **delta_astar**: Tempo de viagem acumulado até aqui
- **delta_comb**: Tempo de batalha acumulado até aqui
- **astar**: Tempo **incremental** de A* deste trecho
- **comb**: Tempo **incremental** de batalha deste trecho

---

## 🔍 Tratamento de Erros

```python
if not caminho_trecho:
    print(f"ERRO: Caminho bloqueado entre '{chave_origem}' e '{chave_destino}'.")
    return [], []
```

Se A* não encontrar caminho entre dois checkpoints:
- Imprime mensagem de erro
- Retorna listas vazias
- main.py detecta falha e imprime "Falha ao calcular a jornada"

---

## 💡 Fórmula do Tempo Total

```
Tempo Total = Tempo_Viagens + Tempo_Batalhas

Onde:
  Tempo_Viagens = Σ tempo_a_estrela(checkpoint_i → checkpoint_i+1)
  Tempo_Batalhas = Σ (dificuldade[checkpoint_i] / agilidade_total[checkpoint_i])
```

**Exemplo Concreto:**
```
Etapas: 0 → 1 → 2 → B → Z

Viagens:
  0→1: 45.3 min (A*)
  1→2: 38.2 min (A*)
  2→B: 52.1 min (A*)
  B→Z: 145.6 min (A*)
  Total: 281.2 min

Batalhas:
  Em 1: 100 / (1.8+1.6) = 14.7 min
  Em 2: 80 / (1.4+1.6) = 26.7 min
  Em B: 150 / (1.8+1.6+1.6) = 29.4 min
  Em Z: 200 / (1.8+1.6+1.6+1.4) = 32.8 min
  Total: 125.6 min

TOTAL: 281.2 + 125.6 = 406.8 minutos (≈ 6 horas 47 min)
```

---

## 🎯 Saídas do Sistema

### Saída Textual (Console)
```
Inicializando sistema...
Mapa carregado: 50x40
Checkpoints encontrados: 26

Criando agente...

Calculando rotas e estratégias...
Gerando 20 indivíduos iniciais...
Gen   0: 8.5234 min (CPU: 2.3s)
...
Concluído: 7.8765 min (CPU: 72.1s)

Planejando estratégia de batalhas...

======================================================================
                         JORNADA DO AVATAR
...
```

### Saída Gráfica (GUI)
- Mapa com cores de terreno
- Caminho do avatar destacado
- Painel lateral com métricas
- Tabela de etapas na ordem de execução

### Dados Estruturados Retornados
```python
(caminho_completo, log_jornada)
# Usados pela GUI para visualizar e animar
```

---

## 📈 Complexidade Total

| Componente | Complexidade |
|-----------|------------|
| Carregar mapa | O(L × C) |
| Otimizar alocação (AG) | O(AG_POP × AG_GEN × HC_OPS) |
| A* (por trecho) | O(n × log n) |
| Processar etapas | O(checkpoints) |
| **Total** | **~Segundos a 2 minutos** |

Típicamente:
- Carregamento: <1s
- Algoritmo Genético: 30-120s
- A*: <1s por trecho
- Compilação: <1s

---

## 🎓 Fluxo de Dados

```
ENTRADA:
  data/mapa.txt
  constants.py (CONFIG_EQUIPE, DIFICULDADES)

PROCESSAMENTO:
  main() → MapaAang → AgenteAvatar
  resolver_jornada_completa():
    ├─ otimizar_alocacao_equipe() → alocacao
    ├─ executar_a_estrela() → caminho
    └─ Integrar dados → log
  
SAÍDA:
  caminho_completo: lista de (x,y)
  log_jornada: lista de dicts
  
VISUALIZAÇÃO:
  VisualizadorPygame(mapa, caminho, log)
  └─ Interface interativa com pygame
```

---

## 🚀 Para Executar

```bash
# Terminal no diretório do projeto
python main.py

# Alternativa com ambiente virtual
source venv/bin/activate
python main.py
```

---

## 📚 Integração com Módulos

| Módulo | Função | Entrada | Saída |
|--------|--------|---------|-------|
| **map_core** | Carregar estrutura | arquivo | matriz + checkpoints |
| **astar** | Buscar caminho | (x1,y1), (x2,y2) | caminho, custo |
| **allocation** | Otimizar equipe | dificuldades | alocacao, energia |
| **renderer** | Visualizar | mapa, caminho, log | interface interativa |

---

## 💭 Decisões de Design

1. **Separação Agent-Main**: Agent encapsula lógica, main apenas orquestra
2. **Relatório Textual**: Informa usuário antes da GUI abrir
3. **Log Estruturado**: GUI pode acessar dados específicos de cada etapa
4. **Falha Graceful**: Se A* falhar, retorna listas vazias em vez de crashes
5. **Padrão Entry Point**: Permite importar módulos sem executar código
