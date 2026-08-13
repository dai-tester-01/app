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

Strategy: ETH Channel-Breakout (Donchian / turtle-style)
─────────────────────────────────────────────────────
Entry  : Close breaks above the 20-day high AND close > 50-day EMA.
Exit   : Close breaks below the 10-day low OR price drops 3×ATR(14) below
         the peak close since entry (ATR trailing stop). Force-exit after 90 days.
Sizing : Risk 2% of equity per trade; initial stop 2×ATR; max 100% exposure.
Costs  : 0.10% taker fee + 0.05% slippage per side.

Evaluation criteria for trend-following strategies:
• Sharpe ratio and max drawdown (risk-adjusted view)
• Profit factor (gross win / gross loss)
• Time in market vs buy-and-hold
• False breakout rate

Question: Identify the single biggest structural weakness in these rules and
propose one concrete, parameter-specific fix. Quantify the expected effect on
false breakouts or drawdown if possible.\
"""

_FINANCE_SIGNALS = """\
You are a quantitative analyst comparing two entry signals for an ETH daily strategy.

Signal A — Donchian Breakout:
  BUY  when close > max(prior 20-day high) AND close > EMA(50)
  SELL when close < min(prior 10-day low)  OR ATR(14) trailing stop hit (3×ATR below peak)

Signal B — SMA Crossover:
  BUY  when SMA(5) crosses above SMA(20)   AND close > SMA(50)
  SELL when SMA(5) crosses below SMA(20)   OR ATR(14) trailing stop hit (3×ATR below peak)

Both signals use the same position sizing: risk 2% of equity, initial stop 2×ATR.

Compare on these four dimensions:
1. Entry frequency and lag
2. False signal rate in range-bound vs trending markets
3. Expected drawdown profile
4. Which is better for a single asset vs a diversified multi-asset crypto portfolio?

Give a concrete recommendation with specific parameter values.\
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
        title="Review an ETH trend-following strategy",
        prompt=_FINANCE_STRATEGY,
    ),
    UseCase(
        id="finance-signal-compare",
        category="Finance",
        title="Donchian breakout vs SMA crossover",
        prompt=_FINANCE_SIGNALS,
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
