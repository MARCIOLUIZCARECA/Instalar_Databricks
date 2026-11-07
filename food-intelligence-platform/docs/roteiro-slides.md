# Roteiro de fala · slide a slide

Para cada slide: **o que dizer** (em linguagem de conversa) e, quando útil, **se perguntarem**. Os tempos somam ~4h. Apresentação: <https://claude.ai/artifact/UFhcfvGJBqyJgqYZmvxuFj>.

Fio condutor da aula: **fomos contratados para implementar o Databricks numa empresa global** (cenário de exercício inspirado na Coca-Cola, sem nenhum dado ou informação da empresa). Cada bloco responde a uma pergunta que esse cliente faria.

---

## Abertura (09:00)

**1 · Capa**
- "Bom dia! Hoje a gente sai do zero e chega numa plataforma Databricks com cara de empresa."
- Formato: vocês assistem agora, repetem depois. Tudo está no repositório: manual com prints, Terraform e o projeto.

**1a · Seja bem-vindo à Jornada de Dados** (3 a 5 min)
- Faça as quatro perguntas e peça respostas no chat: quem é novo, quem assiste pela primeira vez, quem está há muito tempo, quem quer compartilhar um sucesso.
- Leia alguns nomes em voz alta. Se alguém antigo tiver um caso (vaga, promoção, projeto em produção), convide para contar em 1 minuto.

**1b · O time**
- Apresente Luciano Vasconcelos, Michelle Perrone, Jennifer Maia e Caio Machado, e agradeça as participações de Luiza, Allan e Laender.
- "O time está no chat para ajudar durante toda a aula."

**1c · O foco de hoje: o início do projeto**
- "Hoje é aula de começo de projeto: conta, ambientes, acesso, primeira pipeline, custos e decisões."
- "Muita coisa vamos tocar rapidamente: aplicações no Databricks, infraestrutura na AWS e Terraform. Cada uma tem uma trilha completa na Jornada (AWS, Databricks e Engenharia de Dados)."

**2 · Agenda**
- Três atos: começar é fácil (Express), entender cada peça (setup manual) e escalar com código (Terraform, DEV e PROD).
- Depois: o que transforma infraestrutura em plataforma (governança, pipeline, consumo) e quanto tudo isso custa.

## O desafio e o mercado (09:05–09:35)

**3 · O desafio**
- "Imaginem: a Coca-Cola contratou o nosso time para implementar o Databricks. Antes de abrir qualquer console, o cliente faz quatro perguntas." Leia as quatro.
- "A aula de hoje é a resposta para cada uma delas."
- Reforce: é um exercício. Nenhum dado ou arquitetura real da empresa.

**4 · Uma experiência real (2017)**
- **O time técnico:** "Em 2017 a gente já tinha um time de engenharia de dados que trabalhava majoritariamente com AWS. Era um time que veio de back-end: muito processamento em Lambda, contratos e pipelines na AWS."
- **O gap:** "A AWS é muito técnica, não tem uma interface amigável. O time de produto usava Power BI, o time técnico usava AWS, e tinha uma desavença e um gap enorme no meio. O dado existia, mas o produto não conseguia usar sem depender da engenharia para cada número."
- **A decisão:** "Contratamos o Databricks para ser a ponte entre a AWS e o Power BI: os engenheiros continuaram na AWS, aproveitando contratos e pipelines, e o produto passou a ter dados prontos para consumir."
- **Ligação com hoje:** "Escolher plataforma é resolver um problema entre pessoas, não só de tecnologia. Guardem isso para o slide de como convencer a organização."
- *Se perguntarem "por que não só Athena/Redshift?"*: a dor era usabilidade e colaboração entre times técnicos e de produto; o Databricks juntava notebooks, SQL e um caminho direto para o Power BI, sobre os dados que já estavam no S3.

**5 · Quatro caminhos**
- "Não existe a melhor plataforma; existe a que encaixa."
- Databricks: engenharia + BI + IA juntos, formatos abertos. Snowflake: SQL simples, pouca administração. Fabric: casa Microsoft e Power BI. On-premise: controle total, mas tudo por sua conta.
- *Se perguntarem "qual é mais barato?"*: depende do uso; o que muda é o modelo de cobrança (próximos slides e bloco de custos).

