# Policies prontas · conta AWS 928844615034

Gerado por `manual/policies/gerar_policies.py`. Copie cada bloco na ordem, no lugar indicado.

| Valor | Usado como |
|---|---|
| `928844615034` | AWS_ACCOUNT_ID |
| `bee83b2f-4880-413a-9b08-badf19a3d7a2` | DATABRICKS_ACCOUNT_ID |
| `databricks-workshop-root-928844615034` | NOME_DO_BUCKET |
| `databricks-workshop-storage-role` | NOME_DA_STORAGE_ROLE |
| `databricks-workshop-cross-account-role` | NOME_DA_CROSS_ACCOUNT_ROLE |
| `food-intelligence-raw-928844615034` | BUCKET_RAW |
| `food-intelligence-lakehouse-928844615034` | BUCKET_LAKEHOUSE |
| `food-intelligence-uc-role` | NOME_DA_ROLE_DE_DADOS |
| `bee83b2f-4880-413a-9b08-badf19a3d7a2` | EXTERNAL_ID_DA_STORAGE_CREDENTIAL |


## PARTE 1 · Workspace clássico (manual, seções 2 a 6)

### 1. Bucket policy do bucket raiz

**Onde:** S3 → bucket `databricks-workshop-root-928844615034` → aba **Permissions** → **Bucket policy** → **Edit** → colar → **Save changes**

