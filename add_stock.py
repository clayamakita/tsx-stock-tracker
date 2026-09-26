"""
Part 1 -- onboard a new TSX stock.

Back-fills its daily OHLC prices from a chosen start date up to
yesterday, and (by default) adds it to tickers.txt so the daily job
(daily_update.py) keeps it up to date from now on.

Usage:
    python add_stock.py RY.TO --start 2015-01-01
    python add_stock.py SHOP.TO --start 2020-06-01 --no-track
"""

import argparse

from stock_data import add_tracked_ticker, fetch_history, get_connection, upsert_prices


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ticker", help="TSX ticker with .TO suffix, e.g. RY.TO, SHOP.TO, TD.TO"
    )
    parser.add_argument(
        "--start", required=True, help="Start date to backfill from, format YYYY-MM-DD"
    )
    parser.add_argument(
        "--no-track",
        action="store_true",
        help="Fetch the history but don't add this ticker to tickers.txt "
        "(it won't be picked up by the daily job)",
    )
    args = parser.parse_args()

    print(f"Fetching {args.ticker} from {args.start} to yesterday...")
    df = fetch_history(args.ticker, start=args.start)

    if df.empty:
        print(
            f"No data returned for '{args.ticker}'. Double check the symbol -- "
            "TSX tickers need the .TO suffix (e.g. RY.TO, not RY)."
        )
        return

    conn = get_connection()
    n = upsert_prices(conn, df)
    conn.close()
    print(f"Wrote {n} rows for {args.ticker}, covering {df['date'].min()} to {df['date'].max()}.")

    if not args.no_track:
        add_tracked_ticker(args.ticker)
        print(f"{args.ticker} added to tickers.txt -- the daily job will now keep it updated.")


if __name__ == "__main__":
    main()
