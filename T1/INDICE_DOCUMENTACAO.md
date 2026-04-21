# 📚 Guia Completo de Documentação - Projeto Avatar Path

## 🎯 Bem-vindo!

Este é um guia completo que explica **cada passo** do código do projeto Avatar Path (INF1771). O projeto implementa um sistema de otimização de rotas e alocação de equipe usando Algoritmos Genéticos e A*.

---

## 📖 Arquivos de Documentação

### 1. **DOCUMENTACAO_ALLOCATION.md** 
**Algoritmo Genético para Otimização de Equipe**

📍 Arquivo correspondente: `algorithms/allocation.py`

**O que você vai aprender:**
- Como o Algoritmo Genético trabalha
- Funções de fitness e seleção
- Operadores genéticos (crossover, mutação)
- Busca local (Hill Climbing)
- Fórmula para calcular tempo de batalha

**Quando ler:**
- ✅ Quer entender otimização de equipes
- ✅ Precisa saber como o AG distribui personagens
- ✅ Quer aprender sobre evolução algoritmos

**Tempo de leitura:** 15-20 minutos

---

### 2. **DOCUMENTACAO_ASTAR.md**
**Algoritmo A* para Busca de Caminho**

📍 Arquivo correspondente: `algorithms/astar.py`

**O que você vai aprender:**
- O algoritmo A* passo-a-passo
- Classe Nó e fila de prioridade
- Heurística de Manhattan
- Por que A* é melhor que Dijkstra
- Exemplo prático detalhado com grid

**Quando ler:**
- ✅ Quer entender busca de caminhos
- ✅ Precisa saber como encontrar rotas ótimas
- ✅ Quer aprender sobre heurísticas

**Tempo de leitura:** 10-15 minutos

---

### 3. **DOCUMENTACAO_MAPA.md**
**Carregamento e Gerenciamento do Mapa**

📍 Arquivos correspondentes: `map/map_core.py` + `map/constants.py`

**O que você vai aprender:**
- Estrutura do mapa (matriz 2D)
- Custos de terrenos
- Dificuldades de etapas
- Configuração da equipe (energia e agilidade)
- Métodos de exploração do mapa
- Formato do arquivo mapa.txt

**Quando ler:**
- ✅ Quer entender a estrutura de dados
- ✅ Precisa modificar custos de terreno
- ✅ Quer adicionar novos checkpoints
- ✅ Quer alterar configuração da equipe

**Tempo de leitura:** 12-18 minutos

---

### 4. **DOCUMENTACAO_ORQUESTRADOR.md**
**Sistema Principal de Resolução**

📍 Arquivos correspondentes: `main.py` + `entities/agent.py`

**O que você vai aprender:**
- Fluxo completo do programa
- Como main.py inicializa tudo
- Como AgenteAvatar orquestra a solução
- Integração de A* + Algoritmo Genético
- Estrutura do log da jornada
- Fórmula do tempo total

**Quando ler:**
- ✅ Quer entender o fluxo geral
- ✅ Precisa saber como tudo se conecta
- ✅ Quer entender a entrada e saída do sistema
- ✅ Quer modificar a lógica principal

**Tempo de leitura:** 15-20 minutos

---

## 🗺️ Mapa Conceitual

```
                    PROJETO AVATAR PATH
                            |
                ┌───────────┼───────────┐
                |           |           |
            ENTRADA     PROCESSAMENTO  SAÍDA
            |           |           |
    ┌───────────────────────────────────────┐
    │ Arquivo: data/mapa.txt                │
    │ ├─ Matriz de terrenos                 │
    │ └─ Checkpoints (etapas)               │
    └───────────────────────────────────────┘
                    |
                    ↓
        ┌─────────────────────────────┐
        │   MapaAang (map_core.py)    │
        │   └─ Estrutura de dados     │
        └─────────────────────────────┘
                    |
                    ↓
        ┌─────────────────────────────┐
        │  AgenteAvatar (agent.py)    │
        │  └─ Orquestrador            │
        └─────────────────────────────┘
              |                 |
              ↓                 ↓
    ┌──────────────────┐  ┌──────────────────────────┐
    │  A* (astar.py)   │  │  AG (allocation.py)      │
    │  └─ Rota ótima   │  │  └─ Equipe ótima         │
    │                  │  │                          │
    │ Entrada: 2 pontos│  │ Entrada: Dificuldades    │
    │ Saída: caminho   │  │ Saída: alocacao_equipe   │
    └──────────────────┘  └──────────────────────────┘
              |                 |
              └─────────┬───────┘
                        |
                        ↓
    ┌─────────────────────────────────────────┐
    │    Log Integrado (agent.py)             │
    │    ├─ Cada trecho processado            │
    │    ├─ Tempos acumulados                 │
    │    └─ Equipe alocada por etapa          │
    └─────────────────────────────────────────┘
                        |
                        ↓
    ┌─────────────────────────────────────────┐
    │  VisualizadorPygame (gui/renderer.py)   │
    │  └─ Interface interativa                │
    └─────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Execução

```
1. main.py - Inicializa
   ↓
