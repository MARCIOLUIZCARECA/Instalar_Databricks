# Fundamentos · Databricks na AWS

O mínimo que você precisa saber **antes** de criar um workspace. Leitura de 10 minutos.

> Adaptado das aulas 1.1, 1.2 e 1.3 do curso *AWS Databricks Platform Architect* (Databricks Learning).

---

## 1. Onde a Databricks roda

Todo workspace tem duas metades:

| | Onde fica | O que tem |
|---|---|---|
| **Control plane** | Sempre na conta AWS **da Databricks** | Interface web, APIs, notebooks, agendador de jobs, gerenciador de clusters, Unity Catalog |
| **Compute plane serverless** | Conta AWS **da Databricks** | SQL, jobs e notebooks serverless |
| **Compute plane clássico** | **Sua** conta AWS | Clusters EC2 na sua VPC e os seus buckets S3 |

A diferença entre os tipos de workspace é **onde roda o compute**. O control plane é sempre da Databricks.

### Como uma empresa começa

| Caminho | Para quem | Como paga |
|---|---|---|
| **Express Setup** | Testar rápido | Só e-mail, cria um workspace **serverless**, 14 dias de crédito trial |
| **AWS Marketplace** | Empresa que já compra pela AWS | Vem na **fatura da AWS** e abate do compromisso EDP |
| **Contrato direto** | Grandes empresas | Fatura direta da Databricks, DBU com desconto |
| **Free Edition** | Estudo | Grátis, só serverless, com limites. Não é para produção |

> O preço da DBU é o mesmo no Marketplace. Muda só **quem te cobra**.

### Tiers

- **Premium:** o padrão. Unity Catalog, permissões, audit logs, serverless, Databricks SQL.
- **Enterprise:** para ambientes regulados. PrivateLink, chaves gerenciadas pelo cliente (CMK), compliance security profile.
- **Standard:** acabou. Os workspaces Standard viraram Premium em 01/10/2025.

### Região é decisão de feature

A Databricks está na maioria das regiões comerciais da AWS (e no GovCloud), mas **nem toda feature está em toda região**. Escolher a região não é só uma questão de latência.

### "E2" é nome antigo

Você vai ver **E2** em blogs antigos e nos recursos Terraform `databricks_mws_*`. Era o nome da arquitetura atual (várias workspaces por conta, VPC própria, secure cluster connectivity). Hoje é só "a plataforma".

---

## 2. Serverless ou clássico?

**Desde janeiro de 2026 o padrão é serverless.** Clássico virou escolha consciente.

### Serverless

- **Zero configuração na AWS:** sem role, sem bucket, sem VPC. Fica pronto em minutos.
- **Default storage:** a Databricks guarda os dados do catálogo do workspace.
- **Unity Catalog** ligado desde o primeiro dia. Dados externos no S3 entram por credenciais do UC.
- Usa **environment versions** no lugar das versões do Databricks Runtime.

### Quando o clássico ainda é obrigatório

```
Precisa do compute DENTRO da sua VPC?            ── sim ──►  Clássico (customer-managed VPC)
(inspeção de tráfego, rota para on-premise, IP allow-list)
        │ não
Precisa de instância que o serverless não tem?   ── sim ──►  Clássico
(GPU específica, NVMe local, imagem de container própria)
        │ não
A feature não existe na sua região?              ── sim ──►  Clássico
        │ não
        ▼
Serverless (padrão)
```

### Lado a lado

| | Serverless | Clássico |
|---|---|---|
| O que criar na AWS | Nada | IAM role, bucket raiz, VPC (opcional) |
| Onde roda o compute | Conta da Databricks | Sua VPC (e pode usar serverless também) |
| Storage do workspace | Default storage (Databricks) | Seu bucket raiz |
| Versões | Environment versions | Databricks Runtime |
| Controle de rede | Egress policies, private endpoints (NCC) | Total: firewall, rotas, endpoints |
| Custo | DBU já inclui a máquina | DBU + EC2/EBS na fatura da AWS |

> **Atenção:** compute clássico **não acessa** o default storage. Se os dois tipos vão compartilhar dados, guarde-os num bucket seu.

### Antes de prometer, confira a matriz feature × região

Para cada workload ou região nova:

- [ ] A região suporta serverless?
- [ ] A feature que você precisa (ex.: GPU serverless, conectividade privada) está nessa região?
- [ ] As normas de compliance que você precisa cobrem serverless nessa região?
- [ ] O modelo de custo serve (DBU com máquina inclusa vs DBU + EC2)?

---

## 3. Como um workspace clássico é montado

Um workspace clássico é a soma de **objetos registrados na conta Databricks**. Cada objeto só aponta para algo que já existe na sua AWS.

| Objeto | Aponta para | No manual |
|---|---|---|
| **Credential configuration** | Cross-account role (confia na conta `414351767826` com o seu Account ID como External ID) | Passo 5 |
| **Storage configuration** | Bucket raiz + bucket policy, e a storage role (opcional) | Passos 2, 3 e 4 |
| **Network configuration** | VPC, subnets, security groups (opcional) | Não usamos: Databricks-managed VPC |

- A **policy da cross-account role muda** conforme a rede (managed ou customer-managed VPC).
- **Sem a storage role**, o workspace nasce **sem catálogo do workspace**.
- O bucket raiz guarda: dados de sistema (notebooks, resultados de jobs, logs), o catálogo do workspace (`unity-catalog/`) e, só em contas antigas, o DBFS root.

### Quatro jeitos de criar

| Jeito | Quando usar |
|---|---|
| **Quickstart (CloudFormation)** | Primeiro workspace, o mais rápido possível |
| **Console manual** | Aprender as peças. **É o nosso caminho.** |
| **Account API / CLI** | Automatizar com scripts (`databricks account ...`) |
| **Terraform** (`databricks_mws_*`) | Escala e ambiente versionado. Veja [`terraform/`](../terraform/README.md) |

### Escolhas sem volta

| Decisão | Dá para mudar? |
|---|---|
| **Região** | Não. |
| **Managed → customer-managed VPC** | Não. (Customer-managed pode trocar para outra customer-managed.) |
| **Bucket raiz** | Considere fixo. |
| **Credential** | A role pode ser trocada, mas escolha a versão da policy desde o início. |

> **Em produção, na dúvida: customer-managed VPC.** Ela deixa a porta da rede aberta; a managed fecha para sempre. No workshop usamos managed porque o ambiente é descartável.

---

## Resumo para a aula

- Control plane é sempre da Databricks. O compute clássico roda na sua conta; o serverless, na deles.
- Serverless é o padrão desde 2026. Clássico quando precisa de VPC própria, instância específica ou feature que falta na região.
- Workspace clássico = **credential** + **storage** + **network** (opcional).
- Região e modelo de rede **não mudam depois**: decida antes.
- Premium é o tier padrão. PrivateLink e CMK pedem Enterprise.