Crie antes o bucket `databricks-workshop-root-928844615034` em us-east-2: ACLs disabled, Block all public access, SSE-S3, versionamento desligado.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Grant Databricks Access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::414351767826:root"
      },
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": ["arn:aws:s3:::databricks-workshop-root-928844615034/*", "arn:aws:s3:::databricks-workshop-root-928844615034"],
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/DatabricksAccountId": ["bee83b2f-4880-413a-9b08-badf19a3d7a2"]
        }
      }
    },
    {
      "Sid": "Prevent DBFS from accessing Unity Catalog metastore",
      "Effect": "Deny",
      "Principal": {
        "AWS": "arn:aws:iam::414351767826:root"
      },
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::databricks-workshop-root-928844615034/unity-catalog/*"]
    }
  ]
}
```

### 2. Storage role · trust policy (etapa 1, provisória)

**Onde:** IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**

External ID provisório `0000`. A AWS não deixa a role citar a si mesma antes de existir.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "0000"
        }
      }
    }
  ]
}
```

### 3. Storage role · permissões no S3 (inline policy)

**Onde:** Em **Add permissions** → **Create inline policy** → aba **JSON** → colar → nome da policy: `databricks-uc-s3-access`

Nome da role: `databricks-workshop-storage-role`. Descrição: `Unity Catalog: acesso ao prefixo unity-catalog/ do bucket raiz`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::databricks-workshop-root-928844615034/unity-catalog/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::databricks-workshop-root-928844615034"
    },
    {
      "Action": [
        "sts:AssumeRole"
      ],
      "Resource": [
        "arn:aws:iam::928844615034:role/databricks-workshop-storage-role"
      ],
      "Effect": "Allow"
    }
  ]
}
```

### 4. Storage role · trust policy (etapa 2, definitiva, self-assuming)

**Onde:** IAM → Roles → `databricks-workshop-storage-role` → aba **Trust relationships** → **Edit trust policy** → colar → **Update policy**

Troca o External ID `0000` pelo Databricks Account ID e coloca a própria role como principal.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
          "arn:aws:iam::928844615034:role/databricks-workshop-storage-role"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "bee83b2f-4880-413a-9b08-badf19a3d7a2"
        }
      }
    }
  ]
}
```

### 5. Storage role · file events (OPCIONAL)

**Onde:** IAM → Roles → `databricks-workshop-storage-role` → **Add permissions** → **Create inline policy** → JSON → colar → nome: `databricks-uc-file-events`

Não cria nada; só autoriza a Databricks a criar SQS/SNS para o Auto Loader. Pode pular no workshop.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManagedFileEventsSetupStatement",
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketNotification",
        "s3:PutBucketNotification",
        "sns:ListSubscriptionsByTopic",
        "sns:GetTopicAttributes",
        "sns:SetTopicAttributes",
        "sns:CreateTopic",
        "sns:TagResource",
        "sns:Publish",
        "sns:Subscribe",
        "sqs:CreateQueue",
        "sqs:DeleteMessage",
        "sqs:ReceiveMessage",
        "sqs:SendMessage",
        "sqs:GetQueueUrl",
        "sqs:GetQueueAttributes",
        "sqs:SetQueueAttributes",
        "sqs:TagQueue",
        "sqs:ChangeMessageVisibility",
        "sqs:PurgeQueue"
      ],
      "Resource": ["arn:aws:s3:::databricks-workshop-root-928844615034", "arn:aws:sqs:*:*:*", "arn:aws:sns:*:*:*"]
    },
    {
      "Sid": "ManagedFileEventsListStatement",
      "Effect": "Allow",
      "Action": ["sqs:ListQueues", "sqs:ListQueueTags", "sns:ListTopics"],
      "Resource": "*"
    },
    {
      "Sid": "ManagedFileEventsTeardownStatement",
      "Effect": "Allow",
      "Action": ["sns:Unsubscribe", "sns:DeleteTopic", "sqs:DeleteQueue"],
      "Resource": ["arn:aws:sqs:*:*:*", "arn:aws:sns:*:*:*"]
    }
  ]
}
```

### 6. Cross-account role · trust policy

**Onde:** IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**

Nome da role: `databricks-workshop-cross-account-role`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::414351767826:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "bee83b2f-4880-413a-9b08-badf19a3d7a2"
        }
      }
    }
  ]
}
```

### 7. Cross-account role · permissões EC2/VPC (inline policy)

**Onde:** Em **Add permissions** → **Create inline policy** → JSON → colar → nome: `databricks-cross-account-ec2`

Versão para Databricks-managed VPC. Não tem nada para trocar.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1403287045000",
      "Effect": "Allow",
      "Action": [
        "ec2:AllocateAddress",
        "ec2:AssignPrivateIpAddresses",
        "ec2:AssociateDhcpOptions",
        "ec2:AssociateIamInstanceProfile",
        "ec2:AssociateRouteTable",
        "ec2:AttachInternetGateway",
        "ec2:AttachVolume",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:CancelSpotInstanceRequests",
        "ec2:CreateDhcpOptions",
        "ec2:CreateFleet",
        "ec2:CreateInternetGateway",
        "ec2:CreateLaunchTemplate",
        "ec2:CreateLaunchTemplateVersion",
        "ec2:CreateNatGateway",
        "ec2:CreateRoute",
        "ec2:CreateRouteTable",
        "ec2:CreateSecurityGroup",
        "ec2:CreateSubnet",
        "ec2:CreateTags",
        "ec2:CreateVolume",
        "ec2:CreateVpc",
        "ec2:CreateVpcEndpoint",
        "ec2:DeleteDhcpOptions",
        "ec2:DeleteFleets",
        "ec2:DeleteInternetGateway",
        "ec2:DeleteLaunchTemplate",
        "ec2:DeleteLaunchTemplateVersions",
        "ec2:DeleteNatGateway",
        "ec2:DeleteRoute",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSecurityGroup",
        "ec2:DeleteSubnet",
        "ec2:DeleteTags",
        "ec2:DeleteVolume",
        "ec2:DeleteVpc",
        "ec2:DeleteVpcEndpoints",
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeFleetHistory",
        "ec2:DescribeFleetInstances",
        "ec2:DescribeFleets",
        "ec2:DescribeIamInstanceProfileAssociations",
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeInstances",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeLaunchTemplates",
        "ec2:DescribeLaunchTemplateVersions",
        "ec2:DescribeNatGateways",
        "ec2:DescribePrefixLists",
        "ec2:DescribeReservedInstancesOfferings",
        "ec2:DescribeRouteTables",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSpotInstanceRequests",
        "ec2:DescribeSpotPriceHistory",
        "ec2:DescribeSubnets",
        "ec2:DescribeVolumes",
        "ec2:DescribeVpcs",
        "ec2:DetachInternetGateway",
        "ec2:DisassociateIamInstanceProfile",
        "ec2:DisassociateRouteTable",
        "ec2:GetLaunchTemplateData",
        "ec2:GetSpotPlacementScores",
        "ec2:ModifyFleet",
        "ec2:ModifyLaunchTemplate",
        "ec2:ModifyVpcAttribute",
        "ec2:ReleaseAddress",
        "ec2:ReplaceIamInstanceProfileAssociation",
        "ec2:RequestSpotInstances",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RunInstances",
        "ec2:TerminateInstances"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": ["iam:CreateServiceLinkedRole", "iam:PutRolePolicy"],
      "Resource": "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot",
      "Condition": {
        "StringLike": {
          "iam:AWSServiceName": "spot.amazonaws.com"
        }
      }
    }
  ]
}
```


## PARTE 2 · Dados do projeto Food Intelligence (o Terraform de governança faz sozinho; à mão, siga esta parte)

### 8. Role de dados · trust policy (etapa 1, provisória)

**Onde:** IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**

Mesma policy provisória da storage role. Crie antes os buckets `food-intelligence-raw-928844615034` e `food-intelligence-lakehouse-928844615034` (privados, SSE-S3, us-east-2).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "0000"
        }
      }
    }
  ]
}
```

### 9. Role de dados · permissões nos buckets raw e lakehouse

**Onde:** Em **Add permissions** → **Create inline policy** → JSON → colar → nome: `food-intelligence-s3-access`

Nome da role: `food-intelligence-uc-role`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": [
        "arn:aws:s3:::food-intelligence-raw-928844615034/*",
        "arn:aws:s3:::food-intelligence-lakehouse-928844615034/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": [
        "arn:aws:s3:::food-intelligence-raw-928844615034",
        "arn:aws:s3:::food-intelligence-lakehouse-928844615034"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["sts:AssumeRole"],
      "Resource": ["arn:aws:iam::928844615034:role/food-intelligence-uc-role"]
    }
  ]
}
```

### 10. Role de dados · trust policy (etapa 2, com o External ID da storage credential)

**Onde:** IAM → Roles → `food-intelligence-uc-role` → **Trust relationships** → **Edit trust policy** → colar → **Update policy**

Antes: Catalog Explorer → **External data** → **Credentials** → **Create credential** → IAM role ARN `arn:aws:iam::928844615034:role/food-intelligence-uc-role` → copie o **External ID** que aparecer e rode o gerador de novo com `--external-id`. Depois: crie as external locations e clique em **Validate**.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
          "arn:aws:iam::928844615034:role/food-intelligence-uc-role"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "bee83b2f-4880-413a-9b08-badf19a3d7a2"
        }
      }
    }
  ]
}
```


## PARTE 3 · Só se a conta AWS estiver numa AWS Organization

### 11. Exceção na RCP para a conta da Databricks

**Onde:** Management Account → **AWS Organizations** → **Policies** → **Resource control policies** → `ManagedAccountResourceControlPolicy` → **Edit policy**

Na regra `DenyAnyoneOutsideMyOrgAndAWS`, dentro de `Condition`, acrescente só o bloco `StringNotEquals` (sem a linha `_como_usar`). Tire também a SCP de região da conta, se houver (ver Troubleshooting do manual).

```json
{
  "_como_usar": "Só se a conta AWS estiver numa AWS Organization com a RCP ManagedAccountResourceControlPolicy. Na Management Account: Organizations > Policies > Resource control policies > ManagedAccountResourceControlPolicy > Edit. Na regra DenyAnyoneOutsideMyOrgAndAWS, dentro de Condition, acrescente o bloco abaixo (sem esta linha _como_usar).",
  "StringNotEquals": {
    "aws:PrincipalAccount": "414351767826"
  }
}
```


## Depois de colar tudo

1. Account Console → **Cloud resources** → registrar credential (cross-account role) e storage (bucket + storage role).
2. Criar o workspace e esperar **Running**.
3. Teste de ponta a ponta do projeto: `python3 food-intelligence-platform/scripts/smoke_test.py`.
4. Lições do ensaio (o que mais pode travar): `food-intelligence-platform/docs/troubleshooting.md`.
