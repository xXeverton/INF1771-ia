# Documentação do Módulo de Alocação de Equipe (allocation.py)

## 📋 Visão Geral

O módulo `allocation.py` implementa um **Algoritmo Genético (AG)** para otimizar a alocação de personagens em etapas de batalha, minimizando o tempo total da missão.

### Objetivo Principal
Distribuir uma equipe de personagens entre diferentes etapas de batalha considerando:
- **Dificuldade de cada etapa** (custo em tempo)
- **Agilidade de cada personagem** (velocidade)
- **Energia disponível** (quantas etapas cada um pode participar)

---

## ⚙️ Parâmetros do Algoritmo Genético

```python
AG_POPULACAO = 20              # Número de indivíduos por geração
AG_GERACOES = 200              # Número máximo de gerações
AG_ELITE = 3                   # Número de melhores indivíduos preservados
AG_TAXA_CROSSOVER = 0.85       # Probabilidade de reprodução
AG_TAXA_MUTACAO = 0.40         # Probabilidade de mutação
AG_TAXA_MUTACAO_GENE = 0.35    # Probabilidade de mutar cada gene
AG_K_TORNEIO = 3               # Número de competidores no torneio
AG_SEED = 42                   # Semente para reprodutibilidade
AG_PARADA_ESTAGNACAO = 80      # Gerações sem melhora para parar
```

---

## 🔧 Funções Utilitárias

### 1. `_cromossomo_para_alocacao(cromossomo, etapas_batalha)`

**Propósito:** Converter representação do problema de **formato por personagem** para **formato por etapa**.

**Entrada:**
- `cromossomo`: Dict com personagem como chave e lista de etapas como valor
  ```python
  {"Aang": ["E1", "E3"], "Katara": ["E1", "E2"]}
  ```

**Saída:**
- `alocacao`: Dict com etapa como chave e lista de personagens como valor
  ```python
  {"E1": ["Aang", "Katara"], "E2": ["Katara"], "E3": ["Aang"]}
  ```

**Exemplo:**
```
Entrada:  Aang participa de E1 e E3, Katara de E1 e E2
Saída:    E1 tem [Aang, Katara], E2 tem [Katara], E3 tem [Aang]
```

---

### 2. `_calcular_fitness(cromossomo, etapas_batalha, config_equipe)`

**Propósito:** Avaliação da qualidade de uma solução (quanto menor, melhor).

**Fórmula:**
```
fitness = Σ (dificuldade_etapa / agilidade_total_etapa)
```

**Passos:**
1. Converte cromossomo para alocação por etapa
2. Para cada etapa:
   - Soma agilidade de todos personagens presentes
   - Calcula tempo: dificuldade / agilidade
   - Acumula no fitness total
3. Retorna penalidade infinita se agilidade for 0

**Exemplo:**
```
Etapa E1: dificuldade=100, personagens=[Aang(ag=50), Katara(ag=40)]
Tempo_E1 = 100 / (50+40) = 100/90 ≈ 1.11 minutos

Etapa E2: dificuldade=80, personagens=[Katara(ag=40)]
Tempo_E2 = 80 / 40 = 2.0 minutos

Fitness total = 1.11 + 2.0 = 3.11 minutos
```

---

### 3. `_gerar_individuo_aleatorio(etapas_batalha, config_equipe, pers_por_agilidade, seed)`

**Propósito:** Criar solução inicial usando heurística de **benefício marginal**.

**Fase 1 - Alocação Básica:**
1. Ordena personagens por agilidade (com ruído aleatório)
2. Para cada etapa (ordenada por dificuldade):
   - Aloca o personagem com mais agilidade disponível
   - Decrementa energia desse personagem

**Fase 2 - Distribuição Inteligente:**
1. Enquanto houver energia disponível:
   - Para cada etapa sem esse personagem:
     - Calcula benefício marginal: tempo_antes - tempo_depois
   - Aloca personagem que trará maior benefício