**6 · Databricks × Snowflake**
- Pergunta de negócio: "a empresa quer só analytics, ou dados + IA como plataforma?"
- Diferença de fundo: no Databricks o dado fica no S3 da empresa, em Delta/Iceberg. No Snowflake o armazenamento é gerenciado por eles.
- Os dois estão convergindo: Snowflake adiciona Python e formatos abertos; Databricks simplifica com serverless.

**7 · Fabric e on-premise**
- Fabric faz sentido para empresa 100% Microsoft com foco em BI. Muitas usam os dois: Databricks para engenharia e IA, Power BI para relatórios.
- On-premise faz sentido quando a regulação proíbe nuvem. O custo escondido é o time e o tempo para escalar.
- A escolha de nuvem e a de plataforma são separadas: Databricks roda em AWS, Azure e GCP.

**8 · Uma plataforma, os seus dados, a sua conta**
- Seis argumentos, do técnico ao comercial. Destaque dois: dados no S3 da empresa em formato aberto, e compra pelo Marketplace.

**9 · Como convencer a sua organização**
- "Executivo compra resultado e redução de risco, não tecnologia."
- Um caso de negócio concreto (previsão de demanda, churn), custo total, piloto de 60 a 90 dias com uma métrica.
- Prepare as três objeções: segurança (dado na conta da empresa), custo (pago pelo uso, com budgets) e lock-in (formato aberto).
- Volte à história de 2017: o argumento que convenceu foi de negócio (o produto no Power BI não conseguia usar o dado da AWS), não técnico.

**10 · O cenário da demo: Food Intelligence**
- "Para não usar dado real, a demo usa uma rede de delivery fictícia: pedidos, lojas, cardápios chegando no S3."
- O foco não é analytics sofisticado; é como um arquiteto organiza a plataforma.

**11 · A jornada de hoje**
- Mapa do dia: AWS → Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Consumo → Negócio.
- "Cada bloco acende uma etapa. No fim, a gente volta aqui."

## Fundamentos (09:35–09:45)

**12 · Uma conta, vários workspaces**
- Account = prédio inteiro (usuários, grupos, metastore, cobrança). Workspace = um andar (notebooks, jobs, compute).
- O usuário é cadastrado uma vez na conta e entra nos workspaces que precisar: "o mesmo usuário pode estar em DEV e não em PROD".

**13 · Control plane × compute plane**
- Control plane: na conta da Databricks (interface, agendador, Unity Catalog).
- Compute plane (no clássico): na conta AWS da empresa (EC2 e S3). Para operar essa metade, a Databricks recebe duas "chaves" (IAM roles) e um bucket.

**14 · Serverless ou clássico?**
- Serverless: roda na conta da Databricks, começa em minutos, uma fatura só.
- Clássico: roda na sua VPC, controle total de rede, duas faturas.
- "Hoje usamos os dois: workspace clássico por exigência corporativa, compute serverless para jobs e SQL."

**15 · Quem cobra o quê: duas decisões**
- "São duas perguntas separadas. A técnica: onde o compute roda? A comercial: de quem eu compro o DBU?"
- **Onde roda:** serverless (na conta da Databricks; o compute já está no DBU) ou clássico (na VPC da empresa; a AWS cobra EC2, NAT e S3).
- **Como compra:** direto com a Databricks (contrato e desconto negociados) ou pelo Marketplace da AWS (o DBU aparece na fatura da AWS).
- Percorra a matriz:
  - Serverless + direto: uma fatura, da Databricks.
  - Serverless + Marketplace: uma fatura, da AWS.
  - Clássico + direto: duas faturas (Databricks e AWS).
  - Clássico + Marketplace: tudo na fatura da AWS, em linhas separadas.
- Marketplace pode abater o compromisso com a AWS (EDP), **se o contrato considerar esse gasto elegível** (confirme com a AWS).
- Hoje: workspace clássico, com compute serverless para jobs e SQL.

## Bloco 1 · Free, Trial e Express (09:45–09:55)

**16 · Free, Trial, Express ou setup completo?**
- Free Edition: estudar, grátis, só serverless, sem Account Console, sem uso comercial.
- Free Trial: empresa avaliando, 14 dias de créditos, plataforma completa.
- Express: workspace serverless em minutos, pago pelo uso.
- Setup clássico: requisitos corporativos, bucket + IAM + rede na sua conta.
- *Se perguntarem "dá para fazer a aula na Free Edition?"*: os notebooks sim; o setup de conta (workspaces, grupos) não, porque ela não tem Account Console.

