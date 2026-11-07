# Roteiro de fala · slide a slide

Para cada slide: **o que dizer** (em linguagem de conversa) e, quando útil, **se perguntarem**. Os números são os do deck (124 slides). Os tempos somam ~4h. Apresentação: <https://claude.ai/artifact/UFhcfvGJBqyJgqYZmvxuFj>.

Fio condutor da aula: **a RedRex foi contratada pela Coca-Cola para implementar o Databricks** (cenário de exercício inspirado em experiência real, sem nenhum dado ou informação da empresa). Cada bloco responde a uma pergunta que esse cliente faria.

**Como a aula anda:** até o Bloco 2, tudo à mão (cadastro, Account Console, workspace DEV pelo manual). Do Bloco 3 em diante, a plataforma sai do **Claude Code a partir dos PRDs** da pasta [`prds/`](../../prds/README.md). Cada PRD é um ciclo de três momentos:

1. **Slide do prompt:** cole o prompt no Claude Code e aprove os passos que ele pedir.
2. **Slides de explicação** enquanto ele trabalha (5 a 10 minutos). Volte ao terminal a cada pedido de aprovação.
3. **Slide "O que foi criado":** mostre cada peça no console, na ordem da tabela.

---

## Abertura (09:00–09:05)

**1 · Capa**
- "Bom dia! Hoje a gente sai do zero e chega numa plataforma Databricks com cara de empresa."
- Formato: vocês assistem agora, repetem depois. Tudo está no repositório: o manual com prints e os PRDs para o Claude Code.

**2 · Seja bem-vindo à Jornada de Dados** (3 a 5 min)
- Faça as quatro perguntas e peça respostas no chat: quem é novo, quem assiste pela primeira vez, quem está há muito tempo, quem quer compartilhar um sucesso.
- Leia alguns nomes em voz alta. Se alguém antigo tiver um caso (vaga, promoção, projeto em produção), convide para contar em 1 minuto.

**3 · O time**
- Apresente Luciano Vasconcelos, Michelle Perrone, Jennifer Maia e Caio Machado, e agradeça as participações de Luiza, Allan e Laender.
- "O time está no chat para ajudar durante toda a aula."

**4 · O foco de hoje: o início do projeto**
- "Hoje é aula de começo de projeto: conta, ambientes, acesso, primeira pipeline, custos e decisões."
- "Muita coisa vamos tocar rapidamente: aplicações no Databricks, infraestrutura na AWS e agentes de IA. Cada uma tem uma trilha completa na Jornada."

**5 · Agenda**
- Três atos: começar é fácil (Express), entender cada peça (setup manual) e escalar com um agente (Claude Code + PRDs).
- Depois: o que transforma infraestrutura em plataforma (governança, pipeline, consumo) e quanto tudo isso custa. Repare na barra no topo de cada slide: ela mostra em que bloco estamos.

## O desafio e o mercado (09:05–09:35)

**6 · Abertura do bloco**
- "Antes de abrir qualquer console: por que Databricks, e como convencer a empresa."

**7 · A RedRex foi contratada pela Coca-Cola**
- "Hoje vocês são o time da RedRex, a nossa empresa de engenharia de dados. Imaginem: a Coca-Cola contratou a RedRex para implementar o Databricks. Antes de abrir qualquer console, o cliente faz quatro perguntas." Leia as quatro.
- Cite rapidamente com quem a RedRex trabalha (os logos da faixa).
- "A aula de hoje é a resposta para cada uma delas." Reforce: é um exercício. Nenhum dado ou arquitetura real da empresa.

**8 · Uma experiência real (2017)**
- **O time técnico:** "Em 2017 a gente já tinha um time de engenharia de dados que trabalhava majoritariamente com AWS. Era um time que veio de back-end: muito processamento em Lambda, contratos e pipelines na AWS."
- **O gap:** "A AWS é muito técnica, não tem uma interface amigável. O time de produto usava Power BI, o time técnico usava AWS, e tinha um gap enorme no meio. O dado existia, mas o produto não conseguia usar sem depender da engenharia para cada número."
- **A decisão:** "Contratamos o Databricks para ser a ponte entre a AWS e o Power BI: os engenheiros continuaram na AWS, aproveitando contratos e pipelines, e o produto passou a ter dados prontos para consumir."
- **Ligação com hoje:** "Escolher plataforma é resolver um problema entre pessoas, não só de tecnologia."
- *Se perguntarem "por que não só Athena/Redshift?"*: a dor era usabilidade e colaboração entre times técnicos e de produto; o Databricks juntava notebooks, SQL e um caminho direto para o Power BI, sobre os dados que já estavam no S3.

