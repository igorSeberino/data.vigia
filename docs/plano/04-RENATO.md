# Tarefas do Renato — T4 (modelagem preditiva)

> Leia antes: `00-VISAO-GERAL.md` (principalmente §2.1, §3, §7 e §8).
> Identidade git: `Renato Colin Neto <renato.colin@catolicasc.edu.br>` · login **`rcolinneto`**
> (não a conta antiga `RenatoColin`).
> Revisor do seu T4: **Igor**. Você revisa: **T1 (Igor)** e **T6 (Gabriel)**.

O código de referência abaixo foi executado e testado antes de entrar no plano (ruff e pytest
verdes; o pipeline completo roda em cerca de 75 s num notebook comum).

---

## Preparação (uma vez)

```bash
# 1) aceitar o convite: https://github.com/igorSeberino/data.vigia/invitations
git clone https://github.com/igorSeberino/data.vigia.git   # fora de OneDrive/Drive
cd data.vigia
git config user.name "Renato Colin Neto"
git config user.email "renato.colin@catolicasc.edu.br"
gh auth refresh -h github.com -s project                  # para mover os cards do Project
uv venv --python 3.12 .venv
source .venv/Scripts/activate        # Windows Git Bash (macOS/Linux: source .venv/bin/activate)
uv pip install -r requirements.txt
claude                               # na sessão: /setup — só siga com tudo OK
```

Fluxo de cada tarefa (detalhe na §8 e §11 do plano mestre): `/tbd-start <issue>` →
implementação seguindo este arquivo → `/tbd-commit` a cada commit sugerido → `/tbd-pr` → merge →
`/tbd-pr` de novo para finalizar.

**Primeira entrega sua é a revisão do T1 (Igor)** — ela desbloqueia o grupo todo. Conferir:
`pytest -q` verde no branch dele; `validar()` toda `ok`; `separar_x_y` recusa vazamento; a
divisão é estratificada e determinística. Comentar ao menos 1 ponto e aprovar
(`gh pr review <n> --approve --body "..."`).

---

## T4 — Modelagem preditiva (issue #4 · `feat/4-predictive-models`)

```bash
/tbd-start 4      # assume a issue #4, card em In Progress, branch feat/4-predictive-models
```

### Desenho experimental (o que você vai defender)

- **Tarefa:** classificação binária do alvo `falha` (3,39 % positivos).
- **Dados:** só o **treino** (8.000 ciclos) de `dividir_treino_teste()` para comparar e ajustar;
  o **teste** (2.000 ciclos, 68 falhas) é usado **uma única vez**, no fim, com o modelo já
  escolhido.
- **Validação:** `StratifiedKFold(5, shuffle=True, random_state=42)`.
- **Métrica principal:** PR-AUC (*average precision*) — com classe rara, a ROC-AUC fica alta
  mesmo com muitos falsos alarmes (SAITO; REHMSMEIER, 2015). Também: ROC-AUC, recall, precisão,
  F1, MCC (CHICCO; JURMAN, 2020), acurácia balanceada.
- **Desbalanceamento:** `class_weight="balanced"` (sem reamostragem sintética — mais simples,
  sem risco de vazar informação entre dobras).
- **Modelos:** Dummy (piso), Regressão Logística (linear, com padronização), Árvore de Decisão
  (interpretável), Random Forest (BREIMAN, 2001), HistGradientBoosting (FRIEDMAN, 2001) — todos
  do scikit-learn (PEDREGOSA *et al.*, 2011).
- **Ablação de atributos:** `bruto` (6 atributos medidos) × `engenharia` (+ diferença de
  temperatura, potência, esforço da ferramenta). Mostra quanto o conhecimento do domínio vale.
- **Ajuste:** `RandomizedSearchCV` (15 combinações, PR-AUC, mesma validação) **só no modelo de
  maior PR-AUC média com `engenharia`**.
- **Saídas para o Gabriel (T6):** probabilidades *out-of-fold* no treino e probabilidades no
  teste (contrato na §7 do plano mestre).

