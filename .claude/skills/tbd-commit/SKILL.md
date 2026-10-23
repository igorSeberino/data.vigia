---
name: tbd-commit
description: Gera um commit Conventional Commits em português a partir do que está staged, conferindo antes que a identidade do commit é a do usuário. Use sempre que for commitar.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git config user.email), Bash(git config user.name), Bash(git commit:*)
disallowed-tools: Bash(git add:*)
---

1. **Identidade** — `git config user.name` e `git config user.email`. O e-mail tem que ser o do
   usuário na tabela §4 de `docs/plano/00-VISAO-GERAL.md`; se não for, **pare** (commit com
   e-mail errado não conta como contribuição de ninguém).
2. **Estado** — `git status` e `git diff --staged`. Se nada estiver staged, mostre `git diff --stat`
   e pergunte o que incluir. **Nunca rode `git add`.**
3. **Tipo** — pela branch: `feat/`→`feat`, `fix/`→`fix`, `refactor/`→`refactor`, `test/`→`test`,
   `docs/`→`docs`, `infra/`→`chore`, `cleanup/`→`cleanup` (remoção de escopo, arquivo ou
   regra que não serve mais). Se o diff claramente não bate com o tipo da branch
   (ex.: só testes numa `feat/`), use o tipo do diff (`test`) — é normal ter vários tipos numa branch.
4. **Escopo** — `references/scope-detection.md`.
5. **Mensagem** — `{tipo}({escopo}): {descrição no imperativo, minúscula, sem ponto final}`, em
   português, até 72 caracteres. Proibido: `update`, `ajustes`, `wip`, `melhorias` — descreva o
   efeito real. Corpo opcional depois de uma linha em branco.
6. **Confirmar** — mostre a mensagem e pergunte antes.
7. `git commit -m "{mensagem}"`.
