# Relatório de Simulação Discreta — Operações Aeroportuárias (Prova II)

**Universidade Federal do Pará (UFPA)**  
**Instituto de Ciências Exatas e Naturais (ICEN)** — **Faculdade de Computação**  
**Disciplina:** Simulação Discreta (EN05225)  
**Professor:** Dr. Filipe de Oliveira Saraiva  
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

O trabalho consiste na modelagem e simulação de eventos discretos para o planejamento de capacidade e análise de gargalos de um aeroporto comercial.

O aeroporto atende aeronaves de dois portes:
* **Pequeno Porte (P):** Opera em pistas pequenas (`pista_p`).
* **Grande Porte (G):** Opera em pistas grandes (`pista_g`).

### Fluxo Operacional das Aeronaves:
1. **Pouso:** Solicita a pista apropriada (`pista_p` ou `pista_g`) e a libera imediatamente após o pouso.
2. **Desembarque:** Dirige-se a uma plataforma de desembarque disponível.
3. **Hangar:** Após desembarcar, exige um hangar para manutenção/preparo. A plataforma de desembarque só é liberada quando a aeronave ocupa o hangar.
4. **Embarque:** Após os preparativos, a aeronave libera o hangar e aguarda por uma plataforma disponível para embarque.
5. **Decolagem:** Solicita a pista correspondente para decolar. A plataforma de embarque só é liberada no momento do acesso à pista de decolagem.

### Tempos Operacionais Fixos (em minutos):
| Operação | Pequeno Porte (P) | Grande Porte (G) |
| :--- | :---: | :---: |
| **Pouso** | 40 | 60 |
| **Desembarque** | 20 | 40 |
| **Hangar** | 35 | 70 |
| **Embarque** | 30 | 60 |
| **Decolagem** | 40 | 60 |

---

## 2. Modelagem ACD (Activity Cycle Diagram)

![Diagrama ACD do Cenário Aeroportuário](diagrama_acd.png)

---

## 3. Implementação Computacional (SimPy / Python)

A simulação foi implementada em **Python 3** utilizando a biblioteca **SimPy**.

### Arquitetura da Solução (`simulacao.py`):
* **`Metricas`:** Registra tempos de espera em fila por etapa e horário de conclusão dos voos.
* **`Aviao`:** Define o processo assíncrono da aeronave no SimPy (`operar()`). A retenção física de recursos e a liberação de buffers intermediários (como a saída do hangar para aguardar o embarque) são garantidas via requisições manuais (`request()`) e liberações controladas (`release()`).
* **`simular()`:** Instancia os recursos (`pista_p`, `pista_g`, `plataforma`, `hangar`), realiza a leitura dos eventos de `chegadas.csv` e calcula o **Tempo Final de Simulação** ($TF$) e as **Filas Máximas**.

---

## 4. Análise dos Cenários e Resultados das Simulações

Foram executadas três configurações de infraestrutura para comparar o tempo de processamento total e o acúmulo de filas.

### Tabela Comparativa de Desempenho:

| Categoria | Métrica / Parâmetro | Cenário 1 <br> *(Base)* | Cenário 2 <br> *(Intermediário)* | Cenário 3 <br> *(Recomendado)* | Redução <br> *(C3 vs C1)* |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Infraestrutura** | **Plataformas** | 5 | 5 | 7 | — |
| | **Hangares** | 3 | 3 | 5 | — |
| | **Pistas Pequeno Porte (P)** | 2 | 3 | 3 | +50% |
| | **Pistas Grande Porte (G)** | 1 | 2 | 2 | +100% |
| **Tempo Total** | **Tempo Final de Simulação** | **3.640,0 min** <br> *(~60,6h)* | **2.250,0 min** <br> *(~37,5h)* | **2.065,0 min** <br> *(~34,4h)* | **-43,2%** |
| **Filas Máximas** | **Fila (Pouso)** | 572,0 min | 126,0 min | **179,0 min** | **-68,7%** |
| | **Fila (Desembarque)** | 880,0 min | 335,0 min | **265,0 min** | **-69,8%** |
| | **Fila (Hangar)** | 70,0 min | 50,0 min | **25,0 min** | **-64,2%** |
| | **Fila (Embarque)** | 880,0 min | 350,0 min | **265,0 min** | **-69,8%** |
| | **Fila (Decolagem)** | 510,0 min | 125,0 min | **190,0 min** | **-62,7%** |

