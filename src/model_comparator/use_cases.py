"""Pre-built prompt templates for real-world model comparison use-cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UseCase:
    id: str
    category: str
    title: str
    prompt: str


_FINANCE_STRATEGY = """\
You are a quantitative analyst reviewing an Ethereum trend-following strategy.

Strategy: ETH Channel-Breakout v2 (Donchian / turtle-style with pyramid entries)
──────────────────────────────────────────────────────────────────────────────────
Entry  : Close breaks above the 20-day high AND close > 50-day EMA.
Pyramid: While long, add a second tranche when a new buy signal fires AND price
         is at least 0.5 ATR(14) above the previous entry price (up to 3 tranches).
Exit   : Close breaks below the 10-day low OR price drops 3×ATR(14) below the
         peak close since entry (ATR trailing stop). Force-exit after 90 days.
Sizing : Each tranche risks 2% of remaining equity; initial stop 2×ATR; max 100% exposure.
Costs  : 0.10% taker fee + 0.05% slippage per side (charged on every fill).
Metrics: Sharpe, Sortino (downside-only volatility), and Calmar (CAGR / max-drawdown).

Evaluation criteria for trend-following strategies:
• Sortino and Calmar ratios (preferred over Sharpe for fat-tailed assets like crypto)
• Profit factor (gross win / gross loss)
• Time in market vs buy-and-hold
• False breakout rate and pyramid add frequency

Question: Evaluate whether the 3-tranche pyramid entry improves or degrades the
risk-adjusted return profile compared to a single-entry version of the same
strategy. Identify the biggest remaining structural weakness and propose one
concrete, parameter-specific fix. Quantify the expected effect on Calmar ratio
or max drawdown where possible.\
"""

_FINANCE_SIGNALS = """\
You are a quantitative analyst comparing three entry signals for an ETH daily strategy.

Signal A — Donchian Breakout with pyramid:
  BUY  when close > max(prior 20-day high) AND close > EMA(50)
  ADD  second/third tranche on each subsequent buy signal while held,
       provided price is 0.5 ATR above the last entry (up to 3 adds total)
  SELL when close < min(prior 10-day low) OR ATR(14) trailing stop hit (3×ATR below peak)

Signal B — SMA Crossover (single entry):
  BUY  when SMA(5) crosses above SMA(20) AND close > SMA(50)
  SELL when SMA(5) crosses below SMA(20) OR ATR(14) trailing stop hit (3×ATR below peak)

Signal C — Confidence-Weighted SMA Crossover (spread-scaled sizing):
  BUY  when SMA(5) crosses above SMA(20) AND SMA(20) > SMA(50)
  CONFIDENCE = (SMA(5) − SMA(20)) / SMA(20)          (normalised SMA spread)
  SIZE = base_risk × clamp(1 + CONFIDENCE × 15, 0.5, 2.0)
         (half position on weak crossovers; up to double on wide separations)
  SELL when SMA(5) crosses below SMA(20) OR ATR(14) trailing stop hit (3×ATR below peak)
  Restarts: persists the last SMA values so the signal recovers correctly after a process restart.

All signals use base_risk = 2% of equity, initial stop 2×ATR.
Evaluation metrics: Sharpe, Sortino, Calmar ratio, max drawdown, profit factor.

Compare on these five dimensions:
1. Entry frequency, lag, and pyramid / add-on opportunity rate
2. False signal rate in range-bound vs trending markets
3. Expected drawdown profile and Calmar ratio
4. Which is better for a single asset vs a diversified multi-asset crypto portfolio?
5. How does confidence-scaled sizing (Signal C) affect risk-adjusted returns vs a fixed 2% rule,
   and what is the main failure mode in low-volatility, choppy regimes?

Give a concrete recommendation with specific parameter values.\
"""

_FINANCE_SWEEP = """\
You are a quantitative analyst interpreting two parameter sensitivity sweeps for
ETH trend-following strategies. Both sweeps used 227 days of 2024 ETH daily OHLC
data, 0.10% fee + 0.05% slippage per side, and report: total_return_pct, sharpe,
sortino, calmar, max_drawdown_pct, win_rate_pct, n_trades.

Sweep 1 — Donchian pyramid strategy:
  entry_window : [15, 20, 25]   (breakout lookback, days)
  n_tranches   : [1, 2, 3]      (pyramid tranches; 1 = single entry)
  Fixed: exit_window=10, ATR(14) trailing stop at 3×ATR, 2% risk per tranche.

Sweep 2 — Confidence-weighted SMA crossover (Signal C):
  short_sma    : [3, 5, 8]      (fast SMA period, days)
  long_sma     : [15, 20, 25]   (slow SMA period, days)
  Fixed: SMA(50) trend filter, ATR(14) trailing stop at 3×ATR, base_risk=2%,
         confidence_scale=15 (position multiplier), SMA(50) restart-persistence enabled.

Questions:
1. In Sweep 1, which entry_window / n_tranches combination would you expect to
   show the best Calmar ratio, and why?
2. In Sweep 2, how does the ratio short_sma / long_sma affect signal quality?
   At what ratio does the crossover become too noisy or too slow?
