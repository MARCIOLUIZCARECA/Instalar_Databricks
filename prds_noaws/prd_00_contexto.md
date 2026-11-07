# PRD 00 · Contexto, valores e regras · versão SEM AWS (leia antes de qualquer outro PRD)

**Para quem lê:** o Claude Code. Este arquivo vale para **todos** os PRDs da pasta `prds_noaws/`. Os outros (`prd_01` a `prd_06`) dizem o que construir em cada etapa; este diz o cenário, os nomes e as regras que não mudam.

**Por que existe esta versão:** muitos alunos não têm conta AWS (ou não conseguem configurar roles, buckets e VPC). Eles fazem a aula só com a conta Databricks criada pelo **Express setup**: um workspace **serverless**, com **storage padrão gerenciado pela Databricks** (default storage). A plataforma que se monta é a mesma; muda **onde** as peças moram.

---

## 1. O cenário

Workshop **"Do Zero à Produção — Databricks Enterprise"**. A turma monta, com o Claude Code, uma plataforma Databricks com cara de empresa.

- **Exercício:** "a RedRex (empresa de engenharia de dados do instrutor; na repetição em casa, o time é você) foi contratada pela Coca-Cola para implementar o Databricks". Cenário inspirado em experiência real. **Nenhum dado, número ou arquitetura da Coca-Cola é usado.**
- **Dados da demo:** uma rede de delivery fictícia, **Food Intelligence** (pedidos e lojas sintéticos).
- **Foco:** como um arquiteto de plataforma organiza o Databricks numa empresa.

A jornada que o aluno precisa enxergar no fim:

**Databricks Account → Workspace → Ambientes (catálogos) → Grupos → Unity Catalog → Volume → Pipeline → Dados para o negócio.**

## 2. O que muda em relação à versão com AWS

| Na versão com AWS | Na versão SEM AWS (Express) | Por quê |
|---|---|---|
| Workspace DEV e workspace PROD (clássicos, VPC própria) | **Um workspace só** (o do Express). DEV e PROD são **catálogos** separados: `food_dev` e `food_prod` | Express não cria VPC, bucket nem role na sua conta; e não queremos depender de criar workspaces novos |
| Bucket raiz, storage role, cross-account role | **Nada disso.** O storage é o *default storage* da Databricks | A Databricks hospeda o storage |
| Buckets raw e lakehouse no S3, storage credential, external locations | **Catálogos com storage padrão** + **volume gerenciado** `raw` em cada catálogo | Sem S3 próprio, os arquivos brutos vão para um volume do Unity Catalog |
| `upload_to_s3.sh` | `upload_to_volume.sh` (`databricks fs cp` para `/Volumes/...`) | Mesmo papel: "o arquivo bruto chega ao lake" |
| Isolamento por *workspace binding* | Isolamento por **GRANTs** (quem enxerga qual catálogo) | Só existe um workspace |
| Bundle com targets em dois workspaces | Bundle com targets `dev` e `prod` **no mesmo workspace**, mudando catálogo, pasta e permissões | Mesma ideia de promoção |
| Mostrar `_delta_log/` no bucket S3 | Mostrar o `location` no `DESCRIBE DETAIL` e explicar que o storage é gerenciado | Não há console S3 para abrir |

O que **não muda**: grupos, Unity Catalog, medalhão Bronze/Silver/Gold, testes, promoção com Asset Bundles, Dashboard, App e Genie.

## 3. Valores do projeto

| O quê | Valor |
|---|---|
| Workspace | `{{WS}}` (profile do CLI com o mesmo nome), URL `{{WS_URL}}` |
| Catálogos do projeto (criados no PRD 01) | `food_dev` (DEV), `food_prod` (PROD) |
| Schema / tabelas | `orders` · `bronze_orders`, `silver_orders`, `gold_sales_by_store` |
| Volume dos arquivos brutos | `food_<env>.orders.raw` (gerenciado) |
| SQL warehouse | `{{WAREHOUSE_ID}}` (serverless, vem com o Express) |
| Compute | **Só serverless** (jobs, notebooks e warehouse) |

