#!/usr/bin/env python3
"""Stock Portfolio Performance Tracker.

Enter ticker symbols, buy prices and share quantities. The tool looks up
current prices (local S&P 500 sample CSV, or live via yfinance with --live),
computes invested capital vs. market value and per-holding % gain/loss, prints
a formatted table and logs the run to 'portfolio_summary.csv'.

Usage
-----
    python portfolio.py                      # interactive entry
    python portfolio.py --demo               # use data/sample_holdings.csv
    python portfolio.py --input my.csv       # CSV with symbol,buy_price,shares
    python portfolio.py --live               # live prices (needs yfinance)

NOTE: prices in data/sp500_sample_prices.csv are illustrative sample values.
"""
import argparse
import csv
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
PRICES_FILE = BASE / "data" / "sp500_sample_prices.csv"
DEMO_HOLDINGS = BASE / "data" / "sample_holdings.csv"
SUMMARY_FILE = BASE / "portfolio_summary.csv"
SUMMARY_FIELDS = ["run_timestamp", "symbol", "company", "shares", "buy_price",
                  "current_price", "invested", "market_value", "gain_loss",
                  "gain_loss_pct"]


# ---------- price lookup ----------
def load_price_table(path: Path = PRICES_FILE) -> dict[str, dict]:
    """Return {symbol: {'name':..., 'price': float}} from the CSV."""
    table: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            table[row["Symbol"].upper()] = {
                "name": row["Security"],
                "price": float(row["Price"]),
            }
    return table


def live_price(symbol: str) -> float | None:
    """Fetch the latest price via yfinance; None if unavailable."""
    try:
        import yfinance as yf  # optional dependency
        hist = yf.Ticker(symbol).history(period="1d")
        return float(hist["Close"].iloc[-1]) if not hist.empty else None
    except Exception:
        return None


def get_price(symbol: str, table: dict, live: bool) -> tuple[str, float | None]:
    name = table.get(symbol, {}).get("name", symbol)
    if live:
        price = live_price(symbol)
        if price is not None:
            return name, price
        print(f"  (live price for {symbol} unavailable - using CSV)")
    return name, table.get(symbol, {}).get("price")


# ---------- portfolio data ----------
def add_position(portfolio: dict, symbol: str, buy_price: float, shares: float) -> None:
    """Add a position; merge with an existing one using a weighted average cost."""
    if symbol in portfolio:
        p = portfolio[symbol]
        total = p["shares"] + shares
        p["buy_price"] = (p["buy_price"] * p["shares"] + buy_price * shares) / total
        p["shares"] = total
    else:
        portfolio[symbol] = {"buy_price": buy_price, "shares": shares}


def read_holdings_csv(path: Path) -> dict:
    portfolio: dict = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            add_position(portfolio, row["symbol"].strip().upper(),
                         float(row["buy_price"]), float(row["shares"]))
    return portfolio


def prompt_positive(msg: str) -> float:
    while True:
        try:
            value = float(input(msg))
            if value > 0:
                return value
        except ValueError:
            pass
        print("  Please enter a positive number.")


def interactive_entry(table: dict) -> dict:
    portfolio: dict = {}
    print("Enter your holdings. Leave the ticker blank to finish.\n")
    while True:
        symbol = input("Ticker symbol: ").strip().upper()
        if not symbol:
            break
        if symbol not in table:
            print(f"  '{symbol}' not in dataset - price lookup may fail.")
        buy = prompt_positive("  Buy price per share: ")
        qty = prompt_positive("  Number of shares:    ")
        add_position(portfolio, symbol, buy, qty)
    return portfolio


# ---------- calculations ----------
def evaluate(portfolio: dict, table: dict, live: bool) -> list[dict]:
    rows = []
    for symbol, pos in portfolio.items():
        name, current = get_price(symbol, table, live)
        if current is None:
            print(f"  Skipping {symbol}: no price found.")
            continue
        invested = pos["buy_price"] * pos["shares"]
        value = current * pos["shares"]
        rows.append({
            "symbol": symbol, "company": name, "shares": pos["shares"],
            "buy_price": pos["buy_price"], "current_price": current,
            "invested": invested, "market_value": value,
            "gain_loss": value - invested,
            "gain_loss_pct": (value - invested) / invested * 100,
        })
    return rows


def totals(rows: list[dict]) -> dict:
    invested = sum(r["invested"] for r in rows)
    value = sum(r["market_value"] for r in rows)
    return {"invested": invested, "market_value": value,
            "gain_loss": value - invested,
            "gain_loss_pct": (value - invested) / invested * 100 if invested else 0.0}


# ---------- output ----------
def print_report(rows: list[dict], t: dict) -> None:
    header = (f"{'Symbol':<7}{'Shares':>8}{'Buy':>10}{'Now':>10}"
              f"{'Invested':>12}{'Value':>12}{'P/L':>11}{'P/L %':>9}")
    line = "-" * len(header)
    print("\n" + line + "\n" + header + "\n" + line)
    for r in rows:
        print(f"{r['symbol']:<7}{r['shares']:>8.2f}{r['buy_price']:>10.2f}"
              f"{r['current_price']:>10.2f}{r['invested']:>12,.2f}"
              f"{r['market_value']:>12,.2f}{r['gain_loss']:>+11,.2f}"
              f"{r['gain_loss_pct']:>+8.2f}%")
    print(line)
    print(f"{'TOTAL':<7}{'':>8}{'':>10}{'':>10}{t['invested']:>12,.2f}"
          f"{t['market_value']:>12,.2f}{t['gain_loss']:>+11,.2f}"
          f"{t['gain_loss_pct']:>+8.2f}%")
    print(line)


def log_summary(rows: list[dict], t: dict, path: Path = SUMMARY_FILE) -> None:
    """Append this run to the CSV log (header written only for a new file)."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow({"run_timestamp": stamp, **{k: round(r[k], 2) if isinstance(r[k], float) else r[k]
                                                   for k in r}})
        w.writerow({"run_timestamp": stamp, "symbol": "TOTAL",
                    "invested": round(t["invested"], 2),
                    "market_value": round(t["market_value"], 2),
                    "gain_loss": round(t["gain_loss"], 2),
                    "gain_loss_pct": round(t["gain_loss_pct"], 2)})
    print(f"\nSummary logged to {path.name}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Stock portfolio performance tracker")
    ap.add_argument("--demo", action="store_true", help="use sample holdings")
    ap.add_argument("--input", type=Path, help="CSV: symbol,buy_price,shares")
    ap.add_argument("--live", action="store_true", help="fetch live prices (yfinance)")
    ap.add_argument("--output", type=Path, default=SUMMARY_FILE)
    args = ap.parse_args()

    table = load_price_table()
    if args.demo:
        portfolio = read_holdings_csv(DEMO_HOLDINGS)
    elif args.input:
        portfolio = read_holdings_csv(args.input)
    else:
        portfolio = interactive_entry(table)

    if not portfolio:
        print("No holdings entered.")
        return
    rows = evaluate(portfolio, table, args.live)
    if not rows:
        print("Nothing to report.")
        return
    t = totals(rows)
    print_report(rows, t)
    log_summary(rows, t, args.output)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
