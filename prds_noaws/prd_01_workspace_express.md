# PRD 01 · Workspace padrão (Express) com os ambientes DEV e PROD (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Contexto:** na versão com AWS, este PRD criava um workspace de PRODUÇÃO (bucket, roles, VPC). Aqui não há infraestrutura para criar: usamos o **workspace padrão** que o cadastro Express entregou (serverless, storage gerenciado pela Databricks). Neste PRD, o Claude Code se conecta a ele, preenche o `config.yaml` e **já cria os dois ambientes**: o catálogo `food_dev` (DEV) e o catálogo `food_prod` (PROD), cada um com o schema `orders` e o volume `raw`.

A mensagem da aula: *"na empresa, DEV e PROD seriam dois workspaces; aqui, são dois catálogos isolados no mesmo workspace. O resto da plataforma é igual."*

---

## 1. Objetivo

- CLI autenticado no workspace padrão.
- `config.yaml` preenchido.
- Ambientes **DEV** (`food_dev`) e **PROD** (`food_prod`) criados no storage padrão, prontos para os próximos PRDs.

Fora de escopo: grupos e permissões (PRD 02), dados (PRD 03), pipeline (PRD 04). Qualquer coisa na AWS. Criar outro workspace.

## 2. Valores

| Ambiente | Catálogo | Schema | Volume (gerenciado) |
|---|---|---|---|
| DEV | `food_dev` | `food_dev.orders` | `food_dev.orders.raw` |
| PROD | `food_prod` | `food_prod.orders` | `food_prod.orders.raw` |

Catálogos **sem `MANAGED LOCATION`**: usam o storage padrão do workspace.

## 3. Passo a passo

Em cada passo: (a) explique o que a peça é, em linguagem de aula; (b) rode; (c) diga **onde ver no workspace**.

| # | Passo | Onde ver |
|---|---|---|
| 0 | **Conferir o CLI:** `databricks --version` (se não tiver, instalar conforme a skill `databricks-core`) | Terminal |
| 1 | **Login no workspace padrão:** pedir ao aluno a URL do workspace (barra do navegador, `https://dbc-....cloud.databricks.com`) e rodar `databricks auth login --host <url> --profile <nome>` (sugestão: `food`) | Navegador |
| 2 | **Descobrir o que já existe (só leitura):** `databricks current-user me`, `databricks catalogs list`, `databricks warehouses list`, `databricks metastores current` | Catalog Explorer; SQL Warehouses |
| 3 | **Identificar o catálogo automático** (o que veio com o workspace) e explicar que **não** será usado (PRD 00, seção 3.1). Se `food_dev` ou `food_prod` já existirem, **pare e pergunte** | Catalog Explorer |
| 4 | **Preencher o [`config.yaml`](config.yaml):** mostrar a tabela com tudo que descobriu, perguntar o que faltar (`EMAIL_BASE`) e **gravar só depois da confirmação** | Arquivo |
| 5 | **Criar o ambiente DEV** (com aprovação): `CREATE CATALOG IF NOT EXISTS food_dev COMMENT 'Food Intelligence · ambiente de desenvolvimento'`; `CREATE SCHEMA food_dev.orders`; `CREATE VOLUME food_dev.orders.raw` | Catalog Explorer → `food_dev` |
| 6 | **Criar o ambiente PROD** (com aprovação): o mesmo para `food_prod` (`COMMENT '... · ambiente de produção'`) | Catalog Explorer → `food_prod` |
| 7 | **Catálogo padrão do workspace → `food_dev`** (o projeto, não o automático) | Settings → Advanced → Default catalog |
| 8 | **Teste no warehouse serverless:** `SHOW SCHEMAS IN food_prod` e `LIST '/Volumes/food_prod/orders/raw/'` (vazio, sem erro) | SQL Editor |
| 9 | **Tour de aula (5 min):** Catalog, Workspace, Jobs & Pipelines, SQL Warehouses, Dashboards, Genie, Apps. Comparar com o slide da arquitetura AWS: "na versão empresa, DEV e PROD seriam workspaces com VPC, bucket e roles na sua conta" | Workspace |

Rode o SQL pelo warehouse (skill `databricks-dbsql` ou `databricks api post /api/2.0/sql/statements`), sempre com nomes em três partes.

## 4. Lições

1. **Não procure AWS.** Não existe bucket, role nem VPC na conta do aluno.
2. **Não crie outro workspace.** DEV e PROD são catálogos no workspace padrão.
3. Se `CREATE CATALOG` falhar pedindo localização ou privilégio, **mostre o erro** e consulte a documentação de *default storage*. **Não** crie storage credential nem external location.
4. **`food_prod` ≠ catálogo automático.** Releia o nome antes de cada comando.

## 5. Critérios de aceite

- [ ] `databricks current-user me --profile {{WS}}` responde com o e-mail do aluno.
- [ ] `config.yaml` preenchido e confirmado.
- [ ] `food_dev` e `food_prod` criados no storage padrão, cada um com `orders` e o volume `raw`.
- [ ] Catálogo padrão = `food_dev`; catálogo automático intacto e marcado como "não usado".
- [ ] O warehouse serverless lista o volume `raw` de PROD sem erro.
- [ ] Tabela final: ambiente × catálogo × schema × volume, e onde ver cada um.
