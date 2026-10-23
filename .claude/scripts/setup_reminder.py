"""Hook SessionStart: lembra de rodar /setup enquanto o ambiente não foi validado.

O marcador é gravado por ``.claude/skills/setup/scripts/check_environment.py``.
O esquema de hash precisa ficar igual nos dois arquivos.
"""

import hashlib
import json
import sys
from pathlib import Path


def caminho_marcador(cwd: str) -> Path:
    normalizado = str(Path(cwd).resolve()).lower()
    digest = hashlib.sha256(normalizado.encode("utf-8")).hexdigest()[:16]
    return Path.home() / ".claude" / "data-vigia" / "setup" / f"{digest}.json"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd", "")
        if not cwd or caminho_marcador(cwd).exists():
            return
        print(
            json.dumps(
                {
                    "systemMessage": (
                        "Ambiente do data.vigia ainda não validado nesta máquina. "
                        "Rode /setup (confere git, identidade do commit, gh, venv e dados) "
                        "antes de começar uma tarefa."
                    )
                }
            )
        )
    except Exception:  # noqa: BLE001 — hook nunca pode quebrar a sessão
        return


if __name__ == "__main__":
    main()
