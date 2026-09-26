"""
Shared helpers for fetching TSX stock price data with yfinance and
storing it in a local SQLite database (data/stocks.db).

TSX tickers on Yahoo Finance use a ".TO" suffix, e.g.:
    RY.TO    Royal Bank of Canada
    SHOP.TO  Shopify
    TD.TO    TD Bank
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

DB_PATH = Path(__file__).parent / "data" / "stocks.db"
TICKERS_FILE = Path(__file__).parent / "tickers.txt"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open (and if needed, create) the SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT NOT NULL,
            date   TEXT NOT NULL,   -- YYYY-MM-DD
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
        """
    )
    conn.commit()


def fetch_history(ticker: str, start: str) -> pd.DataFrame:
    """
    Fetch daily OHLC data for `ticker` from `start` (YYYY-MM-DD) up to
    and including yesterday. Any partial/in-progress "today" row that
    Yahoo sometimes returns is dropped so results are always final,
    closed trading days.
    """
    raw = yf.Ticker(ticker).history(start=start, interval="1d", auto_adjust=False)
    if raw.empty:
        return raw

    df = raw.reset_index()
    df["date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df = df[df["date"] < date.today().isoformat()]
    df["ticker"] = ticker

    return df[["ticker", "date", "Open", "High", "Low", "Close", "Volume"]].rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )


def upsert_prices(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """
    Write rows into the prices table. If a (ticker, date) row already
    exists it's overwritten -- this is what makes it safe to fetch
    overlapping date ranges (e.g. a trailing 7-day window every day)
    without worrying about duplicates.
    """
    if df.empty:
        return 0
    conn.executemany(
        """
        INSERT INTO prices (ticker, date, open, high, low, close, volume)
        VALUES (:ticker, :date, :open, :high, :low, :close, :volume)
        ON CONFLICT(ticker, date) DO UPDATE SET
            open   = excluded.open,
            high   = excluded.high,
            low    = excluded.low,
            close  = excluded.close,
            volume = excluded.volume
        """,
        df.to_dict("records"),
    )
    conn.commit()
    return len(df)


def read_tracked_tickers(path: Path = TICKERS_FILE) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def add_tracked_ticker(ticker: str, path: Path = TICKERS_FILE) -> None:
    """Add a ticker to tickers.txt (the list the daily job reads) if not already there."""
    tickers = read_tracked_tickers(path)
    if ticker not in tickers:
        tickers.append(ticker)
        path.write_text("\n".join(tickers) + "\n")
