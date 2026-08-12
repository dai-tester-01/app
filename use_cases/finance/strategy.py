"""Channel-Breakout ETH trend-following strategy — improved modular engine.

Improvements inspired by the0 (https://github.com/alexanderwanyoike/the0),
an open-source algorithmic trading execution platform. No code was copied;
the following patterns were adapted from the concepts demonstrated there:

1. SMA-crossover dual-confirmation (entry filter)
   the0's example-bots/ directory ships SMA-crossover implementations in
   Python, C++, TypeScript, Rust, Scala, C#, and Haskell. All share the same
   core idea: enter only when a fast moving average crosses above a slow one.
   Adding `fast_sma > slow_sma` as an optional gate on the Donchian breakout
   entry means a position opens only when both the longer-term structural
   breakout and the shorter-term momentum agree, reducing false entries.

2. DCA periodic-investment baseline
   the0 ships a Python Dollar-Cost Averaging bot example that buys a fixed
   notional on a recurring schedule. Monthly DCA is added as a second baseline
   alongside buy-and-hold because it represents a realistic alternative for an
   investor with recurring cash flow, making the comparison fairer.

3. Multi-asset portfolio wrapper
   the0's platform is exchange-agnostic and manages multiple concurrent bots
   across different markets. `backtest_portfolio()` mirrors that idea: run the
   same strategy config across any collection of OHLCV CSVs and return
   per-asset results with an aggregated summary table.

The strategy (classic Donchian / turtle-style trend following):
  BUY  when close breaks ABOVE the trailing N-day high AND close > long EMA
       AND (optionally) fast SMA > slow SMA.
  SELL when close breaks BELOW the trailing M-day low, OR an ATR trailing
       stop is hit.
  SIZE positions by ATR so each trade risks a fixed % of equity.

Educational backtest on a small, synthetic dataset. Not financial advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class StrategyConfig:
    # Entry (breakout)
    entry_window: int = 20
    regime_ema: int = 50
    breakout_buffer: float = 0.0

    # SMA-crossover dual-confirmation (new — inspired by the0's SMA-crossover bots)
    use_sma_filter: bool = True
    fast_sma_window: int = 10
    slow_sma_window: int = 30

    # Exit
    exit_window: int = 10
    atr_window: int = 14
    atr_trail_mult: float = 3.0
    max_hold_days: int = 90

    # Position sizing
    risk_per_trade: float = 0.02
    init_stop_mult: float = 2.0
    max_exposure: float = 1.00

    # Costs
    fee_bps: float = 10.0
    slippage_bps: float = 5.0

    # Accounting
    start_cash: float = 10_000.0
    trading_days_per_year: int = 365


# --------------------------------------------------------------------------- #
# Indicators
# --------------------------------------------------------------------------- #
def _atr(df: pd.DataFrame, window: int) -> pd.Series:
    """Average True Range (Wilder smoothing)."""
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean()


# --------------------------------------------------------------------------- #
# Signal generation
# --------------------------------------------------------------------------- #
def generate_signals(df: pd.DataFrame, cfg: StrategyConfig = StrategyConfig()) -> pd.DataFrame:
    """Return a copy of df with indicator and signal columns added."""
    out = df.copy()

    # Donchian channels use prior days only (shift 1) — no look-ahead.
    out["upper"] = out["high"].rolling(cfg.entry_window).max().shift(1)
    out["lower"] = out["low"].rolling(cfg.exit_window).min().shift(1)
    out["ema"] = out["close"].ewm(span=cfg.regime_ema, adjust=False).mean()
    out["atr"] = _atr(out, cfg.atr_window)

    # SMA crossover (new) — inspired by the0's SMA-crossover example bots.
    out["fast_sma"] = out["close"].rolling(cfg.fast_sma_window).mean()
    out["slow_sma"] = out["close"].rolling(cfg.slow_sma_window).mean()
    out["sma_bull"] = out["fast_sma"] > out["slow_sma"]

    broke_out = out["close"] > out["upper"] * (1 + cfg.breakout_buffer)
    out["trend_ok"] = out["close"] > out["ema"]

    buy_cond = broke_out & out["trend_ok"]
    if cfg.use_sma_filter:
        buy_cond = buy_cond & out["sma_bull"]
    out["buy_signal"] = buy_cond

    out["channel_exit"] = out["close"] < out["lower"]
    return out


# --------------------------------------------------------------------------- #
# Execution
# --------------------------------------------------------------------------- #
def _fill_price(price: float, side: str, cfg: StrategyConfig) -> float:
    slip = cfg.slippage_bps / 10_000.0
    return price * (1 + slip) if side == "BUY" else price * (1 - slip)


def backtest(df: pd.DataFrame, cfg: StrategyConfig = StrategyConfig()) -> dict:
    """Run the long/flat backtest; return signals, trades, equity, and metrics."""
    sig = generate_signals(df, cfg).reset_index(drop=True)
    fee = cfg.fee_bps / 10_000.0

    cash = cfg.start_cash
    units = 0.0
    entry_price: Optional[float] = None
    entry_idx: Optional[int] = None
    peak_close: Optional[float] = None
    trades: list[dict] = []
    equity: list[float] = []

    for i, row in sig.iterrows():
        price = row["close"]
        atr = row["atr"]
        flat = units == 0.0

        # Entry
        if flat and row["buy_signal"] and pd.notna(atr) and atr > 0:
            risk_capital = cash * cfg.risk_per_trade
            risk_per_unit = cfg.init_stop_mult * atr
            want_units = risk_capital / risk_per_unit
            max_units = (cash * cfg.max_exposure) / price
            size_units = min(want_units, max_units)

            fill = _fill_price(price, "BUY", cfg)
            spend = size_units * fill
            cash -= spend + spend * fee
            units = size_units
            entry_price = fill
            entry_idx = i
            peak_close = price
            entry_reason = "breakout+sma" if cfg.use_sma_filter else "breakout"
            trades.append({
                "date": row.get("date"),
                "action": "BUY",
                "price": round(fill, 2),
                "units": round(units, 4),
                "exposure": round(spend / (cash + spend), 3),
                "atr": round(float(atr), 2),
                "reason": entry_reason,
            })

        # Exit
        elif not flat:
            peak_close = max(peak_close, price)  # type: ignore[type-var]
            trail_stop = peak_close - cfg.atr_trail_mult * atr if pd.notna(atr) else -np.inf

            reason = None
            if row["channel_exit"]:
                reason = "channel"
            elif price <= trail_stop:
                reason = "trail_stop"
            elif entry_idx is not None and (i - entry_idx) >= cfg.max_hold_days:
                reason = "max_hold"

            if reason is not None:
                fill = _fill_price(price, "SELL", cfg)
                proceeds = units * fill
                cash += proceeds - proceeds * fee
                pnl = proceeds - units * entry_price if entry_price else 0.0
                trades.append({
                    "date": row.get("date"),
                    "action": "SELL",
                    "price": round(fill, 2),
                    "units": round(units, 4),
                    "exposure": 0.0,
                    "atr": round(float(atr), 2) if pd.notna(atr) else None,
                    "reason": reason,
                    "trade_pnl": round(pnl, 2),
                })
                units = 0.0
                entry_price = None
                entry_idx = None
                peak_close = None

        equity.append(cash + units * price)

    sig["equity"] = equity

    bh_units = (cfg.start_cash * (1 - fee)) / _fill_price(sig["close"].iloc[0], "BUY", cfg)
    sig["buy_hold"] = bh_units * sig["close"]

    # DCA baseline (new) — inspired by the0's DCA bot example.
    sig["dca"] = _dca_baseline(sig, cfg)

    trades_df = pd.DataFrame(trades)
    metrics = compute_metrics(sig, trades_df, cfg)
    return {"signals": sig, "trades": trades_df, "metrics": metrics}


# --------------------------------------------------------------------------- #
# DCA baseline — inspired by the0's DCA (Dollar-Cost Averaging) bot
# --------------------------------------------------------------------------- #
def _dca_baseline(sig: pd.DataFrame, cfg: StrategyConfig) -> pd.Series:
    """Monthly fixed-amount purchases at close with fees.

    Divides start_cash into 12 equal monthly instalments, buying at each
    month's first available close. This mirrors the0's DCA bot pattern and
    provides a fairer baseline than lump-sum buy-and-hold for investors
    with recurring cash flow.
    """
    fee = cfg.fee_bps / 10_000.0
    monthly_amount = cfg.start_cash / 12.0
    cash = cfg.start_cash
    units = 0.0
    values: list[float] = []
    last_period: Optional[int] = None
    has_dates = "date" in sig.columns

    for i, row in sig.iterrows():
        price = row["close"]

        # Determine current month-period; fall back to 30-day buckets if no dates.
        if has_dates:
            d = row["date"]
            period = d.year * 12 + d.month
        else:
            period = int(i) // 30

        if period != last_period and cash >= monthly_amount:
            fill = price * (1 + cfg.slippage_bps / 10_000.0)
            bought = (monthly_amount * (1 - fee)) / fill
            units += bought
            cash -= monthly_amount
            last_period = period

        values.append(cash + units * price)

    return pd.Series(values, index=sig.index)


# --------------------------------------------------------------------------- #
# Performance metrics
# --------------------------------------------------------------------------- #
def _max_drawdown(series: pd.Series) -> float:
    roll_max = series.cummax()
    return float((series / roll_max - 1).min())


def _sharpe(equity: pd.Series, periods_per_year: int) -> float:
    rets = equity.pct_change().dropna()
    if len(rets) == 0 or rets.std(ddof=0) == 0:
        return 0.0
    return float(rets.mean() / rets.std(ddof=0) * np.sqrt(periods_per_year))


def _time_in_market(sig: pd.DataFrame, trades_df: pd.DataFrame) -> float:
    """Fraction of days a position was open, reconstructed from BUY/SELL pairs."""
    if trades_df.empty:
        return 0.0
    n = len(sig)
    held = np.zeros(n, dtype=bool)
    dates = sig["date"] if "date" in sig.columns else pd.Series(range(n), name="date")
    date_to_idx = {d: i for i, d in enumerate(dates)}
    open_from: Optional[int] = None
    for _, t in trades_df.iterrows():
        idx = date_to_idx.get(t["date"])
        if idx is None:
            continue
        if t["action"] == "BUY":
            open_from = idx
        elif t["action"] == "SELL" and open_from is not None:
            held[open_from:idx + 1] = True
            open_from = None
    if open_from is not None:
        held[open_from:] = True
    return float(held.mean())


def compute_metrics(sig: pd.DataFrame, trades_df: pd.DataFrame, cfg: StrategyConfig) -> dict:
    equity = sig["equity"]
    bh = sig["buy_hold"]
    dca = sig["dca"]
    years = max(len(sig) / cfg.trading_days_per_year, 1e-9)

    strat_ret = float(equity.iloc[-1] / cfg.start_cash - 1)
    bh_ret = float(bh.iloc[-1] / cfg.start_cash - 1)
    dca_ret = float(dca.iloc[-1] / cfg.start_cash - 1)

    closed = trades_df[trades_df["action"] == "SELL"] if not trades_df.empty else pd.DataFrame()
    pnl = closed["trade_pnl"] if "trade_pnl" in closed.columns else pd.Series(dtype=float)
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    profit_factor = float(wins.sum() / abs(losses.sum())) if losses.sum() != 0 else float("inf")

    return {
        "final_value": round(float(equity.iloc[-1]), 2),
        "total_return_pct": round(strat_ret * 100, 2),
        "buy_hold_return_pct": round(bh_ret * 100, 2),
        "dca_return_pct": round(dca_ret * 100, 2),
        "excess_vs_buy_hold_pts": round((strat_ret - bh_ret) * 100, 2),
        "excess_vs_dca_pts": round((strat_ret - dca_ret) * 100, 2),
        "cagr_pct": round(((equity.iloc[-1] / cfg.start_cash) ** (1 / years) - 1) * 100, 2),
        "sharpe": round(_sharpe(equity, cfg.trading_days_per_year), 2),
        "max_drawdown_pct": round(_max_drawdown(equity) * 100, 2),
        "buy_hold_max_drawdown_pct": round(_max_drawdown(bh) * 100, 2),
        "dca_max_drawdown_pct": round(_max_drawdown(dca) * 100, 2),
        "exposure_pct": round(_time_in_market(sig, trades_df) * 100, 1),
        "n_trades": int(len(closed)),
        "win_rate_pct": round(len(wins) / len(closed) * 100, 1) if len(closed) else 0.0,
        "profit_factor": round(profit_factor, 2) if np.isfinite(profit_factor) else None,
        "sma_filter_active": cfg.use_sma_filter,
    }


# --------------------------------------------------------------------------- #
# Multi-asset portfolio wrapper
# Inspired by the0's exchange-agnostic, multi-bot architecture
# --------------------------------------------------------------------------- #
def backtest_portfolio(
    asset_paths: dict[str, str],
    cfg: StrategyConfig = StrategyConfig(),
) -> dict[str, dict]:
    """Run the strategy on multiple assets and return per-asset results.

    Mirrors the0's multi-bot, exchange-agnostic architecture: one strategy
    config deployed across many markets.

    Args:
        asset_paths: mapping of asset label to OHLCV CSV path.
        cfg: shared strategy config applied to all assets.
    """
    return {asset: backtest(_load_prices(path), cfg) for asset, path in asset_paths.items()}


def portfolio_summary(portfolio_results: dict[str, dict]) -> pd.DataFrame:
    """Tabulate per-asset metrics from a portfolio backtest."""
    rows = [{"asset": asset, **result["metrics"]} for asset, result in portfolio_results.items()]
    return pd.DataFrame(rows).set_index("asset")


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #
def _load_prices(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Backtest the Channel-Breakout strategy.")
    parser.add_argument("--data", default="data/eth_2024.csv")
    parser.add_argument(
        "--no-sma-filter",
        action="store_true",
        help="Disable the SMA-crossover dual-confirmation filter.",
    )
    args = parser.parse_args()

    cfg = StrategyConfig(use_sma_filter=not args.no_sma_filter)
    df = _load_prices(args.data)
    result = backtest(df, cfg)

    print(f"Loaded {len(df)} rows: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"SMA filter: {'ON (fast={cfg.fast_sma_window}d > slow={cfg.slow_sma_window}d)' if cfg.use_sma_filter else 'OFF'}\n")
    if not result["trades"].empty:
        print("Trades:")
        print(result["trades"].to_string(index=False))
    else:
        print("No trades fired.")
    print("\nMetrics:")
    for k, v in result["metrics"].items():
        print(f"  {k:36s} {v}")


if __name__ == "__main__":
    main()