**O que esperar (e não esconder):** com `engenharia`, os modelos de árvore acertam praticamente
todos os HDF, PWF e OSF, porque esses modos são regras determinísticas das variáveis medidas
(ver §2.1 do plano). Os erros se concentram em TWF, RNF e falhas sem modo. Isso é **resultado**,
não defeito: entra na discussão (3.3.1) junto com a limitação de o dataset ser sintético.
Se `engenharia` **não** superar `bruto`, ou se a PR-AUC no teste ficar muito acima da média da
validação cruzada, algo está errado (vazamento ou uso do teste) — investigar antes de seguir.

### T4.1 `src/manutencao/modelagem.py`

```python
"""Modelagem preditiva: pipelines, validação cruzada, ajuste e avaliação."""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    make_scorer,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from manutencao.config import COL_TIPO, ORDEM_TIPO, SEED

METRICAS = {
    "pr_auc": "average_precision",
    "roc_auc": "roc_auc",
    "recall": make_scorer(recall_score, zero_division=0),
    "precisao": make_scorer(precision_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
    "mcc": make_scorer(matthews_corrcoef),
    "acuracia_balanceada": "balanced_accuracy",
}


def validacao(seed: int = SEED) -> StratifiedKFold:
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)


def preprocessador(atributos: list[str], escalar: bool) -> ColumnTransformer:
    """Tipo → ordinal (L<M<H); numéricas → padronizadas (só se ``escalar``)."""
    numericas = [c for c in atributos if c != COL_TIPO]
    return ColumnTransformer(
        [
            ("tipo", OrdinalEncoder(categories=[ORDEM_TIPO]), [COL_TIPO]),
            ("num", StandardScaler() if escalar else "passthrough", numericas),
        ]
    )


def modelos_candidatos(seed: int = SEED) -> dict[str, tuple[object, bool]]:
    """Nome → (estimador, precisa_escalar)."""
    return {
        "dummy": (DummyClassifier(strategy="prior"), False),
        "regressao_logistica": (
            LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed),
            True,
        ),
        "arvore_decisao": (
            DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=seed),
            False,
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=300, class_weight="balanced_subsample", n_jobs=-1, random_state=seed
            ),
            False,
        ),
        "gradient_boosting": (
            HistGradientBoostingClassifier(class_weight="balanced", random_state=seed),
            False,
        ),
    }


def montar_pipeline(nome: str, atributos: list[str], seed: int = SEED) -> Pipeline:
    estimador, escalar = modelos_candidatos(seed)[nome]
    return Pipeline([("prep", preprocessador(atributos, escalar)), ("modelo", clone(estimador))])


def avaliar_cv(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, seed: int = SEED) -> dict:
    """Validação cruzada estratificada 5-fold; devolve média e desvio de cada métrica."""
    res = cross_validate(pipeline, X, y, cv=validacao(seed), scoring=METRICAS, n_jobs=1)
    saida = {}
    for m in METRICAS:
        saida[f"{m}_media"] = float(np.mean(res[f"test_{m}"]))
        saida[f"{m}_dp"] = float(np.std(res[f"test_{m}"]))
    saida["tempo_ajuste_s"] = float(np.mean(res["fit_time"]))
    return saida


def comparar_modelos(
    treino: pd.DataFrame, conjuntos: dict[str, list[str]], seed: int = SEED
) -> pd.DataFrame:
    """Roda ``avaliar_cv`` para cada modelo × conjunto de atributos."""
    linhas = []
    y = treino["falha"]
    for nome_conj, atributos in conjuntos.items():
        X = treino[atributos]
        for nome in modelos_candidatos(seed):
            linhas.append(
                {
                    "modelo": nome,
                    "conjunto": nome_conj,
                    **avaliar_cv(montar_pipeline(nome, atributos, seed), X, y, seed),
                }
            )
    return pd.DataFrame(linhas).sort_values("pr_auc_media", ascending=False).reset_index(drop=True)


ESPACOS_BUSCA = {
    "regressao_logistica": {"modelo__C": [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]},
    "arvore_decisao": {
        "modelo__max_depth": [3, 4, 5, 6, 8, 10, 12, None],
        "modelo__min_samples_leaf": [1, 2, 5, 10, 20],
    },
    "random_forest": {
        "modelo__n_estimators": [200, 300, 500],
        "modelo__max_depth": [None, 8, 12, 16],
        "modelo__min_samples_leaf": [1, 2, 4],
        "modelo__max_features": ["sqrt", 0.5, None],
    },
    "gradient_boosting": {
        "modelo__learning_rate": [0.03, 0.05, 0.1, 0.2],
        "modelo__max_iter": [200, 400],
        "modelo__max_leaf_nodes": [15, 31, 63],
        "modelo__min_samples_leaf": [10, 20, 40],
        "modelo__l2_regularization": [0.0, 0.1, 1.0],
    },
}


def ajustar_hiperparametros(
    nome: str,
    atributos: list[str],
    X: pd.DataFrame,
    y: pd.Series,
    n_iter: int = 15,
    seed: int = SEED,
) -> RandomizedSearchCV:
    """Busca aleatória (PR-AUC, 5-fold) no espaço de ``ESPACOS_BUSCA[nome]``; refit no treino todo."""
    espaco = ESPACOS_BUSCA[nome]
    total = int(np.prod([len(v) for v in espaco.values()]))
    busca = RandomizedSearchCV(
        montar_pipeline(nome, atributos, seed),
        espaco,
        n_iter=min(n_iter, total),
        scoring="average_precision",
        cv=validacao(seed),
        random_state=seed,
        n_jobs=-1,
        refit=True,
    )
    return busca.fit(X, y)


def probabilidades_oof(
    pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, seed: int = SEED
) -> np.ndarray:
    """Probabilidade da classe 1 fora da dobra (para escolher limiar sem tocar no teste)."""
    return cross_val_predict(
        clone(pipeline), X, y, cv=validacao(seed), method="predict_proba", n_jobs=-1
    )[:, 1]


def metricas_teste(y: pd.Series, proba: np.ndarray, limiar: float = 0.5) -> dict:
    pred = (proba >= limiar).astype(int)
    return {
        "pr_auc": average_precision_score(y, proba),
        "roc_auc": roc_auc_score(y, proba),
        "recall": recall_score(y, pred, zero_division=0),
        "precisao": precision_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "mcc": matthews_corrcoef(y, pred),
        "acuracia_balanceada": balanced_accuracy_score(y, pred),
        "limiar": limiar,
    }


def recall_por_modo(teste: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    """Para cada modo de falha: ciclos do teste com o modo e fração prevista como falha."""
    linhas = []
    for col in ["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]:
        m = (teste[col] == 1).to_numpy()
        linhas.append(
            {
                "modo": col.replace("falha_", "").upper(),
                "ciclos_no_teste": int(m.sum()),
                "detectados": int(pred[m].sum()),
                "recall": float(pred[m].mean()) if m.any() else np.nan,
            }
        )
    sem_modo = (
        (teste["falha"] == 1)
        & (
            teste[["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]].sum(axis=1)
            == 0
        )
    ).to_numpy()
    linhas.append(
        {
            "modo": "SEM MODO",
            "ciclos_no_teste": int(sem_modo.sum()),
            "detectados": int(pred[sem_modo].sum()),
            "recall": float(pred[sem_modo].mean()) if sem_modo.any() else np.nan,
        }
    )
    return pd.DataFrame(linhas)
```

