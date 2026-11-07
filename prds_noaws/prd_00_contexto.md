# PRD 00 · Contexto, valores e regras · versão SEM AWS (leia antes de qualquer outro PRD)

**Para quem lê:** o Claude Code. Este arquivo vale para **todos** os PRDs da pasta `prds_noaws/`. Os outros (`prd_01` a `prd_06`) dizem o que construir em cada etapa; este diz o cenário, os nomes e as regras que não mudam.

**Por que existe esta versão:** muitos alunos não têm conta AWS (ou não conseguem configurar roles, buckets e VPC). Eles fazem a aula só com a conta Databricks criada pelo **Express setup**. Em vez de workspaces clássicos, usam **workspaces serverless**, com **storage padrão gerenciado pela Databricks** (default storage). A plataforma que se monta é a mesma, com DEV e PROD em workspaces separados; muda **onde** as peças moram.

---

## 1. O cenário

Workshop **"Do Zero à Produção — Databricks Enterprise"**. A turma monta, com o Claude Code, uma plataforma Databricks com cara de empresa.

- **Exercício:** "a RedRex (empresa de engenharia de dados do instrutor; na repetição em casa, o time é você) foi contratada pela Coca-Cola para implementar o Databricks". Cenário inspirado em experiência real. **Nenhum dado, número ou arquitetura da Coca-Cola é usado.**
- **Dados da demo:** uma rede de delivery fictícia, **Food Intelligence** (pedidos e lojas sintéticos).
- **Foco:** como um arquiteto de plataforma organiza o Databricks numa empresa.

A jornada que o aluno precisa enxergar no fim:

**Databricks Account → Workspaces DEV e PROD → Grupos → Unity Catalog → Volume → Pipeline → Dados para o negócio.**

## 2. O que muda em relação à versão com AWS

| Na versão com AWS | Na versão SEM AWS (Express) | Por quê |
|---|---|---|
| Workspace DEV (à mão) e PROD (Claude Code), clássicos, com VPC própria | Workspaces **serverless** `{{WS_DEV}}` e `{{WS_PROD}}`, criados pelo Claude Code com `compute_mode: SERVERLESS` | Serverless não precisa de VPC, bucket nem role na sua conta |
| Bucket raiz, storage role, cross-account role, credential e storage configuration | **Nada disso.** O storage é o *default storage* da Databricks | A Databricks hospeda o storage e o compute |
| Buckets raw e lakehouse no S3, storage credential, external locations | **Catálogos no storage padrão** + **volume gerenciado** `raw` em cada catálogo | Sem S3 próprio, os arquivos brutos vão para um volume do Unity Catalog |
| `upload_to_s3.sh` | `upload_to_volume.sh` (`databricks fs cp` para `/Volumes/...`) | Mesmo papel: "o arquivo bruto chega ao lake" |
| Isolamento por *workspace binding* | Catálogo no storage padrão **já nasce preso ao workspace** onde foi criado, + GRANTs | Mesmo efeito, sem configurar |
| Bundle com targets em dois workspaces | Igual: target `dev` no `{{WS_DEV}}`, target `prod` no `{{WS_PROD}}` | — |
| Mostrar `_delta_log/` no bucket S3 | Mostrar o `location` no `DESCRIBE DETAIL` e explicar que o storage é gerenciado | Não há console S3 para abrir |

O que **não muda**: dois workspaces, grupos, Unity Catalog, medalhão Bronze/Silver/Gold, testes, promoção com Asset Bundles, Dashboard, App e Genie.

O workspace **Express** do cadastro continua existindo e **não é usado** pelo projeto (como na versão AWS).

**Plano B (um workspace só):** se o aluno não conseguir criar workspaces (sem acesso ao Account Console ou limite da conta trial), o PRD 01 registra `MODO: um-workspace` no `config.yaml`. Nesse caso, `{{WS_DEV}}` e `{{WS_PROD}}` são o mesmo workspace (o Express), os dois catálogos ficam nele, o isolamento é só por GRANTs e o bundle usa pastas diferentes (`root_path`) por target.

## 3. Valores do projeto

| O quê | Valor |
|---|---|
| Conta | `{{DATABRICKS_ACCOUNT_ID}}` · profile de conta `{{DATABRICKS_ACCOUNT_PROFILE}}` |
| Região | `{{REGIAO}}` (a do Express) · metastore `{{METASTORE}}` |
| Workspaces | `{{WS_DEV}}` (DEV) e `{{WS_PROD}}` (PROD), serverless. Profiles do CLI com os mesmos nomes |
| Catálogos do projeto (criados no PRD 01) | `food_dev` (só no DEV), `food_prod` (só no PROD) |
| Schema / tabelas | `orders` · `bronze_orders`, `silver_orders`, `gold_sales_by_store` |
| Volume dos arquivos brutos | `food_<env>.orders.raw` (gerenciado) |
| SQL warehouses | `{{WAREHOUSE_ID_DEV}}` e `{{WAREHOUSE_ID_PROD}}` (serverless) |
| Compute | **Só serverless** (jobs, notebooks e warehouse) |

