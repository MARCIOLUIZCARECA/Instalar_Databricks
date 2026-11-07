# Lições do ensaio (06/11/2026) · como montar uma conta nova sem estes problemas

Tudo o que travou no ensaio, a causa e o que fazer **antes** de começar numa conta AWS e Databricks nova.

## Checklist antes de começar (conta nova)

| # | Faça | Por quê (problema que evita) |
|---|---|---|
| 1 | Use uma **conta AWS avulsa e paga**, fora de AWS Organization. Se precisar ser de uma Organization, ajuste SCP e RCP **antes** (item A) | SCP/RCP bloqueiam a Databricks |
| 2 | Faça `aws login` numa **janela/sessão do console só com essa conta** e confira com `aws sts get-caller-identity` | O login pegou a conta errada (sessões múltiplas do console) |
| 3 | Grave a região no profile: `aws configure set region us-east-2 --profile <profile>` | Erro `NoRegion` no upload para o S3 |
| 4 | Planeje os workspaces e crie **no máximo 2 ou 3 por dia**, com antecedência | Limite diário de criação de workspaces (item B) |
| 5 | Defina o nome final dos workspaces antes do `apply` | Renomear pelo Terraform recria o workspace (item C) |
| 6 | Depois de criar os workspaces, **apague os catálogos automáticos vazios** com o mesmo nome dos catálogos do projeto, antes do Terraform de governança | Conflito `Catalog 'food_dev' already exists` (item D) |
| 7 | Logo depois da governança, **teste o SQL warehouse serverless** lendo uma tabela do projeto | 403 no SQL serverless (item E) |
| 8 | Publique o bundle em duas passadas: `deploy` → `run` da pipeline → `deploy` | Genie exige a tabela Gold existir (item F) |
| 9 | Gere as policies preenchidas com `manual/policies/gerar_policies.py` e cole na ordem do `COLAR.md` | Erro de digitação em ARN, nome de bucket ou External ID |
| 10 | No fim, rode `python3 scripts/smoke_test.py` e só siga com tudo **OK** | Descobrir o problema na frente da turma |

> **External ID da role de dados:** quando quem cria a storage credential é **admin da conta** (e não só do workspace), o External ID é o próprio **Databricks Account ID**. Caso contrário, é um ID gerado: copie o que aparecer na tela da credential.

---

## A. AWS Organization: SCP e RCP

**Sintoma:** `Failed credential validation checks` ao registrar a credential; ou a Databricks não consegue assumir a role.

**Causa:** contas criadas pela tela "Projects" da AWS ficam numa Organization com:
- SCP de região (`AdvancedModeRegionRestrictionSecurityControlPolicy`): bloqueia EC2 fora de uma região;
- RCP (`ManagedAccountResourceControlPolicy`): nega `s3:*`, `sts:*` etc. para principais fora da Organization.

