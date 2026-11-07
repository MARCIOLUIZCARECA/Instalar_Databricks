# PRDs · Food Intelligence com Claude Code

O PRD único do projeto (`.llm/prd.md`) dividido em etapas, para usar num projeto novo, ao vivo, com o Claude Code.

**Como usar:** copie esta pasta para a raiz do projeto novo, faça os logins (AWS CLI e Databricks CLI na sua conta) e preencha ou deixe o Claude Code preencher o [`config.yaml`](config.yaml) e peça, uma etapa por vez:

> Leia `prds/prd_00_contexto.md` e `prds/prd_0X_....md` e vamos executar juntos, passo a passo.

| PRD | Etapa | Bloco da aula |
|---|---|---|
| [`prd_00_contexto.md`](prd_00_contexto.md) | Cenário, valores, regras e lições do ensaio (vale para todos) | — |
| [`prd_01_workspace_prod.md`](prd_01_workspace_prod.md) | Workspace `{{WS_PROD}}` (bucket, roles, credential, storage, VPC) | 3 |
| [`prd_02_governanca.md`](prd_02_governanca.md) | Grupos, usuários, buckets de dados, Unity Catalog, permissões | 4 |
| [`prd_03_dados.md`](prd_03_dados.md) | Pedidos e lojas sintéticos no bucket raw | 4/5 |
| [`prd_04_pipeline.md`](prd_04_pipeline.md) | Raw → Bronze → Silver → Gold em DEV, com testes | 5 |
| [`prd_05_promocao.md`](prd_05_promocao.md) | DEV → TEST → PROD com Asset Bundles | 5 |
| [`prd_06_consumo.md`](prd_06_consumo.md) | Dashboard, App e Genie sobre a Gold | 6 |

Cada PRD tem: objetivo, pré-requisitos, valores, passo a passo com **onde mostrar no console**, lições do ensaio e critérios de aceite. O Claude Code pede aprovação antes de criar, alterar ou apagar qualquer coisa.
