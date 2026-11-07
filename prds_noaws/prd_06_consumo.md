# PRD 06 · Consumo: Dashboard, App e Genie sobre a mesma Gold (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** `food_prod.orders.gold_sales_by_store` preenchida (PRD 05) e o SQL warehouse serverless `{{WAREHOUSE_ID}}`.

**Mensagem da aula:** *"a mesma Gold, três experiências; outra interface não é outra porta"*.

---

## 1. Objetivo

Três formas de consumo, no target `prod`, todas lendo **a mesma tabela Gold**, sem regra de negócio duplicada e respeitando as permissões de quem usa.

| Componente | Para quê | Perfil |
|---|---|---|
| AI/BI Dashboard | Indicadores fixos | Executivos e analistas |
| Databricks App | Interação e comparação | Usuários de negócio |
| Genie | Perguntas em português | Quem não escreve SQL |

## 2. O que construir (tudo no bundle, target `prod`)

**Dashboard "Food Intelligence — Executive Overview"** (skill `databricks-aibi-dashboards`), no warehouse `{{WAREHOUSE_ID}}`:
- KPIs: faturamento, pedidos, ticket médio, número de lojas.
- Gráficos: faturamento por dia, por região, ranking de lojas, pedidos por período, ticket médio por loja.
- Filtros: período, estado, cidade, loja.
- Cálculos na Gold, não nos gráficos. **Testar cada query via CLI antes do deploy.**

**App "Food Intelligence Explorer"** (Python + Streamlit, Databricks Apps; skill `databricks-apps-python`):
- Escolher loja(s) e período; ver faturamento, pedidos, ticket médio, histórico e comparação entre lojas.
- Lê a Gold com **autorização do usuário** (identidade de quem usa), sem credencial no código.
- **Plano B:** se Apps não estiver disponível na conta Express, ou a autorização do usuário não estiver habilitada, mostrar o erro, usar a identidade do App (service principal do App com `SELECT` só na Gold) e explicar a diferença; se Apps não existir de jeito nenhum, pular o App e dar mais tempo ao Genie.

**Genie "Food Business Analyst"** (skill `databricks-genie-agents`):
- Fonte: só a Gold; descrições de colunas e instruções de negócio (faturamento = só entregues; ticket médio = faturamento ÷ pedidos).
- Perguntas de exemplo: faturamento total no período; top 5 lojas por faturamento; estado com maior volume; ticket médio por loja; evolução nos últimos meses; lojas com queda de faturamento; pedidos por região.

## 3. Ordem de publicação

1. `bundle deploy -t prod` (job, dashboard, App).
2. `bundle run food_orders_pipeline -t prod` (garante a Gold).
3. `bundle deploy -t prod` de novo (o Genie exige a tabela existir).
4. `bundle run food_explorer -t prod` (sobe o App).

Ligue o warehouse uns 15 minutos antes da aula.

## 4. Critérios de aceite

- [ ] Dashboard com KPIs e filtros funcionando.
- [ ] App consultando a Gold (com a identidade do usuário, ou o plano B explicado).
- [ ] Genie respondendo as perguntas de exemplo em português, com o SQL certo.
- [ ] As três lendo `food_prod.orders.gold_sales_by_store`.
- [ ] Nenhum arquivo, consulta ou recurso usa o catálogo automático; tudo é `food_<ambiente>` em três partes.
- [ ] Com um usuário de marketing: Dashboard, App e Genie funcionam na Gold; ninguém lê a Silver nem `food_dev` por outra interface.
