# PRD 02 · Governança: grupos, usuários e permissões (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** PRD 01 concluído: login no `{{WS}}` e os catálogos `food_dev` e `food_prod` criados, com `orders` e o volume `raw`.

**Mensagem da aula:** *"grupos, não pessoas, recebem acesso"* e *"DEV e PROD separados por permissão, mesmo num workspace só"*.

---

## 1. Objetivo

Organizar quem acessa o quê nos dois ambientes criados no PRD 01.

Fora de escopo: criar catálogos (já feito no PRD 01), dados (PRD 03), pipeline (PRD 04). Buckets, roles, storage credentials e external locations (não existem nesta versão).

## 2. Grupos e usuários

| Grupo | Responsabilidade |
|---|---|
| `platform-admins` | Administração da plataforma |
| `data-engineering` | Engenharia de dados |
| `marketing-team` | Informações comerciais |
| `operations-team` | Informações operacionais |
| `executives` | Indicadores executivos |

**Usuários fictícios:** um por grupo, com *plus addressing* do `{{EMAIL_BASE}}` (ex.: `voce@gmail.com` → `voce+engenheiro@gmail.com`). Se `EMAIL_BASE` estiver vazio, **pergunte** antes de criar. O aluno entra no grupo `platform-admins`.

## 3. Política de acesso

Como só há um workspace, o isolamento é feito por **privilégios no Unity Catalog**, não por *workspace binding*.

| Grupo | `food_dev` | `food_prod` |
|---|---|---|
| `platform-admins` | Dono (`ALL PRIVILEGES`) | Dono (`ALL PRIVILEGES`) |
| `data-engineering` | Escrita (`USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`, `CREATE TABLE`, `READ VOLUME`, `WRITE VOLUME`) | Leitura de tudo (`USE CATALOG`, `USE SCHEMA`, `SELECT`, `READ VOLUME`), sem `MODIFY` |
| `marketing-team` | — (não enxerga) | Só a Gold |
| `operations-team` | — | Só a Gold |
| `executives` | — | Só a Gold |

O `SELECT` na Gold é dado no PRD 05, quando a tabela existir. Aqui, os grupos de negócio recebem só `USE CATALOG` / `USE SCHEMA` em `food_prod`.

## 4. Passo a passo

| # | Passo | Onde ver |
|---|---|---|
| 0 | Leitura: grupos, usuários e grants atuais de `food_dev` e `food_prod` | Settings → Identity and access; Catalog Explorer → Permissions |
| 1 | **Grupos e usuários.** Tentar na **conta** (`databricks account groups create --profile {{DATABRICKS_ACCOUNT_PROFILE}}`), se o aluno tiver acesso ao Account Console. **Plano B:** grupos e usuários do **workspace** (`databricks groups create` / `databricks users create --profile {{WS}}`). Explicar a diferença em uma frase | Settings → Identity and access → Groups |
| 2 | Entitlements: os 5 grupos com *Workspace access*; `marketing-team`, `operations-team` e `executives` também com *Databricks SQL access* | Settings → Groups → Entitlements |
| 3 | Dono dos dois catálogos → `platform-admins` | Catalog Explorer → `food_*` → Owner |
| 4 | Grants da seção 3 | Catalog Explorer → Permissions |
| 5 | Conferir com `SHOW GRANTS ON CATALOG food_dev` e `food_prod` | SQL Editor |

## 5. Lições específicas

- Grupos de workspace (plano B) funcionam nos GRANTs do Unity Catalog do mesmo jeito; explique que, em empresa, eles vivem na **conta**.
- **`food_prod` ≠ catálogo automático.** Releia o nome antes de cada GRANT.
- Não dê nada no catálogo automático.

## 6. Critérios de aceite

- [ ] 5 grupos e 5 usuários fictícios (na conta ou no workspace, e o resumo diz qual).
- [ ] Grants da seção 3 aplicados; marketing **não** enxerga `food_dev`.
- [ ] Nenhum GRANT no catálogo automático.
- [ ] Tabela-resumo: grupo × catálogo × privilégio, e onde conferir cada um.

## 7. Como validar com dois perfis (para a aula)

Janelas anônimas com dois usuários fictícios (o convite chega no e-mail com `+alias`):

1. Marketing no Catalog Explorer: vê `food_prod`, **não** vê `food_dev`.
2. Marketing: `SELECT` na Gold funciona; na Silver, `PERMISSION_DENIED` (depois do PRD 05).
3. Engenheiro: lê a Silver de PROD, mas não consegue `DELETE`.
