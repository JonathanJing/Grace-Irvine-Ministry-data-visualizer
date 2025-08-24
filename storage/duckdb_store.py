from __future__ import annotations

import os
import threading
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
    # Class-level lock to prevent concurrent schema initialization
    _schema_lock = threading.Lock()
    _initialized_dbs = set()
    
    def __init__(self, cfg: DuckDBConfig) -> None:
        os.makedirs(os.path.dirname(cfg.db_path), exist_ok=True)
        self.cfg = cfg
        self.con = duckdb.connect(cfg.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        # Use class-level lock to prevent concurrent schema initialization
        with self._schema_lock:
            # Check if this database has already been initialized
            db_path = os.path.abspath(self.cfg.db_path)
            if db_path in self._initialized_dbs:
                return
                
            # Execute schema creation with explicit transaction and error handling
            try:
                self.con.begin()
                # Check if tables already exist to avoid unnecessary operations
                tables_exist = self.con.execute("""
                    SELECT COUNT(*) as count FROM information_schema.tables 
                    WHERE table_name IN ('volunteer', 'volunteer_alias', 'service_type', 'date_dim', 'source_row', 'service_fact')
                """).fetchone()[0]
                
                # Only create tables if they don't all exist
                if tables_exist < 6:
                    # Split SCHEMA_SQL into individual statements to avoid conflicts
                    statements = [stmt.strip() for stmt in SCHEMA_SQL.split(';') if stmt.strip()]
                    for statement in statements:
                        if statement:
                            self.con.execute(statement)
                self.con.commit()
                # Mark this database as initialized
                self._initialized_dbs.add(db_path)
            except Exception as e:
                # If there's a conflict, rollback and try to continue
                # (tables might already exist from another process)
                try:
                    self.con.rollback()
                except:
                    pass
                # Verify that essential tables exist
                try:
                    self.con.execute("SELECT 1 FROM volunteer LIMIT 1")
                    # If we can access the table, mark as initialized
                    self._initialized_dbs.add(db_path)
                except:
                    # If tables don't exist, re-raise the original error
                    raise e

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

    def query_monthly_ministry_flow(self, 
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    strategy: str = 'most_frequent',
                                    top_k_ministries: Optional[int] = None,
                                    include_inactive: bool = True) -> pd.DataFrame:
        """
        查询同工月际事工流动数据（用于桑基图）
        
        参数:
        - start_date: 开始日期 (YYYY-MM-DD格式)
        - end_date: 结束日期 (YYYY-MM-DD格式)
        - strategy: 主事工判定策略 ('most_frequent'最高频 或 'most_recent'最近一次)
        - top_k_ministries: 只保留前K个事工，其余归为"其他"
        - include_inactive: 是否包含"未参与"状态
        """
        
        # 日期条件
        date_filter = ""
        if start_date:
            date_filter += f" AND f.service_date >= '{start_date}'"
        if end_date:
            date_filter += f" AND f.service_date <= '{end_date}'"
        
        # 主事工判定SQL
        if strategy == 'most_frequent':
            main_ministry_logic = """
                -- 最高频策略：选择每月次数最多的事工
                ROW_NUMBER() OVER (
                    PARTITION BY volunteer_id, year_month 
                    ORDER BY service_count DESC, service_type_id
                ) as rn
            """
        else:  # most_recent
            main_ministry_logic = """
                -- 最近一次策略：选择每月最后一次的事工
                ROW_NUMBER() OVER (
                    PARTITION BY volunteer_id, year_month 
                    ORDER BY last_service_date DESC, service_type_id
                ) as rn
            """
        
        sql = f"""
        WITH monthly_services AS (
            -- 统计每个同工每月在各事工的参与情况
            SELECT 
                f.volunteer_id,
                v.display_name as volunteer_name,
                DATE_TRUNC('month', f.service_date) as year_month,
                f.service_type_id,
                COUNT(*) as service_count,
                MAX(f.service_date) as last_service_date
            FROM service_fact f
            JOIN volunteer v ON f.volunteer_id = v.volunteer_id
            WHERE 1=1 {date_filter}
            GROUP BY f.volunteer_id, v.display_name, DATE_TRUNC('month', f.service_date), f.service_type_id
        ),
        main_ministry AS (
            -- 确定每个同工每月的主事工
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                service_type_id,
                service_count,
                {main_ministry_logic}
            FROM monthly_services
        ),
        volunteer_monthly AS (
            -- 获取每个同工每月的主事工
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                service_type_id as main_ministry,
                service_count
            FROM main_ministry
            WHERE rn = 1
        ),
        all_months AS (
            -- 生成完整的月份序列
            SELECT DISTINCT DATE_TRUNC('month', service_date) as year_month
            FROM service_fact
            WHERE 1=1 {date_filter}
            ORDER BY year_month
        ),
        volunteer_full AS (
            -- 补充未参与的月份
            SELECT DISTINCT
                v.volunteer_id,
                v.display_name as volunteer_name,
                m.year_month,
                COALESCE(vm.main_ministry, '未参与') as main_ministry
            FROM (
                SELECT DISTINCT volunteer_id, display_name 
                FROM volunteer
            ) v
            CROSS JOIN all_months m
            LEFT JOIN volunteer_monthly vm 
                ON v.volunteer_id = vm.volunteer_id 
                AND m.year_month = vm.year_month
        ),
        transitions AS (
            -- 计算相邻月份间的转换
            SELECT 
                curr.volunteer_id,
                curr.volunteer_name,
                curr.year_month as from_month,
                curr.main_ministry as from_ministry,
                next.year_month as to_month,
                next.main_ministry as to_ministry,
                -- 构造节点标识
                STRFTIME(curr.year_month, '%Y-%m') || '_' || curr.main_ministry as source,
                STRFTIME(next.year_month, '%Y-%m') || '_' || next.main_ministry as target
            FROM volunteer_full curr
            JOIN volunteer_full next 
                ON curr.volunteer_id = next.volunteer_id
                AND next.year_month = DATE_TRUNC('month', curr.year_month + INTERVAL '1 month')
        )
        -- 聚合转换数据
        SELECT 
            source,
            target,
            from_month,
            to_month,
            from_ministry,
            to_ministry,
            COUNT(DISTINCT volunteer_id) as flow_count,
            STRING_AGG(DISTINCT volunteer_name, ', ' ORDER BY volunteer_name) as volunteers_list
        FROM transitions
        {"WHERE from_ministry != '未参与' OR to_ministry != '未参与'" if not include_inactive else ""}
        GROUP BY source, target, from_month, to_month, from_ministry, to_ministry
        HAVING COUNT(DISTINCT volunteer_id) > 0
        ORDER BY from_month, flow_count DESC
        """
        
        df = self.con.execute(sql).df()
        
        # 如果需要限制Top-K事工
        if top_k_ministries and not df.empty:
            # 统计各事工总参与度
            ministry_counts = {}
            for _, row in df.iterrows():
                ministry_counts[row['from_ministry']] = ministry_counts.get(row['from_ministry'], 0) + row['flow_count']
                ministry_counts[row['to_ministry']] = ministry_counts.get(row['to_ministry'], 0) + row['flow_count']
            
            # 保留Top-K和特殊事工
            top_ministries = sorted(ministry_counts.items(), key=lambda x: x[1], reverse=True)[:top_k_ministries]
            keep_ministries = set([m[0] for m in top_ministries]) | {'未参与'}
            
            # 重新标记非Top-K事工为"其他"
            df['from_ministry'] = df['from_ministry'].apply(lambda x: x if x in keep_ministries else '其他')
            df['to_ministry'] = df['to_ministry'].apply(lambda x: x if x in keep_ministries else '其他')
            
            # 重新构造source和target
            df['source'] = df.apply(lambda r: f"{r['from_month'].strftime('%Y-%m')}_{r['from_ministry']}", axis=1)
            df['target'] = df.apply(lambda r: f"{r['to_month'].strftime('%Y-%m')}_{r['to_ministry']}", axis=1)
            
            # 重新聚合
            df = df.groupby(['source', 'target', 'from_month', 'to_month', 'from_ministry', 'to_ministry']).agg({
                'flow_count': 'sum',
                'volunteers_list': lambda x: ', '.join(set(', '.join(x).split(', ')))
            }).reset_index()
        
        return df

    def query_ministry_specific_flow(self, 
                                     ministry_id: str,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询特定事工的进出流动数据
        
        参数:
        - ministry_id: 事工ID
        - start_date: 开始日期
        - end_date: 结束日期
        """
        
        # 获取完整流动数据
        full_flow = self.query_monthly_ministry_flow(start_date, end_date)
        
        if full_flow.empty:
            return pd.DataFrame()
        
        # 筛选涉及指定事工的流动
        ministry_flow = full_flow[
            (full_flow['from_ministry'] == ministry_id) | 
            (full_flow['to_ministry'] == ministry_id)
        ]
        
        return ministry_flow

    def query_volunteer_ministry_path(self, 
                                      volunteer_id: str,
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询单个同工的事工路径
        
        参数:
        - volunteer_id: 同工ID
        - start_date: 开始日期
        - end_date: 结束日期
        """
        
        # 日期条件
        date_filter = ""
        if start_date:
            date_filter += f" AND f.service_date >= '{start_date}'"
        if end_date:
            date_filter += f" AND f.service_date <= '{end_date}'"
        
        sql = f"""
        WITH monthly_services AS (
            -- 统计指定同工每月在各事工的参与情况
            SELECT 
                f.volunteer_id,
                v.display_name as volunteer_name,
                DATE_TRUNC('month', f.service_date) as year_month,
                f.service_type_id,
                COUNT(*) as service_count,
                MAX(f.service_date) as last_service_date
            FROM service_fact f
            JOIN volunteer v ON f.volunteer_id = v.volunteer_id
            WHERE f.volunteer_id = '{volunteer_id}' {date_filter}
            GROUP BY f.volunteer_id, v.display_name, DATE_TRUNC('month', f.service_date), f.service_type_id
        ),
        main_ministry AS (
            -- 确定每月的主事工（最高频）
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                service_type_id,
                service_count,
                ROW_NUMBER() OVER (
                    PARTITION BY year_month 
                    ORDER BY service_count DESC, service_type_id
                ) as rn
            FROM monthly_services
        ),
        volunteer_path AS (
            -- 获取事工路径
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                service_type_id as main_ministry,
                service_count,
                LAG(service_type_id) OVER (ORDER BY year_month) as prev_ministry,
                LEAD(service_type_id) OVER (ORDER BY year_month) as next_ministry
            FROM main_ministry
            WHERE rn = 1
        )
        SELECT 
            volunteer_name,
            year_month,
            main_ministry,
            service_count,
            prev_ministry,
            next_ministry,
            CASE 
                WHEN prev_ministry IS NULL THEN '开始'
                WHEN prev_ministry != main_ministry THEN '转换'
                ELSE '继续'
            END as status
        FROM volunteer_path
        ORDER BY year_month
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