**9 · Quatro caminhos**
- "Não existe a melhor plataforma; existe a que encaixa."
- Databricks: engenharia + BI + IA juntos, formatos abertos. Snowflake: SQL simples, pouca administração. Fabric: casa Microsoft e Power BI. On-premise: controle total, mas tudo por sua conta.
- *Se perguntarem "qual é mais barato?"*: depende do uso; o que muda é o modelo de cobrança (bloco de custos).

**10 · Databricks × Snowflake**
- Pergunta de negócio: "a empresa quer só analytics, ou dados + IA como plataforma?"
- No Databricks o dado fica no S3 da empresa, em Delta/Iceberg. No Snowflake o armazenamento é gerenciado por eles. Os dois estão convergindo.

**11 · Fabric e on-premise**
- Fabric faz sentido para empresa 100% Microsoft com foco em BI. On-premise, quando a regulação proíbe nuvem; o custo escondido é o time e o tempo para escalar.
- A escolha de nuvem e a de plataforma são separadas: Databricks roda em AWS, Azure e GCP.

**12 · Uma plataforma, os seus dados, a sua conta**
- Seis argumentos, do técnico ao comercial. Destaque dois: dados no S3 da empresa em formato aberto, e compra pelo Marketplace.

**13 · Como convencer a sua organização**
- "Executivo compra resultado e redução de risco, não tecnologia."
- Um caso de negócio concreto, custo total, piloto de 60 a 90 dias com uma métrica. Prepare as três objeções: segurança, custo e lock-in.
- Volte à história de 2017: o argumento que convenceu foi de negócio, não técnico.

**14 · O cenário da demo: Food Intelligence**
- "Para não usar dado real, a demo usa uma rede de delivery fictícia: pedidos e lojas chegando no S3."
- O foco não é analytics sofisticado; é como um arquiteto organiza a plataforma.

**15 · A jornada de hoje**
- Mapa do dia: AWS → Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Consumo → Negócio. "No fim, a gente volta aqui."

## Bloco 1 · Fundamentos e Express (09:35–09:55)

Bloco denso: 23 slides em 20 minutos. Os slides 32 a 38 (um por item do Account Console) são de passagem rápida; se o tempo apertar, fique no 29 a 31.

**16 · Abertura do bloco**
- "Vamos criar a conta do zero, na frente de vocês."

**17 · Dois caminhos, sem cartão de crédito** (print do cadastro)
- "Em login.databricks.com/signup aparece essa tela." Work = Free Trial (14 dias, US$ 400 em créditos, plataforma completa). Personal = Free Edition (grátis para sempre, para estudar, sem Account Console).
- "Para a aula, **Work → Start a trial**. A Free Edition não serve: sem Account Console, não dá para criar o workspace clássico nem grupos."

**18 · Uma conta, vários workspaces**
- Account = prédio inteiro (usuários, grupos, metastore, cobrança). Workspace = um andar (notebooks, jobs, compute).
- "O mesmo usuário pode estar em DEV e não em PROD." No rodapé, o link para criar a conta.

**19 · Control plane × compute plane**
- Control plane: na conta da Databricks. Compute plane (no clássico): na conta AWS da empresa.

**20 · Serverless ou clássico?**
- Serverless: roda na conta da Databricks, começa em minutos, uma fatura só. Clássico: roda na sua VPC, controle total de rede, duas faturas.

**21 · Quem cobra o quê: duas decisões**
- "Duas perguntas separadas. A técnica: onde o compute roda? A comercial: de quem eu compro o DBU?"
- Percorra a matriz: serverless + direto (uma fatura, Databricks); serverless + Marketplace (uma fatura, AWS); clássico + direto (duas faturas); clássico + Marketplace (tudo na AWS, em linhas separadas).

**22 · Free, Trial, Express ou setup completo?**
- *Se perguntarem "dá para fazer a aula na Free Edition?"*: os notebooks sim; o setup de conta não.

**23 · Nome da conta e cloud** (print)
- Nome da conta = em geral, o nome da empresa. Cloud: **AWS**. "Ao clicar em Continue, a Databricks cria a conta e um workspace serverless sozinha. Esse é o Express."

