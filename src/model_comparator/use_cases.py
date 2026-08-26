""Pre-built prompt templates for real-world model comparison use-cases."""

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
You are a quantitative analyst comparing two entry signals for an ETH daily strategy.

Signal A — Donchian Breakout with pyramid:
  BUY  when close > max(prior 20-day high) AND close > EMA(50)
  ADD  second/third tranche on each subsequent buy signal while held,
       provided price is 0.5 ATR above the last entry (up to 3 adds total)
  SELL when close < min(prior 10-day low) OR ATR(14) trailing stop hit (3×ATR below peak)

Signal B — SMA Crossover (single entry):
  BUY  when SMA(5) crosses above SMA(20) AND close > SMA(50)
  SELL when SMA(5) crosses below SMA(20) OR ATR(14) trailing stop hit (3×ATR below peak)

Both signals use the same per-tranche position sizing: risk 2% of equity, initial stop 2×ATR.
Evaluation metrics: Sharpe, Sortino, Calmar ratio, max drawdown, profit factor.

Compare on these four dimensions:
1. Entry frequency, lag, and pyramid opportunity rate
2. False signal rate in range-bound vs trending markets
3. Expected drawdown profile and Calmar ratio
4. Which is better for a single asset vs a diversified multi-asset crypto portfolio?

Give a concrete recommendation with specific parameter values.\
"""

_FINANCE_SWEEP = """\
You are a quantitative analyst interpreting a parameter sensitivity sweep for an
ETH trend-following strategy. The sweep grid was:

  entry_window : [15, 20, 25]   (Donchian breakout lookback, days)
  n_tranches   : [1, 2, 3]      (pyramid entry tranches; 1 = single entry)

Each combination was backtested on 227 days of 2024 ETH daily OHLC data with
these fixed parameters: exit_window=10, ATR(14) trailing stop at 3×ATR, 2% risk
per tranche, 0.10% fee + 0.05% slippage per side.

Metrics reported per combination: total_return_pct, sharpe, sortino, calmar,
max_drawdown_pct, win_rate_pct, n_trades.

Questions:
1. Which entry_window / n_tranches combination would you expect to show the best
   Calmar ratio, and why?
2. At what point does adding more tranches likely hurt performance (over-trading,
   compounding drawdown risk)?
3. What is the right way to select a final configuration given the small sample
   size, and what additional validation would you require before trading live?\
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
