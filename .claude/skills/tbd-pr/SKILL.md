---
name: tbd-pr
description: Abre o PR quando a branch está pronta — roda lint, testes, execução do notebook e a revisão de conformidade do agente revisor-dados antes do push — ou finaliza o ciclo depois do merge (volta para a main, apaga a branch, confere a autoria no GitHub). Detecta o estado sozinho. Use ao terminar a branch e de novo depois do merge.
allowed-tools: Bash(gh issue view:*), Bash(gh pr list:*), Bash(gh pr create:*), Bash(gh pr edit:*), Bash(gh api repos/igorSeberino/data.vigia/commits/*), Bash(python .claude/scripts/projeto.py:*), Bash(git status:*), Bash(git push:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git switch:*), Bash(git pull:*), Bash(git fetch:*), Bash(git rebase origin/main), Bash(git rev-parse:*), Bash(ruff check:*), Bash(ruff format --check:*), Bash(pytest:*), Bash(jupyter nbconvert:*), Read, Agent(revisor-dados)
---

Branch atual: !`git branch --show-current`

Se a branch for `main`, **aborte** e oriente `/tbd-start`.

## 1. Estado do PR desta branch

`gh pr list --repo igorSeberino/data.vigia --head {branch} --state all --json number,state,url --limit 1`

- vazio → **Abrir PR** · `OPEN` → mostre a URL e pare · `MERGED` → **Finalizar** ·
  `CLOSED` sem merge → pergunte o que fazer.

## Abrir PR

O nome da branch é `{tipo}/{número}-{slug}`; se não for, aborte e oriente `/tbd-start`.

1. `gh issue view {número} --repo igorSeberino/data.vigia --json title,body` — guarde o título.
2. `git status` — se houver mudança não commitada, oriente `/tbd-commit` e pare.
3. Atualize com a main: `git fetch origin && git rebase origin/main`. Conflito → pare e ajude a
   resolver mantendo o trabalho dos dois lados.
4. **Portões (rode, não pergunte)** — todos precisam passar:
   - `ruff check .` e `ruff format --check .`
   - `pytest -q`
   - se a branch tocou um notebook: `jupyter nbconvert --to notebook --execute notebooks/{nb}.ipynb --output-dir {pasta temporária}`
     (só confere que executa; o notebook commitado precisa já estar executado com saída)
5. **Revisão de conformidade** — `Agent(revisor-dados)`, Modo 2, sobre esta branch. Achado ❌ →
   mostre e corrija antes de seguir. Só pule se o usuário pedir explicitamente (ex.: branch só de
   texto) e registre o pulo em "Notas ao revisor".
6. Confirme com o usuário e faça `git push -u origin {branch}` (com `--force-with-lease` só se o
   rebase reescreveu commits já enviados).
7. Corpo: `templates/pr-body.md`, preenchido com `git log origin/main..HEAD --oneline` e
   `git diff origin/main...HEAD --stat`. Título = **título exato da issue**.
8. Mostre título e corpo e **pergunte antes de criar**.
9. `gh pr create --repo igorSeberino/data.vigia --base main --title "..." --body "..."`
10. Revisor pela matriz (§5 do plano):

    | Issue | Revisor |
    |---|---|
    | #1 | `rcolinneto` |
    | #2 | `adrian-cesar` |
    | #3 | `gabrielcarvallho` |
    | #4 | `igorSeberino` |
    | #5 | `igorSeberino` |
    | #6 | `rcolinneto` |
    | #7 | `gabrielcarvallho,adrian-cesar` |
    | outra | quem o usuário indicar |

    `gh pr edit {pr} --repo igorSeberino/data.vigia --add-reviewer {revisor}`
11. `python .claude/scripts/projeto.py status {número} "In Review"` (se falhar por escopo, siga).
12. Informe a URL, o revisor e que o merge exige CI verde + 1 aprovação, com
    **"Create a merge commit"** (nunca squash — preserva a autoria de cada commit). Depois do
    merge, rode `/tbd-pr` de novo.

## Finalizar (PR já mergeado)

1. `git switch main && git pull`
2. Autoria: pegue o commit de merge com
   `gh pr list --repo igorSeberino/data.vigia --head {branch} --state merged --json mergeCommit --jq '.[0].mergeCommit.oid'`,
   liste os commits do PR com `git log --format=%H {merge}^1..{merge}^2` e, para cada um, confira
   `gh api repos/igorSeberino/data.vigia/commits/{sha} --jq .author.login`. Se algum vier `null`,
   avise: o e-mail usado não está vinculado à conta — adicionar em https://github.com/settings/emails
   (a atribuição passa a valer retroativamente quando o e-mail é verificado).
3. `git branch -d {branch}` (nunca `-D`; se o git recusar, avise e não force).
4. O card vai para Done sozinho quando a issue fecha pelo `Closes #`. Confirme com
   `python .claude/scripts/projeto.py ver {número}`; se não estiver, `... status {número} Done`.
5. Ciclo encerrado — próximo: revisar o PR que é seu na matriz, ou `/tbd-start`.
