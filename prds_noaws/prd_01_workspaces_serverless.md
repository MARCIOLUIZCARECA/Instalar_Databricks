# PRD 01 · Workspaces DEV e PROD serverless, com os ambientes do projeto (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Contexto:** na versão com AWS, este PRD criava um workspace clássico de PRODUÇÃO (bucket, roles, VPC). Aqui, o cadastro Express já entregou um workspace serverless, e criamos **mais dois do mesmo tipo**, `{{WS_DEV}}` e `{{WS_PROD}}`, pela API de conta. Workspace serverless já vem com compute serverless e **storage padrão** gerenciado pela Databricks, então não há nada para criar na AWS. Em cada um, o Claude Code cria o catálogo do ambiente: `food_dev` no DEV e `food_prod` no PROD.

A mensagem da aula: *"na versão empresa, um workspace novo pede bucket, roles e VPC; no serverless, é um comando e alguns minutos. A separação DEV × PROD por workspace é a mesma."*

---

## 1. Objetivo

- Login de **conta** no CLI e `config.yaml` preenchido.
- Workspaces serverless `{{WS_DEV}}` e `{{WS_PROD}}` em **Running**, na região `{{REGIAO}}` e no metastore `{{METASTORE}}`.
- `food_dev` criado no `{{WS_DEV}}` e `food_prod` no `{{WS_PROD}}`, cada um com o schema `orders` e o volume `raw`, no storage padrão.

Fora de escopo: grupos e permissões (PRD 02), dados (PRD 03), pipeline (PRD 04). Qualquer coisa na AWS. Workspace clássico.

## 2. Valores

| Ambiente | Workspace (= profile do CLI) | Catálogo | Schema | Volume (gerenciado) |
|---|---|---|---|---|
| DEV | `{{WS_DEV}}` (sugestão: `{{PREFIXO}}-dev`) | `food_dev` | `food_dev.orders` | `food_dev.orders.raw` |
| PROD | `{{WS_PROD}}` (sugestão: `{{PREFIXO}}-prod`) | `food_prod` | `food_prod.orders` | `food_prod.orders.raw` |

- **Região:** a mesma do workspace Express (`{{REGIAO}}`). Assim os três ficam no mesmo metastore, sem criar outro.
- **Catálogos sem `MANAGED LOCATION`:** usam o storage padrão. Um catálogo no storage padrão, por padrão, **só aparece no workspace onde foi criado**: `food_prod` não aparece no DEV, e `food_dev` não aparece no PROD. É o isolamento que a versão AWS faz com *workspace binding*.
- **`{{PREFIXO}}` diferente de `food`**, para o catálogo automático (`{{PREFIXO}}_dev`, `{{PREFIXO}}_prod`) não se confundir com `food_dev` e `food_prod`.

## 3. O que NÃO pode ser tocado

- O workspace Express `{{WS_EXPRESS}}` e o catálogo automático dele.
- Nada na AWS. Nenhum workspace clássico, credential, storage configuration ou network.

## 4. Passo a passo

Em cada passo: (a) explique o que a peça é, em linguagem de aula; (b) rode; (c) diga **onde ver no console**.

