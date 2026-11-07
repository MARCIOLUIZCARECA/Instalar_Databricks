# Grupos, permissões e Unity Catalog

Tudo aqui é criado por [`../infrastructure/terraform`](../infrastructure/terraform). As versões em SQL abaixo servem para demonstrar ao vivo.

## Grupos (nível de conta)

| Grupo | Responsabilidade | Usuário fictício (`demo_users`) |
|---|---|---|
| platform-admins | Administração da plataforma | `voce+admin@...` (+ você, em `platform_admins`) |
| data-engineering | Engenharia de dados | `voce+engenheiro@...` |
| marketing-team | Informações comerciais | `voce+marketing@...` |
| operations-team | Informações operacionais | `voce+operacional@...` |
| executives | Indicadores executivos | `voce+diretor@...` |

Plus-addressing (`voce+algo@empresa.com`) faz todos os convites caírem no seu e-mail, então dá para logar com cada perfil numa janela anônima.

Grupos são atribuídos aos workspaces (não pessoas uma a uma). Quem muda de time muda de grupo, e o acesso acompanha.

## Matriz de acesso

| Grupo | DEV (`food_dev`) | PROD (`food_prod`) |
|---|---|---|
| platform-admins | admin do workspace, dono do catálogo | idem |
| data-engineering | escrita (cria e altera tabelas) | leitura (acesso controlado) |
| marketing-team | sem acesso ao workspace | SELECT só na Gold |
| operations-team | sem acesso ao workspace | SELECT só na Gold |
| executives | sem acesso ao workspace | SELECT só na Gold |

Com HML (opcional), engenharia tem leitura em `food_hml` para validar, e o negócio não entra.

Duas camadas de controle:

1. **Workspace** (`databricks_mws_permission_assignment`): quem consegue entrar.
2. **Unity Catalog** (`databricks_grant` + `GRANT` no `04_gold.py`): o que cada um lê ou escreve.

E uma terceira, de isolamento: cada catálogo é `ISOLATED` e vinculado só ao seu workspace. Mesmo um admin em FOOD-DEV não enxerga `food_prod` dali.

## Em SQL (para a aula)

```sql
-- Catálogo, schema e volume (o Terraform já fez; aqui é para mostrar)
CREATE CATALOG IF NOT EXISTS food_dev MANAGED LOCATION 's3://food-intelligence-lakehouse-<conta>/dev/';
CREATE SCHEMA  IF NOT EXISTS food_dev.orders;
CREATE EXTERNAL VOLUME IF NOT EXISTS food_dev.orders.raw
  LOCATION 's3://food-intelligence-raw-<conta>/dev/orders';

-- Engenharia escreve em DEV
GRANT USE CATALOG, USE SCHEMA, CREATE TABLE, SELECT, MODIFY, READ VOLUME ON CATALOG food_dev TO `data-engineering`;

-- Negócio lê só a Gold de PROD
GRANT USE CATALOG ON CATALOG food_prod TO `marketing-team`;
GRANT USE SCHEMA  ON SCHEMA  food_prod.orders TO `marketing-team`;
GRANT SELECT      ON TABLE   food_prod.orders.gold_sales_by_store TO `marketing-team`;

-- Conferir
SHOW GRANTS ON TABLE food_prod.orders.gold_sales_by_store;
SHOW GRANTS `marketing-team` ON CATALOG food_prod;
```

## Validar com dois perfis (direto no dado)

Logado como **marketing** no FOOD-PROD (SQL editor):

```sql
SELECT * FROM food_prod.orders.gold_sales_by_store LIMIT 5;   -- funciona
SELECT * FROM food_prod.orders.silver_orders LIMIT 5;         -- PERMISSION_DENIED
SELECT * FROM food_prod.orders.bronze_orders LIMIT 5;         -- PERMISSION_DENIED
LIST '/Volumes/food_prod/orders/raw';                         -- PERMISSION_DENIED
```

Logado como **engenheiro** no FOOD-PROD:

```sql
SELECT count(*) FROM food_prod.orders.silver_orders;          -- funciona (leitura)
DELETE FROM food_prod.orders.silver_orders WHERE 1 = 1;       -- PERMISSION_DENIED (sem MODIFY)
```

## Service principal do App

O App consulta a Gold com **o token de quem está usando** (autorização de usuário, escopo `sql`), então as regras acima valem também dentro do App. Se a autorização de usuário não estiver habilitada no workspace, o App usa o próprio service principal, que precisa de leitura só na Gold:

```bash
SP=$(databricks apps get food-explorer --profile food-prod -o json | python3 -c 'import json,sys;print(json.load(sys.stdin)["service_principal_client_id"])')
```

```sql
GRANT USE CATALOG ON CATALOG food_prod TO `<SP>`;
GRANT USE SCHEMA  ON SCHEMA  food_prod.orders TO `<SP>`;
GRANT SELECT      ON TABLE   food_prod.orders.gold_sales_by_store TO `<SP>`;
```

## Aplicar o Terraform de governança

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# workspace_ids = (terraform output workspace_ids no stack ../../../terraform): dev e prod; hml opcional
# platform_admins e demo_users com os seus e-mails
terraform init && terraform plan && terraform apply
```
