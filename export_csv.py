"""
Export price data to CSV -- handy for opening in Excel/Numbers, or
importing straight into Google Sheets (File > Import > Upload).

Usage:
    python export_csv.py RY.TO              # one ticker -> exports/RY_TO.csv
    python export_csv.py RY.TO SHOP.TO       # multiple tickers, one CSV each
    python export_csv.py --all               # every tracked ticker, one combined CSV
    python export_csv.py                     # (no args) exports every tracked ticker, one CSV each
"""

import argparse
from pathlib import Path

import pandas as pd

from stock_data import get_connection, read_tracked_tickers

EXPORT_DIR = Path(__file__).parent / "exports"


def export_ticker(conn, ticker: str) -> Path:
    df = pd.read_sql(
        "SELECT date, open, high, low, close, volume FROM prices WHERE ticker = ? ORDER BY date",
        conn,
        params=(ticker,),
    )
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / f"{ticker.replace('.', '_')}.csv"
    df.to_csv(path, index=False)
    return path


def export_all(conn) -> Path:
    df = pd.read_sql(
        "SELECT ticker, date, open, high, low, close, volume FROM prices ORDER BY ticker, date",
        conn,
    )
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / "all_stocks.csv"
    df.to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tickers", nargs="*", help="Tickers to export, e.g. RY.TO SHOP.TO")
    parser.add_argument(
        "--all", action="store_true", help="Export every tracked ticker into one combined CSV"
    )
    args = parser.parse_args()

    conn = get_connection()

    if args.all:
        path = export_all(conn)
        print(f"Wrote {path}")
    else:
        tickers = args.tickers or read_tracked_tickers()
        if not tickers:
            print("No tickers tracked yet, and none specified. Try: python export_csv.py RY.TO")
            conn.close()
            return
        for t in tickers:
            path = export_ticker(conn, t)
            print(f"Wrote {path}")

    conn.close()


if __name__ == "__main__":
    main()
