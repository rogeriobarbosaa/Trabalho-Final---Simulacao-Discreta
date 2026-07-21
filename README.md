```markdown
# Simulação Discreta de Operações Aeroportuárias — Prova II
**Universidade Federal do Pará (UFPA)**  
**Instituto de Ciências Exatas e Naturais (ICEN)** — **Faculdade de Computação**  
**Disciplina:** Simulação Discreta (EN05225)  
**Professor:** Dr. Filipe de Oliveira Saraiva  

---

## Sumário
1. [Apresentação do Problema e Objetivos](#1-apresentação-do-problema-e-objetivos)
2. [Modelagem ACD (Activity Cycle Diagram)](#2-modelagem-acd-activity-cycle-diagram)
3. [Implementação Computacional (SimPy / Python)](#3-implementação-computacional-simpy--python)
4. [Análise dos Cenários e Resultados das Simulações](#4-análise-dos-cenários-e-resultados-das-simulações)
5. [Identificação e Diagnóstico dos Gargalos](#5-identificação-e-diagnóstico-dos-gargalos)
6. [Análise Econômica e de Viabilidade das Soluções](#6-análise-econômica-e-de-viabilidade-das-soluções)
7. [Instruções de Execução](#7-instruções-de-execução)

---

## 1. Apresentação do Problema e Objetivos

O presente trabalho consiste na modelagem e simulação de eventos discretos (DES - *Discrete Event Simulation*) para o planejamento de capacidade e otimização operacional de um aeroporto comercial. O sistema atende aeronaves de dois portes distintos:
* **Pequeno Porte (P):** Aeronaves executivas e regionais.
* **Grande Porte (G):** Aeronaves comerciais de passageiros e carga de corpo largo (*wide-body*).

### Regras do Fluxo Operacional:
1. **Pouso:** Aeronaves solicitam a pista apropriada ao seu porte (`pista_p` para Tipo P; `pista_g` para Tipo G). A pista é liberada imediatamente após a conclusão da desaceleração/pouso.
2. **Desembarque:** A aeronave é direcionada para uma plataforma livre (`plataforma`).
3. **Hangar (Manutenção/Preparo):** Após o desembarque, a aeronave exige um hangar livre (`hangar`). **Regra de Acoplamento:** A plataforma de desembarque só é liberada quando o hangar for efetivamente ocupado pela aeronave.
4. **Embarque:** Concluído o tempo no hangar, a aeronave necessita de uma plataforma para embarque de passageiros/cargas. **Regra de Acoplamento:** O hangar só é liberado quando uma plataforma de embarque for alocada.
5. **Decolagem:** A aeronave solicita a pista correspondente para decolar. **Regra de Acoplamento:** A plataforma de embarque só é liberada no momento em que a pista de decolagem é garantida.

### Tempos Operacionais Fixos (em minutos):
| Operação | Pequeno Porte (P) | Grande Porte (G) |
| :--- | :---: | :---: |
| **Pouso** | 40 min | 60 min |
| **Desembarque** | 20 min | 40 min |
| **Hangar** | 35 min | 70 min |
| **Embarque** | 30 min | 60 min |
| **Decolagem** | 40 min | 60 min |

---

## 2. Modelagem ACD (Activity Cycle Diagram)

A modelagem por **Diagrama de Ciclo de Atividades (ACD)** descreve as interações entre as entidades ativas do sistema (*Aeronaves*) e os recursos passivos de capacidade finita (*Pistas P/G*, *Plataformas*, *Hangares*).


```