3. Across both sweeps, which strategy family — pyramid Donchian or confidence-
   weighted SMA — is more robust to parameter choice on a small 227-day sample?
4. What is the right way to select a final configuration given the small sample
   size, and what additional validation would you require before trading live?\
"""

_FINANCE_SMA_CONFIDENCE = """\
You are a quantitative analyst evaluating a confidence-weighted SMA crossover
strategy for daily ETH trading.

Strategy: Confidence-Weighted SMA Crossover (ETH, daily bars)
──────────────────────────────────────────────────────────────────────────────────
Entry  : SMA(5) crosses above SMA(20) AND SMA(20) > SMA(50) (trend filter).
Confidence: Normalised SMA spread = (SMA(5) − SMA(20)) / SMA(20).
           A wider spread signals a stronger trend and justifies a larger position.
Sizing : base_risk = 2% of equity.
         position_size = base_risk × clamp(1 + spread × 15, 0.5, 2.0)
         (scales from 1% equity at a weak crossover to 4% at a high-conviction one)
Exit   : SMA(5) crosses below SMA(20) OR ATR(14) trailing stop at 3×ATR below peak.
Restart: Last SMA(5), SMA(20), and SMA(50) values are persisted every 10 bars so
         the strategy recovers the correct signal state after a process restart.
Costs  : 0.10% taker fee + 0.05% slippage per side.
Metrics: Sharpe, Sortino (downside-only volatility), Calmar (CAGR / max-drawdown).

Questions:
1. Does confidence-scaled sizing improve or degrade risk-adjusted return vs a fixed
   2% rule? Which metric — Sortino or Calmar — would you expect to improve most, and why?
2. What is the main failure mode in low-volatility, choppy markets where the SMA
   spread stays narrow for extended periods?
3. How should the spread multiplier (currently ×15) be calibrated without overfitting
   to the backtest window? What data or cross-validation approach would you use?
4. Propose one additional filter (e.g. volume, volatility regime, or a macro signal)
   that would improve the quality of high-confidence signals without significantly
   reducing trade frequency.\
"""

_FINANCE_DCA = """\
You are a quantitative analyst comparing Dollar-Cost Averaging (DCA) against a
trend-following entry for ETH daily trading.

Strategy A — Fixed-Interval DCA:
  Execution : Buy a fixed USD amount of ETH every 7 calendar days, unconditionally.
  Exit      : No exit; positions accumulate indefinitely (long-only hold).
  Costs     : 0.10% taker fee per purchase. No slippage assumed (limit order DCA).
  Metrics   : TWAP cost basis, total return, max portfolio drawdown, Sharpe vs buy-and-hold.

Strategy B — SMA Golden/Death Cross (for comparison):
  BUY  when SMA(5) crosses above SMA(20) AND SMA(20) > SMA(50).
  SELL when SMA(5) crosses below SMA(20) OR ATR(14) trailing stop hit (3×ATR below peak).
  Sizing: 2% equity risk per trade; 0.10% fee + 0.05% slippage per side.

Questions:
1. Under which market regimes (sustained uptrend, sideways chop, sharp crash) does DCA
   outperform or underperform the SMA crossover entry? Quantify the directional impact
   on average cost basis and max drawdown for each regime.
2. How does purchase interval (weekly vs monthly) affect TWAP cost basis and volatility
   drag on a high-volatility asset like ETH? What interval minimises basis risk?
3. DCA eliminates timing risk but carries continuous drawdown exposure. Propose one
   signal-based filter (e.g. a volatility gate or trend confirmation) that preserves
   DCA simplicity while reducing drawdown during sustained bear markets, and estimate
   the expected improvement in Calmar ratio.\
"""

_FINANCE_PORTFOLIO_ROTATION = """\
You are a quantitative analyst evaluating a systematic momentum rotation strategy
across a multi-asset crypto portfolio.

Strategy: Weekly Momentum Rotation (BTC / ETH / SOL + USDC reserve)
──────────────────────────────────────────────────────────────────────────────────
Assets  : BTC, ETH, SOL as tradeable assets; 20% USDC cash reserve at all times.
Signal  : Each Monday, rank the three assets by 30-day momentum (total return).
          Allocate the 80% risk budget entirely to the top-ranked asset.
Rebalance: Execute rotation every 7 days OR immediately if the top-ranked asset changes.
Costs   : 0.10% taker fee + 0.05% slippage per rotation trade.
Metrics : Sharpe, Sortino, Calmar ratio, max drawdown, annual turnover.

Questions:
1. BTC, ETH, and SOL frequently exhibit correlation > 0.85 during macro risk-off events.
   What is the principal failure mode of momentum rotation under high correlation, and
   how should the strategy adapt its rebalancing logic to reduce whipsaw costs?
2. How should the 20% USDC reserve be sized dynamically — e.g. scaled by a volatility
   measure or correlation signal — to balance drawdown protection and return drag during
   sustained bull markets?
3. Compare weekly calendar rebalancing to a threshold-based trigger (rebalance only when
   the top-ranked asset changes). Estimate the effect on annual turnover and Calmar ratio.
