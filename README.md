# data.vigia

<p align="center">
  <img src=".github/assets/logo.svg" alt="vigia: engrenagem com sinal de vibração" width="160">

  <h3 align="center">vigia</h3>

  <p align="center">
    Manutenção preditiva de uma máquina de usinagem na Indústria 4.0
  </p>
</p>

<p align="center">
  <a href="https://github.com/igorSeberino/data.vigia/actions/workflows/ci.yml"><img src="https://github.com/igorSeberino/data.vigia/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://doi.org/10.24432/C5HS5C"><img src="https://img.shields.io/badge/dados-AI4I%202020%20(UCI)-2BB3A3" alt="Dados: AI4I 2020 (UCI)"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licen%C3%A7a-MIT-F5A524" alt="Licença MIT"></a>
</p>

O **vigia** prevê, a partir das leituras de sensores de uma máquina de usinagem (temperaturas,
rotação, torque e desgaste da ferramenta), se um ciclo de processo vai falhar, e mede quanto
isso economiza frente às manutenções corretiva e preventiva. O trabalho passa por todo o ciclo
de ciência de dados: coleta e validação dos dados, modelo dimensional em SQLite, análise
exploratória com testes estatísticos, modelos de classificação e análise de custo.

> Projeto acadêmico — disciplina de Inteligência Artificial (avaliação de Ciência de Dados),
> Prof. Claudinei Dias (Ney), Engenharia de Software, Centro Universitário Católica de Santa Catarina.

**Integrantes:** Adrian Cesar Gonçalves (@adrian-cesar) · Gabriel Carvalho (@gabrielcarvallho) ·
Igor Thiago Seberino (@igorSeberino) · Renato Colin Neto (@rcolinneto)

Este README é o relatório completo do trabalho. Backlog e andamento no Project
[**@vigia**](https://github.com/users/igorSeberino/projects/2); plano e divisão de tarefas em
[`docs/plano/`](docs/plano/).

| Notebook | Conteúdo | Colab |
|---|---|---|
| [01 – Coleta e preparação](notebooks/01_coleta_e_preparacao.ipynb) | origem, validação, atributos físicos, divisão | [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorSeberino/data.vigia/blob/main/notebooks/01_coleta_e_preparacao.ipynb) |
| [02 – Modelo de dados (SQL)](notebooks/02_modelo_de_dados_sql.ipynb) | esquema estrela em SQLite e consultas | [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorSeberino/data.vigia/blob/main/notebooks/02_modelo_de_dados_sql.ipynb) |
| [03 – Análise exploratória](notebooks/03_analise_exploratoria.ipynb) | distribuições, testes estatísticos, regras físicas | [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorSeberino/data.vigia/blob/main/notebooks/03_analise_exploratoria.ipynb) |
| [04 – Modelagem preditiva](notebooks/04_modelagem_preditiva.ipynb) | comparação, ajuste e avaliação dos modelos | [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorSeberino/data.vigia/blob/main/notebooks/04_modelagem_preditiva.ipynb) |
| [05 – Impacto no negócio](notebooks/05_impacto_no_negocio.ipynb) | custo, limiar ótimo, estratégias de manutenção | [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorSeberino/data.vigia/blob/main/notebooks/05_impacto_no_negocio.ipynb) |

## Resumo
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

## 1. Introdução
### 1.1 A Indústria 4.0 e sua importância
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
_Em construção._

### 1.2 Definição do problema
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
_Em construção._

### 1.3 Objetivos
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
_Em construção._

## 2. Metodologia
### 2.1 Descrição dos dados (fontes, tipos, volume)
<!-- RESPONSÁVEL: @igorSeberino · T1 -->
_Em construção._

### 2.2 Coleta e preparação dos dados
<!-- RESPONSÁVEL: @igorSeberino · T1 -->
_Em construção._

### 2.3 Ferramentas e técnicas de modelagem de dados
<!-- RESPONSÁVEL: @igorSeberino · T1 (tabela de ferramentas) -->
_Em construção._

#### 2.3.1 Modelagem dimensional (esquema estrela em SQLite)
<!-- RESPONSÁVEL: @gabrielcarvallho · T2 -->
_Em construção._

#### 2.3.2 Modelagem preditiva (aprendizado supervisionado)
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

### 2.4 Métodos de análise de dados
#### 2.4.1 Análise exploratória e testes estatísticos
<!-- RESPONSÁVEL: @adrian-cesar · T3 -->
_Em construção._

#### 2.4.2 Validação e métricas dos modelos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 2.4.3 Análise de custo e estratégias de manutenção
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

## 3. Desenvolvimento
### 3.1 Implementação dos modelos de dados
#### 3.1.1 Modelo dimensional
<!-- RESPONSÁVEL: @gabrielcarvallho · T2 -->
_Em construção._

#### 3.1.2 Modelos preditivos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

### 3.2 Análise dos resultados
#### 3.2.1 O que a exploração mostrou
<!-- RESPONSÁVEL: @adrian-cesar · T3 -->
_Em construção._

#### 3.2.2 Consultas analíticas no modelo dimensional
<!-- RESPONSÁVEL: @gabrielcarvallho · T2 -->
_Em construção._

#### 3.2.3 Desempenho dos modelos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 3.2.4 Impacto financeiro
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

### 3.3 Discussão sobre a eficácia das soluções propostas
#### 3.3.1 Eficácia técnica e limitações do modelo
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 3.3.2 Eficácia para o negócio
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

### 3.4 Implementação em Python
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

### 3.5 Considerações finais
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

## 4. Referências
<!-- RESPONSÁVEL: @adrian-cesar · T5 (demais integrantes acrescentam as que citarem) -->
_Em construção._

## Contribuições
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

## Uso de IA
<!-- Cada integrante acrescenta uma linha no próprio PR -->
| Integrante | Tarefa | Ferramenta | O que a IA fez | O que o integrante fez/conferiu |
|---|---|---|---|---|

## Contribuindo

Fluxo Trunk-Based com o time de agentes do Claude Code em [`.claude/`](.claude/README.md):
`/setup` → `/tbd-start <issue>` → implementação → `/tbd-commit` → `/tbd-pr`. Regras do projeto
em [`CLAUDE.md`](CLAUDE.md); cada PR precisa de CI verde e aprovação de outro integrante.

## Dados e licença
Dados: *AI4I 2020 Predictive Maintenance Dataset*, UCI Machine Learning Repository,
https://doi.org/10.24432/C5HS5C, licença CC BY 4.0 (cópia em `data/raw/ai4i2020.csv`).
Código: licença MIT (ver `LICENSE`).
