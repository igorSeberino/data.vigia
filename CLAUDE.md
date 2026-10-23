# CLAUDE.md — data.vigia (manutenção preditiva, AI4I 2020)

Regras para o Claude de qualquer integrante. O plano completo está em `docs/plano/`.
Cada integrante assina e defende o que commita.

## Projeto
- Problema: prever falha de ciclo de usinagem (alvo `falha`, 3,39 % positivos) e medir o
  impacto financeiro frente às manutenções corretiva e preventiva.
- Dados: `data/raw/ai4i2020.csv` (UCI id 601, CC BY 4.0). Ler SEMPRE via
  `manutencao.dados.carregar_bruto()` / `manutencao.preparacao.carregar_preparado()`.
- Código em `src/manutencao/`; notebooks em `notebooks/`; artefatos em `reports/`.
- Comandos: `ruff check .` · `ruff format .` · `pytest -q` ·
  `jupyter nbconvert --to notebook --execute --inplace notebooks/<nb>.ipynb`.

## Regras que não se quebram
1. Atributos proibidos: `udi`, `id_produto`, `falha_twf`, `falha_hdf`, `falha_pwf`,
   `falha_osf`, `falha_rnf` (use `separar_x_y`, que recusa vazamento).
2. Divisão treino/teste só por `dividir_treino_teste()` (80/20, estratificada, SEED=42).
   O conjunto de teste só é usado no fim do notebook 04 e no notebook 05.
3. Limiar de decisão e parâmetros de estratégia são escolhidos no TREINO (predições
   out-of-fold); o teste só mede.
4. `SEED = 42` (de `manutencao.config`) em tudo que é aleatório.
5. Nenhum número escrito no README sem vir de saída de notebook ou de `reports/tables/`.
   Não invente resultado, referência, autor, data ou revisor.
6. Nunca nomeie função/classe de `src/` começando com `test`/`Test` (ex.: `teste_*`):
   o pytest coleta e quebra. Use `mann_whitney`, `qui_quadrado`, etc.
7. Não altere módulos/seções de outro integrante; peça no PR dele.
8. Figuras via `salvar_figura(fig, "NN_nome")`, tabelas via `salvar_tabela(df, "NN_nome")`,
   NN = número do notebook. Títulos e rótulos de eixo em português, com unidade.

## Notebooks
- Primeira célula de código é SEMPRE a célula padrão de ambiente (abaixo).
- Markdown explica o porquê de cada etapa; conclusões no fim, com números das saídas.
- Commitar executado, com saída, após `ruff format`.

Célula padrão de ambiente:

    # Ambiente: funciona localmente (pasta notebooks/) e no Google Colab
    # (o Colab já traz pandas, scikit-learn e cia.; só falta o código do repositório)
    import subprocess
    import sys
    from pathlib import Path

    REPO = "data.vigia"
    if "google.colab" in sys.modules and not Path(REPO).exists():
        subprocess.run(
            ["git", "clone", "-q", f"https://github.com/igorSeberino/{REPO}.git"], check=True
        )
    RAIZ = next(
        p
        for p in (Path.cwd(), Path.cwd().parent, Path(REPO).resolve())
        if (p / "pyproject.toml").exists()
    )
    sys.path.insert(0, str(RAIZ / "src"))

## Fluxo de trabalho (time de agentes em `.claude/`)
- Primeira vez na máquina: `/setup` (confere identidade do commit, gh, venv e dados).
- Começar tarefa: `/tbd-start <número da issue>` — assume a issue, move o card no Project
  @vigia (https://github.com/users/igorSeberino/projects/2) e cria a branch.
- Commitar: `/tbd-commit` (Conventional Commits em português; nunca `git add` automático).
- Abrir PR: `/tbd-pr` — roda ruff, pytest, o notebook e o agente `revisor-dados` antes do push;
  depois do merge, rodar de novo para finalizar e conferir a autoria.
- Branch: `{tipo}/{número}-{slug-em-inglês}` (ex.: `feat/3-eda`); nunca commitar na `main`.
- Identificadores de código, docstrings, commits, issues e documentação em português;
  só o slug da branch é em inglês.
- PR com o template preenchido (inclusive **Uso de IA**), CI verde e aprovação do revisor da
  matriz (§5 do plano). Merge com "Create a merge commit" (nunca squash).
- Nunca commitar em nome de outra pessoa (`--author`) nem implementar a issue de outro integrante.
