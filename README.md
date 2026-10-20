# Does trade promotion pay for itself?

### Price, promotion and basket economics across 77 US grocery stores, 2009–2012

A notebook-first analysis of a weekly **store × SKU** grocery panel — 524,950 records
of sales, price and promotion flags over 156 weeks. It asks what the discounting in the
panel actually earns back, and what that answer depends on: whether the lift is real,
whether the shelf price is set before or after demand, and whether a ratio of revenue
to discount can stand in for a profit statement.

The dataset carries **no customer identifier and no cost or margin field**. That rules
out household-level analysis entirely — no LTV, no retention, no cohort curves — and it
means promotion economics can be measured as *revenue against discount*, never as
profit. Both limits shape what the notebooks claim, and both are stated where they bite
rather than in a footnote.

The analysis is descriptive throughout. Where a number looks causal — price elasticity
most of all — the notebook says why it is not identified.

## Data

| | |
| --- | --- |
| Source | <https://www.kaggle.com/datasets/frtgnn/dunnhumby-the-complete-journey> |
| File | `data/dunnhumby - Breakfast at the Frat.xlsx` (~31 MB, ~30 s to parse) |
| Panel | 156 weeks, 2009-01-14 → 2012-01-04, every week ending on a Wednesday |
| Coverage | 77 stores · 55 UPCs · 4 categories · 9 MSAs across 4 states |

Four sheets: `Glossary`, `dh Store Lookup`, `dh Products Lookup`, `dh Transaction Data`.

Parsing quirks — get these wrong and cells fail or silently misread:

- the three data sheets carry a title banner on row 1, so `header=1`; `Glossary` needs `header=3`
- `Glossary` parses with a junk `Unnamed: 3` column that has to be dropped
- `dh Store Lookup` ships 79 rows for 77 stores — `STORE_ID` 4503 and 17627 appear twice
  with conflicting `SEG_VALUE_NAME`, so `drop_duplicates("STORE_ID")` before any join
- the lookups describe 58 UPCs while 55 appear in transactions; this is a
  lookup-versus-facts mismatch, not a data error

`*.xlsx` is gitignored, so **a fresh clone has no data**. Download it first and keep the
filename exactly as written above — it contains spaces.

## Running the analysis

```sh
uv sync
cd notebooks && uv run jupyter lab
```

Run Jupyter **from inside `notebooks/`**. Every notebook hardcodes
`Path("../data/dunnhumby - Breakfast at the Frat.xlsx")`, which resolves against the
working directory, so launching from the repo root silently breaks every data cell.

Python 3.14 · pandas 3.0 · seaborn · scipy · scikit-learn, managed with `uv`.

## What is in here

| notebook | scope |
| --- | --- |
| `notebooks/0_prelim_analysis.ipynb` | shape, quality, coverage, referential integrity, first-order patterns |
| `notebooks/1_distribution_analysis.ipynb` | distribution of the six key metrics — which test and transformation each one justifies |
| `notebooks/EDA.ipynb` | trend, seasonality, store cohorts, and the metrics the panel can actually support |

`EDA.ipynb` carries its outputs. The other two ship unexecuted, so checking a number
means running the cell rather than reading the file.

## Findings

Each figure below is printed by the section it cites.

- **The panel is losing volume and gaining value.** Weekly `UNITS` trends −0.21%/yr while
  `SPEND` trends +3.25%/yr — the last 13 weeks are 5.65% below the first 13 in units and
  3.58% above in spend. *(EDA §2)*
- **Seasonality dominates the trend.** The seasonal component carries 43.07% of `UNITS`
  variance against 6.83% for trend, swinging 81.21% peak to trough; for `SPEND` it is
  39.86% against 9.98%, swinging 56.57%. *(EDA §3)*
- **But it does not repeat year over year.** Across 52 paired ISO weeks, the 2010-vs-2011
  correlation runs from 0.521 (VALUE stores) down to 0.144 (large stores) and −0.000
  (MSA 47540), so "the same week last year" is not a usable baseline. *(EDA §4)*
- **Price is clearly elastic and not causally identified.** −0.79 pooled, −0.995 within
  UPC, −1.66 within UPC × store: the estimate moves as controls are added because price
  is set in response to demand, so no specification here isolates a causal elasticity.
  *(EDA §6.1)*
- **Promotion is frequent, shallow and large in the tail.** 28.43% of rows carry a
  promotion flag at a median discount depth of 19.05%; across 3,857 paired SKU–store
  cells the median lift is +183.4% units and +147.7% spend. *(EDA §6.2)*
- **The headline promotion ratio is 0.86x — and it is not a profitability statement.**
  $3,576,964 of discount against $3,073,881 of incremental spend. The ratio charges the
  full shelf discount to every promo unit, including units that would not have sold at
  all, and the dataset has no cost field to net them against. Read it as the
  revenue-versus-discount figure the notebook prints, with the caveats in that section,
  not as a verdict. *(EDA §6.2)*
- **Baskets are not growing, they are getting more expensive.** Median spend per basket
  climbs $3.05 → $3.09 → $3.24 across 2009–2011 while units per basket *falls*
  1.14 → 1.13 → 1.12. *(EDA §6.3)*
- **Assortment, not demand, moves UPC reach.** 8 of the 55 UPCs do not span the 156
  weeks: three KING frozen pizzas enter on 2010-02-24 and `COLG SPEARMINT WISP` is
  delisted on 2011-03-30 — the panel's one clean exit event. *(EDA §6.4)*

## Limitations

- **No customer key anywhere.** `HHS` and `VISITS` are per-row counts, not IDs, so no
  household can be followed across weeks. Customer-level anything is not computable.
- **No cost, margin or COGS field.** Promotion economics stop at revenue. A 60%-margin
  and a 20%-margin item score identically here.
- **Promotions are scheduled, not randomly assigned.** Lifts are confounded with weeks
  the retailer already expected to be strong; there is no A/B test in this data.
- **One retailer, four categories, 77 stores, 2009–2012.** External validity is narrow.
- **2012 is a single week.** Per-year figures for 2012 should be read as noise.
- **Aggregation bias.** Market-level elasticities are compressed relative to
  household-level ones; the −0.79 … −1.66 range is consistent with that compression.

## Repository layout

```
.
├── notebooks/                     analysis; run from this directory
│   ├── 0_prelim_analysis.ipynb
│   ├── 1_distribution_analysis.ipynb
│   └── EDA.ipynb
├── data/                          put the .xlsx here (gitignored)
├── src/ecommerce_analysis/        not usable — see Status
├── pyproject.toml
├── uv.lock
└── AGENTS.md                      working notes and conventions for agents
```

## Status

No tests, no linter or formatter config, no CI. Verification means re-running a notebook
and checking the printed numbers against the prose — which is the standard the notebooks
themselves are written to.

`src/ecommerce_analysis/` is a leftover: its `__init__.py` imports a module deleted in
`4066928`, so `import ecommerce_analysis` raises `ModuleNotFoundError`. Nothing in the
analysis depends on it.
