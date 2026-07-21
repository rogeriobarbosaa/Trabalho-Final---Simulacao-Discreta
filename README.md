# Relatório de Simulação Discreta — Operações Aeroportuárias (Prova II)

**Universidade Federal do Pará (UFPA)**[cite: 5]  
**Instituto de Ciências Exatas e Naturais (ICEN)** — **Faculdade de Computação**[cite: 5]  
**Disciplina:** Simulação Discreta (EN05225)[cite: 5]  
**Professor:** Dr. Filipe de Oliveira Saraiva[cite: 5] 
**Alunos:** Christian Amarildo, Daniel Naiff, David Galhego e Rogério Barbosa 

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

O trabalho consiste na modelagem e simulação de eventos discretos para o planejamento de capacidade e análise de gargalos de um aeroporto comercial[cite: 5].

O aeroporto atende aeronaves de dois portes[cite: 5]:
* **Pequeno Porte (P):** Opera em pistas pequenas (`pista_p`)[cite: 5].
* **Grande Porte (G):** Opera em pistas grandes (`pista_g`)[cite: 5].

### Fluxo Operacional das Aeronaves[cite: 5]:
1. **Pouso:** Solicita a pista apropriada (`pista_p` ou `pista_g`) e a libera imediatamente após o pouso[cite: 5].
2. **Desembarque:** Dirige-se a uma plataforma de desembarque disponível[cite: 5].
3. **Hangar:** Após desembarcar, exige um hangar para manutenção/preparo[cite: 5]. A plataforma de desembarque só é liberada quando a aeronave ocupa o hangar[cite: 5].
4. **Embarque:** Após o hangar, solicita uma plataforma disponível para embarque[cite: 5]. O hangar só é liberado quando a plataforma de embarque for alocada[cite: 5].
5. **Decolagem:** Solicita a pista correspondente para decolar[cite: 5]. A plataforma de embarque só é liberada no momento do acesso à pista de decolagem[cite: 5].

### Tempos Operacionais Fixos (em minutos)[cite: 5]:
| Operação | Pequeno Porte (P) | Grande Porte (G) |
| :--- | :---: | :---: |
| **Pouso** | 40 min | 60 min |
| **Desembarque** | 20 min | 40 min |
| **Hangar** | 35 min | 70 min |
| **Embarque** | 30 min | 60 min |
| **Decolagem** | 40 min | 60 min |

---

## 2. Modelagem ACD (Activity Cycle Diagram)

*(Seção reservada para anexar o diagrama ACD em imagem/pdf)*[cite: 5]

---

## 3. Implementação Computacional (SimPy / Python)

A simulação foi implementada em **Python 3** utilizando a biblioteca **SimPy**[cite: 6].

### Arquitetura da Solução (`simulacao.py`)[cite: 6]:
* **`Metricas`:** Registra tempos de espera em fila por etapa e horário de conclusão dos voos[cite: 6].
* **`Aviao`:** Define o processo assíncrono da aeronave no SimPy (`operar()`)[cite: 6]. A retenção física de recursos é garantida via requisições manuais (`request()`) e liberações encadeadas (`release()`)[cite: 6].
* **`simular()`:** Instancia os recursos (`pista_p`, `pista_g`, `plataforma`, `hangar`), realiza a leitura dos eventos de `chegadas.csv` e calcula o **Tempo Final de Simulação** ($TF$) e as **Filas Máximas**[cite: 5, 6].

---

## 4. Análise dos Cenários e Resultados das Simulações

Foram executadas três configurações de infraestrutura para comparar o tempo de processamento total e o acúmulo de filas[cite: 5].

### Tabela Comparativa de Desempenho[cite: 5]:

