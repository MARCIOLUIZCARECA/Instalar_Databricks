# Workspaces DEV e PROD

## Uma conta, dois workspaces

O projeto usa **DEV e PROD**. HML é opcional; a comparação das opções (e quanto custa cada uma) está em [environments.md](environments.md#quantos-ambientes).

| Workspace | Objetivo | Quem entra |
|---|---|---|
| FOOD-DEV | Desenvolver e testar: notebooks, experimentos, TEST automático | platform-admins (admin), data-engineering |
| FOOD-PROD | Produção: pipelines aprovadas e consumo | platform-admins (admin), data-engineering, marketing, operações, diretoria |

Cada workspace tem a sua URL, os seus usuários atribuídos, as suas configurações e o seu compute. Os dois compartilham a **conta** (grupos, usuários, metastore) e, neste projeto, a **credential** e a **storage configuration** da AWS.

## Criar (Terraform)

Pré-requisito: logins da seção 0.1 do [manual](../../manual/README.md#01-login-pelo-terminal-cli).

```bash
cd ../terraform
cp terraform.tfvars.example terraform.tfvars
# preencha: databricks_account_id, aws_profile, prefix = "food"
terraform init
terraform plan        # confira: 2 x databricks_mws_workspaces
terraform apply       # ~10 a 15 minutos; sobem em paralelo
terraform output workspace_urls
terraform output workspace_ids
```

> **Custo:** cada workspace clássico tem a sua Databricks-managed VPC com NAT Gateway e IP público (~US$ 0,05/h, ~US$ 1,20/dia, mesmo parado). Para um ensaio barato, crie só DEV com `environments = { dev = "FOOD-DEV" }`.
>
> **Limite diário:** a conta Databricks limita quantos workspaces podem ser **criados por dia** (erro `Limit reached for workspace creation ... try again in 24 hours`). No ensaio de 06/11 batemos esse limite no 5º workspace do dia. Planeje a criação com antecedência; apagar workspaces não libera o limite.
>
> **Renomear sem recriar:** mudar `workspace_name` no Terraform recria o workspace. Para só trocar o nome, use `databricks account workspaces update <id> --workspace-name NOVO --update-mask workspace_name` e depois `terraform state mv` (foi assim que o FOOD-HML do ensaio virou FOOD-PROD).

## Login em cada workspace

```bash
databricks auth login --host https://<url-dev>  --profile food-dev
databricks auth login --host https://<url-prod> --profile food-prod
```

Os nomes `food-dev` e `food-prod` são usados pelo bundle (`databricks.yml`) e pelo Terraform de governança.

## Demonstrar "DEV sim, PROD não"

1. Logue como `voce+engenheiro@...` (grupo data-engineering): entra em DEV e PROD, mas só escreve em `food_dev`.
2. Logue como `voce+marketing@...` (marketing-team): a URL de DEV responde que o usuário não tem acesso ao workspace; em PROD, só lê a Gold.
3. Mesmo dentro de PROD, `SELECT * FROM food_prod.orders.silver_orders` falha para marketing: o workspace deixa entrar, o Unity Catalog decide o dado.

## Limpeza

Na ordem inversa da criação:

```bash
cd food-intelligence-platform
databricks bundle destroy -t prod && databricks bundle destroy -t dev
cd infrastructure/terraform && terraform destroy
cd ../../../terraform && terraform destroy     # apaga workspaces, VPCs, NAT Gateways, roles e bucket raiz
```

Confira no console da AWS (região `us-east-2`) se não sobrou NAT Gateway, Elastic IP ou VPC com tag do Databricks.
