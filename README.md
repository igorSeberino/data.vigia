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
</p>

O **vigia** prevê, a partir das leituras de sensores de uma máquina de usinagem (temperaturas,
rotação, torque e desgaste da ferramenta), se um ciclo de processo vai falhar, e mede quanto
isso economiza frente às manutenções corretiva e preventiva. O trabalho passa por todo o ciclo
de ciência de dados: coleta e validação dos dados, modelo dimensional em SQLite, análise
exploratória com testes estatísticos, modelos de classificação e análise de custo.

> Projeto acadêmico — disciplina de Ciência de Dados, Prof. Claudinei Dias (Ney), Engenharia de Software, Centro Universitário Católica de Santa Catarina.

**Integrantes:** Adrian Cesar Gonçalves (@adrian-cesar) · Gabriel Carvalho (@gabrielcarvallho) ·
Igor Thiago Seberino (@igorSeberino) · Renato Colin Neto (@rcolinneto)

Este README é o relatório completo do trabalho. Backlog e andamento no Project
[**@vigia**](https://github.com/users/igorSeberino/projects/2); plano e divisão de tarefas em
[`docs/plano/`](docs/plano/).

| Notebook | Conteúdo |
|---|---|
| [01 – Coleta e preparação](notebooks/01_coleta_e_preparacao.ipynb) | origem, validação, atributos físicos, divisão |
| [02 – Modelo de dados (SQL)](notebooks/02_modelo_de_dados_sql.ipynb) | esquema estrela em SQLite e consultas |
| [03 – Análise exploratória](notebooks/03_analise_exploratoria.ipynb) | distribuições, testes estatísticos, regras físicas |
| [04 – Modelagem preditiva](notebooks/04_modelagem_preditiva.ipynb) | comparação, ajuste e avaliação dos modelos |
| [05 – Impacto no negócio](notebooks/05_impacto_no_negocio.ipynb) | custo, limiar ótimo, estratégias de manutenção |

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
**Fonte.** *AI4I 2020 Predictive Maintenance Dataset*, publicado no UCI Machine Learning
Repository (id 601) com licença CC BY 4.0 (UCI MACHINE LEARNING REPOSITORY, 2020) e descrito por
Matzka (2020). É um conjunto **sintético**, construído para reproduzir dados reais de manutenção
preditiva de uma máquina de usinagem: cada linha é um ciclo de processo, com as leituras de
sensores daquele ciclo e o rótulo de falha.

**Volume.** 10.000 ciclos × 14 colunas, em um CSV de 522.048 bytes. A preparação acrescenta 3
colunas derivadas, e o DataFrame analítico fica com 17 colunas (notebook 01).

**Tipos.**

| Grupo | Colunas | Tipo |
|---|---|---|
| Identificadores | `udi`, `id_produto` | inteiro e texto (proibidos como atributo) |
| Variante do produto | `tipo` (L, M, H) | categórica ordinal |
| Sensores | `temp_ar_k`, `temp_processo_k` (K), `rotacao_rpm` (rpm), `torque_nm` (N·m), `desgaste_ferramenta_min` (min) | numéricas contínuas e inteiras |
| Alvo | `falha` | binário |
| Modos de falha | `falha_twf`, `falha_hdf`, `falha_pwf`, `falha_osf`, `falha_rnf` | binários (proibidos como atributo: são a própria falha) |
| Derivadas | `dif_temperatura_k` (K), `potencia_w` (W), `esforco_ferramenta_min_nm` (min·N·m) | numéricas contínuas |

O dicionário completo, com unidade, papel e descrição de cada uma das 17 colunas, está em
[`reports/tables/01_dicionario_dados.csv`](reports/tables/01_dicionario_dados.csv).

**Distribuição do alvo.** 339 dos 10.000 ciclos terminam em falha (3,39 %): a base é
**desbalanceada**, o que orienta a escolha de métricas na seção 2.4.2. A taxa de falha cai com a
qualidade do produto:

| Tipo | Ciclos | Falhas | Taxa de falha |
|---|---:|---:|---:|
| L (baixa) | 6.000 | 235 | 3,92 % |
| M (média) | 2.997 | 83 | 2,77 % |
| H (alta) | 1.003 | 21 | 2,09 % |

### 2.2 Coleta e preparação dos dados
<!-- RESPONSÁVEL: @igorSeberino · T1 -->
O pipeline está em `src/manutencao/dados.py` e `src/manutencao/preparacao.py` e é executado no
[notebook 01](notebooks/01_coleta_e_preparacao.ipynb):

1. **Coleta.** O CSV original fica versionado em `data/raw/ai4i2020.csv`. Se faltar,
   `baixar_csv()` baixa o zip oficial da UCI e só aceita o arquivo se o SHA-256 bater com o
   publicado. O `.gitattributes` marca o CSV como binário para o git não converter o fim de linha
   (CRLF) e alterar o hash.
2. **Leitura.** O cabeçalho tem BOM UTF-8, por isso a leitura usa `encoding="utf-8-sig"`.
3. **Validação.** 14 verificações de estrutura, completude, unicidade, coerência de domínio e
   rótulos binários, todas aprovadas: nenhum valor ausente, nenhuma linha duplicada, `UDI` e
   `Product ID` únicos, temperaturas entre 290 e 320 K, processo mais quente que o ar
   ([`01_validacao_qualidade.csv`](reports/tables/01_validacao_qualidade.csv)).
4. **Inconsistências de rótulo.** 27 linhas não seguem a regra "falha = pelo menos um modo":
   9 com falha e nenhum modo, 18 com RNF marcado e sem falha. A página da UCI fala em 5 casos de
   RNF; o arquivo tem 19. **Decisão D5:** o alvo é mantido como publicado, para o resultado ser
   comparável com outros trabalhos, e as linhas ficam documentadas como ruído de rótulo
   ([`01_inconsistencias_rotulo.csv`](reports/tables/01_inconsistencias_rotulo.csv)).
5. **Renomeação e tipagem.** Nomes em português, sem espaços e com a unidade no sufixo;
   `tipo` vira categórica ordenada L < M < H.
6. **Atributos físicos.** Três grandezas da física da usinagem:
   diferença de temperatura $\Delta T = T_{proc} - T_{ar}$ (dissipação de calor),
   potência $P = \tau \cdot n \cdot 2\pi/60$ (W) e esforço da ferramenta
   $E = \text{desgaste} \cdot \tau$ (min·N·m). Aplicadas às regras documentadas pela UCI, elas
   reproduzem **100 %** dos rótulos de HDF (115 ciclos), PWF (95) e OSF (98)
   ([`01_regras_vs_rotulos.csv`](reports/tables/01_regras_vs_rotulos.csv)). Esses três modos
   respondem por 287 das 339 falhas; as outras 52 (desgaste da ferramenta, falha aleatória e
   falhas sem modo) não seguem uma regra sobre a leitura do ciclo. Isso explica o desempenho dos
   modelos (seção 3.2.3) e é a principal limitação discutida na seção 3.3.1.
7. **Divisão treino/teste.** Única no projeto, por `dividir_treino_teste()`: 80/20, estratificada
   pelo alvo, `SEED = 42`. Treino com 8.000 ciclos e 271 falhas (3,39 %); teste com 2.000 ciclos
   e 68 falhas (3,40 %) ([`01_divisao_treino_teste.csv`](reports/tables/01_divisao_treino_teste.csv)).
   O teste fica reservado para o fim do notebook 04 e para o notebook 05.

### 2.3 Ferramentas e técnicas de modelagem de dados
<!-- RESPONSÁVEL: @igorSeberino · T1 (tabela de ferramentas) -->
| Ferramenta | Uso no trabalho |
|---|---|
| Python 3.12 | linguagem de todo o trabalho |
| pandas (McKINNEY, 2010) e NumPy (HARRIS *et al.*, 2020) | leitura, validação e manipulação dos dados |
| SQLite (`sqlite3`, biblioteca padrão) | modelo dimensional em esquema estrela |
| scikit-learn (PEDREGOSA *et al.*, 2011) | modelos de classificação, validação cruzada e métricas |
| SciPy (VIRTANEN *et al.*, 2020) | testes estatísticos |
| Matplotlib (HUNTER, 2007) e seaborn (WASKOM, 2021) | gráficos |
| Jupyter | notebooks executados e versionados com saída |
| pytest e ruff | testes automatizados e padrão de código |
| GitHub Actions | CI que roda lint, testes e os cinco notebooks a cada PR |
| uv | criação do ambiente virtual e instalação das dependências |

O trabalho segue as fases do CRISP-DM (SHEARER, 2000): entendimento do negócio (seção 1),
entendimento dos dados (notebooks 01 e 03), preparação (notebooks 01 e 02), modelagem
(notebook 04), avaliação (notebooks 04 e 05) e implantação, que fica fora do escopo e entra como
trabalho futuro na seção 3.5.

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

## Contribuindo

Fluxo Trunk-Based com o time de agentes do Claude Code em [`.claude/`](.claude/README.md):
`/setup` → `/tbd-start <issue>` → implementação → `/tbd-commit` → `/tbd-pr`. Regras do projeto
em [`CLAUDE.md`](CLAUDE.md); cada PR precisa de CI verde e aprovação de outro integrante.

## Dados
Dados: *AI4I 2020 Predictive Maintenance Dataset*, UCI Machine Learning Repository,
https://doi.org/10.24432/C5HS5C, licença CC BY 4.0 (cópia em `data/raw/ai4i2020.csv`).
