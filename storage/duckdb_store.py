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

    def query_volunteer_count_trend(self, granularity: str = "month") -> pd.DataFrame:
        """查询同工总人数趋势"""
        if granularity not in {"year", "quarter", "month", "week"}:
            raise ValueError("granularity must be one of year|quarter|month|week")
        
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
            "week": "STRFTIME('%Y-W%V', f.service_date)"
        }[granularity]
        
        sql = f"""
        SELECT 
            {group_expr} AS period,
            COUNT(DISTINCT f.volunteer_id) as volunteer_count,
            COUNT(*) as total_services
        FROM service_fact f
        JOIN date_dim d ON f.service_date = d.date
        WHERE f.service_date <= CURRENT_DATE
        GROUP BY 1
        ORDER BY 1
        """
        return self.con.execute(sql).df()

    def query_cumulative_participation(self, granularity: str = "month") -> pd.DataFrame:
        """查询累计参与次数趋势"""
        if granularity not in {"year", "quarter", "month", "week"}:
            raise ValueError("granularity must be one of year|quarter|month|week")
        
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
            "week": "STRFTIME('%Y-W%V', f.service_date)"
        }[granularity]
        
        sql = f"""
        WITH period_services AS (
            SELECT 
                {group_expr} AS period,
                COUNT(*) as period_services
            FROM service_fact f
            JOIN date_dim d ON f.service_date = d.date
            WHERE f.service_date <= CURRENT_DATE
            GROUP BY 1
        )
        SELECT 
            period,
            period_services,
            SUM(period_services) OVER (ORDER BY period) as cumulative_services
        FROM period_services
        ORDER BY period
        """
        return self.con.execute(sql).df()

    def query_individual_volunteer_trends(self, top_n: int = 10, weeks: int = 12) -> pd.DataFrame:
        """查询前N名同工的个人事工次数趋势"""
        sql = f"""
        WITH top_volunteers AS (
            SELECT volunteer_id
            FROM service_fact
            WHERE service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
              AND service_date <= CURRENT_DATE
            GROUP BY volunteer_id
            ORDER BY COUNT(*) DESC
            LIMIT {top_n}
        ),
        weekly_data AS (
            SELECT 
                f.volunteer_id,
                STRFTIME('%Y-W%V', f.service_date) as week_label,
                DATE_TRUNC('week', f.service_date) as week_start,
                COUNT(*) as services_count
            FROM service_fact f
            WHERE f.volunteer_id IN (SELECT volunteer_id FROM top_volunteers)
              AND f.service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, week_label, week_start
        )
        SELECT 
            volunteer_id,
            week_label,
            week_start,
            services_count
        FROM weekly_data
        ORDER BY week_start, volunteer_id
        """
        return self.con.execute(sql).df()

    def query_volunteer_join_leave_analysis(self, granularity: str = "month") -> pd.DataFrame:
        """查询同工新增/离开分析"""
        if granularity not in {"year", "quarter", "month"}:
            raise ValueError("granularity must be one of year|quarter|month")
        
        group_expr = {
            "year": "CAST(d.year AS VARCHAR)",
            "quarter": "d.year || '-Q' || CAST(d.quarter AS VARCHAR)",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')"
        }[granularity]
        
        sql = f"""
        WITH volunteer_periods AS (
            SELECT 
                f.volunteer_id,
                {group_expr} AS period,
                MIN(f.service_date) as first_service_in_period,
                MAX(f.service_date) as last_service_in_period
            FROM service_fact f
            JOIN date_dim d ON f.service_date = d.date
            WHERE f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, {group_expr}
        ),
        volunteer_first_last AS (
            SELECT 
                volunteer_id,
                MIN(first_service_in_period) as first_ever_service,
                MAX(last_service_in_period) as last_ever_service
            FROM volunteer_periods
            GROUP BY volunteer_id
        ),
        period_stats AS (
            SELECT 
                vp.period,
                COUNT(*) as active_volunteers,
                COUNT(CASE WHEN vfl.first_ever_service = vp.first_service_in_period THEN 1 END) as new_volunteers
            FROM volunteer_periods vp
            JOIN volunteer_first_last vfl ON vp.volunteer_id = vfl.volunteer_id
            GROUP BY vp.period
        )
        SELECT 
            period,
            active_volunteers,
            new_volunteers,
            LAG(active_volunteers) OVER (ORDER BY period) as prev_active_volunteers,
            active_volunteers - LAG(active_volunteers, 1, 0) OVER (ORDER BY period) as net_change
        FROM period_stats
        ORDER BY period
        """
        return self.con.execute(sql).df()

    def query_participation_distribution(self, weeks: int = 12) -> pd.DataFrame:
        """查询参与次数分布（直方图数据）"""
        sql = f"""
        WITH volunteer_counts AS (
            SELECT 
                volunteer_id,
                COUNT(*) as service_count
            FROM service_fact
            WHERE service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
              AND service_date <= CURRENT_DATE
            GROUP BY volunteer_id
        ),
        count_ranges AS (
            SELECT 
                CASE 
                    WHEN service_count = 0 THEN '0次'
                    WHEN service_count BETWEEN 1 AND 2 THEN '1-2次'
                    WHEN service_count BETWEEN 3 AND 5 THEN '3-5次'
                    WHEN service_count BETWEEN 6 AND 10 THEN '6-10次'
                    WHEN service_count BETWEEN 11 AND 20 THEN '11-20次'
                    WHEN service_count > 20 THEN '20次以上'
                    ELSE '其他'
                END as range_label,
                service_count
            FROM volunteer_counts
        )
        SELECT 
            range_label,
            COUNT(*) as volunteer_count,
            ROUND(AVG(service_count), 1) as avg_services_in_range
        FROM count_ranges
        GROUP BY range_label
        ORDER BY 
            CASE range_label
                WHEN '0次' THEN 1
                WHEN '1-2次' THEN 2
                WHEN '3-5次' THEN 3
                WHEN '6-10次' THEN 4
                WHEN '11-20次' THEN 5
                WHEN '20次以上' THEN 6
                ELSE 7
            END
        """
        return self.con.execute(sql).df()

    def query_service_stats_for_boxplot(self, weeks: int = 12) -> pd.DataFrame:
        """查询同工服务次数统计（用于箱型图）"""
        sql = f"""
        SELECT 
            volunteer_id,
            COUNT(*) as service_count
        FROM service_fact
        WHERE service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
          AND service_date <= CURRENT_DATE
        GROUP BY volunteer_id
        ORDER BY service_count
        """
        return self.con.execute(sql).df()

    def query_volunteer_service_network(self, min_services: int = 3) -> pd.DataFrame:
        """查询同工-服务类型网络关系数据"""
        sql = f"""
        SELECT 
            f.volunteer_id,
            f.service_type_id,
            COUNT(*) as collaboration_count
        FROM service_fact f
        WHERE f.service_date >= CURRENT_DATE - INTERVAL 12 WEEKS
          AND f.service_date <= CURRENT_DATE
        GROUP BY f.volunteer_id, f.service_type_id
        HAVING COUNT(*) >= {min_services}
        ORDER BY collaboration_count DESC
        """
        return self.con.execute(sql).df()

    def query_period_comparison_stats(self, weeks: int = 4) -> pd.DataFrame:
        """查询不同时期的同工事工环比变化"""
        sql = f"""
        WITH current_period AS (
            SELECT 
                volunteer_id,
                COUNT(*) as current_services
            FROM service_fact
            WHERE service_date >= CURRENT_DATE - INTERVAL {weeks} WEEKS
              AND service_date <= CURRENT_DATE
            GROUP BY volunteer_id
        ),
        previous_period AS (
            SELECT 
                volunteer_id,
                COUNT(*) as previous_services
            FROM service_fact
            WHERE service_date >= CURRENT_DATE - INTERVAL {weeks * 2} WEEKS
              AND service_date < CURRENT_DATE - INTERVAL {weeks} WEEKS
            GROUP BY volunteer_id
        )
        SELECT 
            COALESCE(cp.volunteer_id, pp.volunteer_id) as volunteer_id,
            COALESCE(cp.current_services, 0) as current_services,
            COALESCE(pp.previous_services, 0) as previous_services,
            COALESCE(cp.current_services, 0) - COALESCE(pp.previous_services, 0) as change_amount,
            CASE 
                WHEN pp.previous_services > 0 THEN 
                    ROUND((COALESCE(cp.current_services, 0) - pp.previous_services) * 100.0 / pp.previous_services, 1)
                WHEN cp.current_services > 0 THEN 100.0
                ELSE 0.0
            END as change_percentage
        FROM current_period cp
        FULL OUTER JOIN previous_period pp ON cp.volunteer_id = pp.volunteer_id
        WHERE COALESCE(cp.current_services, 0) > 0 OR COALESCE(pp.previous_services, 0) > 0
        ORDER BY change_amount DESC
        """
        return self.con.execute(sql).df()

    def query_service_transitions_for_sankey(self, months: int = 6) -> pd.DataFrame:
        """查询同工在不同事工类型之间的转换数据（用于桑基图）"""
        sql = f"""
        WITH volunteer_service_periods AS (
            SELECT 
                f.volunteer_id,
                f.service_type_id,
                DATE_TRUNC('month', f.service_date) as service_month,
                COUNT(*) as services_in_month
            FROM service_fact f
            WHERE f.service_date >= CURRENT_DATE - INTERVAL {months} MONTHS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, f.service_type_id, service_month
            HAVING COUNT(*) >= 1  -- 至少参与1次
        ),
        monthly_primary_service AS (
            -- 每个月每个同工的主要事工类型（参与最多的）
            SELECT 
                volunteer_id,
                service_month,
                service_type_id,
                services_in_month,
                ROW_NUMBER() OVER (PARTITION BY volunteer_id, service_month ORDER BY services_in_month DESC) as rn
            FROM volunteer_service_periods
        ),
        transitions AS (
            SELECT 
                curr.volunteer_id,
                prev.service_type_id as from_service,
                curr.service_type_id as to_service,
                prev.service_month as from_month,
                curr.service_month as to_month
            FROM monthly_primary_service curr
            JOIN monthly_primary_service prev 
                ON curr.volunteer_id = prev.volunteer_id 
                AND curr.service_month = prev.service_month + INTERVAL 1 MONTH
            WHERE curr.rn = 1 AND prev.rn = 1  -- 只考虑主要服务类型
              AND prev.service_type_id != curr.service_type_id  -- 只记录转换
        )
        SELECT 
            from_service,
            to_service,
            COUNT(*) as transition_count,
            COUNT(DISTINCT volunteer_id) as volunteer_count,
            STRING_AGG(DISTINCT volunteer_id, ', ') as volunteers
        FROM transitions
        GROUP BY from_service, to_service
        ORDER BY transition_count DESC
        """
        return self.con.execute(sql).df()

    def query_volunteer_journey_sankey(self, time_periods: int = 6) -> pd.DataFrame:
        """查询同工参与度的演变历程（用于桑基图）"""
        sql = f"""
        WITH period_activity AS (
            SELECT 
                f.volunteer_id,
                DATE_TRUNC('month', f.service_date) as period,
                COUNT(*) as activity_count,
                CASE 
                    WHEN COUNT(*) = 0 THEN '未参与'
                    WHEN COUNT(*) BETWEEN 1 AND 2 THEN '低参与度'
                    WHEN COUNT(*) BETWEEN 3 AND 6 THEN '中参与度'
                    WHEN COUNT(*) BETWEEN 7 AND 12 THEN '高参与度'
                    ELSE '超高参与度'
                END as activity_level
            FROM service_fact f
            WHERE f.service_date >= CURRENT_DATE - INTERVAL {time_periods} MONTHS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, period
        ),
        activity_transitions AS (
            SELECT 
                curr.volunteer_id,
                prev.activity_level as from_level,
                curr.activity_level as to_level,
                prev.period as from_period,
                curr.period as to_period
            FROM period_activity curr
            JOIN period_activity prev 
                ON curr.volunteer_id = prev.volunteer_id 
                AND curr.period = prev.period + INTERVAL 1 MONTH
            WHERE prev.activity_level != curr.activity_level
        )
        SELECT 
            from_level,
            to_level,
            COUNT(*) as transition_count,
            COUNT(DISTINCT volunteer_id) as volunteer_count
        FROM activity_transitions
        GROUP BY from_level, to_level
        ORDER BY transition_count DESC
        """
        return self.con.execute(sql).df()

    def query_seasonal_service_flow(self) -> pd.DataFrame:
        """查询季节性事工流动模式（用于桑基图）"""
        sql = """
        WITH seasonal_services AS (
            SELECT 
                f.volunteer_id,
                f.service_type_id,
                CASE d.quarter
                    WHEN 1 THEN '第一季度 (1-3月)'
                    WHEN 2 THEN '第二季度 (4-6月)'
                    WHEN 3 THEN '第三季度 (7-9月)'
                    WHEN 4 THEN '第四季度 (10-12月)'
                END as season,
                d.quarter,
                COUNT(*) as service_count
            FROM service_fact f
            JOIN date_dim d ON f.service_date = d.date
            WHERE f.service_date >= CURRENT_DATE - INTERVAL 2 YEARS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, f.service_type_id, d.quarter
        ),
        dominant_seasonal_service AS (
            SELECT 
                volunteer_id,
                season,
                quarter,
                service_type_id,
                service_count,
                ROW_NUMBER() OVER (PARTITION BY volunteer_id, season ORDER BY service_count DESC) as rn
            FROM seasonal_services
        ),
        seasonal_transitions AS (
            SELECT 
                curr.volunteer_id,
                prev.season as from_season,
                curr.season as to_season,
                prev.service_type_id as from_service,
                curr.service_type_id as to_service
            FROM dominant_seasonal_service curr
            JOIN dominant_seasonal_service prev 
                ON curr.volunteer_id = prev.volunteer_id 
                AND curr.quarter = (prev.quarter % 4) + 1
            WHERE curr.rn = 1 AND prev.rn = 1
        )
        SELECT 
            from_season || ' → ' || from_service as source,
            to_season || ' → ' || to_service as target,
            COUNT(*) as flow_count,
            COUNT(DISTINCT volunteer_id) as volunteer_count
        FROM seasonal_transitions
        GROUP BY source, target
        HAVING COUNT(*) >= 2  -- 至少2个同工有此流动
        ORDER BY flow_count DESC
        """
        return self.con.execute(sql).df()

    def query_experience_progression_sankey(self) -> pd.DataFrame:
        """查询同工经验积累和进阶路径（用于桑基图）"""
        sql = """
        WITH volunteer_experience AS (
            SELECT 
                f.volunteer_id,
                f.service_type_id,
                COUNT(*) as total_services,
                MIN(f.service_date) as first_service,
                MAX(f.service_date) as last_service,
                CASE 
                    WHEN COUNT(*) BETWEEN 1 AND 5 THEN '新手'
                    WHEN COUNT(*) BETWEEN 6 AND 15 THEN '熟练'
                    WHEN COUNT(*) BETWEEN 16 AND 30 THEN '专家'
                    ELSE '资深'
                END as experience_level
            FROM service_fact f
            WHERE f.service_date >= CURRENT_DATE - INTERVAL 18 MONTHS
              AND f.service_date <= CURRENT_DATE
            GROUP BY f.volunteer_id, f.service_type_id
        ),
        service_combinations AS (
            SELECT 
                volunteer_id,
                STRING_AGG(service_type_id || '(' || experience_level || ')', ', ' ORDER BY total_services DESC) as service_profile,
                COUNT(DISTINCT service_type_id) as service_diversity,
                SUM(total_services) as total_all_services
            FROM volunteer_experience
            GROUP BY volunteer_id
        ),
        diversity_categories AS (
            SELECT 
                volunteer_id,
                service_profile,
                CASE 
                    WHEN service_diversity = 1 THEN '专精型'
                    WHEN service_diversity = 2 THEN '双技能型'
                    WHEN service_diversity >= 3 THEN '多才型'
                    ELSE '其他'
                END as volunteer_type,
                CASE 
                    WHEN total_all_services BETWEEN 1 AND 10 THEN '初级贡献'
                    WHEN total_all_services BETWEEN 11 AND 25 THEN '中级贡献'
                    WHEN total_all_services BETWEEN 26 AND 50 THEN '高级贡献'
                    ELSE '顶级贡献'
                END as contribution_level
            FROM service_combinations
        )
        SELECT 
            volunteer_type as source,
            contribution_level as target,
            COUNT(*) as volunteer_count,
            ROUND(AVG(LENGTH(service_profile) - LENGTH(REPLACE(service_profile, ',', '')) + 1), 1) as avg_skills
        FROM diversity_categories
        GROUP BY volunteer_type, contribution_level
        ORDER BY volunteer_count DESC
        """
        return self.con.execute(sql).df()