2. MapaAang - Carrega data/mapa.txt
   ↓
3. AgenteAvatar - Cria contexto
   ↓
4. resolver_jornada_completa():
   ├─ allocation.otimizar_alocacao_equipe()
   │  └─ Resultado: quem participa de cada etapa
   │
   └─ Para cada checkpoint adjacente:
      ├─ astar.executar_a_estrela()
      │  └─ Resultado: caminho do ponto A ao B
      │
      ├─ Calcula tempo de batalha
      │  └─ tempo = dificuldade / agilidade_total
      │
      └─ Compila dados em log
   ↓
5. main.py - Se sucesso:
   ├─ Cria VisualizadorPygame
   └─ Inicia loop interativo
   ↓
6. GUI - Usuário interage com:
   ├─ Play/Pause animação
   ├─ Ver métricas
   ├─ Tabela de etapas
   └─ Legenda do mapa
```

---

## 📚 Ordem de Leitura Recomendada

### **Iniciante (Entender o que é o projeto)**
```
1. DOCUMENTACAO_ORQUESTRADOR.md  ← Começar aqui!
   └─ Visão geral do sistema
   
2. DOCUMENTACAO_MAPA.md
   └─ Entender estrutura de dados
   
3. DOCUMENTACAO_ASTAR.md
   └─ Aprender sobre buscas
   
4. DOCUMENTACAO_ALLOCATION.md
   └─ Aprender sobre otimização
```

### **Desenvolvedor (Modificar o código)**
```
1. DOCUMENTACAO_MAPA.md         ← Começar aqui!
   └─ Estrutura de dados
   
2. DOCUMENTACAO_ALLOCATION.md
   └─ Alterar AG ou heurística
   
3. DOCUMENTACAO_ASTAR.md
   └─ Alterar busca de caminho
   
4. DOCUMENTACAO_ORQUESTRADOR.md
   └─ Integrar mudanças
```

### **Debugger (Encontrar problemas)**
```
1. DOCUMENTACAO_ORQUESTRADOR.md ← Começar aqui!
   └─ Entender o fluxo
   
2. Arquivo com erro específico
   └─ Ler documentação correspondente
   
3. Usar exemplos práticos
   └─ Simular inputs/outputs
```

---

## 🎓 Conceitos Principais por Módulo

### **allocation.py**
```
Conceitos-chave:
  • Cromossomo = representação de solução
  • Fitness = qualidade (menor = melhor)
  • Crossover = combinar pais
  • Mutação = alterar aleatoriamente
  • Hill Climbing = otimização local
  • Elite = preservar melhores
  • Estagnação = parada antecipada
```

### **astar.py**
```
Conceitos-chave:
  • f(n) = g(n) + h(n)
  • g(n) = custo real
  • h(n) = custo estimado (heurística)
  • Manhattan = distância ortogonal
  • Fila de Prioridade = min-heap
  • Admissibilidade = h ≤ custo real
  • Optimialidade = melhor solução garantida
```

### **map_core.py / constants.py**
```
Conceitos-chave:
  • Matriz 2D = representação do mapa
  • Custo de Terreno = tempo por célula
  • Dificuldade = desafio da etapa
  • Checkpoint = ponto de interesse
  • Energia = limite de participações
  • Agilidade = velocidade de combate
  • Vizinhos Válidos = exploração do mapa
```

### **main.py / agent.py**
```
Conceitos-chave:
  • Orquestração = coordenar módulos
  • Integração = combinar resultados
  • Log Estruturado = rastrear dados
  • Entry Point = início do programa
  • Falha Graceful = tratar erros
  • Fórmula do Tempo = viagem + batalha
```

---

## 🔍 Perguntas Comuns

### **P: Como funciona o Algoritmo Genético?**
→ Ver: **DOCUMENTACAO_ALLOCATION.md** → Seção "Fluxo Completo"

### **P: Por que A* é mais rápido que Dijkstra?**
→ Ver: **DOCUMENTACAO_ASTAR.md** → Seção "Comparação: A* vs Dijkstra"

### **P: Qual é o custo de cada terreno?**
→ Ver: **DOCUMENTACAO_MAPA.md** → Seção "Custos de Terreno"

### **P: Como alterar a configuração da equipe?**
→ Ver: **DOCUMENTACAO_MAPA.md** → Seção "Configuração da Equipe"

### **P: Como é calculado o tempo total?**
→ Ver: **DOCUMENTACAO_ORQUESTRADOR.md** → Seção "Fórmula do Tempo Total"

### **P: Por que checkpoints têm dificuldades diferentes?**
→ Ver: **DOCUMENTACAO_MAPA.md** → Seção "Dificuldades das Etapas"

### **P: Como a GUI mostra o caminho?**
→ Ver: **DOCUMENTACAO_ORQUESTRADOR.md** → Seção "Saídas do Sistema"

---

## 🛠️ Modificações Comuns

### **Quer alterar o tamanho da população de AG?**
```
DOCUMENTACAO_ALLOCATION.md
└─ constants.py, buscar AG_POPULACAO
   Padrão: 20
   Aumentar → Mais preciso, mais lento
   Diminuir → Mais rápido, menos preciso
