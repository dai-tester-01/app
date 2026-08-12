# Use-Cases

This directory contains reference implementations and datasets for the three
real-world task categories exposed as presets in the model comparator UI.

| Category | Description | Directory |
|----------|-------------|-----------|
| Software Engineering | LeetCode-style algorithmic problems | *(prompts only — see `src/model_comparator/use_cases.py`)* |
| Finance Strategy | Trend-following strategy with backtesting | `finance/` |
| Mathematics | Olympiad proofs and combinatorics | *(prompts only — see `src/model_comparator/use_cases.py`)* |

## Finance

The `finance/` subdirectory contains an improved Channel-Breakout ETH
trend-following strategy. Three enhancements were added inspired by the
[the0](https://github.com/alexanderwanyoike/the0) open-source algorithmic
trading platform (no code copied, concepts adapted):

1. **SMA-crossover dual-confirmation** — entry only fires when fast SMA > slow
   SMA, reducing false breakout entries.
2. **DCA periodic-investment baseline** — monthly fixed-amount purchases
   provide a fairer alternative baseline than lump-sum buy-and-hold.
3. **Multi-asset portfolio wrapper** — run the same config across multiple
   OHLCV files and get a summary table of per-asset metrics.

```bash
cd use_cases/finance
pip install pandas numpy
python strategy.py --data data/eth_2024.csv
python strategy.py --data data/eth_2024.csv --no-sma-filter   # compare without filter
```
