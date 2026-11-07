# PRD 02 · Governança: grupos, buckets de dados e Unity Catalog

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md`.

**Pré-requisito:** `{{WS_DEV}}` e `{{WS_PROD}}` em Running, no mesmo metastore `{{METASTORE}}` (PRD 01).

**Mensagem da aula:** *"grupos, não pessoas, recebem acesso"* e *"metadado no catálogo, dado físico no seu bucket"*.

---

## 1. Objetivo

Organizar quem acessa o quê, e ligar o Unity Catalog a buckets S3 da empresa, um catálogo por ambiente.

Fora de escopo: dados (PRD 03), pipeline (PRD 04), HML.

## 2. Valores

| O quê | Valor |
|---|---|
| Bucket raw (arquivos brutos) | `{{PREFIXO}}-food-raw-{{AWS_ACCOUNT_ID}}`, pastas `dev/orders/` e `prod/orders/` |
| Bucket lakehouse (tabelas Delta) | `{{PREFIXO}}-food-lakehouse-{{AWS_ACCOUNT_ID}}`, pastas `dev/` e `prod/` |
| Role de dados (Unity Catalog) | `{{PREFIXO}}-food-uc-role` |
| Storage credential | `{{PREFIXO}}-food-s3` |
| External locations | `food-raw-dev`, `food-raw-prod`, `food-lakehouse-dev`, `food-lakehouse-prod` |
| Catálogos | `food_dev` (managed location `lakehouse/dev`) e `food_prod` (`lakehouse/prod`) |
| Schema | `orders` em cada catálogo, com o volume externo `raw` apontando para `raw/<env>/orders/` |

**Grupos** (na conta, uma vez só):

| Grupo | Responsabilidade |
|---|---|
| `platform-admins` | Administração da plataforma |
| `data-engineering` | Engenharia de dados |
| `marketing-team` | Informações comerciais |
| `operations-team` | Informações operacionais |
| `executives` | Indicadores executivos |

**Usuários fictícios:** um por grupo, com *plus addressing* do `{{EMAIL_BASE}}` (ex.: `voce@gmail.com` → `voce+engenheiro@gmail.com`). Se `EMAIL_BASE` estiver vazio no `config.yaml`, **pergunte** antes de criar.

## 3. Política de acesso

| Grupo | `{{WS_DEV}}` (workspace) | `{{WS_PROD}}` (workspace) | `food_dev` | `food_prod` |
|---|---|---|---|---|
| `platform-admins` | Admin | Admin | Dono | Dono |
| `data-engineering` | User | User | Escrita | Leitura de tudo, sem `MODIFY` |
| `marketing-team` | — | User | — | Só a Gold |
| `operations-team` | — | User | — | Só a Gold |
| `executives` | — | User | — | Só a Gold |

Os catálogos ficam **isolados** (*workspace binding*): `food_dev` só aparece no `{{WS_DEV}}`, e `food_prod` só no `{{WS_PROD}}`.

## 4. Passo a passo

| # | Passo | Mostrar no console |
|---|---|---|
| 0 | Leitura: grupos e catálogos existentes; o catálogo automático de cada workspace (`dev_food`, `prod_food`) | Account Console → User management; Catalog Explorer |
| 1 | Grupos e usuários na conta | Account Console → User management |
| 2 | Atribuir grupos aos workspaces conforme a seção 3 | Account Console → Workspaces → Permissions |
| 3 | Buckets raw e lakehouse (privados, SSE-S3, `{{REGIAO}}`) | S3 |
| 4 | Role de dados com trust provisória + permissões S3 nos dois buckets | IAM → Roles |
| 5 | Storage credential `{{PREFIXO}}-food-s3` com o ARN da role; copiar o **External ID** que ela mostrar | Catalog Explorer → External data → Credentials |
| 6 | Trust definitiva da role de dados (self-assuming, External ID da credential); esperar ~60 s; **Validate** da credential | IAM; Catalog Explorer |
| 7 | External locations (as 4), com *Test connection* | Catalog Explorer → External locations |
| 8 | Catálogos, schemas, volumes e grants da seção 3; workspace bindings | Catalog Explorer → Permissions / Workspaces |
| 9 | Catálogo padrão de cada workspace → `food_dev` / `food_prod` | Workspace settings |
| 10 | **Teste do SQL warehouse serverless** lendo o volume `raw` de PROD. Se der 403, criar o `Food Classic Warehouse` (PRD 00, lições) | SQL Editor |

## 5. Lições específicas

- A role de dados é **outra role**, separada da storage role do workspace.
- *Validate* da external location pode falhar em "file events": é normal sem a policy de SNS/SQS. Não é bloqueante.
- Se o Terraform ou a API tentar criar um catálogo e ele já existir, **pare e pergunte**. Não apague catálogo com dados.

## 6. Critérios de aceite

- [ ] 5 grupos e 5 usuários fictícios na conta.
- [ ] Marketing **não** entra no `{{WS_DEV}}`; entra no `{{WS_PROD}}`.
- [ ] Storage credential validada (READ, LIST, WRITE, DELETE).
- [ ] `food_dev` só no `{{WS_DEV}}`, `food_prod` só no `{{WS_PROD}}`.
- [ ] Um SQL warehouse que lê o volume `raw` de PROD sem erro.
- [ ] Tabela-resumo: grupo × workspace × catálogo × privilégio, e onde conferir cada um.

## 7. Como validar com dois perfis (para a aula)

Janelas anônimas com dois usuários fictícios:

1. Marketing tenta abrir o `{{WS_DEV}}` → sem acesso.
2. Marketing no `{{WS_PROD}}`: `SELECT` na Gold funciona; na Silver, `PERMISSION_DENIED` (depois do PRD 05).
3. Engenheiro no `{{WS_PROD}}`: lê a Silver, mas não consegue `DELETE`.
