---
name: tbd-start
description: Começa uma tarefa no fluxo Trunk-Based do data.vigia. Com o número de uma issue já planejada (#1–#7), assume a issue, move o card para In Progress e cria a branch. Sem número (bug ou débito descoberto no caminho), abre a issue nova, coloca no Project @vigia e cria a branch. Use ao começar qualquer trabalho.
argument-hint: "[número da issue | descrição do que surgiu]"
allowed-tools: Bash(gh issue view:*), Bash(gh issue list:*), Bash(gh issue create:*), Bash(gh issue edit:*), Bash(gh api user:*), Bash(python .claude/scripts/projeto.py:*), Bash(git status:*), Bash(git switch:*), Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*), Read
---

Repositório: `igorSeberino/data.vigia` · Project: `@vigia` (https://github.com/users/igorSeberino/projects/2)
Usuário do gh: !`gh api user --jq .login`
Branch atual: !`git branch --show-current`

Argumento: $ARGUMENTS

## A. Tarefa planejada (argumento é um número)

As tarefas do trabalho já existem como issues #1–#7 (ver `docs/plano/00-VISAO-GERAL.md` §5).

1. `gh issue view {n} --repo igorSeberino/data.vigia --json number,title,state,assignees,labels,body`.
   Se estiver fechada, pare e avise.
2. Confira se a issue é do usuário: o corpo diz "Responsável: @login". Se não for, **pare** e
   pergunte — ninguém implementa a tarefa de outro integrante (a contribuição precisa aparecer
   na conta certa).
3. Confira dependências na tabela §5 do plano: T2, T3, T4 precisam do #1 fechado; o notebook do
   T6 precisa do #4 fechado (o código do T6 pode começar antes); T7 precisa de #1–#6 fechados.
   Se faltar, avise e pergunte se segue mesmo assim.
4. `gh issue edit {n} --repo igorSeberino/data.vigia --add-assignee @me`
5. `python .claude/scripts/projeto.py status {n} "In Progress"` — se falhar por escopo, mostre a
   dica impressa (`gh auth refresh -h github.com -s project`) e siga sem o Project.
6. Branch: o nome já está no corpo da issue ("Branch: `...`"). Use exatamente ele.
7. `git switch main && git pull && git switch -c {branch}`
8. Resuma: issue, card movido, branch criada, arquivo de tarefas a seguir
   (`docs/plano/0X-NOME.md`), revisor do PR, e que o PR deve sair em até 2 dias.

## B. Trabalho novo (bug, débito técnico, ajuste que surgiu)

1. **Tipo**: `feat` / `fix` / `refactor` / `test` / `docs` / `infra`.
2. **Duplicata**: `gh issue list --repo igorSeberino/data.vigia --state all --search "{palavras-chave}"`.
   Se algo já cobre o assunto, pare e mostre.
3. **Título**: `{tipo}: {descrição técnica em português, minúscula após os dois-pontos, sem ponto final}`.
4. **Corpo**: `templates/issue-body.md` (seções fixas). Bug usa o template de bug do repo
   (`.github/ISSUE_TEMPLATE/bug.md`), débito usa `debito-tecnico.md`.
5. Mostre título e corpo e **pergunte antes de criar**.
6. `gh issue create --repo igorSeberino/data.vigia --title "..." --body "..."` e guarde o número.
7. Labels (`gh issue edit {n} --add-label ...`): o `module: ...` do módulo tocado
   (`dados`, `preparacao`, `modelo-dados`, `eda`, `modelagem`, `custo`), `relatório` se mexe no
   README, `bug` / `débito técnico` conforme o tipo.
8. Project: `python .claude/scripts/projeto.py campos {n} --status "In Progress" --area {area} --priority {p}`
   - **Area**: `infra` se o tipo for `infra`; `docs` se for `docs` ou só README; senão pelo módulo —
     `dados` (dados, preparacao, modelo-dados), `análise` (eda, custo), `modelagem` (modelagem).
   - **Priority**: decida sozinho com `references/priority-rubric.md`.
9. Branch: `references/branch-naming.md`. Depois `git switch main && git pull && git switch -c {branch}`.
10. Resuma issue, labels, campos do Project (com uma linha justificando a Priority) e branch.
