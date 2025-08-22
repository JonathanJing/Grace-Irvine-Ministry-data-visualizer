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
    return df


