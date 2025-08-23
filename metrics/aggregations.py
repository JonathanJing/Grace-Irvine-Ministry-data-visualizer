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


def load_volunteer_weekly_trend(weeks: int = 12) -> Optional[pd.DataFrame]:
    """加载最近N周的每周同工事工趋势"""
    store = _get_store()
    try:
        return store.query_volunteer_weekly_trend(weeks)
    except Exception:
        return None


def load_service_type_distribution_recent(weeks: int = 4) -> Optional[pd.DataFrame]:
    """加载最近N周各服务类型的分布情况"""
    store = _get_store()
    try:
        df = store.query_service_type_distribution_recent(weeks)
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty and "service_type_id" in df.columns:
            df = df[df["service_type_id"].isin(include)]
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


def load_individual_volunteer_trends(top_n: int = 10, weeks: int = 12) -> Optional[pd.DataFrame]:
    """加载前N名同工的个人事工次数趋势"""
    store = _get_store()
    try:
        return store.query_individual_volunteer_trends(top_n, weeks)
    except Exception:
        return None


def load_volunteer_join_leave_analysis(granularity: str = "month") -> Optional[pd.DataFrame]:
    """加载同工新增/离开分析"""
    store = _get_store()
    try:
        return store.query_volunteer_join_leave_analysis(granularity)
    except Exception:
        return None


def load_participation_distribution(weeks: int = 12) -> Optional[pd.DataFrame]:
    """加载参与次数分布（直方图数据）"""
    store = _get_store()
    try:
        return store.query_participation_distribution(weeks)
    except Exception:
        return None


def load_service_stats_for_boxplot(weeks: int = 12) -> Optional[pd.DataFrame]:
    """加载同工服务次数统计（用于箱型图）"""
    store = _get_store()
    try:
        return store.query_service_stats_for_boxplot(weeks)
    except Exception:
        return None


def load_volunteer_service_network(min_services: int = 3) -> Optional[pd.DataFrame]:
    """加载同工-服务类型网络关系数据"""
    store = _get_store()
    try:
        df = store.query_volunteer_service_network(min_services)
        cfg = _load_config()
        include = cfg.get("stats", {}).get("include_service_types")
        if include and not df.empty and "service_type_id" in df.columns:
            df = df[df["service_type_id"].isin(include)]
        return df
    except Exception:
        return None


def load_period_comparison_stats(weeks: int = 4) -> Optional[pd.DataFrame]:
    """加载不同时期的同工事工环比变化"""
    store = _get_store()
    try:
        return store.query_period_comparison_stats(weeks)
    except Exception:
        return None