### T4.2 `tests/test_modelagem.py`

```python
import numpy as np
import pandas as pd
import pytest

from manutencao.config import ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA
from manutencao.modelagem import (
    avaliar_cv,
    metricas_teste,
    modelos_candidatos,
    montar_pipeline,
    recall_por_modo,
)
from manutencao.preparacao import dividir_treino_teste


@pytest.fixture(scope="module")
def treino(df):
    return dividir_treino_teste(df)[0]


def test_candidatos():
    assert list(modelos_candidatos()) == [
        "dummy",
        "regressao_logistica",
        "arvore_decisao",
        "random_forest",
        "gradient_boosting",
    ]


@pytest.mark.parametrize("atributos", [ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA])
def test_pipeline_ajusta_e_preve(treino, atributos):
    pipe = montar_pipeline("arvore_decisao", atributos).fit(treino[atributos], treino["falha"])
    proba = pipe.predict_proba(treino[atributos])[:, 1]
    assert proba.shape == (len(treino),) and ((proba >= 0) & (proba <= 1)).all()


def test_dummy_tem_pr_auc_igual_a_prevalencia(treino):
    r = avaliar_cv(
        montar_pipeline("dummy", ATRIBUTOS_BRUTO), treino[ATRIBUTOS_BRUTO], treino["falha"]
    )
    assert r["pr_auc_media"] == pytest.approx(treino["falha"].mean(), abs=0.005)
    assert r["roc_auc_media"] == pytest.approx(0.5)


def test_engenharia_supera_bruto_na_arvore(treino):
    y = treino["falha"]
    bruto = avaliar_cv(
        montar_pipeline("arvore_decisao", ATRIBUTOS_BRUTO), treino[ATRIBUTOS_BRUTO], y
    )
    eng = avaliar_cv(
        montar_pipeline("arvore_decisao", ATRIBUTOS_ENGENHARIA), treino[ATRIBUTOS_ENGENHARIA], y
    )
    assert eng["pr_auc_media"] > bruto["pr_auc_media"]


def test_metricas_teste_classificador_perfeito():
    y = pd.Series([0, 0, 1, 1])
    m = metricas_teste(y, np.array([0.1, 0.2, 0.8, 0.9]))
    assert m["pr_auc"] == 1 and m["recall"] == 1 and m["mcc"] == pytest.approx(1)


def test_recall_por_modo(df):
    _, teste = dividir_treino_teste(df)
    pred = teste["falha"].to_numpy()
    t = recall_por_modo(teste, pred).set_index("modo")
    assert t.loc["HDF", "recall"] == 1.0
    assert t.loc["SEM MODO", "ciclos_no_teste"] >= 0
```