**Antes de rodar qualquer comando, substitua os `{{NOME}}` pelos valores do `config.yaml` desta pasta.** Se algum valor estiver vazio, pergunte; nunca invente.

**Profile certo para cada ambiente:** tudo de DEV usa `--profile {{WS_DEV}}`; tudo de PROD usa `--profile {{WS_PROD}}`. Grupos e workspaces usam `--profile {{DATABRICKS_ACCOUNT_PROFILE}}`.

### 3.1 Regra dos nomes de catálogo

Cada workspace vem com um **catálogo automático** (`{{CATALOGO_AUTOMATICO_DEV}}`, `{{CATALOGO_AUTOMATICO_PROD}}`, normalmente o nome do workspace com `_`). Eles **não são do projeto**.

1. **Todo código, SQL, job, dashboard, App e Genie usa `food_<ambiente>`**, vindo da variável `catalog` do bundle. Nunca o catálogo automático, nunca o nome escrito à mão.
2. **Sempre o nome completo em três partes** (`food_prod.orders.gold_sales_by_store`).
3. **Antes de encerrar qualquer PRD**, procure os catálogos automáticos nos arquivos do projeto e nas consultas que você rodou. Se aparecerem fora de uma explicação, corrija e avise.
4. Em toda tabela de resumo, escreva o catálogo do projeto; quando citar o automático, diga "automático, não usado".
5. **`{{PREFIXO}}` nunca é `food`**: senão o automático vira `food_dev` / `food_prod` e colide com o do projeto.

## 4. Regras para o Claude Code

1. **Aprovação antes de criar, alterar ou apagar.** Mostre o comando, diga em uma frase o que ele faz e espere o "pode". Leitura roda direto.
2. **Explique como em aula.** Antes de cada peça, uma ou duas frases sobre o que ela é e por quê. Depois, diga **onde ver no console**.
3. **Nada de AWS.** Não rode `aws`, não peça conta AWS, não crie bucket, role, credential, external location nem workspace clássico. Se algum passo parecer precisar disso, pare e explique a alternativa serverless.
4. **Workspaces: só os dois do PRD 01**, serverless. Não crie workspaces de teste (a conta trial tem limite diário). Não mexa no workspace Express.
5. **Sem credenciais em arquivo.** Só nomes de profiles.
6. **Deploy no target `prod` só com confirmação explícita** ("pode publicar em PROD").
7. **Use as skills da Databricks** (`databricks-core` e a do produto) e a documentação oficial atual. Não invente flags.
8. **Se um recurso não existir na conta Express** (por exemplo, Account Console, Apps ou alguma permissão), **não contorne nem insista**: mostre o erro, explique em uma frase e siga o plano B escrito no PRD.
9. **Projeto pequeno de propósito.** Nada de ML, agentes, múltiplos domínios, APIs externas ou CI/CD complexo.

## 5. Lições (valem para todos os PRDs)

| Lição | Como evitar |
|---|---|
| Catálogo com `MANAGED LOCATION` não funciona (não há external location) | Criar o catálogo **sem** `MANAGED LOCATION`, dentro do workspace serverless: ele usa o storage padrão |
| Catálogo no storage padrão só aparece no workspace onde nasceu | Criar `food_dev` com o profile `{{WS_DEV}}` e `food_prod` com `{{WS_PROD}}`. Se um catálogo "sumiu", confira o profile |
| **Limite diário de criação de workspaces** na conta trial (apagar não libera) | Criar só os dois. Se falhar por limite, mostrar o erro e seguir o plano B |
| Workspace numa região sem metastore | Criar na mesma região do Express |
| Limites da conta trial/Express (quotas, recursos desligados) | Testar cada recurso uma vez; se falhar por limite, mostrar o erro e seguir o plano B |
| `food_prod` × catálogo automático confundidos | Seção 3.1 |
| Comando de PROD rodado com o profile de DEV (ou o contrário) | Dizer o profile em voz alta antes de cada comando; resumo final por workspace |
| Warehouse desligado demora 2–5 min para responder | Ligar uns 15 min antes da aula |
| Genie exige a tabela Gold antes do deploy | `bundle deploy` → `bundle run` da pipeline → `bundle deploy` de novo |

## 6. Ordem dos PRDs

| PRD | Etapa |
|---|---|
| `prd_01_workspaces_serverless.md` | Login de conta, `config.yaml`, workspaces serverless DEV e PROD e os catálogos `food_dev` / `food_prod` |
| `prd_02_governanca.md` | Grupos na conta, acesso aos workspaces e permissões |
| `prd_03_dados.md` | Dados sintéticos no volume `raw` |
| `prd_04_pipeline.md` | Raw → Bronze → Silver → Gold em DEV |
| `prd_05_promocao.md` | DEV → TEST → PROD com Asset Bundles |
| `prd_06_consumo.md` | Dashboard, App e Genie |