**24 · O workspace Express já está pronto** (print do primeiro login)
- Percorra os 5 números: Manage Trial, seletor de workspace, seu usuário, Catalog, SQL Warehouses/Compute.
- Bastidor: o workspace foi criado em `us-west-2` (Oregon), a região padrão; os da aula ficam em `us-east-2`.

**25 · Acabaram os 14 dias. E agora?**
- Pausa dramática. "Passaram os 14 dias. Perdi tudo? Tenho que recriar?" Deixe a turma responder no chat antes de avançar.

**26 · Duas formas de continuar**
- "Não precisa recriar nada: a conta só precisa de uma forma de pagamento." Cartão (Account Console → Settings) ou AWS Marketplace (fatura da AWS, pode abater o EDP).

**27 · Pelo AWS Marketplace**
- Demo: AWS Marketplace → Databricks Data Intelligence Platform → Subscribe. Oferta pública, paga pelo uso, 1 DCU = US$ 1, fatura emitida pela AWS.
- "Testado no ensaio: o Subscribe **não cria workspace novo**. Liga a assinatura à account."

**28 · Marketplace é canal de compra**
- Igual: console, workspaces, Unity Catalog, preço de lista. Muda: quem cobra, o contrato, o EDP, oferta privada.
- O cadastro direto vem com créditos de trial; o Marketplace cobra pelo uso desde o início.

**29 · Acima dos workspaces: a conta** (print do Account Console)
- "O workspace é onde se trabalha. A conta é onde se administra." accounts.cloud.databricks.com, só account admins entram.

**30 · Uma account, vários workspaces** (desenho da conta)
- A account por fora (usuários, cloud resources, cobrança). Dentro: `us-west-2` com o Express e `us-east-2` com DEV e PROD (vamos criar).
- "Um metastore por região: o Express não enxerga as tabelas de DEV e PROD, e isso é esperado."

**31 · Metastore: o catálogo, não a estante**
- "Pensem numa biblioteca. O metastore é o catálogo de fichas: diz que livro existe, em que estante está e quem pode pegar. Os livros ficam na estante, que aqui é o S3."
- Três níveis: catálogo, schema, tabela (`food_dev.gold.vendas`). Um GRANT vale em todos os workspaces da região.

**32 a 38 · Os sete itens do Account Console** (passagem rápida)
- Workspaces, Catalog, Usage, User management, Security, Cloud resources, Settings. Para cada um: o que é, como está agora no trial e onde usamos hoje. O destaque é Cloud resources: "vazio, porque o Express não usa nada da sua AWS; vai ser preenchido no Bloco 2".
- Bastidor: o workspace leva alguns minutos para aparecer na lista depois do cadastro.

**39 · Funcionou em 2 minutos. Por que a empresa não para aqui?**

| Pergunta | Resposta curta | Onde a aula resolve |
|---|---|---|
| **Onde estão os dados?** | No Express, o armazenamento é gerenciado pela Databricks. Para uma empresa, o natural é o dado no **próprio S3**. | Bloco 2 (bucket raiz) e PRD 02 (buckets de dados) |
| **Quem paga a máquina?** | Serverless: tudo em DBU, uma fatura. Clássico: a AWS cobra a máquina, a Databricks o DBU. | Slide 21 e bloco de custos |
| **Como separo DEV de PROD?** | Um workspace por ambiente, catálogo isolado por ambiente, o mesmo código promovido. | Bloco 2 (DEV à mão) e PRD 01 (PROD pelo agente) |
| **Quem pode ver o quê?** | Grupos na conta, atribuídos aos workspaces, com permissões no Unity Catalog. | PRD 02 |

- Fecho: "Funcionar é fácil. Funcionar com dado na nossa conta, ambientes separados e acesso controlado é o trabalho de hoje."

## Bloco 2 · AWS na mão: o workspace DEV (09:55–10:30)

O passo a passo ao vivo é pelo **manual no GitHub** (`manual/README.md`, seções 2 a 6), que tem os JSONs para copiar e colar. Os slides 41 a 47 são o mapa e o plano B se o console travar.

**40 · Abertura do bloco**
- "Agora o workspace clássico, peça por peça. É ele que vira o DEV."

**41 · Um bucket e duas chaves viram um workspace**
- Três peças na AWS + o registro na Databricks. Abra o manual no GitHub e siga as seções 2 a 6.

**42 · O que a tela "Create workspace" pede**
- Comece pelo destino: cada bloco do formulário é uma peça que vamos criar. **Confira a região:** o formulário pode abrir em São Paulo; troque para `us-east-2`.

