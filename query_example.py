"""
Example: read data back out of the database as a pandas DataFrame.

Usage:
    python query_example.py RY.TO
"""

import sys

import pandas as pd

from stock_data import get_connection

ticker = sys.argv[1] if len(sys.argv) > 1 else "RY.TO"

conn = get_connection()
df = pd.read_sql(
    "SELECT date, open, high, low, close, volume FROM prices WHERE ticker = ? ORDER BY date",
    conn,
    params=(ticker,),
)
conn.close()

print(df.tail(10).to_string(index=False))
