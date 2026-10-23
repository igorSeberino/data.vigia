---
name: setup
description: Confere se a máquina está pronta para trabalhar no data.vigia — git, identidade do commit (e-mail vinculado à conta, senão a contribuição não aparece), gh com permissão no repo, venv com as dependências e o CSV íntegro. Use logo depois de clonar, ou quando o lembrete de início de sessão pedir.
allowed-tools: Bash(python .claude/skills/setup/scripts/check_environment.py)
disallowed-tools: Write, Edit, Bash(git push:*), Bash(git commit:*)
---

Checagem somente leitura. A única escrita é o marcador de "setup validado" em
`~/.claude/data-vigia/setup/`, feita pelo próprio script quando tudo obrigatório passa.

1. Rode, a partir da raiz do repositório: `python .claude/skills/setup/scripts/check_environment.py`
   (com o `.venv` ativo — o script também confere isso).
2. Mostre o relatório inteiro ao usuário, sem resumir.
3. Se houver `FALHA`, aponte a linha `→` de correção que o script imprimiu. Não corrija
   sozinho: `gh auth login` é interativo e a identidade do commit é decisão do usuário.
   Peça para rodar `/setup` de novo depois.
4. Se tudo passou, o próximo passo é `/tbd-start <número da issue>` — a tabela de tarefas
   está em `docs/plano/00-VISAO-GERAL.md` §5 e no Project
   https://github.com/users/igorSeberino/projects/2.