**Correção (na Management Account):** detalhes e JSON no [Troubleshooting do manual](../../manual/README.md#troubleshooting). Resumo: tirar a SCP de região da conta do workshop e incluir na RCP a exceção `"StringNotEquals": {"aws:PrincipalAccount": "414351767826"}`.

**Melhor ainda:** conta AWS avulsa, sem Organization.

## B. Limite diário de criação de workspaces

**Sintoma:** `Limit reached for workspace creation. You've hit your daily limit for workspace creation. Please try again in 24 hours.` O Terraform fica "Still creating..." por até 30 minutos antes de mostrar o erro.

**Causa:** a conta Databricks limita quantos workspaces podem ser **criados por dia**. No ensaio, o 5º do dia falhou. **Apagar workspaces não libera o limite.**

**Como evitar:** criar os workspaces na véspera, poucos por dia, e não usar a conta para testes de criação no mesmo dia. Se precisar de mais, fale com o time de contas da Databricks.

## C. Renomear workspace sem recriar

**Sintoma:** `terraform plan` mostra `workspace_name ... # forces replacement` (destrói e recria o workspace).

**Correção:** renomear pela API e mover o state:

```bash
databricks account workspaces update <ID> --workspace-name FOOD-PROD --update-mask workspace_name -p <profile-conta>
terraform state mv 'databricks_mws_workspaces.this["hml"]' 'databricks_mws_workspaces.this["prod"]'
terraform plan   # deve dar "No changes"
```

O catálogo padrão do workspace continua com o nome antigo: ajuste com `databricks settings default-namespace update` (ver item D).

## D. Catálogo automático com o mesmo nome do workspace

**Sintoma:** `cannot create catalog: Catalog 'food_dev' already exists` no Terraform de governança.

**Causa:** todo workspace novo ganha um **catálogo automático** com o nome do workspace (FOOD-DEV → `food_dev`), vazio, gravando no bucket raiz. Ele vira também o catálogo padrão do workspace.

**Correção (antes do Terraform de governança):**

```bash
databricks schemas list food_dev -p food-dev                 # confira: só default e information_schema
databricks catalogs delete food_dev --force -p food-dev      # apaga o catálogo automático vazio
```

O Terraform recria `food_dev` no bucket lakehouse. Se o workspace foi renomeado, ajuste o catálogo padrão:

```bash
ETAG=$(databricks settings default-namespace get -p food-prod -o json | python3 -c "import json,sys;print(json.load(sys.stdin)['etag'])")
databricks settings default-namespace update -p food-prod --json "{\"allow_missing\": true, \"field_mask\": \"namespace.value\", \"setting\": {\"etag\": \"$ETAG\", \"namespace\": {\"value\": \"food_prod\"}}}"
```

## E. SQL warehouse serverless com 403 nos buckets do projeto

**Sintoma:** Dashboard, App e Genie falham; no SQL aparece `AmazonS3Exception: Forbidden ... Request ID: null ... Proxy: 192.168.200.20`. No App: "Sem acesso à tabela Gold com a sua identidade".

**O que já foi descartado:**
- permissões IAM e Unity Catalog: o *Validate* da storage credential passa em READ, LIST, WRITE e DELETE;
- grants: o usuário é dono dos catálogos;
- política de rede do serverless: `default-policy` com `FULL_ACCESS`;
- os **jobs serverless** leem e gravam normalmente, e um **SQL warehouse clássico** lê a mesma tabela.

**Hipótese:** o bloqueio acontece no proxy de saída do **SQL serverless** (o S3 sempre devolve um Request ID; aqui ele vem nulo). Como a conta 928844615034 está numa Organization com RCP, essa é a principal suspeita.

**Contorno usado no ensaio:** SQL warehouse **clássico** PRO, 2X-Small, desligamento automático em 10 min, com o nome `Food Classic Warehouse` em cada workspace. O bundle procura esse nome (`databricks.yml`, variável `warehouse_id`).

```bash
databricks warehouses create -p food-dev --json '{"name":"Food Classic Warehouse","cluster_size":"2X-Small","min_num_clusters":1,"max_num_clusters":1,"auto_stop_mins":10,"enable_serverless_compute":false,"warehouse_type":"PRO"}'
```

**Na conta nova:** teste primeiro o serverless (`Serverless Starter Warehouse`). Se funcionar, troque a variável `warehouse_id` de volta para ele: é mais barato parado e sobe em segundos.

## F. Genie exige a tabela antes do deploy

**Sintoma:** primeiro `bundle deploy` falha com `Table 'food_prod.orders.gold_sales_by_store' does not exist`.

**Correção:** é a ordem natural: `bundle deploy` (cria job, dashboard, App) → `bundle run food_orders_pipeline` (cria a Gold) → `bundle deploy` de novo (cria o Genie) → `bundle run food_explorer` (sobe o App).

## G. Outros detalhes

| Situação | O que fazer |
|---|---|
| *Validate* da external location mostra falha em "file events" | Normal sem a policy de SNS/SQS. Para Auto Loader com file events, ligue `enable_file_events` (passo 4.5 do manual) |
| `bundle summary` mostra o App como "(not deployed)" mesmo rodando | Confira com `databricks apps get <nome>`; o status real vem dali |
| Deploy em PROD bloqueado pelo Claude Code | É proposital: confirme explicitamente ("pode publicar em PROD") |
| Login de workspace | `databricks auth login --host <url> --profile food-dev` (um por workspace), depois do `apply` da infraestrutura |