**17 · Workspace Express: "Funcionou em 2 minutos. Por que a empresa não para aqui?"**

Demo: Account Console → Create workspace → serverless; abrir notebook; `SELECT` em `samples.nyctaxi.trips`. Depois, as 4 perguntas, com as respostas:

| Pergunta | Resposta curta | Onde a aula resolve |
|---|---|---|
| **Onde estão os dados?** | No Express, o armazenamento padrão é gerenciado pela Databricks, fora da conta AWS da empresa. Para uma empresa, o natural é o dado no **próprio S3**: controle de retenção, criptografia, auditoria e outros motores lendo o mesmo arquivo. | Bloco 2: bucket raiz e storage role. Bloco 4: buckets raw e lakehouse. |
| **Quem paga a máquina?** | No Express (serverless), a Databricks roda a máquina e cobra tudo em DBU, numa fatura só. No clássico, a máquina é EC2 na conta da empresa: a AWS cobra a máquina e a Databricks cobra o DBU. | Slide "Quem cobra o quê" e bloco de custos. |
| **Como separo DEV de PROD?** | Um workspace por ambiente, um catálogo isolado por ambiente e o mesmo código promovido por bundle. Criar à mão é lento e propenso a erro; por isso vira código. | Bloco 3: Terraform com DEV e PROD; promoção com Asset Bundles. |
| **Quem pode ver o quê?** | Grupos criados uma vez na conta, atribuídos aos workspaces (quem entra) e com permissões no Unity Catalog (o que cada um lê). | Bloco 4: governança. |

- Fecho: "Funcionar é fácil. Funcionar com dado na nossa conta, ambientes separados e acesso controlado é o trabalho de hoje."
- **Plano B:** a conta tem limite diário de criação de workspaces. Se falhar, abra o workspace serverless `workspace`, criado no ensaio.

## Bloco 2 · AWS na mão (09:55–10:30)

**18 · Um bucket e duas chaves viram um workspace**
- Três peças na AWS + o registro na Databricks. "Os próximos slides são os prints do ensaio real, na mesma ordem do manual."

**19 · O que a tela "Create workspace" pede**
- Comece pelo destino: cada bloco do formulário é uma peça que vamos criar. Automático (CloudFormation) ou manual: hoje fazemos manual para entender.

**20 · Bucket raiz e bucket policy**
- Privado, criptografado, na mesma região do workspace.
- A policy libera a Databricks só quando a chamada vem com o seu Account ID. O Deny impede o caminho antigo (DBFS) de mexer na pasta do Unity Catalog.

**21 · Storage role do Unity Catalog**
- "A role mais estranha da sua conta": confia na Databricks com External ID e confia **em si mesma**.
- Por isso nasce em duas etapas: a AWS não aceita citar uma role que ainda não existe.

**22 · Cross-account role: a chave do compute**
- Quem pode assumir: a conta da Databricks, com o seu External ID (defesa contra o "confused deputy").
- O que pode fazer: criar a VPC e ligar/desligar EC2.

**23 · Registrar as peças**
- Credential = cross-account role. Storage = bucket + storage role.
- *Se der "Failed credential validation checks"*: espere 20 s (o IAM propaga devagar) ou é SCP/RCP da AWS Organization (apêndice e Troubleshooting do manual).

**24 · De Provisioning a Running**
- A Databricks cria VPC, subnets e NAT Gateway na conta da empresa.
- Gancho de custo: "o NAT começa a cobrar agora, mesmo sem cluster". Gancho do próximo bloco: "imaginem repetir isso para cada ambiente, sem errar um clique".

## Bloco 3 · Ambientes: escolha, custo e código (10:30–11:00)

**25 · O que foi clicado vira código**
- Terraform: um bloco com `for_each` cria um workspace por ambiente. Claude Code: explica, roda o plan, aplica quando você aprova. State: o Terraform lembra o que criou.
- Ao vivo: prompts 1 a 3 do [workshop-guide.md](workshop-guide.md). O `plan` deve dar **"No changes"**: "o Terraform não recria o que já existe".
- Não crie workspace ao vivo (limite diário + 15 min).

**26 · Dois stacks: o prédio e a portaria**
- Infraestrutura muda raramente; governança muda toda semana. Times diferentes podem cuidar de cada um.

