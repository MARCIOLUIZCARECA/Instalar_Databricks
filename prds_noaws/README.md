# PRDs SEM AWS · Food Intelligence com Claude Code (Express setup)

Versão dos PRDs para quem **não tem conta AWS**. Tudo roda numa conta Databricks criada pelo **Express setup** (login.databricks.com/signup): um workspace serverless, com storage gerenciado pela Databricks.

**O que muda:** usamos o workspace padrão do Express; DEV e PROD viram os catálogos `food_dev` e `food_prod`; os CSVs vão para um volume do Unity Catalog em vez do S3. Nada de bucket, role, VPC ou comando `aws`. Detalhes no [`prd_00_contexto.md`](prd_00_contexto.md), seção 2.

## Antes de começar

1. Crie a conta em login.databricks.com/signup (Express) e abra o workspace.
2. Instale o Databricks CLI e o Claude Code.
3. Copie esta pasta para a raiz de um projeto novo, com o nome `prds_noaws/`.

| PRD | Etapa |
|---|---|
| [`prd_00_contexto.md`](prd_00_contexto.md) | Cenário, diferenças para a versão AWS, regras (vale para todos) |
| [`prd_01_workspace_express.md`](prd_01_workspace_express.md) | Login no workspace padrão, `config.yaml` e criação dos ambientes DEV e PROD |
| [`prd_02_governanca.md`](prd_02_governanca.md) | Grupos, usuários e permissões |
| [`prd_03_dados.md`](prd_03_dados.md) | Pedidos e lojas sintéticos no volume `raw` |
| [`prd_04_pipeline.md`](prd_04_pipeline.md) | Raw → Bronze → Silver → Gold em DEV, com testes |
| [`prd_05_promocao.md`](prd_05_promocao.md) | DEV → TEST → PROD com Asset Bundles |
| [`prd_06_consumo.md`](prd_06_consumo.md) | Dashboard, App e Genie sobre a Gold |

## Os 6 prompts (cole um por vez no Claude Code)

**1 · Workspace padrão + ambientes DEV e PROD**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_01_workspace_express.md`. Não tenho conta AWS: vou usar só o workspace padrão do Express. Me ajude a fazer login no CLI, preencher o `prds_noaws/config.yaml` e criar os ambientes DEV (`food_dev`) e PROD (`food_prod`), com o schema `orders` e o volume `raw` em cada um. Vamos passo a passo, pedindo aprovação antes de criar ou alterar qualquer coisa.

**2 · Governança**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_02_governanca.md` e use os valores do `prds_noaws/config.yaml`. Os catálogos `food_dev` e `food_prod` já existem (PRD 01). Crie os grupos, os usuários fictícios e as permissões de cada grupo em DEV e PROD. Mostre cada comando antes e espere meu "pode".

**3 · Dados**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_03_dados.md`. Gere os dados sintéticos de pedidos e lojas, me mostre a sujeira proposital e envie os CSVs para os volumes `raw` de DEV e PROD.

**4 · Pipeline**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_04_pipeline.md`. Construa a pipeline Raw → Bronze → Silver → Gold em DEV, com as regras da Silver testadas por `pytest`, o job serverless no bundle e o notebook de validação. Rode em DEV e me mostre onde ficam as tabelas.

**5 · Promoção**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_05_promocao.md`. Configure o target `prod` do bundle, mostre o que muda em relação a DEV e, só depois que eu disser "pode publicar em PROD", publique e rode o job. Depois aplique os grants da Gold e me ajude a validar com dois usuários.

**6 · Consumo**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_06_consumo.md`. Crie o Dashboard, o App e o Genie lendo `food_prod.orders.gold_sales_by_store`, testando cada query antes do deploy, e publique na ordem do PRD.

O Claude Code pede aprovação antes de criar, alterar ou apagar qualquer coisa.
