# data.vigia · Plano mestre (ponta a ponta)

> Trabalho N2 da disciplina de Ciência de Dados (Prof. Claudinei Dias). Repositório:
> https://github.com/igorSeberino/data.vigia · Project: https://github.com/users/igorSeberino/projects/2

> Documento-base do grupo. Todo integrante (e o Claude de cada um) lê este arquivo **antes** do
> seu arquivo de tarefas (`01-IGOR.md`, `02-GABRIEL.md`, `03-ADRIAN.md`, `04-RENATO.md`).
> Nada aqui é opcional, a menos que esteja marcado como **opcional**.

---

## 1. Requisitos do enunciado

Fonte única: o PDF do enunciado ("Avaliação N2 – Ciência de Dados", Prof. Claudinei Dias (Ney),
"Aplicação de Ciência de Dados na Indústria 4.0", 1 página). O tema é **livre dentro da
Indústria 4.0**; o PDF fixa o que precisa existir. Toda tarefa, issue e artefato do repositório
aponta para um R abaixo ou para uma decisão D (§3).

| R | Trecho do PDF | Onde | Onde é atendido |
|---|---|---|---|
| R1 | "Apresentação da Indústria 4.0 e sua importância no cenário atual." | 1. Introdução | README §1.1 (T5) |
| R2 | "Deve identificar um problema real dentro do contexto da Indústria 4.0, coletar e preparar dados relevantes, construir modelos de dados e realizar análises para propor soluções baseadas em dados." | 1. Introdução | README §1.2 + notebooks 01–05 |
| R3 | "Objetivos do trabalho." | 1. Introdução | README §1.3 (T5) |
| R4 | "Descrição dos dados utilizados (fontes, tipos, volume)." | 2. Metodologia | README §2.1 + `reports/tables/01_dicionario_dados.csv` (T1) |
| R5 | "Processos de coleta e preparação dos dados." | 2. Metodologia | notebook 01 + README §2.2 (T1) |
| R6 | "Ferramentas e técnicas de modelagem de dados." | 2. Metodologia | README §2.3 (T1 ferramentas; T2 dimensional; T4 preditiva) |
| R7 | "Métodos de análise de dados aplicados." | 2. Metodologia | README §2.4 (T3, T4, T6) |
| R8 | "Implementação dos modelos de dados." | 3. Desenvolvimento | notebooks 02 (SQL/estrela) e 04 (ML) + README §3.1 (T2, T4) |
| R9 | "Análise dos resultados obtidos." | 3. Desenvolvimento | notebooks 02–05 + README §3.2 (T2, T3, T4, T6) |
| R10 | "Discussão sobre a eficácia das soluções propostas." | 3. Desenvolvimento | notebook 05 + README §3.3 e §3.5 (T4, T6, T7) |
| R11 | "Implementação em Python." | 3. Desenvolvimento | `src/manutencao/` + notebooks + testes + CI + README §3.4 (T0–T7) |
| R12 | "Listagem das fontes bibliográficas e recursos utilizados." | 4. Referências | README §4 (T5; demais acrescentam) |
| R13 | "Deve ser por um link Google Colab ou GitHub (link público)" | 5. Entrega | repositório público no GitHub (D1) |
| R14 | "Deve ser documentado (notebook ou markdown)" | 5. Entrega | README como relatório + notebooks executados com saída (D2) |
| R15 | "Pode ser realizado em grupo (máximo 6 integrantes)." | Objetivo | 4 integrantes (§4) |