```

### **Quer alterar custos de terreno?**
```
DOCUMENTACAO_MAPA.md
└─ map/constants.py, CUSTOS_TERRENO
   Aumentar custo → Terreno mais caro
   Diminuir custo → Terreno mais barato
```

### **Quer adicionar novo personagem?**
```
DOCUMENTACAO_MAPA.md
└─ map/constants.py, CONFIG_EQUIPE
   Adicionar novo dict com energia e agilidade
```

### **Quer alterar heurística de A*?**
```
DOCUMENTACAO_ASTAR.md
└─ algorithms/astar.py, distancia_manhattan()
   Mudar função de cálculo h
```

---

## 📊 Estatísticas do Projeto

```
Linhas de Código:
  • allocation.py: ~350 linhas
  • astar.py: ~70 linhas
  • map_core.py: ~70 linhas
  • main.py: ~30 linhas
  • agent.py: ~100 linhas
  • TOTAL: ~620 linhas

Complexidade Temporal:
  • Carregar mapa: O(L×C)
  • A* por trecho: O(n log n)
  • Algoritmo Genético: O(AG_POP × AG_GEN × HC)
  • Total típico: 1-2 minutos

Complexidade Espacial:
  • Mapa: O(L×C)
  • Fila A*: O(L×C)
  • População AG: O(AG_POP × personagens)
```

---

## 🎯 Checklist de Aprendizado

Teste seus conhecimentos:

- [ ] Você consegue explicar o que é fitness?
- [ ] Você sabe por que A* usa heurística?
- [ ] Você entende como Manhattan distance funciona?
- [ ] Você sabe qual é o custo de atravessar água?
- [ ] Você consegue calcular tempo de batalha manualmente?
- [ ] Você entende como crossover funciona?
- [ ] Você sabe o que é estagnação em AG?
- [ ] Você consegue rastrear o fluxo completo do programa?
- [ ] Você sabe qual é a entrada e saída de cada módulo?
- [ ] Você entende como o log é estruturado?

Se respondeu ✓ para 8+, parabéns! 🎉 Você entende o projeto!

---

## 📞 Estrutura das Documentações

Cada documento segue este padrão:

```
1. Visão Geral
   └─ O que é e por que existe

2. Conceitos Fundamentais
   └─ Teoria necessária para entender

3. Classes/Funções
   └─ Explicação de cada componente

4. Fluxo Passo-a-Passo
   └─ Como tudo funciona junto

5. Exemplos Práticos
   └─ Casos reais com números

6. Integração
   └─ Como conecta com outros módulos

7. Checklist/Referência
   └─ Resumo e quick-reference
```

---

## 🚀 Próximos Passos

### **Depois de ler tudo:**

1. **Estude o código real**
   - Abra os arquivos .py
   - Correlacione com documentação
   - Tente entender cada linha

2. **Execute o programa**
   ```bash
   python main.py
   ```
   - Observe outputs
   - Compare com exemplos da doc

3. **Modifique pequenas coisas**
   - Altere AG_POPULACAO
   - Mude custos de terreno
   - Observe impacto

4. **Implemente melhorias**
   - Adicione novo terreno
   - Otimize Hill Climbing
   - Mude heurística A*

---

## 📝 Resumo Rápido

| Módulo | Faz | Usa | Retorna |
|--------|-----|-----|---------|
| **astar.py** | Busca caminho | Mapa, coords | Caminho, custo |
| **allocation.py** | Aloca equipe | Dificuldades, equipe | Alocação, energia |
| **map_core.py** | Gerencia mapa | Arquivo | Matriz, checkpoints |
| **main.py** | Inicializa | Todos acima | GUI interativa |
| **agent.py** | Orquestra | Todos acima | Log estruturado |

---

## 📚 Recursos Externos

- **Algoritmo A***: https://en.wikipedia.org/wiki/A*_search_algorithm
- **Algoritmo Genético**: https://en.wikipedia.org/wiki/Genetic_algorithm
- **Distância Manhattan**: https://en.wikipedia.org/wiki/Taxicab_geometry
- **Python Heapq**: https://docs.python.org/3/library/heapq.html

---

## 🎓 Conclusão

Agora você tem documentação completa de cada módulo! 

**Recomendação:** Leia na ordem sugerida e volte sempre que tiver dúvidas.

**Bom estudo!** 🚀

```
┌──────────────────────────────────┐
│  Avatar Path - Sistema Otimizado │
│  ├─ Rota: A* ✓                   │
│  ├─ Equipe: AG ✓                 │
│  ├─ Visualização: Pygame ✓       │
│  └─ Documentação: Completa ✓     │
└──────────────────────────────────┘
```