### T4.3 `notebooks/04_modelagem_preditiva.ipynb` — célula por célula

| # | Tipo | Conteúdo |
|---|---|---|
| 1 | md | `# 04 · Modelagem preditiva` · autor Renato Colin Neto · fase CRISP-DM: modelagem e avaliação · desenho experimental resumido |
| 2 | code | Célula padrão de ambiente |
| 3 | code | imports: `joblib`, `numpy as np`, `pandas as pd`, `matplotlib.pyplot as plt`, `seaborn as sns`; `from sklearn.inspection import permutation_importance`; `from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay`; `from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree`; `from manutencao.config import ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA, DIR_MODELOS, DIR_TABELAS, SEED`; `from manutencao.preparacao import carregar_preparado, dividir_treino_teste, separar_x_y`; `from manutencao import modelagem as mo`; util; `configurar_graficos()` |
| 4 | code | `df = carregar_preparado()` · `treino, teste = dividir_treino_teste(df)` · `CONJUNTOS = {"bruto": ATRIBUTOS_BRUTO, "engenharia": ATRIBUTOS_ENGENHARIA}` · `X_tr, y_tr = separar_x_y(treino, ATRIBUTOS_ENGENHARIA)` · `X_te, y_te = separar_x_y(teste, ATRIBUTOS_ENGENHARIA)` · print dos tamanhos e prevalências |
| 5 | md | Desenho experimental completo (as bullets acima) e por que o teste fica guardado |
| 6 | code | `comp = mo.comparar_modelos(treino, CONJUNTOS)` · `salvar_tabela(comp, "04_comparacao_cv")` · exibir colunas `modelo, conjunto, pr_auc_media, pr_auc_dp, roc_auc_media, recall_media, precisao_media, f1_media, mcc_media, tempo_ajuste_s` |
| 7 | code | Gráfico de barras agrupadas: `pr_auc_media` por modelo, uma cor por conjunto, barras de erro = `pr_auc_dp`, linha horizontal na prevalência → `salvar_figura(fig, "04_comparacao_modelos")` |
| 8 | md | Interpretar: ganho de `engenharia` sobre `bruto` em cada modelo; ROC-AUC alta até em modelos fracos (por isso PR-AUC); qual modelo vence |
| 9 | code | `melhor = comp.query("conjunto == 'engenharia' and modelo != 'dummy'").iloc[0]["modelo"]` · `busca = mo.ajustar_hiperparametros(melhor, ATRIBUTOS_ENGENHARIA, X_tr, y_tr)` · `top = pd.DataFrame(busca.cv_results_).sort_values("rank_test_score").head(10)[["params", "mean_test_score", "std_test_score"]]` · `salvar_tabela(top, "04_busca_hiperparametros")` · print `busca.best_params_`, `busca.best_score_` |
| 10 | code | `final = busca.best_estimator_` · `DIR_MODELOS.mkdir(exist_ok=True)` · `joblib.dump(final, DIR_MODELOS / "modelo_final.joblib")` · `salvar_tabela(pd.DataFrame([{"modelo": melhor, "conjunto": "engenharia", "parametros": str(busca.best_params_), "pr_auc_cv": busca.best_score_}]), "04_modelo_escolhido")` |
| 11 | md | Probabilidades *out-of-fold* (para o limiar de custo do notebook 05) |
| 12 | code | `oof = mo.probabilidades_oof(final, X_tr, y_tr)` · `salvar_tabela(pd.DataFrame({"udi": treino["udi"], "falha": y_tr, "proba": oof}), "04_oof_treino")` |
| 13 | md | **Avaliação final no teste (uma única vez)** |
| 14 | code | `proba = final.predict_proba(X_te)[:, 1]` · `pred = (proba >= 0.5).astype(int)` · `met = pd.DataFrame([mo.metricas_teste(y_te, proba)])` · `salvar_tabela(met, "04_metricas_teste")` · exibir · também salvar `04_predicoes_teste`: `teste[["udi", "falha", "falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]].assign(proba=proba)` com as colunas na ordem do contrato (`udi, falha, proba, falha_twf, falha_hdf, falha_pwf, falha_osf, falha_rnf`) |
| 15 | code | Figura com 3 painéis: `ConfusionMatrixDisplay.from_predictions(y_te, pred)`, `PrecisionRecallDisplay.from_predictions(y_te, proba)`, `RocCurveDisplay.from_predictions(y_te, proba)` → `"04_avaliacao_teste"` |
| 16 | code | `rpm = mo.recall_por_modo(teste, pred)` · `salvar_tabela(rpm, "04_recall_por_modo")` · exibir |
| 17 | md | Interpretar: comparar métricas do teste com a média da CV (consistência = sem sobreajuste); quais modos são detectados e quais escapam, e por quê (ligar com §2.1 do plano e com os gráficos de regra do notebook 03) |
| 18 | code | `imp = permutation_importance(final, X_te, y_te, scoring="average_precision", n_repeats=10, random_state=SEED, n_jobs=-1)` · DataFrame `atributo, importancia_media, importancia_dp` ordenado · `salvar_tabela(..., "04_importancia_permutacao")` · barras horizontais com erro → `"04_importancia_permutacao"` |
| 19 | md | Interpretar a importância (quais atributos o modelo realmente usa; atributos com importância ~0) |
| 20 | md | **Interpretabilidade: árvore rasa** — uma árvore de profundidade 3 treinada no treino com `engenharia`, só para ler as regras aprendidas |
| 21 | code | `arv = mo.montar_pipeline("arvore_decisao", ATRIBUTOS_ENGENHARIA).set_params(modelo__max_depth=3).fit(X_tr, y_tr)` · `nomes = ["tipo"] + [c for c in ATRIBUTOS_ENGENHARIA if c != "tipo"]` (ordem do `ColumnTransformer`) · `texto = export_text(arv.named_steps["modelo"], feature_names=nomes)` · `print(texto)` · `(DIR_TABELAS / "04_regras_arvore_rasa.txt").write_text(texto, encoding="utf-8")` · `plot_tree(..., feature_names=nomes, class_names=["sem falha", "falha"], filled=True)` em figura 16×7 → `"04_arvore_rasa"` |
| 22 | md | Comparar os limiares aprendidos pela árvore com as regras documentadas (8,6 K e 1380 rpm; 3500/9000 W; 11–13 mil min·Nm) — **usar os valores que aparecerem na saída**, não estes |
| 23 | md | **Conclusões** (6–8 bullets com números das tabelas `04_*`) |

