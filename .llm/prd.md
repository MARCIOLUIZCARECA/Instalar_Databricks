# PRD — Food Intelligence Platform
## Workshop: Do Zero à Produção — Databricks Enterprise na AWS

**Público:** Engenheiros de dados, arquitetos, profissionais de cloud e tecnologia.

**Duração:** 4 horas.

**Objetivo:** Demonstrar como implementar e organizar uma plataforma Databricks Enterprise na AWS, passando pela configuração dos workspaces, ambientes, grupos de acesso, integração com S3, governança e execução de uma pipeline simples de dados.

---

# 1. Contexto do projeto

Vamos utilizar como cenário uma empresa fictícia de delivery, inspirada em operações como o iFood.

A empresa possui dados de pedidos, lojas e cardápios armazenados no Amazon S3 e deseja estruturar uma plataforma corporativa de dados utilizando Databricks.

O projeto será utilizado para demonstrar como uma empresa deve organizar sua infraestrutura e governança antes de começar a desenvolver soluções de dados em escala.

O foco não é desenvolver uma solução avançada de analytics, mas demonstrar o processo de implementação de uma plataforma corporativa.

## História de negócio

O instrutor apresentará uma experiência profissional anterior em uma grande empresa global, utilizando a Coca-Cola como contexto histórico.

A experiência será utilizada para explicar por que a escolha de Databricks integrada à AWS pode fazer sentido em grandes organizações.

Um dos fatores relevantes é a possibilidade de aproveitar o relacionamento comercial e os processos de contratação existentes com o provedor de nuvem, reduzindo atritos de aquisição quando a contratação via marketplace for aplicável.

Não utilizar dados, informações confidenciais ou arquitetura proprietária da empresa.

---

# 2. Objetivos do workshop

Ao final das quatro horas, o participante deverá compreender:

1. Como funciona a arquitetura Databricks na AWS.
2. Diferença entre Account e Workspace.
3. Diferença entre Control Plane e Compute Plane.
4. Diferença entre Serverless e Classic Compute.
5. Como organizar DEV, HML e PROD.
6. Como estruturar grupos e permissões.
7. Como conectar o Databricks ao Amazon S3.
8. Como utilizar Unity Catalog para governança.
9. Como executar uma pipeline simples de dados.
10. Como organizar a promoção de código entre ambientes.

---

# 3. Escopo técnico

O projeto será intencionalmente pequeno.

Não desenvolver uma arquitetura complexa de engenharia de dados.

A prioridade é configurar a plataforma e demonstrar o fluxo completo de trabalho.

## 3.1. Infraestrutura AWS

Utilizar:

- Uma conta AWS previamente preparada.
- Um bucket S3.
- IAM Role para integração com Databricks.
- Databricks Account.
- Workspaces.

Estrutura simplificada do S3:

```text
s3://food-intelligence/
│
├── dev/
│   └── orders/
│
├── hml/
│   └── orders/
│
└── prod/
    └── orders/
```

Utilizar arquivos Parquet ou CSV com dados sintéticos de pedidos.

O bucket e as permissões devem ser preparados antes do workshop, caso o provisionamento completo não possa ser realizado dentro do tempo disponível.

## 3.2. Databricks Account e Workspaces

Demonstrar a relação entre uma conta Databricks e seus workspaces.

Criar ou preparar três workspaces:

| Workspace | Objetivo |
|---|---|
| FOOD-DEV | Desenvolvimento |
| FOOD-HML | Homologação |
| FOOD-PROD | Produção |

Explicar que cada workspace possui seu próprio contexto de trabalho, usuários atribuídos, configurações e recursos.

O instrutor deverá demonstrar como um usuário pode ter acesso a DEV, mas não a PROD.

## 3.3. Ambientes

### DEV

Ambiente de desenvolvimento.

Utilizado para:

- Criar notebooks.
- Desenvolver código.
- Testar consultas.
- Criar tabelas.
- Experimentar novas soluções.

### HML

Ambiente de homologação.

Utilizado para:

- Validar código.
- Executar testes.
- Conferir resultados.
- Validar permissões.
- Aprovar alterações.

### PROD

Ambiente de produção.

Utilizado para:

- Executar pipelines aprovadas.
- Disponibilizar tabelas oficiais.
- Executar processos recorrentes.
- Consumir dados confiáveis.

**Conceito fundamental:** uma alteração não deve ser desenvolvida diretamente em produção. Ela deve passar por desenvolvimento, validação e aprovação.

---

# 4. Grupos e controle de acesso

Demonstrar como organizar os usuários por responsabilidade.

Criar os seguintes grupos:

