from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any, Optional

import duckdb
import pandas as pd


@dataclass
class DuckDBConfig:
    db_path: str


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS volunteer (
  volunteer_id VARCHAR PRIMARY KEY,
  display_name VARCHAR,
  normalized_name VARCHAR
);

CREATE TABLE IF NOT EXISTS volunteer_alias (
  alias VARCHAR PRIMARY KEY,
  volunteer_id VARCHAR
);

CREATE TABLE IF NOT EXISTS service_type (
  service_type_id VARCHAR PRIMARY KEY,
  name VARCHAR,
  column_key VARCHAR
);

CREATE TABLE IF NOT EXISTS date_dim (
  date DATE PRIMARY KEY,
  year INTEGER,
  quarter INTEGER,
  month INTEGER
);

CREATE TABLE IF NOT EXISTS source_row (
  source_row_id VARCHAR PRIMARY KEY,
  spreadsheet_id VARCHAR,
  sheet_name VARCHAR,
  row_index INTEGER,
  row_checksum VARCHAR
);

CREATE TABLE IF NOT EXISTS service_fact (
  fact_id VARCHAR PRIMARY KEY,
  volunteer_id VARCHAR,
  service_type_id VARCHAR,
  service_date DATE,
  source_row_id VARCHAR,
  ingested_at TIMESTAMP
);
"""


class DuckDBStore:
    def __init__(self, cfg: DuckDBConfig) -> None:
        os.makedirs(os.path.dirname(cfg.db_path), exist_ok=True)
        self.con = duckdb.connect(cfg.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self.con.execute(SCHEMA_SQL)

    def upsert_date_dim(self, dates: Iterable[pd.Timestamp]) -> None:
        if not dates:
            return
        df = pd.DataFrame({"date": pd.to_datetime(list(dates)).date})
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df["quarter"] = pd.to_datetime(df["date"]).dt.quarter
        df["month"] = pd.to_datetime(df["date"]).dt.month
        self.con.execute("CREATE TEMP TABLE tmp_date AS SELECT * FROM df").df()
        self.con.execute(
            """
            INSERT OR REPLACE INTO date_dim
            SELECT date, year, quarter, month FROM tmp_date
            """
        )

    def insert_facts(self, facts_df: pd.DataFrame) -> None:
        if facts_df is None or facts_df.empty:
            return
        self.con.execute("CREATE TEMP TABLE tmp_facts AS SELECT * FROM facts_df").df()
        self.con.execute(
            """
            INSERT OR REPLACE INTO service_fact
            SELECT fact_id, volunteer_id, service_type_id, service_date, source_row_id, ingested_at
            FROM tmp_facts
            """
        )

    def query_aggregation(self, granularity: str) -> pd.DataFrame:
        if granularity not in {"year", "quarter", "month"}:
            raise ValueError("granularity must be one of year|quarter|month")
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
        }[granularity]
        sql = f"""
        SELECT
          {group_expr} AS period,
          COUNT(*) AS service_count
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        GROUP BY 1
        ORDER BY 1
        """
        return self.con.execute(sql).df()