**43 · Bucket raiz e bucket policy**
- A policy libera a Databricks só com o seu Account ID; o Deny protege a pasta do Unity Catalog.
- **Apague os `< >`** ao trocar os valores: senão, `Policy has invalid resource`.

**44 · Storage role do Unity Catalog**
- "A role mais estranha da sua conta": confia na Databricks e **em si mesma**. Nasce em duas etapas (`0000`, depois a definitiva com o seu Account ID).

**45 · Cross-account role: a chave do compute**
- Quem pode assumir: a Databricks, com o seu External ID. O que pode fazer: criar a VPC e ligar/desligar EC2.

**46 · Registrar as peças**
- Credential = cross-account role. Storage = bucket + storage role.
- *Se der `Storage credential IAM role ... doesn't have access to S3 bucket`*: External ID ou bucket errado na role (aconteceu no ensaio, com uma role reaproveitada). *Se der `Failed credential validation checks`*: espere 60 s ou é SCP/RCP (apêndice).

**47 · De Provisioning a Running**
- A Databricks cria VPC, subnets e NAT Gateway na conta da empresa. "O NAT começa a cobrar agora, mesmo sem cluster."

**48 · Trilha Claude Code**
- "Vocês acabaram de criar cada peça clicando. Entender cada peça é o que permite delegar para um agente sem perder o controle."
- "O que vem agora é um pedaço da Trilha Claude Code: 4 módulos de fundamentos e 4 projetos, um deles de engenharia de dados." Link no rodapé.

## Bloco 3 · Claude Code + PRDs: o workspace PROD (10:30–11:00)

**Antes do bloco:** terminal logado (`aws login --profile aovivo`, `databricks auth login` da conta e do DEV) e o Claude Code aberto no repositório do projeto (`RepoCocaLakehouse`), com os PRDs e o `config.yaml` (manual, seção 7).

**49 · Abertura do bloco**
- "O que eu cliquei no Bloco 2, o agente vai fazer igual, explicando e pedindo aprovação."

**50 · O que eu cliquei vira especificação. O agente executa.**
- PRD → Claude Code → CLIs (Databricks com as skills oficiais, AWS) → consoles.
- "Humano no comando, agente na execução: tudo que cria, altera ou apaga espera o meu 'pode'." O PRD é o mesmo para a turma toda; o que muda de aluno para aluno fica no `config.yaml`.

**51 · Seis PRDs, uma plataforma**
- Um PRD por etapa: 01 PROD, 02 governança, 03 dados, 04 pipeline, 05 promoção, 06 consumo. Antes de todos, o PRD 00 (regras e lições do ensaio) e o `config.yaml`.

**52 · PRD 01 · o prompt: Criar o workspace de produção** (ciclo de ~10 min)
- Cole no Claude Code: `Leia prds/prd_00_contexto.md e prds/prd_01_workspace_prod.md e vamos executar juntos, passo a passo.`
- Primeiro ele preenche o `config.yaml` só lendo (conta AWS, DEV, metastore) e pede confirmação. Depois, bucket, roles, credential, storage e o workspace, cada um com aprovação.
- **Aprove com atenção:** a criação do workspace gasta 1 do limite diário da conta. *Plano B se der limite:* mostre o erro, explique (lição de aula) e siga com o DEV.
- Durante o *Provisioning*: abra **VPC → Your VPCs** e mostre a VPC do PROD nascendo.

**53 a 59 · Enquanto o agente trabalha**

**53 · Dois workspaces, dois papéis**
- DEV: desenvolver e testar. PROD: só o que passou nos testes, tabelas oficiais, consumo.

**54 · Quantos ambientes a sua empresa precisa?**
- Só PROD: barato, mas testa em produção. DEV + PROD: **a escolha de hoje**. DEV + HML + PROD: homologação formal, mais caro e mais lento.
- Bastidor: "no ensaio, batemos o limite diário de criação de workspaces. Lição: planejar ambientes antes de sair criando".

**55 · Quanto custa cada opção parada**
- Cada workspace clássico: NAT Gateway + IP público ≈ US$ 0,05/h ≈ US$ 36/mês, mesmo sem uso. Só PROD ≈ US$ 36/mês; DEV+PROD ≈ US$ 73; com HML ≈ US$ 110.

**56 · Quatro jeitos de dividir workspaces**
- Por ambiente (hoje), por área, por região, ou combinado. "**Poucos workspaces, muitos catálogos.**"

