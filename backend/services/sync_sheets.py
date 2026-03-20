"""
sync_sheets.py — Sync Google Sheets → Neon PostgreSQL.
Adaptado para Santa Cruz FC — Série C.
Puxa CSVs públicos do Google Sheets e faz upsert no banco.
"""

import os
import io
import logging
import urllib.request
from typing import Dict

import pandas as pd

from services.database import init_scouting_tables, upsert_sheet_data, get_sync_status

logger = logging.getLogger(__name__)

# ── Planilhas do Santa Cruz FC (CSV público) ──────────────────────────
SHEET_CADASTRO_URL = os.environ.get(
    "SHEET_CADASTRO_URL",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc74viAa9e3hBoS6HqM7wU4iOM9jq4Jt9JoJvdNH8ahKIQr_3dcdFj9NbXIeYFQw/pub?output=csv"
)

SHEET_FILTROS_URL = os.environ.get(
    "SHEET_FILTROS_URL",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNdzRzcdNsGdRv3qQ2sud5trZLSCEl5mB0HLfGVqVMITrq1YdW7nKDKTQDAmQbqSYQkDzy69haWxlf/pub?output=csv"
)

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")

SHEET_URLS = {
    "cadastro": SHEET_CADASTRO_URL,
    "oferecidos": SHEET_FILTROS_URL,
}

SHEET_NAMES = {
    "analises": "Análises",
    "oferecidos": "Oferecidos",
    "skillcorner": "SkillCorner",
    "wyscout": "WyScout",
}


def _download_csv_public(url: str, label: str) -> pd.DataFrame:
    """Download CSV público direto do Google Sheets."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(raw), dtype=str, na_values=["", "-", "N/A", "nan"])
        logger.info("Downloaded '%s': %d rows x %d cols", label, len(df), len(df.columns))
        return df
    except Exception as e:
        logger.error("Failed to download '%s': %s", label, e)
        return pd.DataFrame()


def _download_sheet_csv(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    """Download a single Google Sheet tab as CSV → DataFrame (via gviz)."""
    import urllib.parse
    encoded = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded}"
    return _download_csv_public(url, sheet_name)


def sync_all_sheets() -> Dict[str, int]:
    """Sync all sheets → Neon PostgreSQL."""
    init_scouting_tables()
    results = {}

    # 1. Sync planilhas públicas diretas (cadastro + filtros)
    for key, url in SHEET_URLS.items():
        try:
            df = _download_csv_public(url, key)
            count = upsert_sheet_data(key, df)
            results[key] = count
        except Exception as e:
            logger.error("Sync failed for '%s': %s", key, e)
            results[key] = -1

    # 2. Sync abas gviz (se GOOGLE_SHEET_ID configurado)
    if GOOGLE_SHEET_ID:
        for key, sheet_name in SHEET_NAMES.items():
            if key in results:
                continue
            try:
                df = _download_sheet_csv(GOOGLE_SHEET_ID, sheet_name)
                count = upsert_sheet_data(key, df)
                results[key] = count
            except Exception as e:
                logger.error("Sync failed for '%s': %s", key, e)
                results[key] = -1

    logger.info("Sync complete: %s", results)
    return results


def sync_single_sheet(sheet_key: str) -> int:
    """Sync a single sheet by key."""
    init_scouting_tables()

    if sheet_key in SHEET_URLS:
        df = _download_csv_public(SHEET_URLS[sheet_key], sheet_key)
        return upsert_sheet_data(sheet_key, df)

    if GOOGLE_SHEET_ID:
        sheet_name = SHEET_NAMES.get(sheet_key)
        if not sheet_name:
            raise ValueError(f"Unknown sheet key: {sheet_key}")
        df = _download_sheet_csv(GOOGLE_SHEET_ID, sheet_name)
        return upsert_sheet_data(sheet_key, df)

    raise ValueError(f"No URL or SHEET_ID configured for: {sheet_key}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = sync_all_sheets()
    print(f"Sync results: {results}")
    status = get_sync_status()
    print(f"Sync status: {status}")
