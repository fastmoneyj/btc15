# BTC 15-Minute Predictor

## Latest call: **UP**
Oct 24, 3:30 AM PT at $80,509 · P(up) 50.8% · lean · resolves 3:45 AM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 72/140 (51.4%) | 29/52 (55.8%) | 51.0% over 96 calls | 51.4% |

Model retrained Oct 24 3:20 AM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.515 | 51.4% |
| gboost | base | 21 | 0.497 | 50.2% |
| logistic | expanded | 36 | 0.500 | 48.6% |
| gboost | expanded | 36 | 0.490 | 48.9% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 140 | 0 | — | — | — | — |
| Kalshi | 140 | 94 | 42.6% | 0.40 | +$0.97 | model 0.2457 vs market 0.2422 (139 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 24 3:30 AM | $80,509 | 50.8% | UP (lean) | 0.53/0.54 | 0.52/0.53 | pending | pending |
| Oct 24 3:15 AM | $80,497 | 53.4% | UP | 0.48/0.49 | 0.47/0.48 | $80,509 | ✅ right |
| Oct 24 3:00 AM | $80,516 | 52.9% | UP (lean) | 0.54/0.55 | 0.44/0.45 | $80,497 | ❌ wrong |
| Oct 24 2:45 AM | $80,378 | 59.3% | UP | 0.53/0.54 | 0.53/0.54 | $80,516 | ✅ right |
| Oct 24 2:30 AM | $80,484 | 55.6% | UP | 0.56/0.57 | 0.54/0.55 | $80,378 | ❌ wrong |
| Oct 24 2:15 AM | $80,535 | 53.3% | UP | 0.44/0.45 | 0.44/0.45 | $80,484 | ❌ wrong |
| Oct 24 2:00 AM | $80,604 | 54.7% | UP | 0.45/0.46 | 0.48/0.49 | $80,535 | ❌ wrong |
| Oct 24 1:45 AM | $80,531 | 58.1% | UP | 0.46/0.47 | 0.47/0.48 | $80,604 | ✅ right |
| Oct 24 1:30 AM | $80,698 | 54.3% | UP | 0.48/0.49 | 0.50/0.51 | $80,531 | ❌ wrong |
| Oct 24 1:15 AM | $80,687 | 53.4% | UP | 0.56/0.57 | 0.57/0.58 | $80,698 | ✅ right |
| Oct 24 1:00 AM | $80,636 | 54.5% | UP | 0.57/0.58 | 0.56/0.57 | $80,687 | ✅ right |
| Oct 24 12:45 AM | $80,732 | 51.7% | UP (lean) | 0.49/0.50 | 0.47/0.48 | $80,636 | ❌ wrong |
| Oct 24 12:30 AM | $80,699 | 52.9% | UP (lean) | 0.43/0.44 | 0.45/0.46 | $80,732 | ✅ right |
| Oct 24 12:15 AM | $80,707 | 50.8% | UP (lean) | 0.41/0.42 | 0.43/0.44 | $80,699 | ❌ wrong |
| Oct 24 12:00 AM | $80,680 | 50.5% | UP (lean) | 0.34/0.35 | 0.38/0.39 | $80,707 | ✅ right |
| Oct 23 11:45 PM | $80,662 | 52.4% | UP (lean) | 0.49/0.50 | 0.48/0.49 | $80,680 | ✅ right |
| Oct 23 11:30 PM | $80,677 | 53.5% | UP | 0.47/0.48 | 0.48/0.49 | $80,662 | ❌ wrong |
| Oct 23 11:15 PM | $80,658 | 55.6% | UP | 0.36/0.37 | 0.38/0.39 | $80,677 | ✅ right |
| Oct 23 11:00 PM | $80,655 | 56.4% | UP | 0.46/0.47 | 0.49/0.50 | $80,658 | ✅ right |
| Oct 23 10:45 PM | $80,658 | 55.2% | UP | 0.51/0.52 | 0.52/0.53 | $80,655 | ❌ wrong |
| Oct 23 10:30 PM | $80,661 | 56.1% | UP | 0.61/0.62 | 0.59/0.60 | $80,658 | ❌ wrong |
| Oct 23 10:15 PM | $80,743 | 57.9% | UP | 0.61/0.62 | 0.60/0.61 | $80,661 | ❌ wrong |
| Oct 23 10:00 PM | $80,782 | 52.2% | UP (lean) | 0.52/0.53 | 0.52/0.53 | $80,743 | ❌ wrong |
| Oct 23 9:45 PM | $80,780 | 53.1% | UP | 0.39/0.40 | 0.42/0.43 | $80,782 | ✅ right |
| Oct 23 9:30 PM | $80,760 | 54.2% | UP | 0.50/0.51 | 0.54/0.55 | $80,780 | ✅ right |
| Oct 23 9:15 PM | $80,804 | 55.6% | UP | 0.54/0.55 | 0.00/0.00 | $80,760 | ❌ wrong |
| Oct 23 9:00 PM | $80,866 | 51.9% | UP (lean) | 0.40/0.41 | 0.41/0.42 | $80,804 | ❌ wrong |
| Oct 23 8:45 PM | $80,846 | 52.2% | UP (lean) | 0.48/0.49 | 0.49/0.50 | $80,866 | ✅ right |
| Oct 23 8:30 PM | $80,860 | 49.5% | DOWN (lean) | 0.50/0.51 | 0.49/0.50 | $80,846 | ✅ right |
| Oct 23 8:15 PM | $80,875 | 52.3% | UP (lean) | 0.53/0.54 | 0.54/0.55 | $80,860 | ❌ wrong |
| Oct 23 8:00 PM | $80,889 | 50.0% | DOWN (lean) | 0.47/0.48 | 0.51/0.52 | $80,875 | ✅ right |
| Oct 23 7:45 PM | $80,834 | 50.6% | UP (lean) | 0.50/0.51 | 0.50/0.51 | $80,889 | ✅ right |
| Oct 23 7:30 PM | $80,855 | 49.5% | DOWN (lean) | 0.40/0.41 | 0.42/0.43 | $80,834 | ✅ right |
| Oct 23 7:15 PM | $80,827 | 47.2% | DOWN (lean) | 0.45/0.46 | 0.46/0.47 | $80,855 | ❌ wrong |
| Oct 23 7:00 PM | $80,823 | 49.0% | DOWN (lean) | 0.44/0.45 | 0.47/0.48 | $80,827 | ❌ wrong |
| Oct 23 6:45 PM | $80,738 | 51.2% | UP (lean) | 0.48/0.49 | 0.50/0.51 | $80,823 | ✅ right |
| Oct 23 6:15 PM | $80,669 | 55.4% | UP | 0.60/0.61 | 0.64/0.65 | $80,709 | ✅ right |
| Oct 23 6:00 PM | $80,508 | 59.9% | UP | 0.48/0.49 | 0.49/0.50 | $80,669 | ✅ right |
| Oct 23 5:45 PM | $80,534 | 56.8% | UP | 0.53/0.54 | 0.53/0.54 | $80,508 | ❌ wrong |
| Oct 23 5:30 PM | $80,680 | 53.7% | UP | 0.49/0.51 | 0.49/0.50 | $80,534 | ❌ wrong |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
