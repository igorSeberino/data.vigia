#!/usr/bin/env python3
"""Checagem de ambiente do data.vigia (somente leitura).

Confere git, identidade do commit, gh, acesso ao repositório, Python/venv, dependências e
o CSV dos dados. Só escreve o marcador de "setup validado" no fim, se tudo obrigatório
passar. O esquema de hash precisa ficar igual ao de ``.claude/scripts/setup_reminder.py``.
"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "igorSeberino/data.vigia"
SHA256_CSV = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"
# login GitHub -> e-mails já vinculados à conta (comprovados por commits atribuídos)
EQUIPE = {
    "igorSeberino": ("Igor Seberino", "igorseberino@gmail.com"),
    "adrian-cesar": ("Adrian Cesar Gonçalves", "adriancg3006@gmail.com"),
    "gabrielcarvallho": ("Gabriel Carvalho", "gabriellccarvalho.dev@gmail.com"),
    "rcolinneto": ("Renato Colin Neto", "renato.colin@catolicasc.edu.br"),
}
PACOTES = ["pandas", "numpy", "sklearn", "scipy", "matplotlib", "seaborn", "pytest", "nbconvert"]


def caminho_marcador(cwd: str) -> Path:
    normalizado = str(Path(cwd).resolve()).lower()
    digest = hashlib.sha256(normalizado.encode("utf-8")).hexdigest()[:16]
    return Path.home() / ".claude" / "data-vigia" / "setup" / f"{digest}.json"


def rodar(args: list[str]) -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


resultados: list[tuple[bool, bool, str, str, str]] = []  # ok, obrigatorio, nome, detalhe, correção


def registrar(ok: bool, nome: str, detalhe: str, correcao: str = "", obrigatorio: bool = True):
    resultados.append((ok, obrigatorio, nome, detalhe, correcao))


def checar_git() -> None:
    if not shutil.which("git"):
        registrar(False, "git", "não encontrado no PATH", "instale: https://git-scm.com/downloads")
        return
    code, origem = rodar(["git", "remote", "get-url", "origin"])
    ok = code == 0 and "data.vigia" in origem
    registrar(
        ok,
        "git — clone do data.vigia",
        origem or "sem origin",
        f"clone https://github.com/{REPO}.git e rode daqui",
    )


def checar_identidade(login: str | None) -> None:
    _, email = rodar(["git", "config", "user.email"])
    _, nome = rodar(["git", "config", "user.name"])
    emails = {e: lg for lg, (_, e) in EQUIPE.items()}
    if email not in emails:
        registrar(
            False,
            "identidade do commit",
            f"user.email = {email or '(vazio)'}",
            "git config user.email <seu e-mail da tabela §4 de docs/plano/00-VISAO-GERAL.md>",
        )
        return
    dono = emails[email]
    if login and login != dono:
        registrar(
            False,
            "identidade do commit",
            f"user.email é de {dono}, mas o gh está logado como {login}",
            "use o seu próprio e-mail e a sua própria conta no gh",
        )
        return
    registrar(True, "identidade do commit", f"{nome} <{email}> → conta {dono}")


def checar_gh() -> str | None:
    if not shutil.which("gh"):
        registrar(False, "gh", "não encontrado no PATH", "instale: https://cli.github.com")
        return None
    code, login = rodar(["gh", "api", "user", "--jq", ".login"])
    if code != 0:
        registrar(False, "gh — autenticado", login, "rode `gh auth login` (fora desta sessão)")
        return None
    code, perm = rodar(["gh", "api", f"repos/{REPO}", "--jq", ".permissions.push"])
    ok = code == 0 and perm == "true"
    registrar(
        ok,
        "gh — permissão de escrita no repo",
        f"{login}: push={perm}",
        f"aceite o convite em https://github.com/{REPO}/invitations",
    )
    code, escopos = rodar(["gh", "auth", "status"])
    registrar(
        "project" in escopos,
        "gh — escopo `project` (mover cards no Project)",
        "ok" if "project" in escopos else "ausente",
        "gh auth refresh -h github.com -s project",
        obrigatorio=False,
    )
    return login


def checar_python() -> None:
    versao = sys.version.split()[0]
    registrar(
        sys.version_info >= (3, 10),
        "python >= 3.10",
        versao,
        "uv venv --python 3.12 .venv e ative o venv",
    )
    no_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    registrar(
        no_venv,
        "venv ativo",
        sys.prefix,
        "source .venv/Scripts/activate (Windows) ou source .venv/bin/activate",
    )
    faltando = [p for p in PACOTES if importlib.util.find_spec(p) is None]
    registrar(
        not faltando,
        "dependências",
        "ok" if not faltando else f"faltam: {', '.join(faltando)}",
        "uv pip install -r requirements-dev.txt",
    )
    for ferramenta in ("ruff", "uv"):
        registrar(
            bool(shutil.which(ferramenta)),
            ferramenta,
            shutil.which(ferramenta) or "ausente",
            "uv pip install -r requirements-dev.txt"
            if ferramenta == "ruff"
            else "winget install --id astral-sh.uv -e",
            obrigatorio=ferramenta == "ruff",
        )


def checar_dados() -> None:
    csv = Path("data/raw/ai4i2020.csv")
    if not csv.exists():
        registrar(False, "dados", "data/raw/ai4i2020.csv ausente", "git pull na main")
        return
    obtido = hashlib.sha256(csv.read_bytes()).hexdigest()
    registrar(
        obtido == SHA256_CSV,
        "dados — SHA-256 do CSV",
        obtido[:16] + "…",
        "git checkout -- data/raw/ai4i2020.csv",
    )


def main() -> None:
    checar_git()
    login = checar_gh()
    checar_identidade(login)
    checar_python()
    checar_dados()
    print("== data.vigia :: checagem de ambiente ==\n")
    tudo_ok = True
    for ok, obrigatorio, nome, detalhe, correcao in resultados:
        marca = "OK   " if ok else ("FALHA" if obrigatorio else "AVISO")
        print(f"[{marca}] {nome}: {detalhe}")
        if not ok:
            print(f"        → {correcao}")
            tudo_ok = tudo_ok and not obrigatorio
    print()
    if tudo_ok:
        marcador = caminho_marcador(os.getcwd())
        marcador.parent.mkdir(parents=True, exist_ok=True)
        marcador.write_text(json.dumps({"validado": True}), encoding="utf-8")
        print("Tudo obrigatório passou. Próximo passo: /tbd-start <número da sua issue>.")
    else:
        print("Corrija os itens em FALHA e rode /setup de novo.")
        sys.exit(1)


if __name__ == "__main__":
    main()
