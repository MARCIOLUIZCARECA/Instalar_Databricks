# PRD 00 · Contexto, valores e regras (leia antes de qualquer outro PRD)

**Para quem lê:** o Claude Code. Este arquivo vale para **todos** os PRDs da pasta. Os outros (`prd_01` a `prd_06`) dizem o que construir em cada etapa; este diz o cenário, os nomes e as regras que não mudam.

---

## 1. O cenário

Workshop ao vivo **"Do Zero à Produção — Databricks Enterprise na AWS"** (4 horas). A turma assiste o instrutor montar, com o Claude Code, uma plataforma Databricks com cara de empresa e depois repete em casa.

- **Exercício:** "a RedRex (empresa de engenharia de dados do instrutor; na repetição em casa, o time é você) foi contratada pela Coca-Cola para implementar o Databricks". Cenário inspirado em experiência real. **Nenhum dado, número ou arquitetura da Coca-Cola é usado.**
- **Dados da demo:** uma rede de delivery fictícia, **Food Intelligence** (pedidos e lojas sintéticos).
- **Foco:** como um arquiteto de plataforma organiza o Databricks numa empresa. Não é analytics sofisticado.

A jornada que o participante precisa enxergar no fim:

**AWS → Databricks Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Dados para o negócio.**

## 2. O que já existe quando o projeto começa

Cada aluno tem a **sua** conta AWS e a **sua** conta Databricks. Os valores de cada um ficam no [`config.yaml`](config.yaml), e os PRDs se referem a eles como `{{NOME}}`. O primeiro passo do PRD 01 preenche esse arquivo (só leitura + confirmação do aluno).

| Peça | Como foi criada | Valores no `config.yaml` |
|---|---|---|
| Conta Databricks (trial) | Cadastro em login.databricks.com/signup (Work → Start a trial, cloud AWS) | `DATABRICKS_ACCOUNT_ID`, `NOME_DA_CONTA`, `DATABRICKS_PROFILE` |
| Workspace serverless do cadastro (Express) | Automático. A região padrão pode não ser a do workshop (no ensaio, `us-west-2`) | — (não mexer) |
| Workspace clássico DEV | À mão, no Bloco 2 (manual, seções 2 a 6) | `WS_DEV`, `WS_DEV_URL`, `DEV_ROOT_BUCKET`, `DEV_STORAGE_ROLE`, `DEV_CROSS_ACCOUNT_ROLE`, `METASTORE` |
| Conta AWS | Do aluno, no plano pago | `AWS_ACCOUNT_ID`, `AWS_PROFILE`, `REGIAO` |

Se a conta AWS estiver numa **AWS Organization** (por exemplo, criada pela tela "Projects"), pode haver SCP/RCP bloqueando a Databricks: veja as lições (seção 5).

## 3. Valores do projeto

| O quê | Valor |
|---|---|
| Região | **`{{REGIAO}}`** para tudo (padrão do workshop: `us-east-2`) |
| Conta AWS da Databricks (aparece nas policies; igual para todos, não trocar) | `414351767826` |
| Prefixo das peças novas | `{{PREFIXO}}` (um por aluno; evita colidir com qualquer montagem anterior) |
| Workspaces | `{{WS_DEV}}` (DEV) e `{{WS_PROD}}` (PROD). Profiles do CLI com os mesmos nomes. HML é opcional: documentar, não criar |
| Catálogos do projeto | `food_dev`, `food_prod` |
| Schema / tabelas | `orders` · `bronze_orders`, `silver_orders`, `gold_sales_by_store` |

**Antes de rodar qualquer comando, substitua os `{{NOME}}` pelos valores do `config.yaml`.** Se algum valor estiver vazio, pergunte; nunca invente.

### 3.1 Regra dos nomes de catálogo (leia com atenção)

Cada workspace tem **dois tipos** de catálogo, e os nomes se parecem:

| Tipo | Nome | Quem cria | Usar? |
|---|---|---|---|
| **Catálogo do projeto** | `food_dev`, `food_prod` (sempre `food_<ambiente>`) | PRD 02 | **Sim: é o único que o projeto usa** |
| **Catálogo automático** | o nome do workspace com `_` no lugar de `-` (ex.: `dev-food` → `dev_food`, `prod-food` → `prod_food`) | a Databricks, ao criar o workspace | **Nunca** |

Com os workspaces `dev-food` e `prod-food`, os dois tipos ficam com as mesmas palavras em ordem trocada (`food_prod` × `prod_food`). É fácil escrever um no lugar do outro, e a consulta funciona sem erro, só que no catálogo errado, que fica no bucket raiz e não no lakehouse.

Regras:

1. **Todo código, SQL, job, dashboard, App e Genie usa `food_<ambiente>`**, vindo da variável `catalog` do bundle. Nunca o catálogo automático, nunca o nome escrito à mão.
2. **Sempre o nome completo em três partes** (`food_prod.orders.gold_sales_by_store`). Não dependa do catálogo padrão do workspace.
3. **Antes de encerrar qualquer PRD**, procure `{{WS_DEV}}` e `{{WS_PROD}}` com `_` (ex.: `dev_food`, `prod_food`) em todos os arquivos do projeto e nas consultas que você rodou. Se aparecer fora de uma explicação, corrija e avise.
4. Em toda tabela de resumo para o aluno, escreva o nome do catálogo do projeto e, quando citar o automático, diga explicitamente "automático, não usado".
5. **Ao criar workspaces novos**, prefira nomes que não repitam as palavras do catálogo do projeto (ex.: `{{PREFIXO}}-dev` e `{{PREFIXO}}-prod`, que geram `{{PREFIXO}}_dev` e `{{PREFIXO}}_prod`). Se os nomes já existirem, siga as regras 1 a 4.

