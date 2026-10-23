# Escopo do commit

Nada de lista fixa decorada: olhe os arquivos staged.

| Arquivos staged | Escopo |
|---|---|
| `src/manutencao/config.py`, `util.py` | `config` |
| `src/manutencao/dados.py` | `dados` |
| `src/manutencao/preparacao.py` | `preparacao` |
| `src/manutencao/modelo_dados.py` | `modelo-dados` |
| `src/manutencao/eda.py` | `eda` |
| `src/manutencao/modelagem.py` | `modelagem` |
| `src/manutencao/custo.py` | `custo` |
| `tests/test_<x>.py` sozinho | o escopo do módulo testado, tipo `test` |
| `notebooks/NN_*.ipynb` + `reports/**/NN_*` | `notebook` |
| `README.md` | `readme` |
| `docs/*.md` (fora do plano) | o tema: `dados`, `modelo-dados` |
| `docs/plano/` | `plano` |
| `.github/` | `ci` |
| `requirements*.txt`, `pyproject.toml` | `deps` |
| `.claude/` | `claude` |

- Módulo + seu teste no mesmo commit: escopo do módulo (é a mesma mudança).
- Assuntos **sem relação** entre si (ex.: módulo novo + correção de README de outra seção):
  pare, explique e pergunte se separa (`git restore --staged <arquivo>` no segundo assunto).
- Mudança ampla de um mesmo assunto sem escopo claro: omita o escopo.

Exemplos:

```
feat(preparacao): criar atributos físicos de potência, esforço e diferença de temperatura
test(dados): conferir SHA-256 do CSV versionado e as inconsistências de rótulo
feat(modelo-dados): carregar fato, dimensões e tabela ponte no SQLite
feat(notebook): executar 03 análise exploratória com testes de Mann-Whitney
docs(readme): escrever seções 2.4.1 e 3.2.1 com números das tabelas 03
fix(custo): escolher o limite de desgaste só com dados de treino
```
