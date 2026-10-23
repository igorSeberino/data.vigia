"""Hook PreToolUse do agente revisor-dados: bloqueia comandos que alteram o repositório.

Recebe o JSON do Claude Code no stdin. Se o comando Bash casar com um padrão de
mutação, devolve ``permissionDecision: deny`` com a explicação.
"""

import json
import re
import sys

PADROES_MUTACAO = [
    r"\bgit\s+(push|commit|merge|rebase|reset|checkout|switch|restore|stash|tag|branch\s+-[dD])\b",
    r"\bgit\s+add\b",
    r"\bgh\s+(issue|pr)\s+(create|edit|close|reopen|comment|merge|review|ready)\b",
    r"\bgh\s+project\s+(item-add|item-edit|item-create|item-delete|edit|field-create)\b",
    r"\bgh\s+api\b.*(-X|--method)\s*(POST|PUT|PATCH|DELETE)\b",
    r"\bruff\s+check\b.*--fix\b",
    r"\bruff\s+format\b(?!.*--check)",
    r"\bnbconvert\b.*--inplace\b",
    r"\b(rm|mv|del)\s",
    r"(^|[^<>])>{1,2}\s*[\w./\\-]",
]


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    comando = payload.get("tool_input", {}).get("command", "")
    for padrao in PADROES_MUTACAO:
        if re.search(padrao, comando, re.IGNORECASE):
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "O revisor-dados é somente leitura — comando bloqueado: "
                                f"`{comando}`. Devolva isso como recomendação, não execute."
                            ),
                        }
                    }
                )
            )
            return


if __name__ == "__main__":
    main()
