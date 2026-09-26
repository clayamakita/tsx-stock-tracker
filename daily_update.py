"""
Part 2 -- daily update job.

Fetches recent prices for every ticker in tickers.txt and upserts them
into the database. Pulls a trailing window (not just "yesterday") so
that a missed run (e.g. the laptop was off, or a workflow run failed)
self-heals the next time it runs, instead of leaving a permanent gap.

Usage:
    python daily_update.py
"""

from datetime import date, timedelta

from stock_data import fetch_history, get_connection, read_tracked_tickers, upsert_prices

LOOKBACK_DAYS = 7  # re-fetch this many trailing days every run; upsert makes it safe


def main() -> None:
    tickers = read_tracked_tickers()
    if not tickers:
        print("tickers.txt is empty -- run add_stock.py first to add a stock to track.")
        return

    start = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()
    conn = get_connection()

    for ticker in tickers:
        df = fetch_history(ticker, start=start)
        n = upsert_prices(conn, df)
        print(f"{ticker}: upserted {n} row(s)")

    conn.close()


if __name__ == "__main__":
    main()
