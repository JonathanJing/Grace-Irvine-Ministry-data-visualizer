from __future__ import annotations

import yaml
import pandas as pd
from pathlib import Path
from typing import Optional

from storage.duckdb_store import DuckDBStore, DuckDBConfig


def _load_config() -> dict:
    cfg_path = Path("configs/config.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_store() -> DuckDBStore:
    cfg = _load_config()
    db_path = cfg.get("storage", {}).get("duckdb_path", "data/ministry.duckdb")
    return DuckDBStore(DuckDBConfig(db_path=db_path))


def load_aggregations(granularity: str = "month") -> Optional[pd.DataFrame]:
    store = _get_store()
    try:
        df = store.query_aggregation(granularity)
    except Exception:
        return None
    cfg = _load_config()
    include = cfg.get("stats", {}).get("include_service_types")
    if include and not df.empty and "service_type_id" in df.columns:
        df = df[df["service_type_id"].isin(include)]
    return df


def load_participants_table(granularity: str = "month") -> Optional[pd.DataFrame]:
    store = _get_store()
    try:
        df = store.query_participants_table(granularity)
    except Exception:
        return None
    cfg = _load_config()
    include = cfg.get("stats", {}).get("include_service_types")
    if include and not df.empty and "service_type_id" in df.columns:
        df = df[df["service_type_id"].isin(include)]
    return df


def list_volunteers() -> list[str]:
    store = _get_store()
    df = store.query_distinct_volunteers()
    return df["volunteer"].tolist()


def volunteer_trend(volunteer: str, granularity: str = "month") -> Optional[pd.DataFrame]:
    store = _get_store()
    try:
        return store.query_volunteer_trend(volunteer, granularity)
    except Exception:
        return None


def volunteer_service_types(volunteer: str, granularity: str = "month") -> Optional[pd.DataFrame]:
    store = _get_store()
    try:
        df = store.query_volunteer_service_types(volunteer, granularity)
    except Exception:
        return None
    cfg = _load_config()
    include = cfg.get("stats", {}).get("include_service_types")
    if include and not df.empty and "service_type_id" in df.columns:
        df = df[df["service_type_id"].isin(include)]
    return df


def load_raw_data() -> Optional[pd.DataFrame]:
    """加载原始数据"""
    store = _get_store()
    try:
        return store.query_raw_data()
    except Exception:
        return None


def load_volunteer_stats_recent_weeks(weeks: int = 4) -> Optional[pd.DataFrame]:
    """加载最近N周的同工事工统计"""
    store = _get_store()
    try:
        df = store.query_volunteer_stats_recent_weeks(weeks)
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的记录
            df = df[df["service_types"].str.contains("|".join(include), na=False)]
        return df
    except Exception:
        return None


def load_volunteer_stats_recent_quarter() -> Optional[pd.DataFrame]:
    """加载最近一季度的同工事工统计"""
    store = _get_store()
    try:
        df = store.query_volunteer_stats_recent_quarter()
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的记录
            df = df[df["service_types"].str.contains("|".join(include), na=False)]
        return df
    except Exception:
        return None




def load_volunteer_count_trend(granularity: str = "month") -> Optional[pd.DataFrame]:
    """加载同工总人数趋势"""
    store = _get_store()
    try:
        return store.query_volunteer_count_trend(granularity)
    except Exception:
        return None


def load_cumulative_participation(granularity: str = "month") -> Optional[pd.DataFrame]:
    """加载累计参与次数趋势"""
    store = _get_store()
    try:
        return store.query_cumulative_participation(granularity)
    except Exception:
        return None



def load_volunteer_join_leave_analysis(granularity: str = "month") -> Optional[pd.DataFrame]:
    """加载同工新增/离开分析"""
    store = _get_store()
    try:
        return store.query_volunteer_join_leave_analysis(granularity)
    except Exception:
        return None







def load_period_comparison_stats(weeks: int = 4) -> Optional[pd.DataFrame]:
    """加载不同时期的同工事工环比变化"""
    store = _get_store()
    try:
        return store.query_period_comparison_stats(weeks)
    except Exception:
        return None


# =============================================================================
# 桑基图数据加载函数
# =============================================================================

def load_service_transitions_for_sankey(months: int = 6) -> Optional[pd.DataFrame]:
    """加载同工在不同事工类型之间的转换数据（用于桑基图）"""
    store = _get_store()
    try:
        df = store.query_service_transitions_for_sankey(months)
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的转换
            df = df[
                (df["from_service"].isin(include)) & 
                (df["to_service"].isin(include))
            ]
        return df
    except Exception:
        return None


def load_volunteer_journey_sankey(time_periods: int = 6) -> Optional[pd.DataFrame]:
    """加载同工参与度的演变历程（用于桑基图）"""
    store = _get_store()
    try:
        return store.query_volunteer_journey_sankey(time_periods)
    except Exception:
        return None


def load_seasonal_service_flow() -> Optional[pd.DataFrame]:
    """加载季节性事工流动模式（用于桑基图）"""
    store = _get_store()
    try:
        df = store.query_seasonal_service_flow()
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的季节性流动
            df = df[
                df["source"].str.contains("|".join(include), na=False) |
                df["target"].str.contains("|".join(include), na=False)
            ]
        return df
    except Exception:
        return None


def load_experience_progression_sankey() -> Optional[pd.DataFrame]:
    """加载同工经验积累和进阶路径（用于桑基图）"""
    store = _get_store()
    try:
        return store.query_experience_progression_sankey()
    except Exception:
        return None


# =============================================================================
# 新增：月际事工流动桑基图数据加载函数
# =============================================================================

def load_monthly_ministry_flow(start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               strategy: str = 'most_frequent',
                               top_k_ministries: Optional[int] = None,
                               include_inactive: bool = True) -> Optional[pd.DataFrame]:
    """
    加载同工月际事工流动数据（用于桑基图）
    
    参数:
    - start_date: 开始日期 (YYYY-MM-DD格式)
    - end_date: 结束日期 (YYYY-MM-DD格式)
    - strategy: 主事工判定策略 ('most_frequent'最高频 或 'most_recent'最近一次)
    - top_k_ministries: 只保留前K个事工，其余归为"其他"
    - include_inactive: 是否包含"未参与"状态
    """
    store = _get_store()
    try:
        df = store.query_monthly_ministry_flow(
            start_date=start_date,
            end_date=end_date,
            strategy=strategy,
            top_k_ministries=top_k_ministries,
            include_inactive=include_inactive
        )
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的流动
            df = df[
                (df['from_ministry'].isin(include + ['未参与', '其他'])) & 
                (df['to_ministry'].isin(include + ['未参与', '其他']))
            ]
        return df
    except Exception:
        return None


def load_ministry_specific_flow(ministry_id: str,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    加载特定事工的进出流动数据
    
    参数:
    - ministry_id: 事工ID
    - start_date: 开始日期
    - end_date: 结束日期
    """
    store = _get_store()
    try:
        return store.query_ministry_specific_flow(ministry_id, start_date, end_date)
    except Exception:
        return None


def load_volunteer_ministry_path(volunteer_id: str,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    加载单个同工的事工路径
    
    参数:
    - volunteer_id: 同工ID
    - start_date: 开始日期
    - end_date: 结束日期
    """
    store = _get_store()
    try:
        return store.query_volunteer_ministry_path(volunteer_id, start_date, end_date)
    except Exception:
        return None


def get_available_ministries() -> list[str]:
    """获取所有可用的事工类型列表"""
    store = _get_store()
    try:
        sql = """
        SELECT DISTINCT service_type_id 
        FROM service_fact 
        ORDER BY service_type_id
        """
        df = store.con.execute(sql).df()
        return df['service_type_id'].tolist()
    except Exception:
        return []


def load_volunteer_ministry_flow_data(start_date: Optional[str] = None,
                                       end_date: Optional[str] = None,
                                       selected_volunteers: Optional[list] = None) -> Optional[pd.DataFrame]:
    """
    加载同工月际事工流动数据（为新桑基图设计）
    
    参数:
    - start_date: 开始日期 (YYYY-MM-DD格式)
    - end_date: 结束日期 (YYYY-MM-DD格式)
    - selected_volunteers: 选中的同工列表，None表示所有同工
    """
    store = _get_store()
    try:
        # 构建日期过滤条件
        date_filter = ""
        if start_date:
            date_filter += f" AND f.service_date >= '{start_date}'"
        if end_date:
            date_filter += f" AND f.service_date <= '{end_date}'"
        
        # 构建同工过滤条件
        volunteer_filter = ""
        if selected_volunteers:
            volunteer_list = "', '".join(selected_volunteers)
            volunteer_filter = f" AND f.volunteer_id IN ('{volunteer_list}')"
        
        sql = f"""
        WITH monthly_services AS (
            -- 统计每个同工每月在各事工的参与情况
            SELECT 
                f.volunteer_id,
                f.volunteer_id as volunteer_name,  -- 直接使用volunteer_id作为显示名称
                DATE_TRUNC('month', f.service_date) as year_month,
                f.service_type_id as ministry,
                COUNT(*) as service_count
            FROM service_fact f
            WHERE 1=1 {date_filter} {volunteer_filter}
            GROUP BY f.volunteer_id, DATE_TRUNC('month', f.service_date), f.service_type_id
        ),
        main_ministry AS (
            -- 确定每个同工每月的主事工（参与次数最多的）
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                ministry,
                service_count,
                ROW_NUMBER() OVER (
                    PARTITION BY volunteer_id, year_month 
                    ORDER BY service_count DESC, ministry
                ) as rn
            FROM monthly_services
        ),
        volunteer_monthly AS (
            -- 获取每个同工每月的主事工
            SELECT 
                volunteer_id,
                volunteer_name,
                year_month,
                ministry as main_ministry
            FROM main_ministry
            WHERE rn = 1
        ),
        flow_transitions AS (
            -- 计算相邻月份间的转换
            SELECT 
                curr.volunteer_name,
                STRFTIME(curr.year_month, '%Y-%m') as from_month,
                STRFTIME(next.year_month, '%Y-%m') as to_month,
                curr.main_ministry as from_ministry,
                next.main_ministry as to_ministry,
                1 as flow_intensity
            FROM volunteer_monthly curr
            JOIN volunteer_monthly next 
                ON curr.volunteer_id = next.volunteer_id
                AND next.year_month = DATE_TRUNC('month', curr.year_month + INTERVAL '1 month')
        )
        SELECT 
            volunteer_name,
            from_month,
            to_month,
            from_ministry,
            to_ministry,
            flow_intensity
        FROM flow_transitions
        ORDER BY volunteer_name, from_month
        """
        
        df = store.con.execute(sql).df()
        
        # 应用配置过滤
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty:
            # 过滤只包含指定服务类型的流动
            df = df[
                (df['from_ministry'].isin(include)) & 
                (df['to_ministry'].isin(include))
            ]
        
        return df
    except Exception:
        return None