**27 · Dois workspaces, dois papéis**
- DEV: desenvolver e testar. PROD: só o que passou nos testes, tabelas oficiais, consumo.

**28 · Quantos ambientes a sua empresa precisa?**
- Só PROD: barato, mas testa em produção. DEV + PROD: produção isolada, custo moderado (**a escolha de hoje**). DEV + HML + PROD: homologação formal, mais caro e mais lento.
- Bastidor: "no ensaio, batemos o limite diário de criação de workspaces. Lição: planejar ambientes antes de sair criando".

**29 · Quanto custa cada opção parada**
- Cada workspace clássico: NAT Gateway + IP público ≈ US$ 0,05/h ≈ US$ 1,20/dia ≈ US$ 36/mês, mesmo sem uso.
- Só PROD ≈ US$ 36/mês; DEV+PROD ≈ US$ 73; com HML ≈ US$ 110. O resto (EC2, DBU, tráfego) cresce com o uso, não com o número de ambientes.

**29a · Quatro jeitos de dividir workspaces**
- Por ambiente (hoje), por área de negócio, por região, ou tudo combinado.
- "O erro comum é um workspace por time: cada workspace clássico tem custo fixo de rede, login, grupos, políticas, e a conta tem limite diário de criação."
- Regra de bolso: **poucos workspaces, muitos catálogos**.

**29b · Exemplo: Brasil e EUA na mesma conta**
- Uma conta Databricks, um time de plataforma, grupos globais.
- O metastore do Unity Catalog é **regional**: workspace em São Paulo usa o metastore de São Paulo; workspace na Virgínia, o da Virgínia. Por isso são dois.
- Dado pessoal fica no país (LGPD/GDPR). A matriz recebe só tabelas agregadas por **Delta Sharing**, sem copiar arquivos.
- Nomes com região e ambiente: `br_prod_vendas`, `us_prod_vendas`.
- *Se perguntarem "e a fatura?"*: cada workspace tem as suas tags e o seu uso em `system.billing.usage`, então dá para separar o custo por país.

**29c · Novo workspace ou novo catálogo?**
- Pergunta para o cliente: "isso é fronteira de rede, região, ambiente ou cobrança?" Se sim, workspace. Se não, catálogo.
- No projeto: uma área nova (ex.: Supply) entraria como catálogo `supply_dev` / `supply_prod`, não como workspace.

**30 · O que a empresa ganha separando ambientes**
- Risco isolado, teste antes, acesso por papel, custo visível, auditoria, mesmo código.

**31 · O mesmo código, três paradas**
- DEV → TEST (pytest + validação no job) → PROD. Só a configuração muda (`databricks.yml`).
- Em empresa, quem publica PROD é um service principal via CI/CD, com aprovação.

## Bloco 4 · Governança (11:00–11:40)

**32 · Grupos, não pessoas, recebem acesso**
- Workspace decide quem entra; Unity Catalog decide o que cada um lê; catálogo isolado: `food_prod` só existe no PROD.
- Demo com duas janelas anônimas: marketing não entra no DEV; no PROD lê a Gold e leva PERMISSION_DENIED na Silver.

**33 · Metadado no catálogo, dado físico no seu bucket**
- "Você vê `food_dev.orders.bronze_orders`; o arquivo está no bucket lakehouse." Abra o console AWS lado a lado com o Catalog Explorer.
- Bucket raw: arquivo como chegou. Bucket lakehouse: tabelas Delta, só o Unity Catalog escreve.

**34 · Uma credential sozinha não dá acesso a ninguém**
- IAM role → storage credential → external location → catálogo/volume. Os grants ficam na external location e no catálogo.
- Mostre o botão **Validate**: "o debugger de IAM mais rápido".

## Bloco 5 · Pipeline e promoção (11:40–12:20)

**35 · Do arquivo bruto ao dado de negócio**
- Raw → Bronze (cópia fiel + auditoria) → Silver (limpeza) → Gold (loja × dia).
- Mostre e rode, não programe ao vivo. Os dados têm "sujeira" de propósito: duplicados, nulos, datas em dois formatos, "R$ 1.234,56", status em português e inglês.
- A validação no fim do job é o portão: falhou, não promove.
- **Caso de uso DEV × PROD (mostre lado a lado):**
  - DEV: job `[dev luciano] food-orders-pipeline-dev`, App `food-explorer-dev`, Genie `[dev luciano] Food Business Analyst`, todos lendo `food_dev`. Prefixo com o nome de quem publicou: "é a minha cópia de trabalho".
  - PROD: job `food-orders-pipeline-prod`, App `food-explorer`, Genie `Food Business Analyst`, lendo `food_prod`, abertos aos grupos de negócio.
  - "Mesmo código, mesmo `databricks.yml`. Só mudou o target: `-t dev` → `-t prod`."

