# TSX Stock Tracker

Two-part tool for building a daily-updated price history for TSX stocks.

- **`add_stock.py`** — one-time: back-fills a new stock's full daily
  OHLC history and starts tracking it going forward.
- **`daily_update.py`** — run daily: pulls the latest prices for every
  tracked stock. Runs automatically for free via GitHub Actions
  (`.github/workflows/daily_update.yml`).

All data is stored in a single SQLite file, `data/stocks.db`, in a
table `prices(ticker, date, open, high, low, close, volume)`.

## 1. Local setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Add your first stocks

```bash
python add_stock.py RY.TO --start 2015-01-01
python add_stock.py SHOP.TO --start 2018-01-01
```

TSX tickers need the **`.TO`** suffix on Yahoo Finance (e.g. `RY.TO`,
`TD.TO`, `SHOP.TO`, `ENB.TO`). This also adds each ticker to
`tickers.txt`, which is what the daily job reads.

Check it worked:

```bash
python query_example.py RY.TO
```

## 3. Run the daily update manually (optional)

```bash
python daily_update.py
```

Safe to run more than once a day, or after a gap — it re-fetches a
trailing 7-day window and overwrites, so it self-heals missed days.

## 4. Automate it for free with GitHub Actions

1. Publish this folder as a GitHub repo — via GitHub Desktop
   (`File → Add Local Repository` → point at this folder → it'll offer
   to create a repo → then click **Publish repository**), or the
   command line (`git init`, `git add .`, `git commit`, `git push`).
2. On github.com, open the repo's **Settings → Actions → General →
   Workflow permissions** and select **"Read and write permissions"**
   (needed so the workflow can commit the updated database back to the
   repo). This is a one-time setting on the website — GitHub Desktop
   doesn't manage repo settings.
3. That's it — `.github/workflows/daily_update.yml` is already set up
   to run Mon–Fri at 22:00 UTC (a couple hours after TSX close) and
   commit the updated `data/stocks.db` back to the repo, from GitHub's
   own servers, whether or not your laptop is on.
4. To add a new stock later: **first sync** (GitHub Desktop:
   `Fetch origin` then `Pull origin`, to grab any changes the daily
   job made while you weren't looking), *then* run `add_stock.py`
   locally, then commit and push the updated `tickers.txt` and
   `data/stocks.db` from GitHub Desktop.
5. You can trigger a run immediately any time from the repo's
   **Actions** tab on github.com → *Daily TSX price update* → **Run
   workflow**.

**A note on using GitHub Desktop alongside the cloud job:** the daily
workflow commits directly to GitHub, not to your laptop, so your local
copy will quietly fall behind — GitHub Desktop won't auto-update it.
Get in the habit of clicking **Fetch origin** (and **Pull origin** if
it finds changes) before you run any script locally. If you ever do
end up with a conflict on `data/stocks.db` (only possible if you and
the cloud job both changed it since your last sync), don't try to
manually merge it — just keep GitHub's version and re-run
`add_stock.py` locally afterward. Since everything is re-fetched from
Yahoo Finance and upserted, nothing is actually lost by doing that.

## Getting the data into Google Sheets

```bash
python export_csv.py RY.TO          # writes exports/RY_TO.csv
python export_csv.py --all          # writes exports/all_stocks.csv (every tracked ticker)
```

Then either:
- **Import directly (easiest):** in Google Sheets, `File → Import → Upload`, pick the CSV, choose "Replace current sheet" or "Insert new sheet".
- **Copy-paste:** open the CSV in Excel/Numbers/a text editor, select all, copy, and paste into Sheets.

## Notes

- `yfinance` is a free, unofficial wrapper around Yahoo Finance. It's
  actively maintained but occasionally breaks for a day or two when
  Yahoo changes something server-side — if the daily job ever comes up
  empty, that's the first thing to check.
- Because prices are upserted on `(ticker, date)`, it's always safe to
  re-run either script — nothing will be duplicated.