Executar `jupyter nbconvert --to notebook --execute --inplace notebooks/04_modelagem_preditiva.ipynb`
e `ruff format notebooks/04_modelagem_preditiva.ipynb`. `models/modelo_final.joblib` **não** é
commitado (está no `.gitignore`); as tabelas `04_*.csv` **são** (o notebook 05 depende delas).

### T4.4 README — o que escrever

- **§2.3.2 Modelagem preditiva**: aprendizado supervisionado, classificação binária; os 5
  modelos e por que cada um está ali; os 2 conjuntos de atributos; tratamento do
  desbalanceamento; pipelines do scikit-learn (pré-processamento dentro da validação →
  sem vazamento).
- **§2.4.2 Validação e métricas**: divisão 80/20 estratificada, CV 5-fold estratificada,
  busca aleatória; definição curta de cada métrica e por que PR-AUC é a principal; regra de
  uso único do teste.
- **§3.1.2 Modelos preditivos (implementação)**: funções de `modelagem.py` (tabela função →
  o que faz); hiperparâmetros escolhidos (`04_modelo_escolhido.csv`); onde o modelo é salvo.
- **§3.2.3 Desempenho dos modelos**: tabela resumida da `04_comparacao_cv.csv` (10 linhas,
  colunas PR-AUC média ± dp, ROC-AUC, recall, precisão, MCC); métricas do teste
  (`04_metricas_teste.csv`); recall por modo (`04_recall_por_modo.csv`); figuras
  `04_comparacao_modelos.png`, `04_avaliacao_teste.png`, `04_importancia_permutacao.png`,
  `04_arvore_rasa.png`.