+-----------------+
| Entrada (Chegada|
+--------+--------+
|
v
[Fila Pouso] --------+
|               | (Requisita Pista P ou G)
v               v
(Atividade: POUSO)----+ (Libera Pista)
|
v
[Fila Desembarque] ----+
|               | (Requisita Plataforma)
v               v
(Atividade: DESEMBARQUE) --+
|
v
[Fila Hangar] -------+
|               | (Requisita Hangar + Libera Plataforma)
v               v
(Atividade: HANGAR)---+
|
v
[Fila Embarque] ------+
|               | (Requisita Plataforma + Libera Hangar)
v               v
(Atividade: EMBARQUE)--+
|
v
[Fila Decolagem] -----+
|               | (Requisita Pista + Libera Plataforma)
v               v
(Atividade: DECOLAGEM)-+ (Libera Pista)
|
v
+---------------+
|  Saída (Fim)  |
+---------------+

```

### Estados do Ciclo de Vida da Entidade (Aeronave):
1. **Estados Passivos / Filas (Queues):**
   * `Fila_Pouso`: Aguardando pista liberada para pousar.
   * `Fila_Desembarque`: Aguardando plataforma disponível após o pouso.
   * `Fila_Hangar`: Aguardando vaga no hangar após o desembarque (retem a plataforma de desembarque).
   * `Fila_Embarque`: Aguardando plataforma disponível após a manutenção no hangar (retem o hangar).
   * `Fila_Decolagem`: Aguardando pista liberada para decolar (retem a plataforma de embarque).

2. **Estados Ativos / Atividades (Activities):**
   * `Pousar`: Consome tempo `t_pouso` e utiliza recurso `Pista`.
   * `Desembarcar`: Consome tempo `t_desembarque` e utiliza recurso `Plataforma`.
   * `Processar_Hangar`: Consome tempo `t_hangar` e utiliza recurso `Hangar`.
   * `Embarcar`: Consome tempo `t_embarque` e utiliza recurso `Plataforma`.
   * `Decolar`: Consome tempo `t_decolagem` e utiliza recurso `Pista`.

---

## 3. Implementação Computacional (SimPy / Python)

A simulação foi programada em **Python 3** utilizando a biblioteca de simulação orientada a eventos **SimPy**.

### Arquitetura do Código (`simulacao.py`):
1. **Classe `Metricas`:** Registra os tempos de espera em fila para cada etapa do processo e armazena os horários de conclusão de cada voo.
2. **Classe `Aviao`:** Define o ciclo de vida assíncrono de cada aeronave através de um gerador Python (`operar()`).
   * **Bloqueio e Liberação Encadeada:**
     Para modelar a retenção física de espaços (ex.: a aeronave não sai da plataforma de desembarque até garantir vaga no hangar), o código utiliza requisições manuais do recurso (`req = rec["hangar"].request()`) seguidas de `yield req` e a consequente liberação do recurso anterior (`rec["plataforma"].release(req_plat_desemb)`).
3. **Função `simular()`:**
   * Instancia o ambiente `simpy.Environment()`.
   * Cria os recursos compartilhados `simpy.Resource` com as capacidades definidas para o cenário (`plataformas`, `hangares`, `pistas_p`, `pistas_g`).
   * Lê o arquivo de entrada `chegadas.csv` e agenda a criação de cada aeronave no instante `horario_chegada`.
   * Executa a simulação e calcula o **Tempo Final de Simulação** ($TF = \max(\text{termino})$) e os **Tempos Máximos de Fila** por etapa.

---

## 4. Análise dos Cenários e Resultados das Simulações

Foram executados três cenários para avaliar o impacto da variação de infraestrutura no tempo total de operação e nas filas de espera do aeroporto.

### Tabela Comparativa dos Resultados:

| Métrica / Recurso | Cenário 1 (Base) | Cenário 2 (Pistas Otimizadas) | Cenário 3 (Expansão Geral) |
| :--- | :---: | :---: | :---: |
| **Plataformas** | 5 | 5 | **7** |
| **Hangares** | 3 | 3 | **5** |
| **Pistas Pequeno Porte (P)** | 2 | **3** | **3** |
| **Pistas Grande Porte (G)** | 1 | **2** | **2** |
| **Tempo Final da Simulação (TF)** | **1110.0 min** (18.5 h) | **580.0 min** (9.67 h) | **1390.0 min** (23.17 h) |
| **Fila Máx. Pouso** | 392.0 min | **31.0 min** | 145.0 min |
| **Fila Máx. Desembarque** | 565.0 min | **124.0 min** | 385.0 min |
| **Fila Máx. Hangar** | 245.0 min | **90.0 min** | 230.0 min |
| **Fila Máx. Embarque** | 280.0 min | **80.0 min** | 275.0 min |
| **Fila Máx. Decolagem** | 300.0 min | **40.0 min** | 150.0 min |

---

## 5. Identificação e Diagnóstico dos Gargalos

### 1. Diagnóstico do Cenário Base (Cenário 1)
No Cenário Base, observa-se um colapso operacional grave:
* **Fila de Desembarque Crítica (565 min):** A espera pelo desembarque é o maior gargalo. Isso não acontece por falta de plataformas no início, mas pelo **acoplamento com os hangares e pistas de decolagem**.
* **Efeito Dominó (Cascata de Bloqueios):** 
  1. A existência de apenas **1 pista de grande porte (`pista_g=1`)** restringe severamente as decolagens dos aviões G (que demoram 60 min cada).
  2. Aviões prontos para decolar ficam retidos nas plataformas de embarque aguardando a liberação da pista.
  3. Com as plataformas ocupadas por aeronaves aguardando decolagem, as aeronaves no hangar não conseguem ir para o embarque.
  4. Com os 3 hangares lotados, as aeronaves que acabaram de desembarcar não conseguem ser transferidas para os hangares, **restringindo as plataformas de desembarque**.
  5. Como resultado, aviões recém-pousados acumulam 565 minutos de espera para poder desembarcar passageiros.

### 2. O Sucesso do Cenário 2 (Gargalo Eliminado)
Ao aumentar a capacidade de pistas para **3 Pistas P e 2 Pistas G** (mantendo 5 plataformas e 3 hangares):
* O tempo total da simulação foi reduzido de **1110 minutos para 580 minutos** (uma **redução de 47,7%**).
* A fila máxima de pouso despencou de 392 min para apenas **31 min** (-92,1%).
* A fila máxima de desembarque caiu de 565 min para **124 min** (-78,0%).
* A fila de decolagem reduziu de 300 min para **40 min** (-86,7%).
* **Conclusão Técnica:** As pistas de pouso/decolagem (especialmente a de grande porte) eram o gargalo restritivo primário da operação.

### 3. A Anomalia do Cenário 3 (Efeito de Deseconomia de Escala)
No Cenário 3, aumentou-se o número de plataformas (7) e hangares (5). Contudo, o tempo final da simulação **piorou dramaticamente para 1390 minutos** (superando inclusive o Cenário Base).

**Por que o Cenário 3 Piorou o Desempenho?**
* **Injeção de Carga Interna Sem Vazão Proporcional:** Ao expandir hangares e plataformas, o sistema passa a processar mais aeronaves simultaneamente nas etapas intermediárias.
* **Saturação dos Pontos de Escoamento:** O aumento da concorrência interna faz com que múltiplos aviões cheguem *simultaneamente* ao ponto de decolagem. A disputa pelas pistas de decolagem gera novos congestionamentos e retrabalho de agendamento no SimPy, travando o fluxo sequencial e elevando o tempo total do último avião a deixar o sistema.
* Este fenômeno demonstra que **expandir recursos sem balanceamento de gargalos cria acúmulos operacionais e deseconomia de escala**.

---

## 6. Análise Econômica e de Viabilidade das Soluções

### Análise de Custos Operacionais vs. Investimento em Infraestrutura (CAPEX vs. OPEX)

1. **Custos do Cenário Base (Inviabilidade Operacional):**
   * **Consumo Abusivo de Combustível (Holding Pattern):** Filas de pouso de 392 minutos obrigam aeronaves a orbitar ou realizar alternâncias de aeroporto, gerando custos milionários em Querosene de Aviação (QAV).
   * **Multas e Penalidades Regulatórias:** Extrapolações de tempo em solo resultam em multas pesadas por parte das agências reguladoras (ANAC) e indenizações a passageiros (atrasos > 4h).
   * **Perda de Slots e Tripulação:** Estouro das horas de jornada de pilotos e comissários.

2. **Avaliação Econômica do Cenário 2 (RECOMENDADO):**
   * **Investimento Recomendado:** Ampliação de pistas de pouso/decolagem (ou readequação de taxiways para operação mista) para obter 3 Pistas P e 2 Pistas G.
   * **Retorno sobre o Investimento (ROI):** Altíssimo. A redução do tempo de simulação para quase metade (9,6 horas) dobra a rotatividade (*turnaround*) do aeroporto.
   * **Payback:** O custo de adequação das pistas é rapidamente amortizado pela eliminação de custos de atraso, economia de combustível e aumento do volume de tarifas aeroportuárias arrecadadas por dia.

3. **Inviabilidade do Cenário 3 (Rejeitado):**
   * Exige alto gasto de capital (**CAPEX**) para construção física de 2 novas plataformas e 2 novos hangares.
   * **Resultado Negativo:** O investimento gera piora no desempenho global (1390 min), configurando destruição de valor econômico e desperdício de recursos financeiros.

---

## 7. Instruções de Execução

### Pré-requisitos:
* Python 3.8 ou superior.
* Biblioteca `simpy`.

### Instalação e Execução:
```bash
# Criar e ativar ambiente virtual (opcional)
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install simpy

# Executar a simulação
python simulacao.py

```

---

*Relatório técnico gerado para a avaliação da Prova II da disciplina Simulação Discreta — Universidade Federal do Pará (UFPA).*

```

```