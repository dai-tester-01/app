"""Preset use-cases for model comparison across real-world tasks.

Three categories: software engineering (LeetCode-style), finance strategy
(trend-following design and critique), and mathematics (olympiad problems).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UseCase:
    id: str
    category: str
    title: str
    prompt: str


CATEGORY_LABELS: dict[str, str] = {
    "software_engineering": "Software Engineering",
    "finance": "Finance Strategy",
    "math": "Mathematics",
}

USE_CASES: list[UseCase] = [
    # ------------------------------------------------------------------ #
    # Software Engineering — LeetCode-style algorithmic problems
    # ------------------------------------------------------------------ #
    UseCase(
        id="se_two_sum",
        category="software_engineering",
        title="Two Sum (LeetCode #1)",
        prompt=(
            "Solve LeetCode #1 — Two Sum.\n\n"
            "Given an array of integers `nums` and a target integer, return the indices of the "
            "two numbers that add up to target. Each input has exactly one solution; the same "
            "element may not be used twice.\n\n"
            "Example: nums = [2, 7, 11, 15], target = 9 → [0, 1]\n\n"
            "Requirements:\n"
            "• Python solution with proper type hints.\n"
            "• O(n) time complexity — explain why.\n"
            "• Analyse space complexity.\n"
            "• Handle edge cases (duplicates, negative numbers)."
        ),
    ),
    UseCase(
        id="se_lru_cache",
        category="software_engineering",
        title="LRU Cache (LeetCode #146)",
        prompt=(
            "Solve LeetCode #146 — LRU Cache.\n\n"
            "Implement an `LRUCache` class:\n"
            "• `__init__(capacity: int)` — initialise with positive capacity.\n"
            "• `get(key: int) -> int` — return the value or -1 if missing.\n"
            "• `put(key: int, value: int) -> None` — insert or update; evict the LRU key "
            "when the cache is at capacity.\n\n"
            "Both get and put must run in O(1) average time.\n\n"
            "Provide a Python implementation (OrderedDict or doubly-linked list + hash map), "
            "justify your data-structure choice, and discuss trade-offs."
        ),
    ),
    UseCase(
        id="se_merge_intervals",
        category="software_engineering",
        title="Merge Intervals (LeetCode #56)",
        prompt=(
            "Solve LeetCode #56 — Merge Intervals.\n\n"
            "Given a list of intervals [[start, end], …], merge all overlapping intervals and "
            "return the minimal non-overlapping set.\n\n"
            "Example: [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]\n\n"
            "Requirements:\n"
            "• Python, O(n log n) time.\n"
            "• Explain the sorting step and why it guarantees correctness.\n"
            "• Cover edge cases: empty list, single interval, fully nested intervals, "
            "touching intervals (e.g. [1,4] and [4,6])."
        ),
    ),
    # ------------------------------------------------------------------ #
    # Finance Strategy — trend-following design, critique, and comparison
    # ------------------------------------------------------------------ #
    UseCase(
        id="fin_strategy_design",
        category="finance",
        title="Design a Trend-Following Strategy",
        prompt=(
            "Design a systematic trend-following strategy for ETH/USD daily OHLCV data.\n\n"
            "Your answer must include:\n"
            "1. Entry signal — indicator(s) and exact thresholds (e.g. Donchian channel "
            "breakout above 20-day high, SMA crossover as dual-confirmation: fast SMA > slow "
            "SMA, regime filter: close > 50-day EMA).\n"
            "2. Exit signal — channel break (10-day low), ATR trailing stop (3×ATR below "
            "peak close), and a max-hold-days backstop.\n"
            "3. Position sizing — ATR risk-targeting: risk 2% of equity to a 2×ATR initial "
            "stop, capped at 100% exposure.\n"
            "4. Risk controls — per-trade fees (0.10%) and slippage (0.05%), max drawdown "
            "threshold, and a hard position cap.\n"
            "5. Validation — evaluate using: Sharpe ratio, max drawdown, profit factor, CAGR "
            "vs buy-and-hold, and a monthly DCA periodic-investment baseline.\n\n"
            "Give concrete parameter values. State at least three limitations of the "
            "approach."
        ),
    ),
    UseCase(
        id="fin_backtest_critique",
        category="finance",
        title="Critique a Backtest",
        prompt=(
            "Critically evaluate this backtest for a Donchian channel breakout strategy on "
            "ETH/USD (daily data, 2024):\n\n"
            "• Entry: close > 20-day high AND close > 50-day EMA AND 10-day SMA > 30-day SMA\n"
            "• Exit: close < 10-day low OR price falls 3×ATR below peak close\n"
            "• Sizing: risk 2% of equity to a 2×ATR initial stop; 100% max exposure\n"
            "• Costs: 0.10% taker fee + 0.05% slippage per side\n"
            "• Dataset: 227 days synthetic ETH OHLCV, single asset, no walk-forward\n\n"
            "Identify at least four methodological flaws (look-ahead bias, overfitting, sample "
            "size, synthetic data, single-asset bias, no out-of-sample). For each, explain its "
            "impact and propose a concrete remedy."
        ),
    ),
    UseCase(
        id="fin_dca_vs_trend",
        category="finance",
        title="DCA vs Trend Following",
        prompt=(
            "Compare Dollar-Cost Averaging (DCA) and trend-following for a crypto asset like "
            "ETH over a multi-year horizon:\n\n"
            "1. Describe the exact mechanics of each (entry timing, sizing, exit rules).\n"
            "2. Which wins in a sustained bull market? Bear market? Sideways/choppy market? "
            "Explain using each strategy's payoff structure.\n"
            "3. What role does volatility play in each strategy's returns?\n"
            "4. For a retail investor with monthly free cash flow and a 3-year horizon, which "
            "would you recommend and why?\n"
            "5. Propose a hybrid approach that captures benefits of both.\n\n"
            "Use concrete numbers where possible (typical Sharpe ranges, drawdown ranges). "
            "Flag all assumptions."
        ),
    ),
    # ------------------------------------------------------------------ #
    # Mathematics — olympiad-style proofs and combinatorics
    # ------------------------------------------------------------------ #
    UseCase(
        id="math_functional_eq",
        category="math",
        title="Functional Equation",
        prompt=(
            "Determine all functions f: ℝ → ℝ satisfying\n\n"
            "    f(x · f(y)) + f(y · f(x)) = 2 · f(x) · f(y)\n\n"
            "for all real numbers x, y.\n\n"
            "Provide a complete proof: find all candidate solutions, verify each satisfies "
            "the equation, and prove no others exist. State every non-trivial step."
        ),
    ),
    UseCase(
        id="math_number_theory",
        category="math",
        title="Number Theory (Quadratic Residues)",
        prompt=(
            "Let p be a prime and n a positive integer such that p divides n² + 1. "
            "Prove that either p = 2 or p ≡ 1 (mod 4).\n\n"
            "Your proof must:\n"
            "1. State the key theorem you use (Euler’s criterion or the structure of "
            "(ℤ/pℤ)*).\n"
            "2. Show −1 is a quadratic residue mod p.\n"
            "3. Derive the congruence condition from the order of −1 in the group.\n"
            "4. Handle p = 2 separately.\n\n"
            "Write a clean, competition-style proof."
        ),
    ),
    UseCase(
        id="math_combinatorics",
        category="math",
        title="Combinatorics (Non-Attacking Rooks)",
        prompt=(
            "1. In how many ways can 8 non-attacking rooks be placed on an 8×8 chessboard? "
            "Give a combinatorial argument.\n"
            "2. Generalise: derive the formula for placing k non-attacking rooks on an n×n "
            "board and prove it counts correctly.\n"
            "3. Verify your formula for k=2, n=4 by a direct count or a second argument.\n"
            "4. Extend to a non-square n×m board (n ≥ k, m ≥ k). Prove the new formula."
        ),
    ),
]


def get_use_cases_by_category() -> dict[str, list[UseCase]]:
    """Return use-cases grouped by category, preserving insertion order."""
    result: dict[str, list[UseCase]] = {cat: [] for cat in CATEGORY_LABELS}
    for uc in USE_CASES:
        result[uc.category].append(uc)
    return result
