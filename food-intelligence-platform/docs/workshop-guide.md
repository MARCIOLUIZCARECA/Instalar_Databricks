# Roteiro do instrutor · 4 horas

Workshop **Do Zero à Produção — Databricks Enterprise na AWS** · sábado, 07/11/2026, 9h às 13h.

**Formato:** os participantes **assistem** ao vivo e **repetem depois**, em casa, com o manual e o código. Quem tentar acompanhar em tempo real deve ser orientado a parar no bloco 2 (o que tiver criado) e seguir só assistindo.

História do dia: **clicar para entender → automatizar para escalar.**

```
Express (2 min)  →  Clássico na mão (entender)  →  DEV e PROD com código (escalar)
                 →  Governança  →  Pipeline  →  Promoção  →  Negócio
```

## Agenda

| Tempo | Bloco | Entrega |
|---|---|---|
| 00:00–00:20 | Contexto e arquitetura | Por que Databricks na AWS |
| 00:20–00:40 | **1 · Workspace Express** | Um workspace serverless funcionando em minutos |
| 00:40–01:30 | **2 · AWS na mão** | Workspace clássico, peça por peça |
| 01:30–02:00 | **3 · Ambientes: escolha, custo e código** | DEV e PROD por Terraform + Claude Code |
| 02:00–02:40 | **4 · Governança** | Grupos, Unity Catalog, permissões testadas |
| 02:40–03:20 | **5 · Pipeline e promoção** | S3 → Bronze → Silver → Gold; DEV → TEST → PROD |
| 03:20–03:45 | **6 · Consumo** | Dashboard, App e Genie na mesma Gold |
| 03:45–04:00 | Fechamento | Jornada completa, custos, como repetir em casa |

---

## Na véspera (preparação)

> Montando numa conta nova? Siga antes o checklist de [troubleshooting.md](troubleshooting.md).

| # | O quê | Pronto quando |
|---|---|---|
| 1 | Logins: `workshop-account` (Databricks) e `food-workshop` (AWS 928844615034) | `databricks auth profiles` válido; `aws sts get-caller-identity --profile food-workshop` = 928844615034 |
| 2 | FOOD-DEV e FOOD-PROD criados (já estão: ensaio de 06/11) | `RUNNING` no Account Console |
| 3 | Profiles `food-dev` e `food-prod` | `databricks current-user me -p food-prod` funciona |
| 4 | Governança aplicada | grupos, usuários, catálogos e volume `raw` visíveis |
| 5 | Dados no bucket raw de DEV e PROD | `LIST '/Volumes/food_dev/orders/raw'` mostra 2 arquivos |
| 6 | Pipeline rodada em DEV e PROD | task `validate` verde nos 2 |
| 7 | Dashboard, App e Genie em PROD | dashboard publicado, App `RUNNING`, Genie responde as 7 perguntas |
| 8 | Janelas anônimas logadas como **marketing** e **engenheiro** | marketing recebe `PERMISSION_DENIED` na Silver |
| 9 | Terminal com fonte grande, Claude Code aberto na raiz do repo | prompts do bloco 3 testados uma vez |
| 10 | **No dia, 15 min antes:** ligar o `Food Classic Warehouse` nos dois workspaces (`databricks warehouses start <id> -p food-prod`) e abrir os Apps uma vez | o warehouse clássico leva 2 a 5 min para ligar e desliga após 10 min parado; sem isso, o App fica esperando na frente da turma |
| 11 | **Teste de ponta a ponta:** `python3 scripts/smoke_test.py` | "Resultado: TUDO OK" (20 checagens em DEV e PROD; o aviso do SQL serverless é esperado nesta conta) |
| 12 | Abas abertas: Account Console, console AWS (us-east-2), os 2 workspaces | — |

**Não crie workspace ao vivo.** A conta Databricks tem **limite diário de criação de workspaces** (no ensaio de 06/11, o 5º do dia falhou com "try again in 24 hours"), e criar leva ~15 min. No bloco 3, rode só o `terraform plan` ao vivo e mostre os workspaces já prontos.

**Planos B (não apague):**

| Workspace | Serve para |
|---|---|
| `workspace` (serverless) | Bloco 1, se a criação do Express falhar pelo limite diário |
| `workshop-aws` (clássico) | Bloco 2, se o workspace criado à mão não subir a tempo |

---

## 00:00–00:20 · Contexto e arquitetura

- História: experiência numa grande empresa global (sem dados nem arquitetura proprietária). Contratação pelo marketplace da AWS e relacionamento comercial existente reduzem atrito de compra.
- Cenário: rede de delivery fictícia; pedidos, lojas e cardápios no S3.
- Desenhar a jornada: **AWS → Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Negócio**.
- Material: [architecture.md](architecture.md), [fundamentos](../../manual/fundamentos.md).