Não é requisito à parte: a frase do Objetivo ("aplicar conceitos de ciência de dados, modelagem
de dados e análise de dados...") está contida em R2.

O que o PDF **não** diz (e este plano decide): tema específico, formato de apresentação.

**"Modelagem de dados"** no enunciado é ambígua (pode ser modelo de dados relacional/dimensional
**ou** modelo preditivo). O plano cobre **as duas leituras**: um modelo dimensional em SQLite
(esquema estrela) **e** modelos de aprendizado de máquina. Assim nenhuma interpretação do
professor deixa o trabalho descoberto.

---

## 2. Tema escolhido e por quê

**Manutenção preditiva de uma máquina de usinagem: prever a falha de um ciclo de processo a
partir de leituras de sensores, e medir quanto isso economiza frente à manutenção corretiva e à
preventiva.**

- Problema real e central da Indústria 4.0 (paradas não planejadas, refugo, troca de ferramenta
  antes/depois da hora).
- Dataset público, sem login, licença CC BY 4.0, pequeno (522 KB), limpo e documentado:
  **AI4I 2020 Predictive Maintenance Dataset** (UCI Machine Learning Repository, id 601).
- Roda em qualquer máquina em poucos minutos; dá para dividir em 4 frentes
  independentes.

### 2.1 Fatos do dataset (verificados baixando o arquivo oficial)

| Fato | Valor |
|---|---|
| URL oficial (zip) | `https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip` |
| Arquivo dentro do zip | `ai4i2020.csv` (522.048 bytes) |
| SHA-256 do CSV | `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` |
| Citação da base | AI4I 2020 Predictive Maintenance Dataset [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C |
| Linhas × colunas | 10.000 × 14 |
| **Armadilha** | o cabeçalho tem **BOM UTF-8** (`\ufeffUDI`) → ler com `encoding="utf-8-sig"` |
| **Armadilha 2** | o CSV oficial tem fim de linha **CRLF**; com `* text=auto eol=lf` o git converte e o SHA-256 muda no clone. Por isso o `.gitattributes` marca `data/raw/*.csv -text` (conferido: clone novo tem o hash oficial) |
| Colunas originais | `UDI, Product ID, Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF` |
| Valores ausentes | 0 · linhas duplicadas: 0 |
| `Type` | L = 6.000 · M = 2.997 · H = 1.003 |
| `Product ID` | 10.000 valores distintos (1 por linha); a 1ª letra é sempre igual ao `Type` |
| `Machine failure` = 1 | 339 (3,39 %) → **desbalanceado** |
| Falhas por tipo | L 235/6000 (3,92 %) · M 83/2997 (2,77 %) · H 21/1003 (2,09 %) |
| Modos de falha | TWF 46 · HDF 115 · PWF 95 · OSF 98 · RNF 19 (soma = 373; 24 linhas têm mais de um modo) |
| Inconsistências de rótulo | 9 linhas com `Machine failure = 1` e nenhum modo; 18 linhas com `RNF = 1` e `Machine failure = 0` |
| Divergência documentação × arquivo | a página da UCI diz "RNF … 5 datapoints"; o arquivo tem 19 → reportar o observado |
| Faixas (mín–máx) | ar 295,3–304,5 K · processo 305,7–313,8 K · rotação 1168–2886 rpm · torque 3,8–76,6 Nm · desgaste 0–253 min |
| Desgaste × falha | [0,50): 52/2349 · [50,100): 51/2271 · [100,150): 52/2290 · [150,200): 61/2289 · [200,∞): 123/801 |

**Regras de geração (documentadas pela UCI e reproduzidas exatamente no arquivo):**

- HDF: `(temp_processo − temp_ar) < 8,6 K` **e** `rotação < 1380 rpm` → 115 linhas (bate 100 %).
- PWF: `potência = torque × rotação × 2π/60` fora de `[3500, 9000] W` → 95 linhas (bate 100 %).
- OSF: `desgaste × torque` > 11.000 (L) / 12.000 (M) / 13.000 (H) min·Nm → 98 linhas (bate 100 %).
- TWF: troca/falha de ferramenta sorteada com desgaste entre ~200 e 240 min (no arquivo: 198–253).
- RNF: 0,1 % de falha aleatória.

**Consequência que precisa estar na discussão (não esconder):** 287 das 339 falhas vêm de
HDF/PWF/OSF, que são funções determinísticas das variáveis medidas. Com as variáveis físicas
derivadas (diferença de temperatura, potência, esforço da ferramenta), modelos de árvore vão
chegar perto da perfeição nesses modos. O erro que sobra se concentra em TWF/RNF/sem modo
(52 falhas), que não são previsíveis por uma leitura isolada. Isso **é** o achado do trabalho:
engenharia de atributos com conhecimento do domínio domina o resultado, e o teto de recall
realista está ligado à parcela de falhas aleatórias. Também é a principal **limitação**: o dataset
é sintético, então o desempenho não se transfere automaticamente para uma fábrica real.

---

## 3. Decisões de projeto (fechadas — não rediscutir durante a implementação)

| # | Decisão | Motivo |
|---|---|---|
| D1 | Repositório público `igorSeberino/data.vigia` (produto **vigia**) + Project `@vigia` | Entrega exige link público; o Igor é o dono dos repos do grupo; "N2" fica fora do nome porque não é o assunto do trabalho |
| D2 | **README.md é o relatório** (seções com os nomes do PDF) + notebooks executados com saída | PDF aceita "notebook ou markdown"; o professor abre o link e lê tudo sem rodar nada |
| D3 | Código reutilizável em `src/manutencao/` (sem instalar pacote; notebooks fazem `sys.path.insert`) | Evita duplicação entre notebooks e permite testes |
| D4 | CSV original versionado em `data/raw/ai4i2020.csv` + download com verificação SHA-256 como alternativa | Reprodutível mesmo se a UCI cair; licença CC BY 4.0 permite redistribuir com atribuição |
| D5 | Alvo = `Machine failure` **como publicado** (sem re-rotular as 9 + 18 inconsistências) | Comparabilidade com a literatura; inconsistências documentadas como ruído de rótulo |
| D6 | Colunas proibidas como atributo: `udi`, `id_produto`, `falha_twf`, `falha_hdf`, `falha_pwf`, `falha_osf`, `falha_rnf` | Vazamento de alvo (os modos *são* a falha) e identificadores |
| D7 | Divisão treino/teste 80/20 estratificada, `random_state=42`, feita **só** por `preparacao.dividir_treino_teste()` | Todos usam a mesma divisão; teste é tocado uma única vez (notebook 04, ao final) |
| D8 | Métrica principal: **PR-AUC (average precision)**; também ROC-AUC, recall, precisão, F1, MCC, acurácia balanceada | Classe positiva = 3,39 %; acurácia engana (Saito & Rehmsmeier, 2015; Chicco & Jurman, 2020) |
| D9 | Modelos: Dummy, Regressão Logística, Árvore de Decisão, Random Forest, HistGradientBoosting (só scikit-learn) | Sem dependência extra (xgboost/lightgbm) |
| D10 | Dois conjuntos de atributos: **bruto** (6) e **engenharia** (bruto + 3 físicos) | Ablação mostra o valor do conhecimento do domínio |
| D11 | Limiar de decisão escolhido por **custo**, nas predições *out-of-fold* do treino, e só aplicado ao teste | Evita otimizar no teste |
| D12 | Custos de negócio são **hipóteses explícitas** (R$ 500 intervenção, R$ 5.000 falha) + análise de sensibilidade (razão 2–50) | Não existe custo real no dataset; o que importa é a razão |
| D13 | Modelo dimensional em **SQLite** (biblioteca padrão), esquema estrela com dimensão degenerada e tabela ponte | Zero instalação; `Product ID` é único por linha → dimensão degenerada (Kimball) |
| D14 | Python 3.12, `uv` para ambiente; dependências com limite inferior | Mesma versão do CI (`ci.yml`); `uv` cria o venv e instala tudo em um comando |
| D15 | Identificadores, docstrings, textos e commits em **português** | Padrão do grupo |
| D16 | Merge de PR por **"Create a merge commit"** (nunca squash) | Preserva cada commit com o autor → contribuição visível por integrante |
| D17 | `SEED = 42` em tudo que é aleatório | Reprodutibilidade |
| D18 | Um arquivo por integrante em `docs/plano/` com código de referência, notebook célula por célula, testes e commits sugeridos | **Decisão do Igor**: deixar tudo mastigado para cada integrante executar sem travar. Por isso o plano é maior que o código. Alternativa descartada: plano só com assinaturas, valores e testes |

---

## 4. Integrantes, contas GitHub e identidade de commit

E-mail de cada um = o que já aparece atribuído à conta no GitHub:

| Integrante | Login GitHub | `user.name` | `user.email` (já vinculado à conta, comprovado por commits atribuídos) |
|---|---|---|---|
| Igor Thiago Seberino | `igorSeberino` | `Igor Seberino` | `igorseberino@gmail.com` |
| Adrian Cesar Gonçalves | `adrian-cesar` | `Adrian Cesar Gonçalves` | `adriancg3006@gmail.com` |
| Gabriel Carvalho | `gabrielcarvallho` | `Gabriel Carvalho` | `gabriellccarvalho.dev@gmail.com` |
| Renato Colin Neto | **`rcolinneto`** | `Renato Colin Neto` | `renato.colin@catolicasc.edu.br` |

- Renato usa a conta **`rcolinneto`** (a antiga `RenatoColin` não é usada).
- Configure o e-mail **local** no clone (`git config user.email ...`), não o global: commit com
  e-mail não vinculado **não conta** como contribuição. Por isso todo arquivo de tarefas começa
  com a verificação de identidade e termina conferindo
  `gh api repos/igorSeberino/data.vigia/commits/<sha> --jq .author.login`.

**Cada integrante implementa a própria parte, na própria máquina, com a própria conta.** Ninguém
commita em nome de outro (nada de `--author` alheio): além de antiético, o professor pode pedir
para cada um explicar o que fez.

---

## 5. Divisão do trabalho (tarefas T0–T7)

| Tarefa | Issue | Responsável | Branch | Entrega | Revisor (aprova o PR) | Depende de | Atende |
|---|---|---|---|---|---|---|---|
| T0 | — (commit inicial) | Igor | direto na `main`, antes da proteção — **feito** | Repo, CI, CLAUDE.md, templates, README-esqueleto, plano em `docs/plano/`, time de agentes em `.claude/`, Project, labels, issues, convites, proteção da `main` | — | — | R11, R13, R14 |
| T1 | [#1](https://github.com/igorSeberino/data.vigia/issues/1) | Igor | `feat/1-data-prep` | `config.py`, `util.py`, `dados.py`, `preparacao.py` + testes; notebook 01; README §2.1, §2.2, §2.3 (tabela de ferramentas) | Renato | T0 | R4, R5, R6, R11 |
| T2 | [#2](https://github.com/igorSeberino/data.vigia/issues/2) | Gabriel | `feat/2-star-schema` | `modelo_dados.py` + testes; notebook 02; README §2.3.1, §3.1.1 (com o diagrama ER), §3.2.2 | Adrian | T1 | R2, R6, R8, R9 |
| T3 | [#3](https://github.com/igorSeberino/data.vigia/issues/3) | Adrian | `feat/3-eda` | `eda.py` + testes; notebook 03; README §2.4.1, §3.2.1 | Gabriel | T1 | R7, R9 |
| T4 | [#4](https://github.com/igorSeberino/data.vigia/issues/4) | Renato | `feat/4-predictive-models` | `modelagem.py` + testes; notebook 04; README §2.3.2, §2.4.2, §3.1.2, §3.2.3, §3.3.1 | Igor | T1 | R6, R7, R8, R9, R10 |
| T5 | [#5](https://github.com/igorSeberino/data.vigia/issues/5) | Adrian | `docs/5-intro-references` | README §1 (1.1, 1.2, 1.3) e §4 Referências (ABNT) | Igor | T0 | R1, R2, R3, R12 |
| T6 | [#6](https://github.com/igorSeberino/data.vigia/issues/6) | Gabriel | `feat/6-business-impact` | `custo.py` + testes; notebook 05; README §2.4.3, §3.2.4, §3.3.2 | Renato | T4 (código e testes podem começar após T1) | R7, R9, R10 |
| T7 | [#7](https://github.com/igorSeberino/data.vigia/issues/7) | Igor | `docs/7-final-report` | §3.4, §3.5, revisão de consistência, envio do link | Gabriel **e** Adrian (basta 1 aprovação; os dois revisam) | T2–T6 | R10, R11, R13, R14 |

As sete issues são sub-issues da issue-mãe [#8](https://github.com/igorSeberino/data.vigia/issues/8)
(barra de progresso no Project). Título do PR = título da issue; corpo termina com `Closes #<n>`.

Revisões por pessoa: Igor (T4, T5) · Renato (T1, T6) · Gabriel (T3, T7) · Adrian (T2, T7).

Grafo:

```text
T0 ─► T1 ─┬─► T2 ───────────────┐
          ├─► T3 ───────────────┤
          ├─► T4 ─► T6 ─────────┼─► T7 ─► entrega
T0 ─► T5 ─┴─────────────────────┘
```

---

## 6. Estrutura final do repositório

```text
data.vigia/
├── README.md                         # O RELATÓRIO (seções do PDF) — porta de entrada
├── CLAUDE.md                         # regras para o Claude de cada integrante
├── pyproject.toml                    # só configuração de ruff e pytest (sem build)
├── requirements.txt                  # dependências únicas (execução, testes, lint)
├── .gitignore  .gitattributes
├── .claude/                          # time de agentes (ver §11)
│   ├── agents/revisor-dados.md       # revisão de conformidade, somente leitura
│   ├── skills/setup|tbd-start|tbd-commit|tbd-pr/
│   ├── scripts/                      # projeto.py (Project @vigia), hooks
│   └── settings.json                 # permissões e hook de início de sessão
├── .github/
│   ├── workflows/ci.yml              # ruff + pytest + executa os 5 notebooks
│   ├── ISSUE_TEMPLATE/               # bug, débito técnico
│   ├── PULL_REQUEST_TEMPLATE.md      # O quê / Por quê / Notas / DoD
│   └── assets/logo.svg
├── data/
│   ├── raw/ai4i2020.csv              # versionado
│   └── processed/                    # gerado, ignorado pelo git
├── docs/
│   └── plano/                        # ESTES arquivos de planejamento
├── notebooks/
│   ├── 01_coleta_e_preparacao.ipynb  # T1 Igor
│   ├── 02_modelo_de_dados_sql.ipynb  # T2 Gabriel
│   ├── 03_analise_exploratoria.ipynb # T3 Adrian
│   ├── 04_modelagem_preditiva.ipynb  # T4 Renato
│   └── 05_impacto_no_negocio.ipynb   # T6 Gabriel
├── reports/
│   ├── figures/NN_*.png              # versionado (o README embute)
│   └── tables/NN_*.csv               # versionado (o README cita)
├── src/manutencao/
│   ├── __init__.py                   # T0
│   ├── config.py   util.py           # T1 Igor
│   ├── dados.py    preparacao.py     # T1 Igor
│   ├── modelo_dados.py               # T2 Gabriel
│   ├── eda.py                        # T3 Adrian
│   ├── modelagem.py                  # T4 Renato
│   └── custo.py                      # T6 Gabriel
└── tests/
    ├── test_estrutura.py             # T0 Igor (CI do 1º commit precisa de 1 teste)
    ├── conftest.py                   # T1 Igor
    ├── test_dados.py  test_preparacao.py   # T1
    ├── test_modelo_dados.py  test_custo.py # T2, T6
    ├── test_eda.py                   # T3
    └── test_modelagem.py             # T4
```

Prefixo `NN` dos artefatos = número do notebook que os gera (`03_correlacao_spearman.png`).

---

## 7. Contrato de interface (o que T2–T6 podem importar de T1)

Implementado no T1 (código completo em `01-IGOR.md`). **Ninguém altera estas assinaturas**; se
precisar de algo novo, cria no próprio módulo.

```python
from manutencao.config import (RAIZ, DIR_RAW, DIR_PROCESSED, DIR_FIGURAS, DIR_TABELAS,
    CAMINHO_CSV, CAMINHO_DB, SEED, COL_ALVO, COLS_MODOS, COLS_VAZAMENTO,
    COLS_NUMERICAS_BRUTAS, COLS_ENGENHARIA, COL_TIPO, ORDEM_TIPO, ATRIBUTOS_BRUTO,
    ATRIBUTOS_ENGENHARIA, MODOS_FALHA)
from manutencao.util import salvar_figura, salvar_tabela, configurar_graficos
from manutencao.dados import carregar_bruto, validar, inconsistencias_rotulo
from manutencao.preparacao import (preparar, carregar_preparado,
    dividir_treino_teste, separar_x_y)
```

| Nome | Valor/assinatura |
|---|---|
| `COL_ALVO` | `"falha"` |
| `COL_TIPO` | `"tipo"`; `ORDEM_TIPO = ["L", "M", "H"]` |
| `COLS_MODOS` | `["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]` |
| `COLS_NUMERICAS_BRUTAS` | `["temp_ar_k", "temp_processo_k", "rotacao_rpm", "torque_nm", "desgaste_ferramenta_min"]` |
| `COLS_ENGENHARIA` | `["dif_temperatura_k", "potencia_w", "esforco_ferramenta_min_nm"]` |
| `ATRIBUTOS_BRUTO` | `["tipo"] + COLS_NUMERICAS_BRUTAS` (6) |
| `ATRIBUTOS_ENGENHARIA` | `ATRIBUTOS_BRUTO + COLS_ENGENHARIA` (9) |
| `COLS_VAZAMENTO` | `["udi", "id_produto"] + COLS_MODOS` |
| `carregar_preparado() -> pd.DataFrame` | 10.000 linhas, colunas renomeadas + 3 de engenharia; `tipo` é `Categorical` ordenado L<M<H |
| `dividir_treino_teste(df) -> (treino, teste)` | 8.000 / 2.000, estratificado por `falha`, `SEED` |
| `separar_x_y(df, atributos) -> (X, y)` | `X = df[atributos]`, `y = df["falha"]`; lança `ValueError` se algum atributo estiver em `COLS_VAZAMENTO` |
| `salvar_figura(fig, nome) -> Path` | grava `reports/figures/<nome>.png` (dpi 120, `bbox_inches="tight"`) |
| `salvar_tabela(df, nome, index=False) -> Path` | grava `reports/tables/<nome>.csv` (UTF-8, separador vírgula, decimal ponto) |

Arquivos trocados entre notebooks (versionados em `reports/tables/`):

| Arquivo | Produzido por | Consumido por | Colunas |
|---|---|---|---|
| `04_oof_treino.csv` | T4 (nb 04) | T6 (nb 05) | `udi, falha, proba` (8.000 linhas) |
| `04_predicoes_teste.csv` | T4 (nb 04) | T6 (nb 05) | `udi, falha, proba, falha_twf, falha_hdf, falha_pwf, falha_osf, falha_rnf` (2.000 linhas) |
| `04_modelo_escolhido.csv` | T4 | T6, T7 | `modelo, conjunto, parametros, pr_auc_cv` (1 linha) |

---

## 8. Fluxo de trabalho Git (vale para todos)

Trunk-Based Development: `main` é a única branch longa; cada tarefa vira uma
branch curta `{tipo}/{issue}-{slug-em-inglês}`, um PR pequeno, CI verde, 1 aprovação, merge.
O time de agentes em `.claude/` (§11) executa cada passo; os comandos manuais ficam como
alternativa.

1. **Ambiente** (uma vez):
   - Instalar `uv`: Windows `winget install --id astral-sh.uv -e`; macOS `brew install uv`;
     Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`. Instalar o Claude Code e o `gh`.
   - Aceitar o convite: https://github.com/igorSeberino/data.vigia/invitations
   - `git clone https://github.com/igorSeberino/data.vigia.git` **fora** de
     OneDrive/Dropbox/Google Drive (o SQLite do T2 quebra em pasta sincronizada).
   - `cd data.vigia && uv venv --python 3.12 .venv`
   - Ativar: Windows Git Bash `source .venv/Scripts/activate`; PowerShell `.venv\Scripts\Activate.ps1`;
     macOS/Linux `source .venv/bin/activate`.
   - `uv pip install -r requirements.txt`
   - `git config user.name "<nome da tabela §4>"` e `git config user.email "<e-mail da tabela §4>"`
   - `gh auth refresh -h github.com -s project` (para mover os cards do Project)
2. **Validar**: abrir `claude` na raiz do repo (com o `.venv` ativo) e rodar `/setup`. Só seguir
   com tudo `OK`.
3. **Começar**: `/tbd-start <número da sua issue>` — assume a issue, move o card para
   *In Progress* e cria a branch da tabela §5.
   Manual: `gh issue edit <n> --add-assignee @me` · `git switch main && git pull && git switch -c <branch>`.
4. **Implementar** seguindo o seu arquivo em `docs/plano/`. Em dúvida de abordagem, peça
   "use o revisor-dados no modo 1 para a issue <n>".
5. **Commitar**: `/tbd-commit` a cada passo (lista de commits sugeridos em cada arquivo de
   tarefa). Manual: Conventional Commits em português,
   `feat(eda): ...`, `test(eda): ...`, `docs(readme): ...`.
6. **Abrir PR**: `/tbd-pr` — roda `ruff check`, `ruff format --check`, `pytest -q`, executa o
   notebook, chama o `revisor-dados`, faz push, cria o PR com o título da issue e pede revisão ao
   revisor da §5, e move o card para *In Review*. Antes, rode você mesmo:
   ```bash
   ruff check --fix . && ruff format .   # corrige import/formatação (inclusive dos notebooks)
   jupyter nbconvert --to notebook --execute --inplace notebooks/<seu_notebook>.ipynb
   ```
   e **commite o notebook executado + figuras + tabelas**.
7. **Merge** só com CI verde + aprovação do revisor, botão **"Create a merge commit"** (nunca
   squash — preserva cada commit com o autor).
8. **Finalizar**: `/tbd-pr` de novo depois do merge — volta para a `main`, apaga a branch e
   confere no GitHub que os commits aparecem com o seu login.
9. **Revisor**: ler o diff, rodar `pytest -q` no branch, comentar pelo menos 1 ponto concreto e
   aprovar com `gh pr review <n> --approve --body "..."`. Revisão vazia ("LGTM") não demonstra
   contribuição.

Trabalho que surgir no caminho (bug, débito, ajuste) entra como issue nova pelo `/tbd-start`
sem número (templates em `.github/ISSUE_TEMPLATE/`).

---

## 9. Estrutura do README (relatório) e dono de cada seção

O T0 cria o README com estes títulos e um marcador `<!-- RESPONSÁVEL ... -->` em cada seção.
Cada PR preenche **somente** as suas seções (troca o texto "_Em construção_" pelo conteúdo).

```text
# Manutenção Preditiva com Ciência de Dados na Indústria 4.0      (T0/T7 Igor)
badges · disciplina · professor · integrantes · links dos notebooks
## 1. Introdução
### 1.1 A Indústria 4.0 e sua importância                          (T5 Adrian)
### 1.2 Definição do problema                                      (T5 Adrian)
### 1.3 Objetivos                                                  (T5 Adrian)
## 2. Metodologia
### 2.1 Descrição dos dados (fontes, tipos, volume)                (T1 Igor)
### 2.2 Coleta e preparação dos dados                              (T1 Igor)
### 2.3 Ferramentas e técnicas de modelagem de dados               (T1 Igor: tabela de ferramentas)
#### 2.3.1 Modelagem dimensional (esquema estrela em SQLite)       (T2 Gabriel)
#### 2.3.2 Modelagem preditiva (aprendizado supervisionado)        (T4 Renato)
### 2.4 Métodos de análise de dados
#### 2.4.1 Análise exploratória e testes estatísticos              (T3 Adrian)
#### 2.4.2 Validação e métricas dos modelos                        (T4 Renato)
#### 2.4.3 Análise de custo e estratégias de manutenção            (T6 Gabriel)
## 3. Desenvolvimento
### 3.1 Implementação dos modelos de dados
#### 3.1.1 Modelo dimensional                                      (T2 Gabriel)
#### 3.1.2 Modelos preditivos                                      (T4 Renato)
### 3.2 Análise dos resultados
#### 3.2.1 O que a exploração mostrou                              (T3 Adrian)
#### 3.2.2 Consultas analíticas no modelo dimensional              (T2 Gabriel)
#### 3.2.3 Desempenho dos modelos                                  (T4 Renato)
#### 3.2.4 Impacto financeiro                                      (T6 Gabriel)
### 3.3 Discussão sobre a eficácia das soluções propostas
#### 3.3.1 Eficácia técnica e limitações do modelo                 (T4 Renato)
#### 3.3.2 Eficácia para o negócio                                 (T6 Gabriel)
### 3.4 Implementação em Python                                    (T7 Igor)
### 3.5 Considerações finais                                       (T7 Igor)
## 4. Referências                                                  (T5 Adrian; outros acrescentam via PR próprio)
## Dados                                                           (T0 Igor)
```

Regras de escrita do README:

- Todo número no texto vem de uma saída real de notebook ou de uma tabela em `reports/tables/`
  (citar o arquivo). **Proibido inventar ou arredondar "de cabeça".**
- Figuras embutidas com caminho relativo: `![Legenda](reports/figures/03_xxx.png)`.
- Citações no texto em formato ABNT autor-data: (MATZKA, 2020); (KAGERMANN; WAHLSTER; HELBIG, 2013).
- Cada referência citada no texto precisa estar em §4, e vice-versa.

---

## 10. Definição de pronto (global)

- [ ] Repositório **público**; `curl -s -o /dev/null -w "%{http_code}" https://github.com/igorSeberino/data.vigia` → `200` sem estar logado.
- [ ] CI verde na `main` (ruff, pytest, 5 notebooks executam de ponta a ponta).
- [ ] Os 5 notebooks commitados **com saída**; abrem no GitHub com gráficos visíveis.
- [ ] README cobre todas as seções da tabela §1, sem nenhum "_Em construção_" restante.
- [ ] `gh api repos/igorSeberino/data.vigia/contributors --jq '.[].login'` lista os 4 logins.
- [ ] Cada integrante tem ≥ 1 PR próprio mergeado e ≥ 1 revisão com comentário.
- [ ] Link enviado ao professor.

---

## 11. Time de agentes

Fica em `.claude/` do repositório (o Claude Code carrega ao abrir a pasta; nada para instalar).
Detalhes em `.claude/README.md`.

| Peça | O que faz |
|---|---|
| `/setup` | além de git/gh/python, confere a **identidade do commit** contra a tabela §4, a permissão no repo, o venv, as dependências e o SHA-256 do CSV |
| `/tbd-start <n>` | modo A: assume uma das issues planejadas (#1–#7), move o card e cria a branch já definida na issue; modo B: abre issue nova (bug/débito) com labels e card no Project |
| `/tbd-commit` | Conventional Commits em português, escopos pelos módulos de `src/manutencao/`, recusa e-mail errado |
| `/tbd-pr` | portões ruff + pytest + execução do notebook + `revisor-dados`, PR com o revisor da matriz §5, card em *In Review*; depois do merge confere a autoria |
| `revisor-dados` | revisão de conformidade somente leitura com 13 regras do projeto (vazamento, uso do teste, semente, números sem fonte, contrato §7, autoria) |
| `.claude/scripts/projeto.py` | move cards no Project sem o agente precisar descobrir ids |

Como cada um começa, com o `.venv` ativo, na raiz do repositório:

```text
claude
> /setup
> /tbd-start <número da minha issue>
> Leia CLAUDE.md, docs/plano/00-VISAO-GERAL.md e docs/plano/0X-<MEU-NOME>.md e execute a
> minha tarefa na ordem dos passos, usando /tbd-commit nos commits sugeridos. Rode ruff,
> pytest e o notebook e me mostre a saída real. Não altere arquivos de outros integrantes.
> No fim, /tbd-pr — e me mostre o texto do PR antes de criar.
```

Depois, **ler o que foi feito** e conseguir explicar cada decisão.

---

## 12. Estado do GitHub

| Item | Onde |
|---|---|
| Repositório | https://github.com/igorSeberino/data.vigia (público, `main` protegida: PR + 1 aprovação + check `ci`; só merge commit) |
| Project | https://github.com/users/igorSeberino/projects/2 — `@vigia`, público; campo Status (Backlog → In Progress → In Review → Done); visões Backlog, Board, My items; Adrian, Gabriel e Renato como editores |
| Issues | #1–#7 (uma por tarefa, com responsável, revisor, escopo, critérios e branch) + #8 issue-mãe |
| Labels | `module: dados`, `module: preparacao`, `module: modelo-dados`, `module: eda`, `module: modelagem`, `module: custo`, `débito técnico`, `bug` |
| Convites | `adrian-cesar`, `gabrielcarvallho`, `rcolinneto` com permissão *write* (aceitar em /invitations; conferir com `gh api repos/igorSeberino/data.vigia/collaborators --jq '.[].login'`) |

---

## 13. Fora do escopo

| Item | Motivo |
|---|---|
| Google Colab (badges, célula que clona o repo) | R13 aceita GitHub **ou** Colab; a entrega é pelo GitHub (D1) |
| Release, tag e número de versão | ninguém consome versões; a entrega é o link (R13) |
| Seções "Resumo" e "Contribuições" no README | o PDF não pede; a autoria aparece no histórico e em *contributors* |
| Seção "Uso de IA" | o PDF não pede |
| `docs/dicionario-de-dados.md` e `docs/modelo-de-dados.md` | duplicavam o README; o dicionário fica em `reports/tables/01_dicionario_dados.csv` e o diagrama ER no README §3.1.1 |
| Modelo serializado (`joblib`) | nenhum notebook nem seção consome; o notebook 05 usa as tabelas `04_*.csv` |
| Implantação do modelo (API, CLP/MES, monitoramento) | R2 pede propor soluções, não implantar; vira trabalho futuro em §3.5 |
| `LICENSE` de código | trabalho de uma entrega, sem reuso por terceiros; a atribuição CC BY dos dados fica no README (seção Dados) |
| Prazos intermediários por data | o PDF não fixa nenhum; a ordem vem do grafo da §5 |
| `requirements-dev.txt`, ambientes dev/prod | não há deploy; um único `requirements.txt` |
| `CODEOWNERS`, campos Area/Priority no Project, labels genéricas | o revisor vem da matriz da §5, a ordem vem do grafo e as labels `module:` já classificam |
| Mínimo de commits por PR, roteiro de defesa | nenhuma fonte pede |
| `.gitkeep` em pastas futuras | a tarefa que usa a pasta cria a pasta |