## 4. Regras para o Claude Code

1. **Aprovação antes de criar, alterar ou apagar.** Mostre o comando, diga em uma frase o que ele faz e espere o "pode". Leitura roda direto.
2. **Explique como em aula.** Antes de cada peça, uma ou duas frases sobre o que ela é e por quê. Depois, diga **onde mostrar no console** (AWS ou Databricks).
3. **Nunca reaproveite peças de outra montagem.** Nomes novos com o prefixo `{{PREFIXO}}`. Se um nome já existir, pare e pergunte.
4. **Não toque no que é do DEV manual** (seção 2), a menos que o PRD peça.
5. **Sem credenciais em arquivo.** Só nomes de profiles.
6. **Nada pago sem autorização.** Workspaces clássicos custam por hora (NAT Gateway) mesmo parados.
7. **Deploy em PROD só com confirmação explícita** ("pode publicar em PROD").
8. **Use as skills da Databricks** (databricks-core e a do produto) e a documentação oficial atual. Não invente flags.
9. **Projeto pequeno de propósito.** Nada de ML, agentes, múltiplos domínios, APIs externas ou CI/CD complexo.

## 5. Lições do ensaio (valem para todos os PRDs)

| Lição | Como evitar |
|---|---|
| `< >` esquecido no JSON de policy → `Policy has invalid resource` | Antes de aplicar, procure `<` e `>` no JSON |
| Role reaproveitada com **External ID de outra conta Databricks** e **bucket antigo** na policy → `Storage credential IAM role ... doesn't have access to S3 bucket` | Peças novas; ler de volta trust e permissões antes de registrar na Databricks |
| IAM demora a propagar | Esperar ~60 s entre criar a role e usá-la |
| Formulário do console abriu em São Paulo | Sempre passar a região `{{REGIAO}}` explicitamente |
| **Limite diário de criação de workspaces** na conta Databricks (apagar não libera) | Não criar workspaces de teste. Se falhar por limite, mostrar o erro e não contornar |
| **Limite AWS de 5 VPCs e 5 Elastic IPs** por região | Conferir antes de criar workspace clássico |
| Workspace novo ganha um **catálogo automático** com o nome dele (ex.: `prod-food` → `prod_food`), que vira o catálogo padrão. No ao vivo, `prod_food` e `food_prod` foram trocados em alguns lugares | Seguir a seção 3.1: só `food_<ambiente>`, sempre em três partes; trocar o catálogo padrão; procurar o nome automático antes de encerrar cada PRD |
| **SQL warehouse serverless com 403** nos buckets do projeto (suspeita: RCP da Organization) | Testar o serverless logo após a governança. Se der 403, usar um warehouse **clássico** PRO 2X-Small, auto-stop 10 min, chamado `Food Classic Warehouse` |
| Genie exige a tabela Gold antes do deploy | `bundle deploy` → `bundle run` da pipeline → `bundle deploy` de novo |
| SCP/RCP da Organization bloqueando a Databricks | Se aparecer `Failed credential validation checks` com policies corretas, investigar SCP/RCP antes de mexer nas roles |

## 6. Fatos que as policies da AWS precisam respeitar

- **Bucket policy do bucket raiz:** `Allow` para `arn:aws:iam::414351767826:root` com a condição `aws:PrincipalTag/DatabricksAccountId` = Databricks Account ID; `Deny` da mesma conta em `<bucket>/unity-catalog/*`.
- **Roles do Unity Catalog (storage e dados):** trust para `arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL` **e** para a própria role (self-assuming), com `sts:ExternalId`. Criar em duas etapas: trust provisória (External ID `0000`, sem self), depois a definitiva.
- **External ID:** na storage role do workspace, é o Databricks Account ID. Na role de dados (storage credential), é o que a credential mostrar; se quem cria é account admin, costuma ser o próprio Account ID.
- **Cross-account role:** trust para `arn:aws:iam::414351767826:root` com `sts:ExternalId` = Databricks Account ID; permissões EC2/VPC da documentação para **Databricks-managed VPC**.

## 7. Ordem dos PRDs

| PRD | Etapa | Bloco da aula |
|---|---|---|
| `prd_01_workspace_prod.md` | Preencher o `config.yaml` e criar o workspace `{{WS_PROD}}` | 3 |
| `prd_02_governanca.md` | Grupos, buckets de dados, Unity Catalog, permissões | 4 |
| `prd_03_dados.md` | Dados sintéticos no S3 | 4/5 |
| `prd_04_pipeline.md` | Raw → Bronze → Silver → Gold em DEV | 5 |
| `prd_05_promocao.md` | DEV → TEST → PROD com Asset Bundles | 5 |
| `prd_06_consumo.md` | Dashboard, App e Genie | 6 |