## 00:20–00:40 · 1 · Workspace Express

**Mensagem:** começar é fácil. Mas "funciona" não é o mesmo que "pronto para a empresa".

1. Account Console → **Workspaces → Create workspace** → opção serverless (sem conta AWS própria).
2. Enquanto sobe (~2 min): o que a Databricks gerencia por você (compute, storage, rede).
3. Abrir o workspace → notebook → `SELECT` em `samples.nyctaxi.trips`.
4. Perguntar à turma: *"Onde estão os dados? Quem paga a máquina? Como separo DEV de PROD? Quem pode ver o quê?"* Essas perguntas guiam o resto da aula.

## 00:40–01:30 · 2 · AWS na mão (workspace clássico)

**Mensagem:** entender cada peça antes de automatizar.

Seguir o [manual](../../manual/README.md), seções 1 a 6, na tela:

| Passo | Explicar |
|---|---|
| Tela "Create workspace" | os blocos do formulário; automático × manual |
| Bucket raiz + bucket policy | o que a Databricks grava ali; o Deny em `unity-catalog/` |
| Storage role | Unity Catalog; self-assuming; External ID |
| Cross-account role | a "chave do compute"; *confused deputy* |
| Registrar e criar | credential + storage + rede = workspace |

Durante os ~5 min de criação: control plane × compute plane, clássico × serverless, custos ([Quanto custa](../../manual/README.md#quanto-custa)).

> Se o tempo apertar, crie as peças da AWS ao vivo e mostre o workspace `workshop-aws` já pronto.

## 01:30–02:00 · 3 · Ambientes: escolha, custo e código

**Mensagem:** quantos ambientes é uma decisão de risco **e** de custo. Depois de decidir, o que foi clicado no bloco 2 vira código e se repete por ambiente.

**Primeiro, a escolha** (slides "Quantos ambientes" e "Quanto custa", 8 min; detalhes em [environments.md](environments.md#quantos-ambientes)):

| Opção | Custo fixo/mês | Quando |
|---|---|---|
| Só PROD | ≈ US$ 36 | Prova de conceito |
| **DEV + PROD** (hoje) | ≈ US$ 73 | A maioria dos times |
| DEV + HML + PROD | ≈ US$ 110 | Reguladas, muitos times |

Conte o bastidor: no ensaio, a conta bateu o limite diário de criação de workspaces. Lição: planejar ambientes antes de sair criando. O TEST automático cobre parte do papel do HML sem custar um workspace.

**Depois, o código.**

Abrir o Claude Code na raiz do repositório. Prompts preparados (copiar e colar):

**Prompt 1 · entender**
```
Explique em 5 tópicos, para uma plateia de engenheiros de dados, o que a pasta terraform/
cria e qual passo do manual cada arquivo substitui.
```

**Prompt 2 · os ambientes**
```
Mostre como o terraform/databricks.tf cria um workspace por ambiente (dev e prod)
reaproveitando a mesma credential e storage configuration. O que é compartilhado e o que
é separado? Como eu adicionaria um terceiro ambiente (hml)?
```

**Prompt 3 · conferir sem custo**
```
Rode terraform plan na pasta terraform e explique o resultado. Não rode apply.
```

O plan deve dizer **"No changes"**: o código e o que existe na conta batem. Ótimo gancho: "o Terraform não recria o que já existe; ele só corrige diferenças".

**Prompt 4 · e se fossem três?** (só mostra, não aplica)
```
Se eu incluir hml no environments do terraform.tfvars, o que o plan mostraria e quanto
isso somaria de custo fixo por mês?
```

Pontos para explicar:

- `for_each`: um bloco, um workspace por ambiente.
- **State**: o Terraform lembra o que criou (`terraform destroy` desfaz tudo).
- **Dois stacks**: infraestrutura (o "prédio") × governança (a "portaria"). Mostrar [`../infrastructure/terraform`](../infrastructure/terraform).
- Login de conta × login de workspace ([manual, seção 7](../../manual/README.md#7-login-pelo-terminal-e-claude-code)).

Fechar mostrando FOOD-DEV e FOOD-PROD `RUNNING` no Account Console ("rodei ontem com este mesmo código; leva ~15 min").

> **Regra de ouro com Claude Code ao vivo:** pedidos curtos, sobre código que já existe. Nunca "crie tudo do zero" na frente da turma.

## 02:00–02:40 · 4 · Governança

| Onde | Mostrar |
|---|---|
| Account Console → User management | os 5 grupos; usuários fictícios; um usuário, vários workspaces |
| Workspaces → FOOD-DEV → Permissions | marketing **não** está; engenharia está |
| Catalog Explorer (FOOD-PROD) → `food_prod` | **Workspaces**: só FOOD-PROD (catálogo isolado); **Permissions** |
| External locations + volume `raw` | **metadado × dado físico**: abrir o bucket raw no console AWS lado a lado |

Demonstração com dois perfis (janelas anônimas), seguindo [governance.md](governance.md#validar-com-dois-perfis-direto-no-dado):

1. Marketing tenta abrir FOOD-DEV → sem acesso ao workspace.
2. Marketing no FOOD-PROD: `SELECT` na Gold funciona; na Silver, `PERMISSION_DENIED`.
3. Engenheiro no FOOD-PROD: lê a Silver, mas não consegue `DELETE`.

## 02:40–03:20 · 5 · Pipeline e promoção

**Pipeline em FOOD-DEV** (já publicada; mostrar e rodar, não programar):

| Notebook | Mostrar |
|---|---|
| `01_ingestion` | volume = bucket raw; datas e valores chegam como texto |
| `02_bronze` | raw → tabela Delta; `_source_file`; `DESCRIBE DETAIL` aponta para o bucket lakehouse |
| `03_silver` | as 6 regras; `src/food/transforms.py` + testes |
| `04_gold` | loja × dia, só entregues; comentários de coluna; `GRANT` só em PROD |
| `05_validate` | as checagens que bloqueiam a promoção |

**Promoção** ([environments.md](environments.md)):

```bash
cd food-intelligence-platform
uv run --no-project --with pytest pytest tests -q        # TEST
databricks bundle run food_orders_pipeline -t dev        # validate verde = pode promover
databricks bundle deploy -t prod                         # mesma versão, outro workspace
```

Mostrar no FOOD-PROD: job sem prefixo `[dev ...]`, pasta `/Workspace/Projects/...`, engenharia só com *Can view*. Citar o exemplo de GitHub Actions + service principal.

## 03:20–03:45 · 6 · Consumo

A mesma Gold, três experiências ([consumption.md](consumption.md)):

1. **Dashboard**: filtrar por estado; KPIs e gráficos mudam juntos.
2. **App**: escolher lojas e período; comparativo.
3. **Genie**: 3 das 7 perguntas, incluindo "Quais lojas tiveram queda de faturamento?".
4. Repetir uma delas como **marketing**: vê a Gold e não vê a Silver por nenhuma das três interfaces.

## 03:45–04:00 · Fechamento

- Voltar à jornada e marcar cada etapa.
- Express × clássico × código: quando usar cada um.
- Custos e limpeza ([workspaces.md#limpeza](workspaces.md#limpeza)).
- **Como repetir em casa** (abaixo).

---

## Para os participantes repetirem depois

Ordem sugerida, do mais simples ao mais completo:

| # | O quê | Guia | Custo |
|---|---|---|---|
| 1 | Workspace Express | Account Console → Create workspace (serverless) | só o que usar |
| 2 | Workspace clássico na mão | [manual](../../manual/README.md) | NAT Gateway por hora |
| 3 | Mesmo setup por código | [terraform/](../../terraform/README.md) com **só DEV**: `environments = { dev = "FOOD-DEV" }` | 1 NAT Gateway |
| 4 | Governança + pipeline + consumo | [README do projeto](../README.md) | serverless, só durante o uso |
| 5 | **Limpeza no mesmo dia** | [workspaces.md#limpeza](workspaces.md#limpeza) | — |

Avisos para a turma:

- Conta AWS **paga** e fora de AWS Organization com SCP/RCP restritivas ([Troubleshooting](../../manual/README.md#troubleshooting)).
- Cada workspace clássico = um NAT Gateway (~US$ 1,20/dia parado). Para estudar, um basta.

---

## Checklist de aceite (PRD, seções 10 e 12.7)

- [ ] Arquitetura AWS + Databricks documentada ([architecture.md](architecture.md))
- [ ] Workspaces DEV e PROD criados (HML documentado como opção)
- [ ] Finalidade de cada ambiente e custo de cada opção claros ([environments.md](environments.md#quantos-ambientes))
- [ ] Grupos configurados; permissões documentadas e testáveis ([governance.md](governance.md))
- [ ] Unity Catalog configurado; S3 integrado (raw + lakehouse)
- [ ] Arquivo de pedidos lido (`01_ingestion`)
- [ ] Bronze, Silver e Gold funcionando (`05_validate` verde)
- [ ] Promoção DEV → TEST → PROD demonstrada
- [ ] Dashboard com indicadores e filtros funcionando
- [ ] App consultando a Gold
- [ ] Genie respondendo as 7 perguntas
- [ ] As três experiências na mesma fonte; permissões validadas com dois perfis