**57 · Brasil e EUA na mesma conta**
- O metastore é **regional**: dois países, dois metastores. Dado pessoal fica no país; a matriz recebe agregados por Delta Sharing.

**58 · Novo workspace ou novo catálogo?**
- "Isso é fronteira de rede, região, ambiente ou cobrança?" Se sim, workspace. Se não, catálogo.

**59 · O que a empresa ganha separando ambientes**
- Risco isolado, teste antes, acesso por papel, custo visível, auditoria, mesmo código.

**60 · PRD 01 · O que foi criado**
- Peça ao Claude Code o resumo em tabela. Mostre, na ordem: `prod-food` em Running no mesmo metastore (Account Console → Workspaces), a VPC nova (AWS → VPC), o bucket e as roles `databricks-<prefixo>-*` (S3, IAM), credential e storage (Cloud resources), e o `config.yaml` preenchido.
- Fecho: "um feito à mão, outro pelo agente. Mesmo resultado, mas o segundo é repetível."

**61 · DEV e PROD: mesma conta, dois mundos** (demonstração, com a aba aberta)
- Catalog Explorer e Workspace → Home no `dev-food`, depois no `prod-food`. Repare no nome no canto superior direito e na URL.
- "Mesma conta, mesmo usuário, mesmo metastore, mas são dois mundos. O notebook que criei no DEV não existe no PROD: para chegar lá, ele precisa ser **promovido** (PRD 05)."
- Fala sua, como experiência: "na minha experiência, a maioria das organizações tem um workspace só. Com DEV e PROD separados, vocês já estão à frente de boa parte delas."
- Gancho: "agora que temos dois mundos, falta decidir quem entra em cada um e o que cada um lê."

## Bloco 4 · Governança e dados (11:00–11:40)

**62 · Abertura do bloco**
- "Temos onde colocar dados. Falta decidir quem acessa o quê."

**63 · PRD 02 · o prompt: Governança** (ciclo de ~10 min)
- Cole: `Leia prds/prd_00_contexto.md e prds/prd_02_governanca.md e vamos executar juntos, passo a passo.`
- Aprovações: grupos e usuários fictícios, buckets de dados, role e storage credential, catálogos, grants e a troca de dono para `platform-admins`.
- **Cuidado com os nomes:** `food_prod` (o catálogo do projeto) ≠ `prod_food` (o catálogo automático do workspace). Releia antes de cada GRANT (PRD 00, seção 3.1).

**64 · Grupos, não pessoas, recebem acesso**
- Workspace decide quem entra; Unity Catalog decide o que cada um lê; catálogo isolado: `food_prod` só existe no PROD.

**65 · Metadado no catálogo, dado físico no seu bucket**
- "Você vê `food_dev.orders.bronze_orders`; o arquivo está no bucket lakehouse." Bucket raw: arquivo como chegou. Bucket lakehouse: tabelas Delta.

**66 · Uma credential sozinha não dá acesso a ninguém**
- IAM role → storage credential → external location → catálogo/volume → GRANT para grupos.

**67 a 77 · O que o PRD 02 criou, peça por peça** (um print por slide, com os cartões "O que é / Como ficou aqui / Onde ver")

**67 · Grupos e usuários, criados uma vez na conta**
- Antes: 1 usuário e 1 grupo. Depois: 5 grupos e 5 usuários fictícios, com origem "Account" (valem para todos os workspaces).
- Users = pessoas; service principals = máquinas (o CI/CD do PRD 05); groups = quem recebe a permissão. "Pessoa entra e sai; o grupo fica."
- Se perguntarem do login automático: SSO e SCIM (sincronizar com Okta ou Entra ID) funcionam no **Premium**, o plano de hoje. O Enterprise é para PrivateLink, chaves próprias (CMK) e compliance.

**68 · Quem entra em cada workspace**
- DEV: só `data-engineering` e `platform-admins`. PROD: os cinco grupos. "Marketing, operações e diretoria nem entram no DEV."
- À mão: Account Console → Workspaces → Permissions → Add permissions.

**69 · Buckets de dados: o dado mora na conta da empresa**
- `coca-food-raw` (arquivo como chegou) e `coca-food-lakehouse` (tabelas Delta), cada um com `dev/` e `prod/`. Os buckets raiz dos workspaces ficam separados dos de dados.

**70 · Role de dados: quem a Databricks é no seu S3**
- `coca-food-uc-role`, separada da storage role do workspace. Trust: a `UCMasterRole` da Databricks + ela mesma + o External ID da conta. Permissions: acesso aos dois buckets.
- "Mesmo padrão da storage role do Bloco 2: trust em duas etapas."

