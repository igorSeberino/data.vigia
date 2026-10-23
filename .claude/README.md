# Time de agentes do data.vigia

Baseado no [`team.ludens`](https://github.com/gcarvalhow/team.ludens), reduzido ao que este projeto usa.
Fica no próprio repositório (`.claude/`): o Claude Code carrega sozinho ao abrir a pasta —
não há plugin para instalar nem marketplace para atualizar.

| Peça | Comando | Para quê |
|---|---|---|
| `skills/setup` | `/setup` | confere git, **identidade do commit**, gh, venv e o CSV antes de começar |
| `skills/tbd-start` | `/tbd-start 3` | assume a issue planejada, move o card e cria a branch `{tipo}/{n}-{slug}` |
| `skills/tbd-commit` | `/tbd-commit` | Conventional Commits em português, conferindo o e-mail do autor |
| `skills/tbd-pr` | `/tbd-pr` | portões (ruff, pytest, notebook), revisão do `revisor-dados`, PR com revisor da matriz; depois do merge, finaliza e confere a autoria |
| `agents/revisor-dados.md` | chamado pelo `/tbd-pr` (ou "use o revisor-dados para…") | revisão de conformidade somente leitura: vazamento de alvo, uso do teste, semente, números sem fonte, contrato entre notebooks |
| `scripts/projeto.py` | usado pelas skills | move cards no Project @vigia |
| `scripts/guard_mutations.py` | hook do revisor | impede o revisor de alterar o repositório |
| `scripts/setup_reminder.py` | hook de início de sessão | lembra de rodar `/setup` |

