# IAM roles que a Databricks vai "assumir" na sua conta AWS (passos 4 e 5 do manual).

# ---------------------------------------------------------------------------
# ② Storage role do Unity Catalog (passo 4)
# ---------------------------------------------------------------------------

# Trust policy (passo 4.4): QUEM pode assumir a role.
# Equivale a manual/policies/05-storage-role-trust-etapa2.json, gerada pelo
# data source oficial do provider Databricks.
#
# O problema do ovo e da galinha: a trust policy final cita a própria role
# (self-assuming). No console, a AWS recusa citar uma role que ainda não existe,
# por isso o manual cria a role em duas etapas (04 com External ID "0000", depois 05).
# No Terraform resolvemos em UMA etapa:
#   1. o ARN da role é montado a partir do NOME + AWS Account ID (locals), sem
#      referenciar aws_iam_role.storage, então não há ciclo no grafo;
#   2. o data source escreve o self-assume como "a minha conta pode assumir,
#      desde que aws:PrincipalArn seja esta role" (condição ArnLike). Esse formato
#      é aceito pela AWS mesmo antes de a role existir e tem o mesmo efeito do 05.
# Resultado: 2 statements, ambos exigindo sts:ExternalId = Databricks Account ID:
#   - UCMasterRole da Databricks (414351767826) pode assumir;
#   - a própria role pode assumir a si mesma.
data "databricks_aws_unity_catalog_assume_role_policy" "storage" {
  provider = databricks.mws

  aws_account_id = local.aws_account_id
  role_name      = local.storage_role_name
  external_id    = var.databricks_account_id
}

resource "aws_iam_role" "storage" {
  name               = local.storage_role_name
  description        = "Unity Catalog: acesso ao prefixo unity-catalog/ do bucket raiz do workspace"
  assume_role_policy = data.databricks_aws_unity_catalog_assume_role_policy.storage.json
}

# Permissions policy (passo 4.2): O QUE a role pode fazer.
# Conteúdo idêntico a manual/policies/06-storage-role-s3-policy.json.
#
# Por que não usamos o data source databricks_aws_unity_catalog_policy?
# Na versão 1.141.0 ele libera o bucket INTEIRO (não só unity-catalog/*) e já
# embute a parte de file events. O manual restringe ao prefixo, então
# escrevemos o JSON aqui.
resource "aws_iam_role_policy" "storage_s3" {
  name = "databricks-uc-s3-access"
  role = aws_iam_role.storage.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Ler, gravar e apagar arquivos SÓ dentro de unity-catalog/.
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ]
        Resource = "${aws_s3_bucket.root.arn}/unity-catalog/*"
      },
      {
        # Listar o bucket e descobrir a região dele.
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
        ]
        Resource = aws_s3_bucket.root.arn
      },
      {
        # Assumir a si mesma (a outra metade do self-assuming).
        Effect   = "Allow"
        Action   = ["sts:AssumeRole"]
        Resource = [local.storage_role_arn]
      },
    ]
  })
}

# Passo 4.5 (OPCIONAL): policy de file events.
# Conteúdo idêntico a manual/policies/07-storage-role-file-events-policy.json.
# Não cria nada; só autoriza a Databricks a criar SQS/SNS quando precisar.
# Ligue com enable_file_events = true no terraform.tfvars.
resource "aws_iam_role_policy" "storage_file_events" {
  count = var.enable_file_events ? 1 : 0

  name = "databricks-uc-file-events"
  role = aws_iam_role.storage.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ManagedFileEventsSetupStatement"
        Effect = "Allow"
        Action = [
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
          "sqs:PurgeQueue",
        ]
        Resource = [
          aws_s3_bucket.root.arn,
          "arn:aws:sqs:*:*:*",
          "arn:aws:sns:*:*:*",
        ]
      },
      {
        Sid      = "ManagedFileEventsListStatement"
        Effect   = "Allow"
        Action   = ["sqs:ListQueues", "sqs:ListQueueTags", "sns:ListTopics"]
        Resource = "*"
      },
      {
        Sid      = "ManagedFileEventsTeardownStatement"
        Effect   = "Allow"
        Action   = ["sns:Unsubscribe", "sns:DeleteTopic", "sqs:DeleteQueue"]
        Resource = ["arn:aws:sqs:*:*:*", "arn:aws:sns:*:*:*"]
      },
    ]
  })
}

# O IAM da AWS é "eventualmente consistente": a role existe, mas leva alguns
# segundos para valer em todas as regiões. Esperamos antes de entregar o ARN
# para a Databricks validar. Passar o ARN pelos triggers faz quem usa
# time_sleep.storage_role.triggers depender automaticamente desta pausa.
resource "time_sleep" "storage_role" {
  create_duration = "20s"

  triggers = {
    role_arn = aws_iam_role.storage.arn
    # Muda se a policy de S3 mudar, garantindo a ordem role -> policy -> pausa.
    s3_policy = aws_iam_role_policy.storage_s3.id
  }
}

# ---------------------------------------------------------------------------
# ③ Cross-account role (passo 5): a "chave do compute"
# ---------------------------------------------------------------------------

# Trust policy (passo 5.1). O data source oficial gera exatamente
# manual/policies/01-cross-account-trust-policy.json:
# a conta 414351767826 pode assumir, desde que sts:ExternalId = Databricks Account ID
# (proteção contra o "confused deputy").
data "databricks_aws_assume_role_policy" "cross_account" {
  provider = databricks.mws

  external_id = var.databricks_account_id
}

resource "aws_iam_role" "cross_account" {
  name               = local.cross_account_role_name
  description        = "Databricks: cria a rede (Databricks-managed VPC) e liga/desliga EC2 dos clusters"
  assume_role_policy = data.databricks_aws_assume_role_policy.cross_account.json
}

# Permissions policy (passo 5.2), versão para Databricks-managed VPC.
# Conteúdo idêntico a manual/policies/02-cross-account-access-policy.json.
#
# Existe o data source databricks_aws_crossaccount_policy (policy_type = "managed"),
# mas na versão 1.141.0 a lista de ações difere um pouco da doc atual
# (tem ec2:DetachVolume, ec2:DescribeNetworkAcls e ec2:DescribeVpcAttribute a mais).
# Para ficar igual ao console, escrevemos o JSON aqui.
resource "aws_iam_role_policy" "cross_account" {
  name = "databricks-cross-account-ec2"
  role = aws_iam_role.cross_account.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Stmt1403287045000"
        Effect = "Allow"
        Action = [
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
          "ec2:TerminateInstances",
        ]
        Resource = ["*"]
      },
      {
        # Permite criar a service-linked role de Spot (instâncias spot).
        Effect   = "Allow"
        Action   = ["iam:CreateServiceLinkedRole", "iam:PutRolePolicy"]
        Resource = "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot"
        Condition = {
          StringLike = {
            "iam:AWSServiceName" = "spot.amazonaws.com"
          }
        }
      },
    ]
  })
}

# Sem esta pausa, a validação da credential na Databricks costuma falhar
# ("Failed credential validation checks") porque o IAM ainda não propagou.
resource "time_sleep" "cross_account_role" {
  create_duration = "20s"

  triggers = {
    role_arn   = aws_iam_role.cross_account.arn
    ec2_policy = aws_iam_role_policy.cross_account.id
  }
}