**71 · Storage credential**
- A role registrada no Unity Catalog. Mostre o **Validate**: *Assume Role*, *Self Assume Role* e *External ID* verdes. "O debugger de IAM mais rápido."

**72 · External locations**
- Uma pasta do S3 + a credential que a abre. Quatro: raw e lakehouse, DEV e PROD. "O DEV nunca escreve na pasta do PROD."

**73 · Um catálogo por ambiente, preso ao seu workspace**
- No DEV, o `food_prod` aparece em "Outside this workspace". No `food_prod`, aba Workspaces: só o `prod-food`.
- "Duas camadas de isolamento: o binding decide **onde** o catálogo existe; o GRANT decide **quem** lê dentro dele."

**74 · Schema `orders` e o volume `raw`**
- Schema = o domínio de negócio. Volume = arquivos que não são tabela, com caminho `/Volumes/...`. Ainda vazio: os CSVs chegam no PRD 03.

**75 · Catálogo padrão de cada workspace**
- "Default catalog: food_prod." O catálogo automático (`prod_food`) deixou de ser o padrão. Mesmo assim, o código sempre usa o nome completo em três partes.

**76 · O dono de tudo é um grupo**
- Catálogos, schemas, volumes, credential e locations com dono `platform-admins`. "Se o dono fosse uma pessoa e ela saísse da empresa, o objeto ficaria órfão."

**77 · Os grants: quem lê o quê no PROD**
- Engenharia: lê tudo, sem `MODIFY`. Negócio: por enquanto só `USE CATALOG`; o `SELECT` na Gold vem no PRD 05. "Menor privilégio."

**78 · PRD 02 · O que foi criado**
- Peça a tabela-resumo ao Claude Code e confira os critérios de aceite: grupos, marketing fora do DEV, credential validada, catálogos isolados, catálogo padrão e o warehouse lendo o `raw` do PROD.

**79 · PRD 03 · o prompt: Os dados chegam no S3** (ciclo de ~3 min)
- Cole: `Leia prds/prd_00_contexto.md e prds/prd_03_dados.md e vamos executar juntos, passo a passo.`
- Peça para ele usar os scripts prontos (`data/generate_orders.py` e `data/upload_to_s3.sh`).

**80 · Os arquivos brutos chegaram no S3 da empresa**
- `orders.csv` (20 mil pedidos, 1,2 MB) e `stores.csv` (30 lojas) em `raw/dev/orders/` e `raw/prod/orders/`.
- "Mesmo arquivo, duas portas: o S3 (o físico) e o volume `/Volumes/food_dev/orders/raw` (governado pelo Unity Catalog)."

**81 · A sujeira é de propósito**
- Linhas reais do arquivo: `R$ 23.80`, `21/10/2026`, `DELIVERED`, quantidade vazia, pedido duplicado. "É o que dado de sistema real tem, e é o trabalho da Silver."

**82 · PRD 03 · O que foi criado**
- Os arquivos no S3 e no volume, dos dois ambientes.

## Bloco 5 · Pipeline e promoção (11:40–12:20)

**83 · Abertura do bloco**
- "Do arquivo bruto ao dado de negócio, e de DEV para PROD."

**84 · PRD 04 · o prompt: Pipeline em DEV** (ciclo de ~10 min)
- Cole: `Leia prds/prd_00_contexto.md e prds/prd_04_pipeline.md e vamos executar juntos, passo a passo.`
- Aprovações: `bundle deploy` e `bundle run` no DEV. Mostre o `pytest` rodando: "regra de negócio testada fora do Databricks".

**85 · Do arquivo bruto ao dado de negócio**
- Raw → Bronze (cópia fiel + auditoria) → Silver (limpeza) → Gold (loja × dia, só entregues). A validação no fim do job é o portão: falhou, não promove.

**86 a 92 · O que o PRD 04 criou**

**86 · O projeto que o agente escreveu**
- `databricks.yml` (o bundle), o job em YAML, os notebooks 01 a 05, `src/food/transforms.py` (as regras) e 6 testes.
- "O catálogo vem por variável: o mesmo código roda em DEV e em PROD sem mudar uma linha."

**87 · O job rodou**
- 5 tarefas verdes em 1 min 45 s, em compute serverless, com `catalog = food_dev`. O nome tem `[dev trilhadatabricksjornada]`: é a cópia de trabalho de quem publicou.
- "Managed by Declarative Automation Bundles: a verdade é o YAML no Git, não a tela."