- **§3.3.1 Eficácia técnica e limitações**: o modelo resolve o problema? (desempenho no teste
  consistente com a CV); ganho da engenharia de atributos; o que escapa (TWF/RNF/sem modo) e
  por que é esperado; **dataset sintético gerado por regras** → desempenho não se transfere
  direto para uma fábrica real; sem série temporal (cada ciclo é independente; não estima vida
  útil restante); rótulos inconsistentes (9 + 18); o que faria diferente com dados reais.
- §4: acrescentar referências que você citar e que não estejam na lista do Adrian.

### T4.5 Commits sugeridos

1. `feat(modelagem): pré-processamento e pipelines dos cinco modelos candidatos`
2. `feat(modelagem): validação cruzada estratificada com PR-AUC, MCC e demais métricas`
3. `feat(modelagem): busca de hiperparâmetros, probabilidades out-of-fold e métricas de teste`
4. `feat(modelagem): recall por modo de falha`
5. `test(modelagem): pipelines, piso do dummy, ganho da engenharia e métricas`
6. `feat(notebook): 04 modelagem preditiva executado`
7. `docs(readme): seções 2.3.2, 2.4.2, 3.1.2, 3.2.3 e 3.3.1`

PR: `/tbd-pr` — título = título da issue #4, `Closes #4`, revisor `igorSeberino`. Avisar o Gabriel no
grupo assim que mergear (o T6 depende das tabelas `04_oof_treino.csv` e `04_predicoes_teste.csv`).

### T4.6 Critérios de aceite

- [ ] `pytest -q` verde (7 testes do T4 + anteriores).
- [ ] Notebook 04 roda do início ao fim (local e CI).
- [ ] Tabelas: `04_comparacao_cv`, `04_busca_hiperparametros`, `04_modelo_escolhido`,
      `04_oof_treino` (8.000 linhas), `04_metricas_teste`, `04_predicoes_teste` (2.000 linhas),
      `04_recall_por_modo`, `04_importancia_permutacao` + `04_regras_arvore_rasa.txt`.
- [ ] Figuras: `04_comparacao_modelos`, `04_avaliacao_teste`, `04_importancia_permutacao`, `04_arvore_rasa`.
- [ ] `X_te`/`y_te` (teste) só são usados a partir da célula 13.
- [ ] Commits aparecem como `rcolinneto`.

---

## Sua revisão do T6 (Gabriel)

Conferir que o limiar e o limite de desgaste são escolhidos com `04_oof_treino.csv` e com o
treino (nunca com o teste); que o `merge` por `udi` usa `validate="one_to_one"`; que o texto
deixa claro que os custos são hipóteses; rodar `pytest -q`. Comentar pelo menos 1 ponto.