| # | Passo | Onde ver |
|---|---|---|
| 0 | **Conferir o CLI:** `databricks --version` (se não tiver, instalar conforme a skill `databricks-core`) | Terminal |
| 1 | **Login de conta:** pedir o Account ID (Account Console → avatar) e rodar `databricks auth login --host https://accounts.cloud.databricks.com --account-id <id> --profile <nome>` (sugestão: `food-account`). Se o aluno não tiver acesso ao Account Console, vá para o **plano B** (seção 5) | Account Console |
| 2 | **Descobrir o que já existe (só leitura):** `databricks account workspaces list` (nome, região e `compute_mode` do Express), `databricks account metastores list` (metastore da região), `databricks current-user me` no Express | Account Console → Workspaces; Catalog |
| 3 | **Preencher o [`config.yaml`](config.yaml):** mostrar a tabela com tudo que descobriu, perguntar o que faltar (`PREFIXO`, `EMAIL_BASE`; confirmar `WS_DEV` e `WS_PROD`) e **gravar só depois da confirmação**. Se `{{WS_DEV}}` ou `{{WS_PROD}}` já existirem, **pare e pergunte** | Arquivo |
| 4 | **Criar o workspace DEV** (com aprovação): `databricks account workspaces create --json '{"workspace_name": "{{WS_DEV}}", "aws_region": "{{REGIAO}}", "compute_mode": "SERVERLESS"}' --no-wait --profile {{DATABRICKS_ACCOUNT_PROFILE}}`. Sem credentials, storage nem network: o modo serverless dispensa os três | Account Console → Workspaces (*Provisioning*) |
| 5 | **Criar o workspace PROD** (com aprovação): o mesmo, com `{{WS_PROD}}` | Account Console → Workspaces |
| 6 | **Acompanhar até Running** (`databricks account workspaces get <id>`, a cada ~30 s). Enquanto espera, comparar no slide com a versão AWS: lá eram bucket, 2 roles, credential, storage e VPC antes do workspace | Account Console → Workspaces |
| 7 | **Metastore:** conferir se os dois foram atribuídos ao `{{METASTORE}}` (`databricks account metastore-assignments get <workspace_id>`). Se não, atribuir (com aprovação) | Account Console → Catalog → metastore → Workspaces |
| 8 | **Login nos dois workspaces:** `databricks auth login --host {{WS_DEV_URL}} --profile {{WS_DEV}}` e o mesmo para PROD. Gravar URLs, warehouses (`databricks warehouses list`) e catálogos automáticos no `config.yaml` (com confirmação) | Navegador |
| 9 | **Criar o ambiente DEV** no `{{WS_DEV}}` (com aprovação): `CREATE CATALOG IF NOT EXISTS food_dev COMMENT 'Food Intelligence · ambiente de desenvolvimento'`; `CREATE SCHEMA food_dev.orders`; `CREATE VOLUME food_dev.orders.raw` | `{{WS_DEV}}` → Catalog Explorer → `food_dev` |
| 10 | **Criar o ambiente PROD** no `{{WS_PROD}}` (com aprovação): o mesmo para `food_prod` (`COMMENT '... · ambiente de produção'`) | `{{WS_PROD}}` → Catalog Explorer → `food_prod` |
| 11 | **Catálogo padrão** de cada workspace → o do projeto (`food_dev` no DEV, `food_prod` no PROD), não o automático | Settings → Advanced → Default catalog |
| 12 | **Teste do isolamento** pelo warehouse de cada workspace: no DEV, `SHOW CATALOGS` mostra `food_dev` e **não** `food_prod`; no PROD, o contrário. `LIST '/Volumes/food_prod/orders/raw/'` no PROD responde vazio, sem erro | SQL Editor dos dois workspaces |

Rode o SQL pelo warehouse do workspace certo (skill `databricks-dbsql` ou `databricks api post /api/2.0/sql/statements --profile <ws>`), sempre com nomes em três partes. Se um workspace novo vier sem warehouse, crie (com aprovação) um serverless **2X-Small**, auto-stop 10 min, chamado `Food Serverless Warehouse`.

## 5. Plano B: um workspace só

Use se o aluno **não tiver acesso ao Account Console**, se a criação falhar pelo **limite diário de workspaces** da conta trial, ou se a região não aceitar workspace serverless. Mostre o erro, explique em uma frase e **não tente contornar**.

No plano B, tudo fica no workspace Express: `{{WS_DEV}}` e `{{WS_PROD}}` recebem o mesmo nome e a mesma URL (o do Express), `food_dev` e `food_prod` nascem nele (passos 9 e 10), e o isolamento é feito só por GRANTs (PRD 02). Registre `MODO: um-workspace` no fim do `config.yaml`, para os próximos PRDs saberem.

## 6. Lições

1. **Não procure AWS.** Workspace serverless não tem bucket, role nem VPC na conta do aluno.
2. **Limite diário de criação de workspaces** na conta trial; apagar não libera. Não crie workspaces de teste: são exatamente dois.
3. **Mesma região do Express**, senão o workspace cai numa região sem metastore e o Unity Catalog fica para configurar.
4. Se `CREATE CATALOG` falhar pedindo localização, confira se está no workspace **serverless** certo: catálogo no storage padrão só nasce em workspace serverless. **Não** crie storage credential nem external location.
5. **`food_prod` ≠ catálogo automático.** Releia o nome e o profile (`{{WS_DEV}}` × `{{WS_PROD}}`) antes de cada comando.

## 7. Critérios de aceite

- [ ] `{{WS_DEV}}` e `{{WS_PROD}}` em **Running**, `compute_mode` SERVERLESS, região `{{REGIAO}}`, metastore `{{METASTORE}}` (ou plano B registrado).
- [ ] Workspace Express intacto.
- [ ] `databricks current-user me` responde nos profiles `{{WS_DEV}}` e `{{WS_PROD}}`.
- [ ] `food_dev` só no DEV e `food_prod` só no PROD, cada um com `orders` e o volume `raw`.
- [ ] Catálogo padrão de cada workspace = o do projeto; catálogos automáticos intactos e marcados como "não usado".
- [ ] Tabela final: ambiente × workspace × URL × catálogo × schema × volume, e onde ver cada um.

## 8. Custos e limpeza

Workspace serverless não cobra por hora parado (não há NAT Gateway): só o que roda (warehouse, jobs). Deixe o auto-stop do warehouse em 10 min. Para apagar depois (com aprovação): `databricks account workspaces delete <id>` nos dois.
