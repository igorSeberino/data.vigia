# Nome da branch

Formato: `{tipo}/{número-da-issue}-{slug}` — slug **em inglês**, minúsculo, hífens, até 20
caracteres. O número já é o rastreio completo (`gh issue view {número}`); o slug só ajuda a
reconhecer a branch.

1. Reduza o assunto a 2–3 palavras-chave.
2. Traduza o sentido para inglês técnico (traduzir de verdade, não só tirar acento).
3. Minúsculo, espaços viram hífen, sem caractere especial, máximo 20 caracteres.

Branches das tarefas planejadas (já escritas no corpo de cada issue):

| Issue | Branch |
|---|---|
| #1 coleta e preparação | `feat/1-data-prep` |
| #2 modelo dimensional | `feat/2-star-schema` |
| #3 análise exploratória | `feat/3-eda` |
| #4 modelagem preditiva | `feat/4-predictive-models` |
| #5 introdução e referências | `docs/5-intro-references` |
| #6 impacto no negócio | `feat/6-business-impact` |
| #7 integração final | `docs/7-final-report` |

Exemplos para trabalho novo:
- `fix`, #12, "notebook 03 falha no Colab por fonte ausente" → `fix/12-colab-font`
- `refactor`, #15, "extrair gráfico de barras repetido" → `refactor/15-bar-chart-helper`
- `docs`, #16, "corrigir referência ABNT do Matzka" → `docs/16-matzka-reference`
