# PRD 01 · Workspace de PRODUÇÃO com Claude Code

**Para quem lê:** o Claude Code, ao vivo no workshop. Leia antes o `prd_00_contexto.md`. O instrutor vai pedir: *"Leia `prds/prd_01_workspace_prod.md` e vamos executar juntos, passo a passo."*

**Contexto:** a conta Databricks e o workspace de desenvolvimento já existem. O `{{WS_DEV}}` foi criado **à mão** no Bloco 2 (manual, seções 2 a 6). Agora criamos o workspace de **produção** com o Claude Code, usando o AWS CLI e o Databricks CLI, e mostrando cada peça nos consoles. A mensagem da aula: *"o que eu cliquei no Bloco 2, o agente faz igual, explicando e pedindo aprovação, e fica registrado."*

---

## 1. Objetivo

Criar o workspace clássico **`{{WS_PROD}}`** na mesma conta Databricks e na mesma conta AWS do `{{WS_DEV}}`, com peças **próprias** (bucket e roles novos), na mesma região e no mesmo metastore.

Fora de escopo neste PRD: grupos, catálogos, pipeline e consumo (próximos PRDs).

## 2. Valores

| O quê | Valor |
|---|---|
| Conta AWS | `{{AWS_ACCOUNT_ID}}` · profile `{{AWS_PROFILE}}` · região **`{{REGIAO}}`** |
| Conta Databricks | `{{DATABRICKS_ACCOUNT_ID}}` · profile `{{DATABRICKS_PROFILE}}` (login de conta: `accounts.cloud.databricks.com`) |
| Conta AWS da Databricks (não trocar) | `414351767826` |
| Workspace novo | **`{{WS_PROD}}`** |
| Bucket raiz | `databricks-{{PREFIXO}}-root-{{AWS_ACCOUNT_ID}}` |
| Storage role (Unity Catalog) | `databricks-{{PREFIXO}}-storage-role` |
| Cross-account role (compute) | `databricks-{{PREFIXO}}-cross-account-role` |
| Credential configuration | `{{PREFIXO}}-cross-account` |
| Storage configuration | `{{PREFIXO}}-storage` |
| Rede | Databricks-managed VPC |
| Metastore | `{{METASTORE}}` (o mesmo do `{{WS_DEV}}`) |

Escreva as policies em arquivos JSON numa pasta `policies/` do projeto (um arquivo por policy, já com os valores acima), seguindo os fatos da seção 6 do `prd_00_contexto.md` e a documentação atual da Databricks. Mostre cada JSON antes de aplicar.

## 3. O que NÃO pode ser tocado

- O workspace **`{{WS_DEV}}`**, a VPC dele, o bucket **`{{DEV_ROOT_BUCKET}}`** e as roles **`{{DEV_STORAGE_ROLE}}`** e **`{{DEV_CROSS_ACCOUNT_ROLE}}`**: são do DEV.
- O workspace serverless criado no cadastro (Express), em qualquer região.
- Nada fora de `{{REGIAO}}`, nada em outra conta.

Antes de qualquer comando que **cria, altera ou apaga**, mostre o comando, diga em uma frase o que ele faz e **espere a aprovação** do instrutor. Comandos de leitura podem rodar direto.

## 4. Passo a passo

Em cada passo: (a) explique o que a peça é, em linguagem de aula; (b) rode; (c) diga **onde mostrar no console** (AWS ou Databricks) para a turma ver a peça nascer.

