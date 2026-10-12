# AGENTS.md

## What this is

Notebook-first EDA of the Dunnhumby "Breakfast at the Frat" dataset: a weekly
store × SKU sales/promo panel (156 weeks, 524,950 transaction rows). All analysis lives in
`notebooks/`; `src/` is effectively unused (see *Repo state*).

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
- Panel vs lookup dimensions differ — do not conflate them. Transactions cover **77 stores ×
  55 UPCs**; the lookup sheets carry 77 unique store IDs (79 rows) and 58 UPCs. The "3 of 58
  products never appear" and store-row-count items below are lookup-vs-facts mismatches, not
  data errors.
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
  data — that is the explicit standard stated in `1_distribution_analysis.ipynb`. An eyeballed
  reading is acceptable only when labelled as one (e.g. "raw plot approximation"); an
  unexplained statistic is not.
- **No notebook carries committed outputs.** Every code cell in both notebooks is
  `"outputs": []` with `execution_count: null` — 14 cells in `1_distribution_analysis.ipynb`,
  17 in `0_prelim_analysis.ipynb`, true in HEAD as well as the working tree. So checking a prose
  claim means re-running the cell, not reading the file. Don't strip or add outputs unasked;
  committing this notebook's 6 figures is a size decision for the user, not a default.
- `1_distribution_analysis.ipynb` closes with `## 6. Conclusion`: one findings paragraph per
  opening question, then an `**Open threads.**` bullet list carrying forward threads raised
  earlier in the prose. Open threads must not introduce a number no cell prints.
- Several cells are the author's own prose rather than generated text. Preserve their voice and
  register when editing nearby — don't silently homogenise their wording or punctuation.
- Reuse the existing preamble and palette (seaborn `whitegrid`, explicit `plt.rcParams`,
  `pd.set_option` float format, `max_columns=50`, fixed promo/no-promo colors) instead of
  inventing new defaults.

## Repo state — verify before relying on it

- `src/ecommerce_analysis/__init__.py` imports `ecommerce_analysis.load`, which was
  deleted in commit `4066928`. `import ecommerce_analysis` raises `ModuleNotFoundError`.
  The package is unusable — don't build on it, and don't silently "fix" it.
- A stale `src/ecommerce_analysis/__pycache__/load.cpython-314.pyc` survives from that deleted
  module (untracked, gitignored). Verified: it does **not** revive the import, which still
  raises `ModuleNotFoundError`. Don't read its presence as evidence the module exists.
- `README.md` documents a DuckDB pipeline (`uv run load-data`, `data/archive.zip`,
  `data/raw/`, `data/analytics.duckdb`). All removed in `4066928`: DuckDB is not a
  dependency, there is no `[project.scripts]`, and `data/archive.zip` does not exist.
  Treat the README's Setup / Load / Query / Export sections as historical.
- No tests, no linter or formatter config, no CI. Verification = re-run the notebook and
  check the printed numbers against the prose claims.
- Commits use one-line conventional-commit English (`feat: add scipy dependency`).