4. Propose one uncorrelated asset (e.g. a commodity index, stablecoin yield, or a
   volatility instrument) whose inclusion would meaningfully reduce portfolio drawdown
   without sacrificing momentum signal quality. Justify with correlation assumptions.\
"""

_FINANCE_VOLUME_BREAKOUT = """\
You are a quantitative analyst evaluating a volume-confirmed SMA crossover strategy
for daily ETH trading, where position size scales with volume conviction.

Strategy: Volume-Confirmed SMA Crossover (ETH, daily bars)
──────────────────────────────────────────────────────────────────────────────────
Entry  : SMA(5) crosses above SMA(20) AND SMA(20) > SMA(50) (trend filter)
         AND today's volume > 1.5× the 20-day average volume (volume gate).
Volume ratio: vol_ratio = clamp(today_vol / avg_vol_20, 0.5, 2.0)
Sizing : base_risk = 2% of equity.
         position_size = base_risk × vol_ratio
         (scales from 1% equity on thin-volume crossovers to 4% on high-conviction spikes)
Exit   : SMA(5) crosses below SMA(20) OR ATR(14) trailing stop at 3×ATR below peak.
Costs  : 0.10% taker fee + 0.05% slippage per side.
Metrics: Sharpe, Sortino, Calmar ratio, false signal rate, trade count.

Questions:
1. Requiring volume > 1.5× average reduces entries in range-bound markets. Estimate the
   expected false-signal reduction and the corresponding cost in missed genuine breakouts.
   At what volume threshold does the filter become too restrictive?
2. Compare volume-scaled sizing (vol_ratio × base_risk) to fixed 2% sizing on Sortino and
   Calmar. In what volatility regime is volume scaling most and least beneficial?
3. Centralised-exchange volume is susceptible to wash trading and spoofing. Propose two
   alternative liquidity or market-microstructure signals that would be more robust for
   on-chain or cross-venue ETH trading.
4. Combine this strategy's volume gate with the confidence-weighted SMA spread from the
   Confidence-Weighted SMA Crossover strategy. Write a concrete composite entry rule
   that uses both signals, and identify the dominant failure mode of the combined filter.\
"""

_SWE_3SUM = """\
Solve the following algorithm problem. Provide a working Python solution, then
analyse time and space complexity.

Problem — 3Sum (LeetCode #15):
  Given an integer array nums, return all unique triplets [a, b, c] such that
  a + b + c == 0 and the indices i, j, k are distinct.

Example:
  Input : nums = [-1, 0, 1, 2, -1, -4]
  Output: [[-1, -1, 2], [-1, 0, 1]]

Constraints: 3 ≤ len(nums) ≤ 3000, −10⁵ ≤ nums[i] ≤ 10⁵

After presenting the solution, explain why a naïve O(n³) approach is too slow
and how your approach achieves better complexity.\
"""

_MATH_OLYMPIAD = """\
Solve the following competition mathematics problem. Show all reasoning steps.

Problem:
  Let p be a prime number and let a, b be positive integers such that
      a + b = p   and   lcm(a, b) = 165.
  Find all possible values of p.

(lcm denotes the least common multiple.)

After solving, explain which property of primes is essential to your argument
and whether the approach generalises to other values of lcm(a, b).\
"""


USE_CASES: list[UseCase] = [
    UseCase(
        id="finance-strategy-review",
        category="Finance",
        title="Review an ETH trend-following strategy (pyramid entries)",
        prompt=_FINANCE_STRATEGY,
    ),
    UseCase(
        id="finance-signal-compare",
        category="Finance",
        title="Donchian breakout (pyramid) vs SMA crossover",
        prompt=_FINANCE_SIGNALS,
    ),
    UseCase(
        id="finance-sweep-analysis",
        category="Finance",
        title="Interpret a parameter sweep: entry window vs pyramid tranches",
        prompt=_FINANCE_SWEEP,
    ),
    UseCase(
        id="finance-sma-confidence",
        category="Finance",
        title="Confidence-weighted SMA crossover: sizing and failure modes",
        prompt=_FINANCE_SMA_CONFIDENCE,
    ),
    UseCase(
        id="finance-dca-vs-trend",
        category="Finance",
        title="DCA vs SMA crossover: regime analysis and hybrid filter",
        prompt=_FINANCE_DCA,
    ),
    UseCase(
        id="finance-portfolio-rotation",
        category="Finance",
        title="Multi-asset momentum rotation: BTC / ETH / SOL",
        prompt=_FINANCE_PORTFOLIO_ROTATION,
    ),
    UseCase(
        id="finance-volume-breakout",
        category="Finance",
        title="Volume-confirmed SMA crossover: sizing and signal quality",
        prompt=_FINANCE_VOLUME_BREAKOUT,
    ),
    UseCase(
        id="swe-3sum",
        category="Software Engineering",
        title="3Sum — algorithm + complexity",
        prompt=_SWE_3SUM,
    ),
    UseCase(
        id="math-prime-lcm",
        category="Mathematics",
        title="Olympiad: primes and LCM",
        prompt=_MATH_OLYMPIAD,
    ),
]
