from __future__ import annotations

import yaml
from pathlib import Path

import pandas as pd

from ingest.sheets_client import read_range_a_to_u
from ingest.transform import rows_to_facts
from storage.duckdb_store import DuckDBStore, DuckDBConfig


def _load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_ingest() -> None:
    values = read_range_a_to_u()
    facts = rows_to_facts(values)
    cfg = _load_config()
    store = DuckDBStore(DuckDBConfig(cfg["storage"]["duckdb_path"]))
    store.upsert_date_dim(pd.to_datetime(facts["service_date"]))
    store.insert_facts(facts)


if __name__ == "__main__":
    run_ingest()


