"""Load the Dunnhumby grocery CSVs into a DuckDB database file."""

from __future__ import annotations

import time
import zipfile
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_PATH = PROJECT_ROOT / "data" / "archive.zip"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "analytics.duckdb"

# (table, csv name). Load order keeps the small dimension tables first so a
# failure on the large fact tables is easy to spot.
TABLES: list[tuple[str, str]] = [
    ("product", "product.csv"),
    ("hh_demographic", "hh_demographic.csv"),
    ("campaign_desc", "campaign_desc.csv"),
    ("campaign_table", "campaign_table.csv"),
    ("coupon", "coupon.csv"),
    ("coupon_redempt", "coupon_redempt.csv"),
    ("transaction_data", "transaction_data.csv"),
    ("causal_data", "causal_data.csv"),
]

# Types are declared explicitly rather than sniffed: sniffing picks VARCHAR for
# causal_data.display / causal_data.mailer (alphanumeric codes, not numbers) and
# would get them wrong on a small sample.
COLUMNS: dict[str, dict[str, str]] = {
    "transaction_data": {
        "household_key": "BIGINT",
        "BASKET_ID": "BIGINT",
        "DAY": "INTEGER",
        "PRODUCT_ID": "BIGINT",
        "QUANTITY": "INTEGER",
        "SALES_VALUE": "DOUBLE",
        "STORE_ID": "INTEGER",
        "RETAIL_DISC": "DOUBLE",
        "TRANS_TIME": "INTEGER",
        "WEEK_NO": "INTEGER",
        "COUPON_DISC": "DOUBLE",
        "COUPON_MATCH_DISC": "DOUBLE",
    },
    "causal_data": {
        "PRODUCT_ID": "BIGINT",
        "STORE_ID": "INTEGER",
        "WEEK_NO": "INTEGER",
        "display": "VARCHAR",
        "mailer": "VARCHAR",
    },
    "hh_demographic": {
        "AGE_DESC": "VARCHAR",
        "MARITAL_STATUS_CODE": "VARCHAR",
        "INCOME_DESC": "VARCHAR",
        "HOMEOWNER_DESC": "VARCHAR",
        "HH_COMP_DESC": "VARCHAR",
        "HOUSEHOLD_SIZE_DESC": "VARCHAR",
        "KID_CATEGORY_DESC": "VARCHAR",
        "household_key": "BIGINT",
    },
    "campaign_desc": {
        "DESCRIPTION": "VARCHAR",
        "CAMPAIGN": "INTEGER",
        "START_DAY": "INTEGER",
        "END_DAY": "INTEGER",
    },
}


def _types_literal(table: str) -> str:
    """Render a DuckDB ``columns={...}`` struct literal for a table."""
    overrides = COLUMNS.get(table)
    if not overrides:
        return ""
    pairs = ", ".join(f"'{name}': '{sql_type}'" for name, sql_type in overrides.items())
    return f", columns={{{pairs}}}"


def extract_archive(force: bool = False) -> Path:
    """Unpack ``data/archive.zip`` into ``data/raw`` unless already done.

    DuckDB cannot read CSVs inside a zip archive (the ``zip`` extension is not
    available for this build), so extraction uses the stdlib.
    """
    if not ARCHIVE_PATH.exists():
        raise FileNotFoundError(f"missing archive: {ARCHIVE_PATH}")
    expected = {csv_name for _, csv_name in TABLES}
    if not force and expected.issubset({p.name for p in RAW_DIR.glob("*.csv")}):
        return RAW_DIR
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"extracting {ARCHIVE_PATH.name} -> {RAW_DIR.relative_to(PROJECT_ROOT)}")
    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        for member in archive.namelist():
            if member != Path(member).name:
                raise ValueError(f"unexpected path in archive: {member}")
            archive.extract(member, RAW_DIR)
    return RAW_DIR


def load(db_path: Path = DB_PATH, replace: bool = False) -> None:
    """Create the DuckDB file and populate it with one table per CSV."""
    raw_dir = extract_archive()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    loaded: list[tuple[str, int, float]] = []
    try:
        for table, csv_name in TABLES:
            csv_path = raw_dir / csv_name
            started = time.perf_counter()
            if replace:
                con.execute(f"DROP TABLE IF EXISTS {table}")
            types = _types_literal(table)
            con.execute(
                f"CREATE TABLE {table} AS "
                f"SELECT * FROM read_csv('{csv_path.as_posix()}', "
                f"header=true, sample_size=-1, null_padding=true{types})"
            )
            rows = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            elapsed = time.perf_counter() - started
            loaded.append((table, rows, elapsed))
            print(f"  {table:<20} {rows:>12,} rows  {elapsed:6.1f}s")
    finally:
        con.close()

    total_rows = sum(rows for _, rows, _ in loaded)
    print(f"\nloaded {len(loaded)} tables, {total_rows:,} rows -> {db_path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    load()


if __name__ == "__main__":
    main()