# Trusted Finance Metrics

An end-to-end analytics engineering project on real public financial data (SEC EDGAR XBRL filings + ECB FX rates), built with dbt, a MetricFlow semantic layer, Airflow orchestration, and an AI agent that is only allowed to answer questions through governed metrics (via MCP) — never raw SQL.

## Why this project exists

Most "AI on data" demos let an LLM write its own SQL, which means it can quietly compute the wrong number with full confidence. This project argues — and tests — that a **semantic layer matters more than the LLM**: an agent that can only call pre-defined, tested metric tools is safer and more trustworthy than one that writes ad hoc queries.

## Architecture

| Layer | What it does | Tech |
|---|---|---|
| 1. Ingestion | Incremental daily extracts of SEC company facts (10–20 financial firms) and ECB USD/EUR FX rates into partitioned bronze Parquet | Python, `requests`, `pyarrow`, `pytest` |
| 2. Transformation | staging → intermediate (EUR-normalized) → marts (`dim_company`, `fct_financials`, `fct_ratios`), incremental models, SCD2 snapshots, source freshness, tests incl. a custom balance-sheet reconciliation check | dbt Core (DuckDB + Databricks targets) |
| 3. Semantic layer | 5–8 governed metrics (revenue, revenue growth, net margin, debt ratio) with company/year dimensions | dbt MetricFlow |
| 4. AI layer | (a) ERD/doc generator: reads `target/manifest.json`, builds a Mermaid ERD, uses RAG + LLM to document tables/relationships. (b) MCP server exposing `list_metrics`, `query_metric`, `get_lineage` — the agent never touches raw SQL | Python, MCP SDK, Claude API / Ollama |
| 5. Evaluation | 25 ground-truth questions, scoring the metrics-governed agent vs a naive text-to-SQL baseline | Python |
| 6. Orchestration & CI | Airflow DAG (`extract_sec` → `extract_fx` → `dbt build` → notify); GitHub Actions running pytest, sqlfluff, `dbt build` on every push | Airflow, GitHub Actions |
| 7. Two engines | Runs locally on DuckDB (free) and on Databricks Free Edition | dbt-duckdb, dbt-databricks |

## Status

- [x] Day 1 — repo scaffold, README, folder structure
- [ ] Day 2–4 — SEC + ECB extractors, bronze Parquet, pytest
- [ ] Day 5–8 — dbt staging/intermediate/marts, incremental models, snapshots, tests
- [ ] Day 9 — MetricFlow metrics
- [ ] Day 10 — Airflow DAG
- [ ] Day 11 — GitHub Actions CI
- [ ] Day 12–14 — ERD/doc generator (RAG + LLM)
- [ ] Day 15–16 — MCP server (list_metrics, query_metric, get_lineage)
- [ ] Day 17–18 — 25-question evaluation (agent vs naive text-to-SQL)
- [ ] Day 19 — Databricks Free Edition run
- [ ] Day 20 — final README, architecture diagram, results

_Last updated: 2026-11-03_

## How to run

```bash
# 1. Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Extract raw data
python extractors/sec_edgar.py
python extractors/ecb_fx.py

# 3. Build dbt models (DuckDB target)
cd dbt && dbt build

# 4. Query metrics
mf query --metrics revenue --group-by company__name,metric_time
```

(Airflow, MCP server, and evaluation instructions will be added as those pieces land — see Status above.)

## Design decisions & trade-offs

_To be filled in as built — e.g. why incremental over full refresh, why SCD2 snapshots, why MCP tools instead of letting the agent write SQL, DuckDB vs Databricks trade-offs._

## Results

_To be filled in after the Day 17–18 evaluation: agent-via-metrics scored **X/25** vs **Y/25** for naive text-to-SQL._

## Data sources

- SEC EDGAR XBRL company facts API: `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (requires a descriptive `User-Agent` header with name + email per SEC's fair-use policy)
- ECB Data Portal, FX reference rates: `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata`