| Grupo | Responsabilidade |
|---|---|
| platform-admins | Administração da plataforma |
| data-engineering | Engenharia de dados |
| marketing-team | Consumo de informações comerciais |
| operations-team | Informações operacionais |
| executives | Indicadores executivos |

Criar alguns usuários fictícios para demonstração.

Exemplo:

| Usuário | Grupo |
|---|---|
| Admin | platform-admins |
| Engenheiro | data-engineering |
| Analista de Marketing | marketing-team |
| Analista Operacional | operations-team |
| Diretor | executives |

Demonstrar:

- Criação de grupos.
- Associação de usuários.
- Atribuição de usuários aos workspaces.
- Permissões diferentes por ambiente.
- Acesso aos catálogos.
- Acesso às tabelas.

## Exemplo de política de acesso

| Grupo | DEV | HML | PROD |
|---|---|---|---|
| platform-admins | Administração | Administração | Administração |
| data-engineering | Escrita | Validação controlada | Acesso controlado |
| marketing-team | Sem acesso | Sem acesso | Leitura autorizada |
| operations-team | Sem acesso | Sem acesso | Leitura autorizada |
| executives | Sem acesso | Sem acesso | Leitura autorizada |

As permissões deverão ser implementadas de acordo com as capacidades do Unity Catalog e as atribuições dos workspaces.

Não depender somente das permissões da interface. Validar o acesso diretamente aos dados.

---

# 5. Unity Catalog

Criar uma estrutura simples de governança.

Utilizar um catálogo por ambiente:

```text
food_dev
food_hml
food_prod
```

Dentro do catálogo de produção:

```text
food_prod
│
└── orders
    └── orders
```

O schema `orders` armazenará a tabela de pedidos.

Demonstrar:

- Criação de catálogo.
- Criação de schema.
- Criação de tabela.
- Permissões de acesso.
- Integração com o armazenamento S3.
- Diferença entre metadados e dados físicos.

Não implementar uma estrutura complexa de catálogos por domínio ou departamento.

O objetivo é entender como o Unity Catalog organiza e governa os dados.

---

# 6. Pipeline de dados simplificada

Esta será a única pipeline funcional desenvolvida durante o workshop.

O objetivo é demonstrar o ciclo de vida de uma informação dentro do Databricks.

## Fonte

Arquivo de pedidos no S3.

Exemplo:

```text
orders.csv
```

Campos:

```text
order_id
store_id
order_date
product_name
quantity
total_amount
order_status
```

## Etapa 1 — Ingestão

Ler o arquivo do S3 utilizando Databricks.

Demonstrar:

- Acesso ao bucket.
- Leitura do arquivo.
- Identificação do schema.
- Visualização dos registros.

## Etapa 2 — Bronze

Salvar os dados originais em uma tabela Delta.

```text
food_dev.orders.bronze_orders
```

O objetivo é mostrar como os dados chegam à plataforma.

## Etapa 3 — Silver

Executar transformações simples:

- Remover registros duplicados.
- Tratar valores nulos.
- Padronizar datas.
- Converter valores monetários.

Salvar em:

```text
food_dev.orders.silver_orders
```

## Etapa 4 — Gold

Criar uma agregação simples:

Quantidade de pedidos e faturamento por loja.

Salvar em:

```text
food_dev.orders.gold_sales_by_store
```

O objetivo é mostrar a transformação de dados brutos em informações prontas para consumo.

Não implementar modelos complexos, algoritmos de recomendação ou análises avançadas de cardápio.

---

# 7. Promoção entre ambientes

Demonstrar como o código desenvolvido em DEV pode ser utilizado em HML e posteriormente em PROD.

O processo será:

```text
DEV
 |
 | Desenvolvimento
 v
TEST
 |
 | Testes básicos
 v
HML
 |
 | Validação e aprovação
 v
PROD
```

TEST será uma etapa de validação automatizada, não necessariamente um workspace adicional.

Demonstrar conceitualmente ou por meio de um exemplo simples:

- Versionamento do código no Git.
- Configuração por ambiente.
- Promoção de notebooks ou pipelines.
- Validação em HML.
- Aprovação para produção.

Utilizar Databricks Asset Bundles, conforme a documentação e nomenclatura vigentes.

Não desenvolver uma estrutura complexa de CI/CD. Basta demonstrar o conceito e deixar um exemplo funcional ou documentado de implantação.

---

# 8. Cronograma de quatro horas

