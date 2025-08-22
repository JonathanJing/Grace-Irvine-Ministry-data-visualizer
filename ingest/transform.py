from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import yaml
from dateutil import parser
from datetime import datetime, timezone


@dataclass
class RoleColumn:
    key: str
    service_type: str


def load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_name(name: str) -> str:
    if name is None:
        return ""
    return str(name).strip().replace("\u3000", " ")


def parse_date(cell: str) -> pd.Timestamp | None:
    if not cell:
        return None
    try:
        dt = parser.parse(str(cell))
        return pd.Timestamp(dt.date())
    except Exception:
        return None


def compute_checksum(cells: List[str]) -> str:
    text = "|".join([str(c or "").strip() for c in cells])
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def rows_to_facts(values: List[List[str]]) -> pd.DataFrame:
    cfg = load_config()
    date_col_letter = cfg["columns"]["date"]
    role_defs = [RoleColumn(**r) for r in cfg["columns"]["roles"]]
    sheet_name = cfg["sheet_name"]
    spreadsheet_id = cfg["spreadsheet_id"]

    letter_to_index = {chr(ord('A') + i): i for i in range(26)}
    date_idx = letter_to_index[date_col_letter]
    role_indices = [(letter_to_index[r.key], r.service_type) for r in role_defs]

    facts: List[Dict[str, str]] = []
    ingested_at = pd.Timestamp(datetime.now(timezone.utc))

    for i, row in enumerate(values):
        if i == 0:
            # Assume header row; skip if it contains non-date in A
            pass
        # Ensure row has enough columns
        max_idx = max([date_idx] + [idx for idx, _ in role_indices])
        if len(row) <= max_idx:
            continue
        service_date = parse_date(row[date_idx])
        if service_date is None:
            continue
        checksum = compute_checksum(row[: max_idx + 1])
        source_row_id = f"{spreadsheet_id}:{sheet_name}:{i+1}:{checksum}"

        for idx, service_type in role_indices:
            name_cell = row[idx] if idx < len(row) else ""
            name = normalize_name(name_cell)
            if not name:
                continue
            volunteer_id = name  # simple key; could be hashed or alias-resolved later
            fact_id = f"{service_date}:{service_type}:{volunteer_id}:{i+1}"
            facts.append(
                {
                    "fact_id": fact_id,
                    "volunteer_id": volunteer_id,
                    "service_type_id": service_type,
                    "service_date": service_date,
                    "source_row_id": source_row_id,
                    "ingested_at": ingested_at,
                }
            )

    if not facts:
        return pd.DataFrame(
            columns=[
                "fact_id",
                "volunteer_id",
                "service_type_id",
                "service_date",
                "source_row_id",
                "ingested_at",
            ]
        )
    df = pd.DataFrame(facts)
    return df