**Exemplo:**
```
Etapa E1: dificuldade=100
- Antes: equipe=[Aang(50)], tempo = 100/50 = 2.0
- Depois: equipe=[Aang(50), Katara(40)], tempo = 100/90 ≈ 1.11
- Benefício marginal = 2.0 - 1.11 = 0.89 minutos economizados
```

---

## 🧬 Operadores Genéticos

### 4. `_busca_local_completa(cromossomo_entrada, etapas_batalha, config_equipe)`

**Propósito:** Otimização local (Hill Climbing) após criar cada solução.

**Operação SWAP:**
1. Tenta trocar personagens entre duas etapas diferentes
2. Se as etapas forem diferentes, permite a troca:
   - Aang sai de E1 e entra em E3
   - Katara sai de E3 e entra em E1
3. Mantém melhoria se fitness diminuir

**Operação MOVE:**
1. Move um personagem de uma etapa para outra
2. Só permite se a etapa de origem tiver mais de 1 personagem
3. Útil para equilibrar carga

**Exemplo:**
```
Antes: E1=[Aang, Katara], E2=[Sokka]
SWAP: Katara <-> Sokka
Depois: E1=[Aang, Sokka], E2=[Katara]
Fitness melhorou? Se sim, mantém!
```

**Loop:**
- Tenta até não conseguir melhorias
- Garante solução localmente ótima

---

### 5. `_crossover(pai1, pai2, etapas_batalha, config_equipe, pers_por_agilidade)`

**Propósito:** Reprodução - combinar duas boas soluções para gerar descendente.

**Passo 1 - Crossover de Ponto:**
1. Escolhe ponto de corte aleatório nas etapas
2. Filho herda etapas 1 até ponto do pai1
3. Filho herda etapas após ponto do pai2

**Exemplo:**
```
Etapas: [E1, E2, E3, E4, E5]
Ponto de corte: 2

Pai1: E1[Aang,Katara], E2[Sokka], E3[Aang], E4[Katara], E5[Sokka]
Pai2: E1[Katara], E2[Aang,Sokka], E3[Katara,Sokka], E4[Aang], E5[Katara]

Filho: E1[Aang,Katara], E2[Sokka], E3[Katara,Sokka], E4[Aang], E5[Katara]
       ↑ de Pai1      ↑ de Pai1   ↑ de Pai2            ↑ de Pai2
```

**Passo 2 - Reparo de Energia:**
1. Verifica se cada personagem excedeu sua energia
2. Remove personagens de etapas com múltiplas alocações
3. Se persistir violação, remove de qualquer etapa

**Passo 3 - Distribuição de Energia Restante:**
- Usa mesma heurística de benefício marginal
- Aloca personagens que melhoram mais o fitness

---

### 6. `_mutacao(cromossomo_entrada, etapas_batalha, config_equipe)`

**Propósito:** Introduzir variabilidade genética.

**Processo:**
1. Para cada personagem:
   - Se random() > taxa_mutacao_gene: pula
   - Senão, tira de uma etapa que permite (com múltiplos personagens)
   - E aloca em uma etapa sem ele

**Exemplo:**
```
Personagem Aang: [E1, E3, E5]
Etapas onde pode sair (múltiplos personagens): [E1, E5]
Etapas onde pode entrar (não está): [E2, E4]

Escolhe: sai de E1, entra em E2
Resultado: [E2, E3, E5]
```

---

### 7. `_torneio(fitness_valores, k)`

**Propósito:** Seleção dos pais para reprodução.

**Processo:**
1. Escolhe K indivíduos aleatoriamente
2. Retorna o com MENOR fitness (melhor)

**Exemplo:**
```
Fitness: [5.2, 3.8, 4.1, 2.9, 6.1]
K = 3

Candidatos sorteados: posições [0, 3, 4]
Fitness dos candidatos: [5.2, 2.9, 6.1]
Vencedor: posição 3 (fitness 2.9 = melhor)
```

---

## 🎯 Função Principal

### 8. `otimizar_alocacao_equipe(dificuldades_etapas, config_equipe, verbose=True)`

**Propósito:** Orquestradora do algoritmo genético completo.