| Tempo | Tema | Entrega |
|---|---|---|
| 00:00–00:25 | Contexto e arquitetura | Entendimento do problema |
| 00:25–01:00 | AWS e Databricks Account | Integração e visão dos componentes |
| 01:00–01:35 | Workspaces e ambientes | DEV, HML e PROD |
| 01:35–02:15 | Grupos e governança | Usuários e Unity Catalog |
| 02:15–03:15 | Pipeline prática | S3 → Bronze → Silver → Gold |
| 03:15–03:45 | Promoção entre ambientes | DEV → HML → PROD |
| 03:45–04:00 | Revisão e encerramento | Arquitetura completa |

---

# 9. Requisitos de implementação para Claude Code

Desenvolver somente o necessário para suportar o workshop.

Priorizar:

1. Estrutura do repositório.
2. Dados sintéticos de pedidos.
3. Script para geração e envio dos arquivos ao S3.
4. Notebook de ingestão.
5. Notebook Bronze.
6. Notebook Silver.
7. Notebook Gold.
8. Configuração dos ambientes.
9. Exemplo de configuração dos grupos e permissões.
10. Documentação de arquitetura e execução.

Estrutura sugerida:

```text
food-intelligence-platform/
│
├── README.md
│
├── docs/
│   ├── architecture.md
│   ├── aws-setup.md
│   ├── workspaces.md
│   ├── environments.md
│   ├── governance.md
│   └── workshop-guide.md
│
├── data/
│   └── generate_orders.py
│
├── notebooks/
│   ├── 01_ingestion.py
│   ├── 02_bronze.py
│   ├── 03_silver.py
│   └── 04_gold.py
│
├── infrastructure/
│   └── terraform/
│
├── tests/
│   └── test_orders.py
│
└── databricks.yml
```

## Regras de desenvolvimento

- Não criar dashboard complexo.
- Não implementar múltiplas pipelines.
- Não criar integrações externas com APIs.
- Não implementar modelos de machine learning.
- Não desenvolver agentes de IA ou MCP.
- Não implementar infraestrutura desnecessária.
- Não criar múltiplos domínios de dados.
- Não utilizar dados reais de clientes.
- Não utilizar credenciais hardcoded.
- Não executar provisionamento pago sem autorização.
- Validar os recursos com documentação oficial atualizada.

Se houver dependências que exigem provisionamento prévio, documentar e preparar essas etapas antes do workshop.

---

# 10. Critérios de aceite

O projeto estará pronto quando:

- [ ] A arquitetura AWS e Databricks estiver documentada.
- [ ] Os três workspaces estiverem criados ou preparados para demonstração.
- [ ] A finalidade de DEV, HML e PROD estiver clara.
- [ ] Os grupos de usuários estiverem configurados ou demonstráveis.
- [ ] As permissões estiverem documentadas e testáveis.
- [ ] O Unity Catalog estiver configurado ou preparado para demonstração.
- [ ] O S3 estiver integrado ao Databricks.
- [ ] O arquivo de pedidos puder ser lido.
- [ ] A pipeline Bronze, Silver e Gold funcionar.
- [ ] O processo de promoção entre ambientes estiver demonstrado.
- [ ] O instrutor tiver um roteiro completo para executar o workshop em quatro horas.

---

# 11. Orientação final

O projeto deve ser desenvolvido com foco educacional e arquitetural.

A prioridade não é construir a solução mais sofisticada possível.

A prioridade é permitir que o participante compreenda como um arquiteto de plataforma organiza o Databricks dentro de uma empresa.

Ao final, o participante deve conseguir visualizar a seguinte jornada:

**AWS → Databricks Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Dados disponíveis para negócio.**

Essa é a entrega principal do workshop.

# 12. Camada de consumo e inteligência de negócio

## Objetivo

Demonstrar como os dados processados e governados no Databricks podem ser disponibilizados para diferentes perfis de usuários por meio de ferramentas nativas da plataforma.

O projeto deverá possuir três formas de consumo:

1. Databricks AI/BI Dashboard.
2. Databricks Apps (Data App).
3. Databricks Genie.

As três soluções deverão utilizar a mesma camada Gold, evitando duplicação de regras de negócio.

**Importante:** o objetivo não é desenvolver três produtos completos, mas demonstrar diferentes maneiras de consumir os dados disponibilizados pela plataforma.

## 12.1. Dataset de consumo

Utilizar a tabela:

```text
food_prod.orders.gold_sales_by_store
```

Campos sugeridos:

```text
store_id
store_name
city
state
order_date
total_orders
total_revenue
average_ticket
```

Essa tabela será a principal fonte para as demonstrações.

Caso seja necessário desenvolver localmente, utilizar a tabela equivalente no ambiente DEV.

## 12.2. Databricks AI/BI Dashboard

Criar um dashboard chamado:

**Food Intelligence — Executive Overview**

Objetivo: disponibilizar uma visão executiva da operação.

