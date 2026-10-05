# ecommerce-analysis

Analysis of the Dunnhumby grocery dataset (households, baskets, products,
campaigns, coupons, and marketing exposure) using DuckDB.

## Setup

```sh
uv sync
```

## Load the data

```sh
uv run load-data
```

Unpacks `data/archive.zip` into `data/raw/`, then creates `data/analytics.duckdb`
with one table per CSV:

| table | rows | notes |
| --- | --- | --- |
| `transaction_data` | 2,595,732 | basket line items, `DAY` 1–711 |
| `causal_data` | 36,786,524 | weekly product/store marketing exposure |
| `product` | 92,353 | product dimensions |
| `coupon` | 124,548 | coupon → product → campaign |
| `campaign_table` | 7,208 | households targeted per campaign |
| `coupon_redempt` | 2,318 | coupon redemptions |
| `hh_demographic` | 801 | household demographics (2,500 keys in transactions) |
| `campaign_desc` | 30 | campaign name and day range |

Load takes about 20 seconds and produces a ~174 MB database. Re-run with
`load(replace=True)` to rebuild tables that already exist.

## Query

```sh
uv run python -c "
import duckdb
con = duckdb.connect('data/analytics.duckdb', read_only=True)
print(con.execute('''
    select p.DEPARTMENT, round(sum(t.SALES_VALUE), 2) as revenue
    from transaction_data t join product p using (PRODUCT_ID)
    group by 1 order by 2 desc
''').df())
"
```

Or use the DuckDB CLI directly:

```sh
uv run duckdb data/analytics.duckdb
```

### Notes on types

Column types are declared explicitly rather than sniffed. `causal_data.display`
and `causal_data.mailer` are alphanumeric codes (values like `0`, `9`, `A`,
`H`), not numbers, so they stay `VARCHAR`; `transaction_data.TRANS_TIME` is
minute-of-day (0–2359) stored as `INTEGER`; discounts are stored as signed
`DOUBLE` (negative means a discount).

## Export results

```sql
COPY (SELECT * FROM transaction_data WHERE DAY < 30)
TO 'data/sample.parquet' (FORMAT PARQUET);

COPY (SELECT DEPARTMENT, sum(SALES_VALUE) FROM transaction_data t
      JOIN product p USING (PRODUCT_ID) GROUP BY 1)
TO 'data/revenue_by_department.csv' (HEADER, DELIMITER ',');
```