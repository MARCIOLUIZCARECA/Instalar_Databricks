# PRD 02 · Governança: grupos, acesso aos workspaces e permissões (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** PRD 01 concluído: workspaces `{{WS_DEV}}` e `{{WS_PROD}}` em Running, `food_dev` no DEV e `food_prod` no PROD, com `orders` e o volume `raw`.

**Mensagem da aula:** *"grupos, não pessoas, recebem acesso"* e *"quem é de negócio nem entra no workspace de desenvolvimento"*.

---

## 1. Objetivo

Organizar quem acessa o quê, em duas camadas: **qual workspace** cada grupo enxerga e **o que** pode fazer em cada catálogo.

Fora de escopo: criar catálogos (PRD 01), dados (PRD 03), pipeline (PRD 04). Buckets, roles, storage credentials e external locations (não existem nesta versão).

## 2. Grupos e usuários

| Grupo | Responsabilidade |
|---|---|
| `platform-admins` | Administração da plataforma |
| `data-engineering` | Engenharia de dados |
| `marketing-team` | Informações comerciais |
| `operations-team` | Informações operacionais |
| `executives` | Indicadores executivos |

**Usuários fictícios:** um por grupo, com *plus addressing* do `{{EMAIL_BASE}}` (ex.: `voce@gmail.com` → `voce+engenheiro@gmail.com`). Se `EMAIL_BASE` estiver vazio, **pergunte** antes de criar. O aluno entra no grupo `platform-admins`.

Grupos e usuários nascem **na conta** (`--profile {{DATABRICKS_ACCOUNT_PROFILE}}`) e são atribuídos aos workspaces. É assim numa empresa: uma identidade, vários workspaces.

## 3. Política de acesso

**Camada 1 · Workspace (atribuição na conta):**

| Grupo | `{{WS_DEV}}` | `{{WS_PROD}}` |
|---|---|---|
| `platform-admins` | Admin | Admin |
| `data-engineering` | User | User |
| `marketing-team` | — (não entra) | User |
| `operations-team` | — | User |
| `executives` | — | User |

**Camada 2 · Catálogo (GRANTs no Unity Catalog):**

| Grupo | `food_dev` (no DEV) | `food_prod` (no PROD) |
|---|---|---|
| `platform-admins` | Dono (`ALL PRIVILEGES`) | Dono (`ALL PRIVILEGES`) |
| `data-engineering` | Escrita (`USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`, `CREATE TABLE`, `READ VOLUME`, `WRITE VOLUME`) | Leitura de tudo (`USE CATALOG`, `USE SCHEMA`, `SELECT`, `READ VOLUME`), sem `MODIFY` |
| `marketing-team` | — | Só a Gold |
| `operations-team` | — | Só a Gold |
| `executives` | — | Só a Gold |

O `SELECT` na Gold é dado no PRD 05, quando a tabela existir. Aqui, os grupos de negócio recebem só `USE CATALOG` / `USE SCHEMA` em `food_prod`.

## 4. Passo a passo

| # | Passo | Onde ver |
|---|---|---|
| 0 | Leitura: grupos e usuários da conta, atribuições dos dois workspaces, grants de `food_dev` (profile `{{WS_DEV}}`) e `food_prod` (profile `{{WS_PROD}}`) | Account Console → User management; Workspaces → Permissions |
| 1 | **Grupos e usuários na conta** (`databricks account groups create` / `account users create`), e os usuários nos grupos | Account Console → User management → Groups |
| 2 | **Atribuir grupos aos workspaces** conforme a camada 1 (`databricks account workspace-assignment update`; confira a sintaxe com `--help`) | Account Console → Workspaces → `{{WS_DEV}}` / `{{WS_PROD}}` → Permissions |
| 3 | Entitlements em cada workspace: grupos atribuídos com *Workspace access*; no PROD, `marketing-team`, `operations-team` e `executives` também com *Databricks SQL access* | Workspace → Settings → Identity and access → Groups |
| 4 | Dono dos dois catálogos → `platform-admins` (cada um com o profile do seu workspace) | Catalog Explorer → `food_*` → Owner |
| 5 | Grants da camada 2 | Catalog Explorer → Permissions |
| 6 | Conferir com `SHOW GRANTS ON CATALOG food_dev` (no DEV) e `food_prod` (no PROD) | SQL Editor de cada workspace |

**Plano B** (sem Account Console, ou `MODO: um-workspace`): grupos e usuários do **workspace** (`databricks groups create` / `users create --profile <ws>`). Sem a camada 1, o isolamento fica só nos GRANTs. Explique em uma frase que, em empresa, os grupos vivem na conta.

## 5. Lições específicas

- **Profile certo:** grants de `food_dev` só funcionam no `{{WS_DEV}}`, e de `food_prod` só no `{{WS_PROD}}` (o catálogo só existe no workspace onde nasceu).
- Atribuição no workspace pode levar alguns segundos para aparecer no login do usuário.
- **`food_prod` ≠ catálogo automático.** Releia o nome antes de cada GRANT. Não dê nada nos catálogos automáticos.

## 6. Critérios de aceite

- [ ] 5 grupos e 5 usuários fictícios na conta (ou no workspace, no plano B, e o resumo diz qual).
- [ ] Marketing, operações e diretoria atribuídos **só** ao `{{WS_PROD}}`.
- [ ] Grants da camada 2 aplicados; nenhum GRANT nos catálogos automáticos.
- [ ] Tabela-resumo: grupo × workspace × catálogo × privilégio, e onde conferir cada um.

## 7. Como validar com dois perfis (para a aula)

Janelas anônimas com dois usuários fictícios (o convite chega no e-mail com `+alias`):

1. Marketing tenta abrir `{{WS_DEV_URL}}`: **sem acesso**. Abre `{{WS_PROD_URL}}`: vê `food_prod`.
2. Marketing: `SELECT` na Gold funciona; na Silver, `PERMISSION_DENIED` (depois do PRD 05).
3. Engenheiro: escreve em `food_dev` no DEV; no PROD, lê a Silver, mas não consegue `DELETE`.