Indicadores:

- Faturamento total.
- Quantidade de pedidos.
- Ticket médio.
- Número de lojas.
- Faturamento por região.
- Ranking de lojas.
- Evolução de faturamento ao longo do tempo.

Gráficos:

1. Faturamento por dia.
2. Faturamento por região.
3. Ranking das lojas.
4. Quantidade de pedidos por período.
5. Ticket médio por loja.

Filtros:

- Período.
- Estado.
- Cidade.
- Loja.

O dashboard deverá consumir a tabela Gold e utilizar queries SQL documentadas.

Não criar cálculos complexos diretamente nos gráficos. Priorizar indicadores preparados na camada Gold.

## 12.3. Databricks Apps — Data App

Criar uma aplicação simples chamada:

**Food Intelligence Explorer**

Objetivo: demonstrar como uma empresa pode construir uma aplicação interna sobre os dados governados no Databricks.

A aplicação deverá permitir:

- Selecionar uma loja.
- Selecionar um período.
- Consultar o faturamento.
- Consultar a quantidade de pedidos.
- Consultar o ticket médio.
- Visualizar o histórico de vendas.
- Comparar o desempenho entre lojas.

A interface deverá ser simples, profissional e responsiva.

Tecnologia preferencial: Python com Streamlit, utilizando Databricks Apps quando disponível.

A aplicação deverá consultar os dados Gold por meio de uma conexão suportada e segura.

Não armazenar credenciais no código.

Não criar uma aplicação com autenticação própria que ignore os controles da plataforma.

O objetivo é demonstrar o consumo de dados por uma aplicação de negócio.

## 12.4. Databricks Genie

Criar um espaço Genie chamado:

**Food Business Analyst**

Objetivo: permitir que usuários de negócio façam perguntas em linguagem natural sobre os dados de vendas.

O Genie deverá utilizar a tabela Gold como fonte principal.

Configurar descrições das colunas e instruções de negócio para melhorar a interpretação das perguntas.

Perguntas de demonstração:

- Qual foi o faturamento total no período?
- Quais são as cinco lojas com maior faturamento?
- Qual estado possui maior volume de vendas?
- Qual é o ticket médio por loja?
- Como evoluíram as vendas nos últimos meses?
- Quais lojas tiveram queda de faturamento?
- Qual foi o volume de pedidos por região?

Configurar:

- Tabela e campos disponíveis.
- Descrições de negócio.
- Relacionamentos necessários.
- Métricas e definições.
- Exemplos de perguntas.
- Instruções SQL quando aplicável.

O Genie deverá respeitar as permissões de acesso do usuário e as configurações de governança da plataforma.

Não criar fontes adicionais ou integrar modelos externos para esta demonstração.

## 12.5. Comparação entre as três formas de consumo

Durante o workshop, explicar a diferença:

| Componente | Finalidade | Perfil |
|---|---|---|
| AI/BI Dashboard | Indicadores e visualizações fixas | Executivos e analistas |
| Databricks Apps | Aplicações com interação e fluxos específicos | Usuários de negócio |
| Genie | Perguntas em linguagem natural | Usuários não técnicos |

A mesma informação poderá ser consultada por diferentes experiências, sem precisar criar três pipelines diferentes.

## 12.6. Integração com governança

Demonstrar que a camada de consumo não deve ser tratada como uma exceção à governança.

- O Dashboard deverá utilizar dados autorizados.
- O App deverá utilizar uma conexão e identidade configuradas de forma segura.
- O Genie deverá respeitar as permissões aplicáveis aos dados e ao espaço Genie.
- Os usuários não deverão conseguir acessar dados restritos apenas por utilizarem outra interface.

Validar as permissões com pelo menos dois perfis diferentes.

## 12.7. Critérios de aceite

- [ ] Dashboard criado e conectado à tabela Gold.
- [ ] Indicadores executivos funcionando.
- [ ] Filtros do Dashboard funcionando.
- [ ] Databricks App criado e consultando os dados Gold.
- [ ] Genie configurado com a tabela Gold.
- [ ] Perguntas de demonstração respondidas corretamente.
- [ ] As três experiências utilizando a mesma fonte de dados.
- [ ] Permissões e limitações de acesso documentadas.

## 12.8. Preparação para o workshop

Como o workshop possui apenas quatro horas, preparar previamente a estrutura do Dashboard, do App e do Genie sempre que o provisionamento ou a configuração consumir muito tempo.

Durante a aula, demonstrar o funcionamento e a integração dessas ferramentas com a plataforma.

Priorizar uma experiência funcional de cada tipo em vez de tentar construir interfaces complexas ao vivo.