**88 · Como o catálogo ficou no DEV**
- `food_dev` → `orders` → `bronze_orders`, `bronze_stores`, `silver_orders`, `gold_sales_by_store` + o volume `raw`. Ao lado, o `dev_food` (automático, não usado) e o `food_prod` fora do workspace.

**89 · Bronze, Silver e Gold**
- Mostre a amostra da Gold: data, loja, cidade, estado, pedidos, faturamento e ticket médio. "É a fonte do Dashboard, do App e do Genie."

**90 · A tabela é arquivo no seu bucket**
- Details da Gold: tipo MANAGED, *Storage location* no `coca-food-lakehouse/dev`. No S3: `_delta_log/` e um `.parquet` de 49 KB.
- **O momento da aula:** "o dado é seu. Se a Databricks sumisse amanhã, o Parquet continua no seu S3, em formato aberto."

**91 · O `_delta_log` por dentro**
- No S3, um `.json` por versão (`000…000.json`, `000…001.json`…), com um `.crc` de verificação. Na aba History, as mesmas 10 versões: 0 cria a tabela, 1 propriedades, 2 a 9 comentários de coluna.
- Demonstração: `DESCRIBE HISTORY food_dev.orders.gold_sales_by_store` e `SELECT * … VERSION AS OF 0` (time travel).

**92 · Delta table × Parquet "puro"**
- "O arquivo é Parquet, o formato que vocês já conhecem. O que transforma uma pasta de Parquet numa tabela é o `_delta_log`."
- Transação ACID, UPDATE/DELETE/MERGE, histórico, schema garantido, leitura sempre de uma versão fechada, e continua aberto. Referência: Armbrust et al., Delta Lake, VLDB 2020.

**93 · PRD 04 · O que foi criado**
- `pytest` verde, job verde, as tabelas em `food_dev.orders` e o `DESCRIBE DETAIL` apontando para o bucket da empresa.

**94 · PRD 05 · o prompt: Promoção DEV → TEST → PROD** (ciclo de ~5 min)
- Cole: `Leia prds/prd_00_contexto.md e prds/prd_05_promocao.md e vamos executar juntos, passo a passo.`
- O `bundle deploy -t prod` **só sai com confirmação explícita** ("pode publicar em PROD"). Faça questão de mostrar esse momento.

**95 · O mesmo código, três paradas**
- DEV → TEST (pytest + validação no job) → PROD. Só a configuração muda. Em empresa, quem publica PROD é um service principal via CI/CD, com aprovação.

**96 a 101 · O que o PRD 05 criou**

**96 · Um `databricks.yml`, dois ambientes**
- Os targets `dev` e `prod` lado a lado: muda o workspace, o catálogo (`food_dev` → `food_prod`), a pasta e as permissões.
- `development` põe o prefixo `[dev]`; `production` exige pasta compartilhada e permissões fixas. "TEST não é workspace: é o pytest + o validate."

**97 · O mesmo job, publicado nos dois workspaces**
- DEV: `[dev trilhadatabricksjornada] food_orders_pipeline`. PROD: `food_orders_pipeline`. "Em DEV, cada um tem a sua cópia; em PROD existe uma versão só."

**98 · Rodou em PROD**
- 5 tarefas verdes, 1 min 52 s, `catalog = food_prod`. No painel: o Git (repositório, `main`, commit `592d559`) e as permissões (engenharia *Can View*, `platform-admins` *Can Manage*).
- "Dá para saber exatamente qual commit está em produção."

**99 · Onde o bundle publicou**
- `/Workspace/Projects/food_lakehouse/prod`: `files` (a cópia do repositório), `state` (o que o bundle já criou, como o state do Terraform) e `artifacts`. "Em PROD, o código não mora na pasta de ninguém."

**100 · Negócio lê a Gold, não lê a Silver**
- Gold: marketing, operações e diretoria com SELECT direto na tabela; engenharia por herança. Silver: só engenharia.
- Demonstração com janela anônima (precisa de um usuário com e-mail real, ex.: `trilhadatabricksjornada+marketing@gmail.com`): SELECT na Gold funciona; na Silver, `PERMISSION_DENIED`.

**101 · Na empresa, quem publica PROD é uma máquina**
- `docs/ci_cd_github_actions.md`, documentado e não executado: push → `pytest` → deploy e run em DEV (o validate é o portão) → aprovação de um reviewer → deploy e run em PROD.
- Quem publica é o service principal, com login por OIDC, sem segredo guardado.