**Entrada:**
```python
dificuldades_etapas = {
    "E1": 100,
    "E2": 80,
    "E3": 120
}

config_equipe = {
    "Aang": {"agilidade": 50, "energia": 3},
    "Katara": {"agilidade": 40, "energia": 2},
    "Sokka": {"agilidade": 35, "energia": 2}
}
```

---

## 📊 Fluxo Completo do Algoritmo

```
┌─ INICIALIZAÇÃO
│  ├─ Define seed para reprodutibilidade
│  ├─ Filtra etapas com dificuldade > 0
│  └─ Ordena personagens por agilidade
│
├─ POPULAÇÃO INICIAL (20 indivíduos)
│  ├─ Gera cada um via heurística de benefício marginal
│  ├─ Aplica busca local completa (Hill Climbing)
│  └─ Ordena por fitness (melhor primeiro)
│
├─ LOOP GENÉTICO (até 200 gerações)
│  ├─ Seleciona elite (3 melhores)
│  │
│  ├─ REPRODUÇÃO (preenche população até 20)
│  │  ├─ Seleciona 2 pais por torneio
│  │  ├─ Com 85% prob: realiza crossover
│  │  ├─ Com 40% prob: realiza mutação
│  │  └─ Aplica Hill Climbing no filho
│  │
│  ├─ Ordena nova população por fitness
│  │
│  ├─ Se melhorou: reseta contador de estagnação
│  │  Senão: incrementa contador
│  │
│  └─ Se 80 gerações sem melhora: PARA
│
└─ SAÍDA
   ├─ Melhor solução encontrada
   └─ Energias restantes não utilizadas
```

---

## 📈 Exemplo de Execução

```
Gerando 20 indivíduos iniciais...

Gen   0: 8.5234 min (CPU: 2.3s)
Gen   5: 8.1567 min (CPU: 5.1s)
Gen  15: 7.9234 min (CPU: 12.3s)
Gen  28: 7.8901 min (CPU: 19.8s)
Gen  50: 7.8765 min (CPU: 35.2s)
Parada por estagnação na geração 130.

Concluído: 7.8765 min (CPU: 72.1s)
```

---

## 🔍 Representação da Solução

**Cromossomo (Representação Interna):**
```python
{
    "Aang": ["E1", "E3"],
    "Katara": ["E1", "E2"],
    "Sokka": ["E2", "E3"]
}
```
*Lê-se: Aang participa de E1 e E3, Katara de E1 e E2, etc.*

**Alocação (Representação Externa):**
```python
{
    "E1": ["Aang", "Katara"],
    "E2": ["Katara", "Sokka"],
    "E3": ["Aang", "Sokka"]
}
```
*Lê-se: Etapa E1 tem Aang e Katara, E2 tem Katara e Sokka, etc.*

---

## 🎓 Conceitos-Chave

| Conceito | Explicação |
|----------|-----------|
| **Fitness** | Medida de qualidade (tempo total). Menor = melhor |
| **Cromossomo** | Representação de uma solução |
| **Geração** | Uma iteração do algoritmo |
| **Elite** | Melhores indivíduos preservados automaticamente |
| **Crossover** | Combina características de dois pais |
| **Mutação** | Altera aleatoriamente um indivíduo |
| **Torneio** | Seleção competitiva dos pais |
| **Hill Climbing** | Otimização local via pequenas melhorias |
| **Estagnação** | Quando o algoritmo não consegue melhorar |

---

## 💡 Por Que Esse Design?

1. **Algoritmo Genético**: Problema é NP-difícil, AG é eficiente
2. **Hill Climbing**: Garante cada solução é localmente ótima
3. **Benefício Marginal**: Inicializa com soluções racionalmente boas
4. **Torneio de 3**: Equilibra exploração e explotação
5. **Elite**: Evita perder boas soluções
6. **Parada por Estagnação**: Economia de tempo sem perder qualidade

---

## 📝 Tempo Computacional

- **População inicial**: ~2-3 segundos
- **Por geração**: ~0.5 segundos
- **Total típico**: 60-120 segundos
- **Melhora típica**: 20-30% vs alocação aleatória