**Antes de rodar qualquer comando, substitua os `{{NOME}}` pelos valores do `config.yaml` desta pasta.** Se algum valor estiver vazio, pergunte; nunca invente.

### 3.1 Regra dos nomes de catálogo

O workspace padrão (Express) já vem com um **catálogo automático** (`{{WS_CATALOGO_AUTOMATICO}}`, normalmente o nome do workspace com `_`). Ele **não é do projeto**.

1. **Todo código, SQL, job, dashboard, App e Genie usa `food_<ambiente>`**, vindo da variável `catalog` do bundle. Nunca o catálogo automático, nunca o nome escrito à mão.
2. **Sempre o nome completo em três partes** (`food_prod.orders.gold_sales_by_store`).
3. **Antes de encerrar qualquer PRD**, procure `{{WS_CATALOGO_AUTOMATICO}}` nos arquivos do projeto e nas consultas que você rodou. Se aparecer fora de uma explicação, corrija e avise.
4. Em toda tabela de resumo, escreva o catálogo do projeto; quando citar o automático, diga "automático, não usado".

## 4. Regras para o Claude Code

1. **Aprovação antes de criar, alterar ou apagar.** Mostre o comando, diga em uma frase o que ele faz e espere o "pode". Leitura roda direto.
2. **Explique como em aula.** Antes de cada peça, uma ou duas frases sobre o que ela é e por quê. Depois, diga **onde ver no workspace**.
3. **Nada de AWS.** Não rode `aws`, não peça conta AWS, não crie bucket, role, credential, external location nem workspace clássico. Se algum passo parecer precisar disso, pare e explique a alternativa Express.
4. **Não crie workspaces.** Tudo acontece no workspace `{{WS}}`.
5. **Sem credenciais em arquivo.** Só nomes de profiles.
6. **Deploy no target `prod` só com confirmação explícita** ("pode publicar em PROD").
7. **Use as skills da Databricks** (`databricks-core` e a do produto) e a documentação oficial atual. Não invente flags.
8. **Se um recurso não existir na conta Express** (por exemplo, gerenciar grupos na conta, Apps, ou alguma permissão), **não contorne nem insista**: mostre o erro, explique em uma frase e siga o plano B escrito no PRD.
9. **Projeto pequeno de propósito.** Nada de ML, agentes, múltiplos domínios, APIs externas ou CI/CD complexo.

## 5. Lições (valem para todos os PRDs)

| Lição | Como evitar |
|---|---|
| O Express pode não deixar criar catálogo com `MANAGED LOCATION` (não há external location) | Criar o catálogo **sem** `MANAGED LOCATION`: ele usa o storage padrão |
| Limites da conta trial/Express (quotas, recursos desligados) | Testar cada recurso uma vez; se falhar por limite, mostrar o erro e seguir o plano B |
| `food_prod` × catálogo automático confundidos | Seção 3.1 |
| Warehouse desligado demora 2–5 min para responder | Ligar uns 15 min antes da aula |
| Genie exige a tabela Gold antes do deploy | `bundle deploy` → `bundle run` da pipeline → `bundle deploy` de novo |
| Os dois targets estão no **mesmo** workspace | Pastas diferentes (`root_path`) e nomes de recursos diferentes; o modo `development` já põe o prefixo `[dev <usuário>]` |

## 6. Ordem dos PRDs

| PRD | Etapa |
|---|---|
| `prd_01_workspace_express.md` | Login no workspace padrão, `config.yaml` e criação dos ambientes DEV (`food_dev`) e PROD (`food_prod`) |
| `prd_02_governanca.md` | Grupos, usuários e permissões |
| `prd_03_dados.md` | Dados sintéticos no volume `raw` |
| `prd_04_pipeline.md` | Raw → Bronze → Silver → Gold em DEV |
| `prd_05_promocao.md` | DEV → TEST → PROD com Asset Bundles |
| `prd_06_consumo.md` | Dashboard, App e Genie |