**102 · PRD 05 · O que foi criado**
- Mesmo commit em DEV e PROD, job de PROD verde, Gold de `food_prod` preenchida, engenharia só com *Can view*, e o exemplo de CI/CD.

## Bloco 6 · Consumo e custos (12:20–12:45)

**103 · Abertura do bloco**
- "A mesma Gold, para três tipos de gente. E quanto tudo isso custa."

**104 · PRD 06 · o prompt: Dashboard, App e Genie** (ciclo de ~10 min)
- Cole: `Leia prds/prd_00_contexto.md e prds/prd_06_consumo.md e vamos executar juntos, passo a passo.`
- Ordem que ele vai seguir (lição do ensaio): deploy → run da pipeline → deploy de novo (o Genie exige a Gold) → subir o App. Ligue o warehouse antes: desligado, leva de 2 a 5 minutos.

**105 · A mesma Gold, três experiências**
- Dashboard (executivos), App (negócio), Genie (quem não escreve SQL). Regra definida uma vez, na Gold.

**106 · Outra interface não é outra porta**
- Dashboard sem credenciais embutidas; App com autorização de usuário; Genie com a identidade de quem pergunta.

**107 · PRD 06 · O que foi criado**
- Dashboard Executive Overview com filtros; App Food Intelligence Explorer; Genie respondendo "Quais são as cinco lojas com maior faturamento?" em português.
- Janela anônima com marketing: os três funcionam na Gold, ninguém lê a Silver.

**108 · Um cluster, duas faturas**
- Serverless: uma fatura. Clássico: DBU (Databricks) + EC2/NAT (AWS). "Olhe as duas juntas."

**109 · Cinco jeitos de baixar as faturas**
- Jobs em vez de all-purpose, auto-termination, fleets, Graviton, spot nos workers com driver on-demand.

**110 · Onde acompanhar**
- Databricks: Account Console → Usage, `system.billing.usage`, Budgets. AWS: Cost Explorer por tag, AWS Budgets, NAT Gateways ligados.

**111 · O setup de hoje**
- O que cobra sempre (NAT dos dois workspaces) × o que cobra no uso (EC2, DBU). "Terminou, limpou." A seção 7 de cada PRD diz como apagar.

## Fechamento (12:45–13:00)

**112 · Abertura do fechamento**

**113 · Para repetir em casa**
- Manual para o DEV, PRDs para o resto: "copiem a pasta de PRDs, façam os logins e peçam o PRD 01". Conta AWS paga, fora de Organization restritiva.

**114 · Para ir além: as trilhas**
- Setup na AWS → **Trilha AWS**; workspaces, Unity Catalog, pipeline, Apps e Genie → **Trilha Databricks**; bundles e CI/CD → **Trilha Engenharia de Dados**. E o agente → **Trilha Claude Code** (slide 48).

**115 · Novos treinamentos de Databricks (ainda em 2026)**
- "Hoje é o começo. Ainda este ano entram dois treinamentos novos de Databricks, preparados com a Jennifer Maia, que usam exatamente a plataforma que montamos hoje."
- **Novembro · DevOps no Databricks (4h)** e **Dezembro · Performance e Operação (4h)**. Datas exatas a confirmar.

**116 · Black Friday Infinita · quinta, 12/11, 19h30, ao vivo no YouTube**
- "Na quinta eu apresento ao vivo o plano do profissional de dados e IA de sucesso dos próximos 5 anos, em 4 etapas." A 4ª é **revelada só ao vivo**. Peça para entrarem na lista e ativarem o lembrete.

**117 · Clicar para entender. Automatizar para escalar. Governar para confiar.**
- Volte à jornada do slide 15 e marque cada etapa. Abra para perguntas.

## Apêndice (118–124, só se perguntarem)

| Slide | Use quando perguntarem… |
|---|---|
| 119 · Storage role por dentro | "Por que a role precisa assumir a si mesma?" |
| 120 · Como a Databricks age na sua conta | "O que exatamente a Databricks pode fazer na minha AWS?" |
| 121 · Quando a SCP bloqueia | "Deu erro de validação / cluster não sobe na conta da empresa" |
| 122 · Qual credencial usar | "Como acessar Glue, Bedrock, Secrets Manager?" |
| 123 · Três testemunhas | "Como auditar quem fez o quê?" |
| 124 · Tags de custo | "Como dividir a conta por time?" |
