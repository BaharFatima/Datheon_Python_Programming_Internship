# Task 2 - Stock Portfolio Performance Tracker

Calculates portfolio valuation and logs results to CSV.

## Run
```bash
python portfolio.py --demo          # sample holdings
python portfolio.py                 # interactive entry
python portfolio.py --input my.csv  # your own holdings (symbol,buy_price,shares)
python portfolio.py --live          # live prices (pip install yfinance)
```

## Data
- `data/sp500_sample_prices.csv` - ticker, company, sector and a **sample** price. For the full S&P 500 list use
  `https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv`
  (add a `Price` column or use `--live`).
- Positions are stored in a dictionary: `{symbol: {"buy_price", "shares"}}`; repeat buys use a weighted average cost.

## Output
Formatted console table + `portfolio_summary.csv` (appended each run with a timestamp, per-holding rows and a TOTAL row).
