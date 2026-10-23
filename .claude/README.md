# Time de agentes do data.vigia

Adaptação do [`team.ludens`](https://github.com/gcarvalhow/team.ludens) para este projeto.
Fica no próprio repositório (`.claude/`): o Claude Code carrega sozinho ao abrir a pasta —
não há plugin para instalar nem marketplace para atualizar.

| Peça | Comando | Para quê |
|---|---|---|
| `skills/setup` | `/setup` | confere git, **identidade do commit**, gh, venv e o CSV antes de começar |
| `skills/tbd-start` | `/tbd-start 3` | assume a issue planejada, move o card e cria a branch `{tipo}/{n}-{slug}` |
| `skills/tbd-commit` | `/tbd-commit` | Conventional Commits em português, conferindo o e-mail do autor |
| `skills/tbd-pr` | `/tbd-pr` | portões (ruff, pytest, notebook), revisão do `revisor-dados`, PR com revisor da matriz; depois do merge, finaliza e confere a autoria |
| `agents/revisor-dados.md` | chamado pelo `/tbd-pr` (ou "use o revisor-dados para…") | revisão de conformidade somente leitura: vazamento de alvo, uso do teste, semente, números sem fonte, contrato entre notebooks |
| `scripts/projeto.py` | usado pelas skills | move cards e define Area/Priority no Project @vigia |
| `scripts/guard_mutations.py` | hook do revisor | impede o revisor de alterar o repositório |
| `scripts/setup_reminder.py` | hook de início de sessão | lembra de rodar `/setup` |

## O que ficou de fora do team.ludens, e por quê

| Peça original | Decisão | Motivo |
|---|---|---|
| `product-thinking` + `feature-design` → `logic-design` → `feature-implementation-spec` | removido | o escopo é fixado pelo enunciado e as specs de implementação (com código) já estão em `docs/plano/`; um pipeline de produto só repetiria esse trabalho |
| `tbd-scope` | removido | todas as tarefas já estão escopadas nas issues #1–#7; trabalho novo é pequeno e entra pelo modo B do `/tbd-start` |
| `backend-architecture` / `frontend-architecture` | trocadas por `CLAUDE.md` + `docs/plano/` | o projeto tem um pacote Python e cinco notebooks; as regras cabem numa página e o plano já descreve a arquitetura |
| `senior-dev` | virou `revisor-dados` | a revisão de conformidade é a parte que mais vale aqui: os erros caros são vazamento de alvo, olhar o teste e número inventado no relatório |
| plugin/marketplace | virou pasta `.claude/` | um único repositório; nada para instalar ou versionar à parte |
