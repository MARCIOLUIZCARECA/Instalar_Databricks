# Consumo: Dashboard, App e Genie

As três experiências leem **a mesma tabela**: `food_prod.orders.gold_sales_by_store`. Nenhuma tem regra de negócio própria: faturamento, pedidos e ticket médio são definidos uma vez, na Gold.

| Componente | Finalidade | Perfil | Arquivos |
|---|---|---|---|
| AI/BI Dashboard | Indicadores e gráficos fixos | Executivos e analistas | [`dashboards/`](../dashboards), [`resources/executive_overview.dashboard.yml`](../resources/executive_overview.dashboard.yml) |
| Databricks App | Aplicação com interação própria | Usuários de negócio | [`app/`](../app), [`resources/food_explorer.app.yml`](../resources/food_explorer.app.yml) |
| Genie | Perguntas em linguagem natural | Usuários não técnicos | [`genie/`](../genie), target `prod` em [`databricks.yml`](../databricks.yml) |

Os três são publicados pelo bundle:

```bash
databricks bundle deploy -t prod
databricks bundle run food_explorer -t prod     # inicia o App
databricks bundle summary -t prod               # links do dashboard, do app e do Genie
```

## Food Intelligence — Executive Overview (Dashboard)

- KPIs: faturamento total, pedidos, ticket médio, lojas.
- Gráficos: faturamento por dia, faturamento por região, pedidos por mês, ranking das lojas, ticket médio por loja.
- Filtros (aba **Filtros**, valem para tudo): período, estado, cidade, loja.

O JSON é gerado por código: edite `dashboards/build_dashboard.py` e rode `python dashboards/build_dashboard.py`. As queries usam só `FROM gold_sales_by_store`; o catálogo vem de `dataset_catalog` no bundle, então o mesmo arquivo serve em DEV e PROD.

Queries de referência (as mesmas medidas do dashboard):

```sql
-- KPIs
SELECT SUM(total_revenue) AS faturamento, SUM(total_orders) AS pedidos,
       SUM(total_revenue) / SUM(total_orders) AS ticket_medio, COUNT(DISTINCT store_id) AS lojas
FROM food_prod.orders.gold_sales_by_store;

-- Faturamento por região
SELECT region, SUM(total_revenue) AS faturamento
FROM food_prod.orders.gold_sales_by_store GROUP BY region ORDER BY faturamento DESC;

-- Ranking das lojas
SELECT store_name, SUM(total_revenue) AS faturamento
FROM food_prod.orders.gold_sales_by_store GROUP BY store_name ORDER BY faturamento DESC;
```

## Food Intelligence Explorer (App)

Streamlit, com filtros de período e lojas: mostra faturamento, pedidos, ticket médio, histórico semanal e comparativo entre lojas.

- Conexão: SQL warehouse declarado como recurso do App (`sql-warehouse`, permissão *Can use*). Nenhuma credencial no código.
- Warehouse: `Food Classic Warehouse` (clássico, PRO, 2X-Small, desliga após 10 min parado). Na conta do ensaio o SQL **serverless** dava 403 nos buckets ([troubleshooting.md](troubleshooting.md#e-sql-warehouse-serverless-com-403-nos-buckets-do-projeto)). Ligado, ele leva 2 a 5 min para responder: o App mostra "Conectando ao SQL warehouse…" nesse tempo.
- Identidade: com **autorização de usuário** ligada (escopo `sql`), cada consulta roda como a pessoa logada, e o Unity Catalog aplica as permissões dela. Um admin do workspace precisa habilitar o recurso (Public Preview) em *Settings → Previews*.
- Sem autorização de usuário, o App usa o seu service principal (ver [governance.md](governance.md#service-principal-do-app)).

Rodar localmente (contra o workspace, com o seu login):

```bash
cd app
DATABRICKS_CONFIG_PROFILE=food-prod DATABRICKS_WAREHOUSE_ID=<id> FOOD_CATALOG=food_prod \
  uv run --with-requirements requirements.txt streamlit run app.py
```

## Food Business Analyst (Genie)

Definição em `genie/food_business_analyst.<catálogo>.geniespace.json`, gerada por `python genie/build_genie_space.py`:

- tabela `gold_sales_by_store` com descrição e sinônimos por coluna;
- instruções de negócio (faturamento, ticket médio = SUM/SUM, "volume" = pedidos, regiões);
- medidas prontas (faturamento, pedidos, ticket médio) e 3 exemplos de SQL;
- as 7 perguntas de demonstração como sugestões.

Perguntas para a demo:

1. Qual foi o faturamento total no período?
2. Quais são as cinco lojas com maior faturamento?
3. Qual estado possui maior volume de vendas?
4. Qual é o ticket médio por loja?
5. Como evoluíram as vendas nos últimos meses?
6. Quais lojas tiveram queda de faturamento? *(os dados têm lojas com tendência de queda de propósito)*
7. Qual foi o volume de pedidos por região?

## Governança na camada de consumo

| Pergunta | Resposta |
|---|---|
| Ter acesso ao Dashboard dá acesso aos dados? | Não. O dashboard de PROD é compartilhado com os grupos de negócio (`CAN_RUN`), e eles também têm SELECT na Gold. |
| Dá para ver a Silver pelo App? | Não. O App só consulta a Gold, e com autorização de usuário a consulta roda com as permissões de quem usa. |
| O Genie pode responder com dados restritos? | Não. O Genie executa SQL com a identidade de quem pergunta; sem SELECT, a resposta é erro de permissão. |

Teste com dois perfis: diretor (vê a Gold de PROD pelas três interfaces) e um usuário fora dos grupos de negócio (o dashboard, o App e o Genie não aparecem ou dão erro de permissão).