## Bloco 6 · Consumo (12:20–12:35)

**36 · A mesma Gold, três experiências**
- Dashboard (executivos), App (negócio), Genie (quem não escreve SQL). Regra definida uma vez, na Gold.
- Os três usam o `Food Classic Warehouse` (clássico), porque o SQL serverless dava 403 nos buckets desta conta ([troubleshooting.md](troubleshooting.md#e-sql-warehouse-serverless-com-403-nos-buckets-do-projeto)). Bom gancho: "na vida real, sempre tenha um plano B de compute".
- Genie testado no ensaio: "Quais são as cinco lojas com maior faturamento?" respondeu em português, com o SQL certo.

**37 · Outra interface não é outra porta**
- Dashboard sem credenciais embutidas; App com autorização de usuário; Genie com a identidade de quem pergunta.

## Custos (12:35–12:45)

**38 · Um cluster, duas faturas**
- Serverless: uma fatura. Clássico: DBU (Databricks) + EC2/NAT (AWS). "Olhe as duas juntas."

**39 · Cinco jeitos de baixar as faturas**
- Jobs em vez de all-purpose, auto-termination, fleets, Graviton, spot nos workers com driver on-demand.

**40 · Onde acompanhar**
- Databricks: Account Console → Usage, `system.billing.usage`, Budgets. AWS: Cost Explorer por tag, AWS Budgets, NAT Gateways ligados.

**41 · O setup de hoje**
- O que cobra sempre (NAT) × o que cobra no uso (EC2, DBU). "Terminou, limpou."

## Fechamento (12:45–13:00)

**42 · Para repetir em casa**
- Do mais simples ao mais completo. Conta AWS paga, fora de Organization restritiva; um workspace basta para estudar.

**42a · Para ir além: as trilhas**
- Ligue cada bloco a uma trilha: setup na AWS → **Trilha AWS**; workspaces, Unity Catalog, pipeline, Apps e Genie → **Trilha Databricks**; Terraform, bundles e CI/CD → **Trilha Engenharia de Dados**.

**42a+ · Novos treinamentos de Databricks (ainda em 2026)**
- "Hoje é o começo. Ainda este ano entram dois treinamentos novos de Databricks, preparados com a Jennifer Maia, que usam exatamente a plataforma que montamos hoje."
- **Novembro · DevOps no Databricks (4h):** do Free Edition para workspaces separados; bundles em vários workspaces, CI/CD com service principal e GitHub Actions, rollback e drift.
- **Dezembro · Performance e Operação (4h):** Delta Lake por dentro, Query Profile e Spark UI, incremental com Auto Loader e CDC, observabilidade e custo por pipeline.
- Datas exatas a confirmar.

**42b · Black Friday Infinita · quinta, 12/11, 19h30, ao vivo no YouTube**
- "Na quinta eu apresento ao vivo o plano do profissional de dados e IA de sucesso dos próximos 5 anos, em 4 etapas."
- 1 Fundamentos · 2 Plataforma de Dados e Engenharia de Dados ("hoje vocês viram o começo dessa") · 3 IA Data Engineer · 4 a etapa do topo, **revelada só ao vivo**.
- Peça para entrarem na lista pelo link e ativarem o lembrete no YouTube.

**43 · Clicar para entender. Automatizar para escalar. Governar para confiar.**
- Volte à jornada do slide 11 e marque cada etapa. Abra para perguntas.

## Apêndice (só se perguntarem)

| Slide | Use quando perguntarem… |
|---|---|
| Storage role por dentro | "Por que a role precisa assumir a si mesma?" |
| Como a Databricks age na sua conta | "O que exatamente a Databricks pode fazer na minha AWS?" |
| Quando a SCP bloqueia | "Deu erro de validação / cluster não sobe na conta da empresa" |
| Qual credencial usar | "Como acessar Glue, Bedrock, Secrets Manager?" |
| Três testemunhas | "Como auditar quem fez o quê?" |
| Tags de custo | "Como dividir a conta por time?" |