| # | Passo | Mostrar no console |
|---|---|---|
| 0a | **Preencher o [`config.yaml`](config.yaml) (só leitura):** descubra o que der (`aws sts get-caller-identity` → `AWS_ACCOUNT_ID`; `databricks account workspaces list` → URL, região, credential e storage do DEV; as configurations do DEV → bucket raiz e ARNs das roles; o metastore atribuído ao DEV). Mostre a tabela com tudo, pergunte o que faltar (`PREFIXO`, `EMAIL_BASE`) e **grave só depois da confirmação**. Daqui em diante, todo `{{NOME}}` vem desse arquivo | Account Console → Workspaces; Cloud resources |
| 0b | **Conferências (só leitura):** logins (`aws sts get-caller-identity`, `databricks account workspaces list`); quantas VPCs e Elastic IPs existem em `{{REGIAO}}` (limite padrão: 5 de cada); se já existe algo com os nomes da seção 2 (se existir, **pare e pergunte**) | Account Console → Workspaces; VPC → Your VPCs |
| 1 | Bucket raiz: privado, ACLs disabled, SSE-S3, versionamento desligado, `{{REGIAO}}` | S3 → Buckets |
| 2 | Bucket policy do bucket raiz | S3 → bucket → Permissions |
| 3 | Storage role com a trust **provisória** (External ID `0000`) + inline policy de S3 | IAM → Roles → Trust relationships / Permissions |
| 4 | Trocar a trust da storage role pela **definitiva** (self-assuming, External ID = Databricks Account ID) | IAM → Roles → Trust relationships |
| 5 | Cross-account role: trust + inline policy de EC2/VPC | IAM → Roles |
| 6 | **Esperar ~60 s** (propagação do IAM) e conferir lendo de volta as duas roles e a bucket policy (seção 5, checklist) | — |
| 7 | Credential configuration (`{{PREFIXO}}-cross-account`) e storage configuration (`{{PREFIXO}}-storage`, bucket + storage role) | Account Console → Cloud resources |
| 8 | Criar o workspace `{{WS_PROD}}` em `{{REGIAO}}`, Databricks-managed VPC | Account Console → Workspaces (*Provisioning*) |
| 9 | Acompanhar até **Running** (alguns minutos). Enquanto isso, mostrar a VPC nova nascendo na AWS: VPC, subnets, NAT Gateway, Elastic IP | VPC → Your VPCs; NAT gateways |
| 10 | Conferir o metastore: `{{WS_PROD}}` atribuído ao `{{METASTORE}}` (se não estiver, atribuir) | Account Console → Catalog |
| 11 | Login no workspace (`databricks auth login --host <url> --profile {{WS_PROD}}`) e abrir no navegador | Workspace → Catalog |

## 5. Lições do ensaio (regras, não sugestões)

1. **Sem `< >` sobrando.** Antes de aplicar qualquer policy, procure `<` e `>` no JSON. A AWS recusa com `Policy has invalid resource`.
2. **External ID certo.** Nas trusts das duas roles, o External ID é `{{DATABRICKS_ACCOUNT_ID}}` (exceto a trust provisória, `0000`). No ensaio, uma role reaproveitada tinha o ID de outra conta Databricks.
3. **Bucket certo na policy da storage role.** As linhas `arn:aws:s3:::` têm que citar `databricks-{{PREFIXO}}-root-{{AWS_ACCOUNT_ID}}`. No ensaio, a role apontava para um bucket antigo, e a criação falhou com `Storage credential IAM role ... doesn't have access to S3 bucket`.
4. **Peças novas, nunca reaproveitadas.** Se um nome da seção 2 já existir, pare e pergunte.
5. **Mesma região para tudo:** `{{REGIAO}}`. O formulário do console abriu em São Paulo no ensaio; pela API, passe a região explicitamente.
6. **Esperar a propagação do IAM** (~60 s) antes de registrar as peças na Databricks.
7. **Checklist antes do passo 7** (leitura): `get-bucket-policy` (existe e cita o Account ID certo), `get-role` das duas roles (External ID certo), `get-role-policy` da storage role (bucket certo).
8. **Limites:** a conta trial tem limite diário de criação de workspaces. Se o passo 8 falhar por limite, **não tente contornar**: mostre o erro e explique (vira lição de aula).
9. **SCP/RCP:** a conta AWS está numa AWS Organization. Se der `Failed credential validation checks` com as policies corretas, consulte o Troubleshooting do manual (seção "Conta AWS dentro de uma Organization").

## 6. Critérios de aceite

- [ ] `{{WS_PROD}}` em **Running**, `{{REGIAO}}`, Premium, metastore `{{METASTORE}}`.
- [ ] `{{WS_DEV}}` e o workspace serverless do cadastro intactos e em Running.
- [ ] Na AWS, em `{{REGIAO}}`: uma VPC a mais (a do `{{WS_PROD}}`), no máximo 3 no total contando a padrão.
- [ ] Bucket e roles `databricks-{{PREFIXO}}-*` criados; nenhuma peça do DEV alterada.
- [ ] No fim, um resumo em tabela: cada peça criada, o ARN ou ID, e onde vê-la no console.

## 7. Custos e limpeza

Enquanto o `{{WS_PROD}}` existir, o **NAT Gateway** cobra por hora, mesmo sem cluster. Para apagar depois da aula (com aprovação): apagar o workspace no Account Console, esperar a VPC sumir (se sobrar, apagar NAT → Elastic IP → Internet Gateway → subnets → route tables → security groups → VPC), depois as configurations, as roles e o bucket `databricks-{{PREFIXO}}-*`.
