from ecommerce_analysis.load import load

__all__ = ["load", "main"]


def main() -> None:
    """Load the raw CSVs into data/analytics.duckdb."""
    load()


if __name__ == "__main__":
    main()