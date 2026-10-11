# AGENTS.md

## What this is

Notebook-first EDA of the Dunnhumby "Breakfast at the Frat" dataset: a weekly
store × SKU sales/promo panel (156 weeks, 79 store rows, 58 UPCs, ~525k transaction rows).
All analysis lives in `notebooks/`; `src/` is effectively unused (see *Repo state*).

## Commands

- Setup: `uv sync` (Python 3.14). Always invoke tooling as `uv run ...`, never bare
  `python`/`jupyter` — the venv is the only place deps exist.
- **Run notebooks from inside `notebooks/`**: `cd notebooks && uv run jupyter lab`.
  Every notebook hardcodes `DATA = Path("../data/dunnhumby - Breakfast at the Frat.xlsx")`,
  which resolves against the *current working directory*, not the notebook location.
  Launching Jupyter from the repo root silently breaks every data cell.
- `uv run` works from `notebooks/` too (uv walks up to find `pyproject.toml`).

## Data

- Source: <https://www.kaggle.com/datasets/frtgnn/dunnhumby-the-complete-journey>.
- `*.xlsx` is gitignored, so a fresh clone has **no data**. Single file, name contains
  spaces — must match exactly.
- Sheets: `Glossary`, `dh Store Lookup`, `dh Products Lookup`, `dh Transaction Data`.
- Parsing quirks — get these wrong and cells fail or silently misread:
  - The three data sheets have a title banner on row 1 → `header=1`. `Glossary` uses `header=3`.
  - `Glossary` also produces a junk `Unnamed: 3` column → `.drop(columns=["Unnamed: 3"])`.
  - `dh Transaction Data` takes ~30 s to parse. Read it once per session, not per cell.
- `dh Store Lookup` has 79 rows for 77 stores: `STORE_ID` 4503 and 17627 each appear twice
  with conflicting `SEG_VALUE_NAME`. Always `stores.drop_duplicates("STORE_ID")` before
  mapping labels onto or joining with transactions.
- Already-triaged data issues (do not re-derive): `PRICE`/`BASE_PRICE` missing or
  non-positive on 209 rows (0.04%); 3 of 58 products never appear in transactions;
  `PARKING_SPACE_QTY` missing on 52/79 store rows. See the findings cell at the end of
  `notebooks/0_prelim_analysis.ipynb`.
- pandas is **3.0.x**, not 2.x: string columns default to the new `str` dtype and
  copy-on-write is on. Check old idioms before reusing them.

## Notebook conventions

- Files are numbered by analysis stage: `0_prelim_analysis`, `1_distribution_analysis`.
  `EDA.ipynb` is scope only (question list, no code) — the top-level analysis lives there.
- Each notebook opens with markdown stating its purpose and the questions it answers, and
  closes with a markdown findings/takeaways cell.
- Numeric claims in prose must be printed by a code cell so they stay checkable against the
  data — that is the explicit standard stated in `1_distribution_analysis.ipynb`.
- Outputs are committed (all 15 code cells in `1_distribution_analysis.ipynb` carry
  outputs); `0_prelim_analysis.ipynb` is clean. Don't strip outputs unless asked.
- Reuse the existing preamble and palette (seaborn `whitegrid`, explicit `plt.rcParams`,
  `pd.set_option` float format, `max_columns=50`, fixed promo/no-promo colors) instead of
  inventing new defaults.

## Repo state — verify before relying on it

- `src/ecommerce_analysis/__init__.py` imports `ecommerce_analysis.load`, which was
  deleted in commit `4066928`. `import ecommerce_analysis` raises `ModuleNotFoundError`.
  The package is unusable — don't build on it, and don't silently "fix" it.
- `README.md` documents a DuckDB pipeline (`uv run load-data`, `data/archive.zip`,
  `data/raw/`, `data/analytics.duckdb`). All removed in `4066928`: DuckDB is not a
  dependency, there is no `[project.scripts]`, and `data/archive.zip` does not exist.
  Treat the README's Setup / Load / Query / Export sections as historical.
- No tests, no linter or formatter config, no CI. Verification = re-run the notebook and
  check the printed numbers against the prose claims.
- Commits use one-line conventional-commit English (`feat: add scipy dependency`).