| Categoria | Métrica / Parâmetro | Cenário 1 <br> *(Base)* | Cenário 2 <br> *(Recomendado)* 🏆 | Cenário 3 <br> *(Expansão)* | Redução <br> *(C2 vs C1)* |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Infraestrutura** | **Plataformas** | 5 | 5 | 7 | — |
| | **Hangares** | 3 | 3 | 5 | — |
| | **Pistas Pequeno Porte (P)** | 2 | 3 | 3 | +50% |
| | **Pistas Grande Porte (G)** | 1 | 2 | 2 | +100% |
| **Tempo Total** | **Tempo Final de Simulação** | **1.110,0 min** <br> *(18,5h)* | **580,0 min** <br> *(9,7h)* | **1.390,0 min** <br> *(23,2h)* | **-47,7%** 📉 |
| **Filas Máximas** | **Fila Máxima (Pouso)** | 392,0 min | **31,0 min** | 145,0 min | **-92,1%** |
| | **Fila Máxima (Desembarque)** | 565,0 min | **124,0 min** | 385,0 min | **-78,1%** |
| | **Fila Máxima (Hangar)** | 245,0 min | **90,0 min** | 230,0 min | **-63,3%** |
| | **Fila Máxima (Embarque)** | 280,0 min | **80,0 min** | 275,0 min | **-71,4%** |
| | **Fila Máxima (Decolagem)** | 300,0 min | **40,0 min** | 150,0 min | **-86,7%** |

---

## 5. Identificação e Diagnóstico dos Gargalos

### 1. Diagnóstico do Cenário Base (Cenário 1)[cite: 5]
O Cenário 1 apresenta retenção excessiva nas etapas operacionais[cite: 5]:
* **Gargalo Primário:** A presença de apenas **1 pista de grande porte (`pista_g=1`)** cria um funil de saída[cite: 5].
* **Efeito Dominó (Cascata de Bloqueios):** Com o afunilamento de decolagem, as aeronaves retêm as plataformas de embarque[cite: 5]. Isso impede que o hangar seja esvaziado, bloqueando as plataformas de desembarque e gerando a **fila crítica de 565 minutos**.

### 2. O Otimização do Cenário 2[cite: 5]
Ao expandir a infraestrutura para **3 Pistas P e 2 Pistas G** (mantendo 5 plataformas e 3 hangares)[cite: 5]:
* O tempo total da simulação caiu de **1.110 min para 580 min** (uma **redução de 47,7%**).
* As filas de espera caíram drasticamente em todas as etapas (pouso diminuiu 92,1% e decolagem diminuiu 86,7%).
* **Conclusão:** O aumento da vazão nas pistas eliminou o represamento das etapas internas de solo.

### 3. Anomalia do Cenário 3 (Deseconomia de Escala)[cite: 5]
Ao aumentar plataformas para 7 e hangares para 5 no Cenário 3, o tempo total **piorou para 1.390 minutos**[cite: 5].
* **Causa:** O aumento da capacidade interna permitiu que mais aeronaves fossem processadas simultaneamente, acumulando múltiplos aviões ao mesmo tempo na fase de decolagem[cite: 5]. Sem pistas suficientes para dar vazão à demanda interna ampliada, formaram-se novos congestionamentos de saída.

---

## 6. Análise Econômica e de Viabilidade das Soluções

1. **Prejuízos do Cenário Base:**
   * **OPEX Elevado:** Filas de pouso de 392 minutos geram gasto excessivo com Querosene de Aviação (QAV) em procedimentos de espera em voo.
   * **Multas e Penalidades:** Atrasos em solo superiores a 4 horas acarretam indenizações a passageiros e multas aplicadas pelos órgãos reguladores.

2. **Viabilidade Econômica do Cenário 2 (RECOMENDADO):**
   * **Alto Retorno sobre Investimento (ROI):** Reduz o tempo de operação quase pela metade (de 18,5h para 9,7h), dobrando a capacidade diária de atendimento do aeroporto.
   * **Amortização Rápida:** O custo de ampliação das pistas é rapidamente coberto pela eliminação dos custos de atraso e aumento do fluxo de voos e tarifas aeroportuárias.

3. **Inviabilidade Econômica do Cenário 3:**
   * Exige alto aporte financeiro (**CAPEX**) para construção de 2 novas plataformas e 2 hangares.
   * **Desperdício de Capital:** O investimento resulta na degradação do desempenho geral (1.390 min), configurando destruição de valor econômico.

---

## 7. Instruções de Execução

### Pré-requisitos:
* Python 3.8+
* Biblioteca `simpy`

### Execução:
```bash
# Instalar dependência
pip install simpy

# Executar a simulação
python simulacao.py