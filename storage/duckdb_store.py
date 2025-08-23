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
        # Handle pandas Series by converting to list
        if hasattr(dates, 'empty') and dates.empty:
            return
        if hasattr(dates, 'tolist'):
            dates = dates.tolist()
        if not dates:
            return
        df = pd.DataFrame({"date": pd.to_datetime(list(dates)).date})
        # Remove duplicates to avoid constraint violations
        df = df.drop_duplicates(subset=['date'])
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
        WHERE f.service_date <= CURRENT_DATE
        GROUP BY 1
        ORDER BY 1
        """
        return self.con.execute(sql).df()

    def query_distinct_volunteers(self) -> pd.DataFrame:
        sql = """
        SELECT DISTINCT volunteer_id AS volunteer
        FROM service_fact
        WHERE service_date <= CURRENT_DATE
        ORDER BY 1
        """
        return self.con.execute(sql).df()

    def query_participants_table(self, granularity: str) -> pd.DataFrame:
        if granularity not in {"year", "quarter", "month"}:
            raise ValueError("granularity must be one of year|quarter|month")
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
        }[granularity]
        sql = f"""
        SELECT {group_expr} AS period, volunteer_id AS volunteer, COUNT(*) AS cnt
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.service_date <= CURRENT_DATE
        GROUP BY 1,2
        ORDER BY 1,2
        """
        return self.con.execute(sql).df()

    def query_volunteer_trend(self, volunteer: str, granularity: str) -> pd.DataFrame:
        if granularity not in {"year", "quarter", "month"}:
            raise ValueError("granularity must be one of year|quarter|month")
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
        }[granularity]
        sql = f"""
        SELECT {group_expr} AS period, COUNT(*) AS service_count
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.volunteer_id = ? AND f.service_date <= CURRENT_DATE
        GROUP BY 1
        ORDER BY 1
        """
        return self.con.execute(sql, [volunteer]).df()

    def query_volunteer_service_types(self, volunteer: str, granularity: str) -> pd.DataFrame:
        if granularity not in {"year", "quarter", "month"}:
            raise ValueError("granularity must be one of year|quarter|month")
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
        }[granularity]
        sql = f"""
        SELECT {group_expr} AS period, service_type_id, COUNT(*) AS service_count
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.volunteer_id = ? AND f.service_date <= CURRENT_DATE
        GROUP BY 1,2
        ORDER BY 1,2
        """
        return self.con.execute(sql, [volunteer]).df()

    def query_raw_data(self) -> pd.DataFrame:
        """查询原始数据，包含所有服事记录"""
        sql = """
        SELECT 
            f.fact_id,
            f.volunteer_id,
            f.service_type_id,
            f.service_date,
            f.source_row_id,
            f.ingested_at,
            d.year,
            d.quarter,
            d.month
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.service_date <= CURRENT_DATE
        ORDER BY f.service_date DESC, f.volunteer_id, f.service_type_id
        """
        return self.con.execute(sql).df()

    def query_volunteer_stats_recent_weeks(self, weeks: int = 4) -> pd.DataFrame:
        """查询最近N周的同工事工统计（截止到当前日期）"""
        sql = f"""
        SELECT 
            f.volunteer_id,
            COUNT(*) as total_services,
            COUNT(DISTINCT f.service_type_id) as service_types_count,
            MIN(f.service_date) as first_service_date,
            MAX(f.service_date) as last_service_date,
            STRING_AGG(DISTINCT f.service_type_id, ', ' ORDER BY f.service_type_id) as service_types
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
          AND f.service_date <= CURRENT_DATE
        GROUP BY f.volunteer_id
        ORDER BY total_services DESC, f.volunteer_id
        """
        return self.con.execute(sql).df()

    def query_volunteer_stats_recent_quarter(self) -> pd.DataFrame:
        """查询最近一季度(3个月)的同工事工统计（截止到当前日期）"""
        sql = """
        SELECT 
            f.volunteer_id,
            COUNT(*) as total_services,
            COUNT(DISTINCT f.service_type_id) as service_types_count,
            MIN(f.service_date) as first_service_date,
            MAX(f.service_date) as last_service_date,
            STRING_AGG(DISTINCT f.service_type_id, ', ' ORDER BY f.service_type_id) as service_types
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.service_date >= CURRENT_DATE - INTERVAL 3 MONTHS
          AND f.service_date <= CURRENT_DATE
        GROUP BY f.volunteer_id
        ORDER BY total_services DESC, f.volunteer_id
        """
        return self.con.execute(sql).df()

    def query_volunteer_weekly_trend(self, weeks: int = 12) -> pd.DataFrame:
        """查询最近N周的每周同工事工趋势（截止到当前日期）"""
        sql = f"""
        WITH week_data AS (
            SELECT 
                f.volunteer_id,
                DATE_TRUNC('week', f.service_date) as week_start,
                COUNT(*) as services_count
            FROM service_fact f
            WHERE f.service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, week_start
        )
        SELECT 
            volunteer_id,
            week_start,
            services_count,
            STRFTIME('%Y-W%V', week_start) as week_label
        FROM week_data
        ORDER BY week_start DESC, services_count DESC
        """
        return self.con.execute(sql).df()

    def query_service_type_distribution_recent(self, weeks: int = 4) -> pd.DataFrame:
        """查询最近N周各服务类型的分布情况（截止到当前日期）"""
        sql = f"""
        SELECT 
            f.service_type_id,
            COUNT(*) as total_services,
            COUNT(DISTINCT f.volunteer_id) as unique_volunteers,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM service_fact f
        WHERE f.service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
          AND f.service_date <= CURRENT_DATE
        GROUP BY f.service_type_id
        ORDER BY total_services DESC
        """
        return self.con.execute(sql).df()