---

## 5. Identificação e Diagnóstico dos Gargalos

### 1. Diagnóstico do Cenário Base (Cenário 1)
O Cenário 1 apresenta um estrangulamento severo em sua capacidade de solo:
* **Gargalo Primário (Plataformas):** As aeronaves recém-chegadas (desembarque) e as que saem do hangar (embarque) disputam simultaneamente o **mesmo recurso restrito** (5 plataformas). Isso gera picos colossais de **880 minutos** de fila para ambas as operações.
* **Efeito Colateral no Espaço Aéreo:** Sem plataformas suficientes para escoar o desembarque, as aeronaves não conseguem sair da pista de pouso, gerando filas de espera em voo de 572 minutos, prolongando a simulação para insustentáveis 3.640 minutos (mais de 60 horas operacionais).

### 2. Efeitos da Expansão Parcial (Cenário 2)
Aumentar as pistas (3 Pequenas e 2 Grandes) quebra o gargalo de entrada e saída.
* O tempo total da simulação cai de **3.640 min para 2.250 min**.
* A fila de pouso reduz expressivamente para 126 minutos, mas o gargalo interno de plataformas ainda persiste com picos de 350 minutos (cerca de 6 horas de espera em solo).

### 3. Solução Completa (Cenário 3)
Ao escalar tanto a infraestrutura de pistas quanto a capacidade de solo (7 Plataformas e 5 Hangares):
* O gargalo interno das plataformas é aliviado. As filas de embarque e desembarque caem para 265 minutos, o menor tempo entre todas as simulações.
* O sistema opera de forma equilibrada, atingindo o melhor **Tempo Final (2.065 minutos)**, representando uma economia de 43,2% no tempo total em relação ao Cenário Base.

---

## 6. Análise Econômica e de Viabilidade das Soluções

1. **Prejuízos do Cenário Base (Inviável):**
   * **Custos Operacionais Elevados:** Filas de pouso de 572 minutos geram gasto excessivo com Querosene de Aviação (QAV) em procedimentos de espera em voo.
   * **Colapso Sistêmico:** Atrasos em solo próximos a 15 horas (880 min) impossibilitam a operação comercial, acarretando indenizações altíssimas a passageiros, multas pesadas das agências reguladoras (como ANAC) e perda de contratos com companhias aéreas.

2. **Viabilidade do Cenário 2 (Medida Paliativa):**
   * Reduz os custos de queima de combustível em voo, resolvendo o afunilamento de pistas. Contudo, os atrasos internos de passageiros em trânsito ainda geram custos substanciais com remarcações de voos e suporte em solo.

3. **Viabilidade Econômica do Cenário 3 (RECOMENDADO):**
   * **Máxima Produtividade:** A expansão completa exige o maior investimento inicial (CAPEX) em obras civis, construção de novos pátios (plataformas) e áreas de manutenção (hangares).
   * **Retorno sobre o Investimento (ROI):** É a única alternativa que viabiliza o fluxo fluido das aeronaves. O custo da obra é rapidamente amortizado pelo aumento drástico na capacidade diária de processamento de voos, elevação na arrecadação de tarifas aeroportuárias e eliminação das pesadas multas geradas no Cenário 1.

---

## 7. Instruções de Execução

### Pré-requisitos
* Python 3.8 ou superior
* Gerenciador de pacotes moderno (`uv`) ou padrão (`pip`)

### Opção 1: Execução com o gerenciador `uv`
Se estiver utilizando o `uv` em seu ambiente, basta rodar o comando (as dependências serão geridas automaticamente ou lidas do seu arquivo de projeto):
```bash
uv run simulacao.py
