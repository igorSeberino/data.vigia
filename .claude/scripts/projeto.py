#!/usr/bin/env python3
"""Atalhos para o Project @vigia (usuário igorSeberino, número 2) via ``gh api graphql``.

Uso (da raiz do repositório):
    python .claude/scripts/projeto.py status 3 "In Progress"
    python .claude/scripts/projeto.py campos 9 --status Backlog --area dados --priority 2
    python .claude/scripts/projeto.py ver 3

Adiciona a issue ao Project se ela ainda não estiver lá. Precisa do escopo ``project`` no
token do gh (``gh auth refresh -h github.com -s project``) e de ser colaborador do Project.
"""

import argparse
import json
import subprocess
import sys

REPO_DONO, REPO_NOME = "igorSeberino", "data.vigia"
PROJETO_ID = "PVT_kwHOCjyo5c4BoYXk"
CAMPOS = {
    "status": (
        "PVTSSF_lAHOCjyo5c4BoYXkzhm4v2c",
        {
            "Backlog": "6eb400d5",
            "In Progress": "8c0f06d3",
            "In Review": "5ce53a89",
            "Done": "c873df1f",
        },
    ),
    "area": (
        "PVTSSF_lAHOCjyo5c4BoYXkzhm4v84",
        {
            "dados": "231b6f66",
            "análise": "cbe4ebd9",
            "modelagem": "e6472304",
            "docs": "7cdabe28",
            "infra": "4dab1bcd",
        },
    ),
    "priority": (
        "PVTSSF_lAHOCjyo5c4BoYXkzhm4v9k",
        {"3": "539f2bf4", "2": "d5fd53c9", "1": "52cc30df", "0": "81cedb2e"},
    ),
}


def graphql(consulta: str, **variaveis) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={consulta}"]
    for chave, valor in variaveis.items():
        args += ["-F" if isinstance(valor, int) else "-f", f"{chave}={valor}"]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        dica = ""
        if "INSUFFICIENT_SCOPES" in r.stdout + r.stderr or "scope" in (r.stdout + r.stderr).lower():
            dica = "\nDica: gh auth refresh -h github.com -s project"
        sys.exit(f"Erro do gh: {r.stderr.strip() or r.stdout.strip()}{dica}")
    return json.loads(r.stdout)


def item_da_issue(numero: int) -> tuple[str, str | None]:
    dados = graphql(
        """query($o:String!,$r:String!,$n:Int!){ repository(owner:$o,name:$r){ issue(number:$n){
             id projectItems(first:10){ nodes{ id project{ id } } } } } }""",
        o=REPO_DONO,
        r=REPO_NOME,
        n=numero,
    )
    issue = dados["data"]["repository"]["issue"]
    if issue is None:
        sys.exit(f"Issue #{numero} não existe em {REPO_DONO}/{REPO_NOME}")
    for item in issue["projectItems"]["nodes"]:
        if item["project"]["id"] == PROJETO_ID:
            return issue["id"], item["id"]
    return issue["id"], None


def garantir_item(numero: int) -> str:
    issue_id, item_id = item_da_issue(numero)
    if item_id:
        return item_id
    dados = graphql(
        """mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p, contentId:$c}){ item{ id } } }""",
        p=PROJETO_ID,
        c=issue_id,
    )
    return dados["data"]["addProjectV2ItemById"]["item"]["id"]


def definir(item_id: str, campo: str, valor: str) -> None:
    campo_id, opcoes = CAMPOS[campo]
    if valor not in opcoes:
        sys.exit(f"Valor inválido para {campo}: {valor!r}. Opções: {', '.join(opcoes)}")
    graphql(
        """mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:{
             projectId:$p, itemId:$i, fieldId:$f, value:{singleSelectOptionId:$o}}){ projectV2Item{ id } } }""",
        p=PROJETO_ID,
        i=item_id,
        f=campo_id,
        o=opcoes[valor],
    )
    print(f"#{args.numero}: {campo} = {valor}")


def ver(numero: int) -> None:
    _, item_id = item_da_issue(numero)
    if not item_id:
        print(f"#{numero} não está no Project")
        return
    dados = graphql(
        """query($i:ID!){ node(id:$i){ ... on ProjectV2Item{ fieldValues(first:20){ nodes{
             ... on ProjectV2ItemFieldSingleSelectValue{ name field{ ... on ProjectV2FieldCommon{ name } } } } } } } }""",
        i=item_id,
    )
    for v in dados["data"]["node"]["fieldValues"]["nodes"]:
        if v:
            print(f"#{numero}: {v['field']['name']} = {v['name']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="acao", required=True)
    p_status = sub.add_parser("status")
    p_status.add_argument("numero", type=int)
    p_status.add_argument("valor", choices=list(CAMPOS["status"][1]))
    p_campos = sub.add_parser("campos")
    p_campos.add_argument("numero", type=int)
    p_campos.add_argument("--status", choices=list(CAMPOS["status"][1]))
    p_campos.add_argument("--area", choices=list(CAMPOS["area"][1]))
    p_campos.add_argument("--priority", choices=list(CAMPOS["priority"][1]))
    p_ver = sub.add_parser("ver")
    p_ver.add_argument("numero", type=int)
    args = parser.parse_args()

    if args.acao == "ver":
        ver(args.numero)
    elif args.acao == "status":
        definir(garantir_item(args.numero), "status", args.valor)
    else:
        item = garantir_item(args.numero)
        for campo in ("status", "area", "priority"):
            if getattr(args, campo):
                definir(item, campo, getattr(args, campo))
