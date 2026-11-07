# Terraform · Setup Plataforma Databricks Profissional do Zero (AWS)

Workshop ao vivo da Jornada de Dados · 07/11/2026.

Este projeto cria, com código, **exatamente o mesmo ambiente** que o [manual](../manual/README.md) cria à mão no console: workspaces Databricks **clássicos** na região **Ohio (`us-east-2`)**, com **Databricks-managed VPC**.

Por padrão são criados **dois** workspaces, um por ambiente do projeto [Food Intelligence](../food-intelligence-platform/README.md): `FOOD-DEV` e `FOOD-PROD` (`FOOD-HML` é opcional, veja [a escolha de ambientes](../food-intelligence-platform/docs/environments.md#quantos-ambientes)). Eles reaproveitam a mesma credential (cross-account role) e a mesma storage configuration (bucket raiz + storage role); cada um ganha a sua VPC e o seu NAT Gateway. Para criar só um, use `environments = { dev = "FOOD-DEV" }` no `terraform.tfvars`.

| # | O que é criado | Onde |
|---|---|---|
| ① | Bucket S3 raiz + bucket policy | Sua conta AWS |
| ② | IAM storage role do Unity Catalog (self-assuming) + policy S3 (+ file events, opcional) | Sua conta AWS |
| ③ | IAM cross-account role + policy EC2 | Sua conta AWS |
| — | Credential configuration, storage configuration e workspace | Account Console da Databricks |
| ④ | VPC, subnets, NAT Gateway (rede) | Criada **pela Databricks** na sua conta, ao subir o workspace |

> O manual explica o **porquê** de cada peça. Aqui o foco é o **como** em código. Leia os dois lado a lado.

---

## Pré-requisitos

1. **Terraform >= 1.5** (`terraform version`).
2. **AWS CLI logado** num profile com permissão para criar IAM roles e buckets S3:

   ```bash
   aws sso login --profile meu-profile-aws        # ou: aws configure --profile meu-profile-aws
   aws sts get-caller-identity --profile meu-profile-aws
   ```

3. **Databricks CLI logado na CONTA** (não num workspace), com um profile de conta:

   ```bash
   databricks auth login \
     --host https://accounts.cloud.databricks.com \
     --account-id <DATABRICKS_ACCOUNT_ID> \
     --profile workshop-account
   ```

   Você precisa ser **account admin**. O Account ID fica no menu do usuário do Account Console.

4. Nenhum segredo vai para arquivo: o Terraform usa só os **nomes** dos profiles (`aws_profile` e `databricks_account_profile`).

### Pré-requisito da conta AWS

Use uma **conta AWS tradicional, no plano pago** (cartão cadastrado).

Contas criadas pela **"nova experiência"** da AWS (login social + projeto, *Free plan*) ficam dentro de uma **AWS Organization gerenciada**, com uma **SCP** que bloqueia EC2 fora da região do projeto. No ensaio, isso fez a validação da credencial falhar com:

```
MALFORMED_REQUEST: Failed credential validation checks
```

O erro não tem a ver com o Terraform nem com as policies: a Databricks testa permissões de EC2 e a SCP nega.

---

## Como usar

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # preencha databricks_account_id e os profiles

terraform init      # baixa os providers (aws, databricks, time)
terraform plan      # mostra o que será criado, sem criar nada
terraform apply     # cria tudo (digite "yes"); o workspace leva alguns minutos
```

Ao final, o Terraform mostra os outputs:

| Output | O que é |
|---|---|
| `workspace_urls` | URL de cada workspace, por ambiente (abra no navegador) |
| `workspace_ids` | ID numérico de cada workspace (entrada do stack de governança) |
| `root_bucket_name` | Nome do bucket raiz ① |
| `storage_role_arn` | ARN da storage role ② |
| `cross_account_role_arn` | ARN da cross-account role ③ |

Para rever depois: `terraform output`.

### Limpeza: `terraform destroy`

```bash
terraform destroy   # digite "yes"
```

**O `destroy` é a limpeza do workshop.** Ele apaga o workspace, as configurações no Account Console, as roles e o bucket (inclusive os arquivos que o workspace gravou nele, porque o bucket usa `force_destroy = true`).

> **Atenção ao custo:** enquanto o workspace existir, o **NAT Gateway** criado pela Databricks cobra **por hora**, mesmo sem nenhum cluster ligado, e as **instâncias EC2** cobram por hora enquanto um cluster estiver ligado. Encerre os clusters e rode o `destroy` no mesmo dia. Depois, confira no console da AWS (região `us-east-2`) se **NAT Gateway, Elastic IP, instâncias EC2 e VPC** sumiram.

---

## O que cada arquivo faz

| Arquivo | Conteúdo |
|---|---|
| `versions.tf` | Versão mínima do Terraform e versões fixadas dos providers (`databricks` 1.141.0, `aws` ~> 6.0, `time` ~> 0.14). |
| `providers.tf` | Autenticação por profile: AWS (`aws_profile`) e Databricks no nível de **conta** (`alias = "mws"`, host `accounts.cloud.databricks.com`). |
| `variables.tf` | Entradas: `databricks_account_id`, `aws_profile`, `databricks_account_profile`, `prefix`, `environments`, `region`, `enable_file_events`, `tags`. Para o Food Intelligence use `prefix = "food"`: assim nada colide com as peças `databricks-workshop-*` do ensaio manual na mesma conta AWS. |
| `main.tf` | Descobre o AWS Account ID e monta os nomes (iguais aos do manual com `prefix = "workshop"`). |
| `aws_storage.tf` | ① Bucket S3 raiz: ACLs desabilitadas, block public access, SSE-S3, sem versionamento, bucket policy. |
| `aws_iam.tf` | ② Storage role do Unity Catalog e ③ cross-account role, com as policies e as pausas de propagação do IAM. |
| `databricks.tf` | Credential, storage configuration e o workspace no Account Console. |
| `outputs.tf` | URL e ID do workspace, ARNs das roles e nome do bucket. |
| `terraform.tfvars.example` | Modelo de variáveis, só com placeholders. |
| `.gitignore` | Impede que state, `.terraform/` e `terraform.tfvars` reais vão para o Git. |

### Nomes gerados (com `prefix = "workshop"`)

| Recurso | Nome |
|---|---|
| Bucket | `databricks-workshop-root-<AWS_ACCOUNT_ID>` |
| Storage role | `databricks-workshop-storage-role` |
| Cross-account role | `databricks-workshop-cross-account-role` |
| Credential | `databricks-workshop-credential` |
| Storage configuration | `databricks-workshop-storage` |
| Workspaces | `FOOD-DEV`, `FOOD-PROD` (+ `FOOD-HML` opcional, variável `environments`) |

---

## Passo do manual ↔ recurso Terraform

| Passo do manual | Recurso Terraform | Equivale a |
|---|---|---|
| 2 · Criar o bucket S3 raiz | `aws_s3_bucket.root` | — |
| 2 · ACLs disabled | `aws_s3_bucket_ownership_controls.root` | — |
| 2 · Block all public access | `aws_s3_bucket_public_access_block.root` | — |
| 2 · Default encryption SSE-S3 | `aws_s3_bucket_server_side_encryption_configuration.root` | — |
| 2 · Versioning: Disable | (nenhum recurso: o bucket nasce sem versionamento) | — |
| 3 · Bucket policy | `aws_s3_bucket_policy.root` | `policies/03-bucket-policy.json` |
| 4.1 + 4.4 · Storage role com trust self-assuming | `aws_iam_role.storage` + data source `databricks_aws_unity_catalog_assume_role_policy.storage` | `policies/04` + `policies/05` (numa etapa só) |
| 4.2 · Inline policy de S3 | `aws_iam_role_policy.storage_s3` | `policies/06-storage-role-s3-policy.json` |
| 4.5 · Policy de file events (opcional) | `aws_iam_role_policy.storage_file_events` (com `enable_file_events = true`) | `policies/07-storage-role-file-events-policy.json` |
| 5.1 · Cross-account role com External ID | `aws_iam_role.cross_account` + data source `databricks_aws_assume_role_policy.cross_account` | `policies/01-cross-account-trust-policy.json` |
| 5.2 · Inline policy EC2 | `aws_iam_role_policy.cross_account` | `policies/02-cross-account-access-policy.json` |
| (esperar o IAM propagar) | `time_sleep.cross_account_role`, `time_sleep.storage_role` | — |
| 6 · Compute credentials | `databricks_mws_credentials.this` | — |
| 6 · Workspace storage (bucket + IAM role) | `databricks_mws_storage_configurations.this` | — |
| 6 · Create workspace (Databricks-managed VPC, sem PrivateLink) | `databricks_mws_workspaces.this` | — |

> **Por que `mws_`?** Vem de *Multi-Workspace Services*, da época em que a plataforma atual na AWS se chamava "E2". O nome ficou nos recursos Terraform, mas hoje "E2" é só a plataforma padrão. Mais em [arquitetura](../manual/arquitetura/README.md#e2-vocabulário-aposentado).

### O "ovo e a galinha" da storage role

A trust policy da storage role cita **a própria role**. No console, a AWS não deixa citar uma role que ainda não existe, por isso o manual cria a role em duas etapas (trust provisória `04` e depois a definitiva `05`).

No Terraform fazemos em **uma etapa**:

1. o ARN da role é montado a partir do **nome** e do AWS Account ID (`data.aws_caller_identity`), sem referenciar o próprio recurso, então não há ciclo;
2. o data source oficial `databricks_aws_unity_catalog_assume_role_policy` escreve o self-assume como "a minha conta pode assumir, **desde que** o principal seja esta role" (`aws:PrincipalArn`). A AWS aceita esse formato antes de a role existir, e o efeito é o mesmo do `05`, sempre com `sts:ExternalId` = Databricks Account ID.

### Por que alguns JSONs estão escritos à mão

O provider Databricks tem data sources que geram policies, mas na versão 1.141.0 nem todos batem com a documentação atual (06/11/2026) que o manual segue. Usamos o data source quando ele é equivalente e escrevemos o JSON quando não é:

| Data source | Usado? | Motivo |
|---|---|---|
| `databricks_aws_assume_role_policy` | Sim | Gera exatamente o `01`. |
| `databricks_aws_unity_catalog_assume_role_policy` | Sim | Equivalente ao `05`, e resolve o self-assume numa etapa. |
| `databricks_aws_bucket_policy` | Não | Não tem o `Deny` em `unity-catalog/*` do `03`. |
| `databricks_aws_crossaccount_policy` | Não | Lista de ações EC2 um pouco diferente da do `02`. |
| `databricks_aws_unity_catalog_policy` | Não | Libera o bucket inteiro (o `06` restringe a `unity-catalog/*`) e já embute file events. |

---

## Custos

| Recurso | Custo |
|---|---|
| Bucket S3 | Centavos: por GB armazenado e por requisição |
| IAM roles e policies | Grátis |
| Credential, storage configuration, workspace | Grátis (só o uso gera custo) |
| VPC, subnets, security group, Internet Gateway | Grátis |
| **NAT Gateway + Elastic IP** | **Por hora** (+ por GB trafegado), mesmo sem cluster ligado |
| **EC2 dos clusters** | **Por hora** na fatura AWS, mais DBUs na fatura Databricks |

Terminou o workshop? `terraform destroy`.
