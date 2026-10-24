# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 23, 7:15 PM PT at $80,827 · P(up) 47.2% · lean · resolves 7:30 PM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 55/107 (51.4%) | 20/34 (58.8%) | 50.0% over 96 calls | 51.1% |

Model retrained Oct 23 6:35 PM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.513 | 51.1% |
| gboost | base | 21 | 0.506 | 50.2% |
| logistic | expanded | 36 | 0.500 | 48.4% |
| gboost | expanded | 36 | 0.494 | 49.4% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 107 | 0 | — | — | — | — |
| Kalshi | 107 | 74 | 43.2% | 0.39 | +$2.10 | model 0.2450 vs market 0.2420 (106 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 23 7:15 PM | $80,827 | 47.2% | DOWN (lean) | 0.45/0.46 | 0.46/0.47 | pending | pending |
| Oct 23 7:00 PM | $80,823 | 49.0% | DOWN (lean) | 0.44/0.45 | 0.47/0.48 | $80,827 | ❌ wrong |
| Oct 23 6:45 PM | $80,738 | 51.2% | UP (lean) | 0.48/0.49 | 0.50/0.51 | $80,823 | ✅ right |
| Oct 23 6:15 PM | $80,669 | 55.4% | UP | 0.60/0.61 | 0.64/0.65 | $80,709 | ✅ right |
| Oct 23 6:00 PM | $80,508 | 59.9% | UP | 0.48/0.49 | 0.49/0.50 | $80,669 | ✅ right |
| Oct 23 5:45 PM | $80,534 | 56.8% | UP | 0.53/0.54 | 0.53/0.54 | $80,508 | ❌ wrong |
| Oct 23 5:30 PM | $80,680 | 53.7% | UP | 0.49/0.51 | 0.49/0.50 | $80,534 | ❌ wrong |
| Oct 23 5:15 PM | $80,830 | 51.7% | UP (lean) | 0.42/0.43 | 0.40/0.41 | $80,680 | ❌ wrong |
| Oct 23 5:00 PM | $81,078 | 47.2% | DOWN (lean) | 0.45/0.46 | 0.46/0.47 | $80,830 | ✅ right |
| Oct 23 4:45 PM | $80,882 | 47.0% | DOWN | 0.57/0.58 | 0.63/0.64 | $81,078 | ❌ wrong |
| Oct 23 4:30 PM | $80,843 | 49.5% | DOWN (lean) | 0.38/0.39 | 0.42/0.43 | $80,882 | ❌ wrong |
| Oct 23 4:15 PM | $80,566 | 55.6% | UP | 0.57/0.59 | 0.55/0.56 | $80,843 | ✅ right |
| Oct 23 4:00 PM | $80,720 | 52.4% | UP (lean) | 0.57/0.58 | 0.55/0.56 | $80,566 | ❌ wrong |
| Oct 23 3:45 PM | $81,000 | 52.1% | UP (lean) | 0.51/0.52 | 0.50/0.51 | $80,720 | ❌ wrong |
| Oct 23 3:30 PM | $81,238 | 49.0% | DOWN (lean) | 0.35/0.36 | 0.38/0.39 | $81,000 | ✅ right |
| Oct 23 3:15 PM | $81,234 | 50.3% | UP (lean) | 0.53/0.54 | 0.50/0.51 | $81,238 | ✅ right |
| Oct 23 3:00 PM | $81,280 | 47.8% | DOWN (lean) | 0.62/0.63 | 0.54/0.55 | $81,234 | ✅ right |
| Oct 23 2:45 PM | $81,254 | 47.6% | DOWN (lean) | 0.55/0.56 | 0.00/0.00 | $81,280 | ❌ wrong |
| Oct 23 2:30 PM | $81,296 | 47.2% | DOWN (lean) | 0.38/0.39 | 0.00/0.00 | $81,254 | ✅ right |
| Oct 23 2:15 PM | $81,330 | 46.8% | DOWN | 0.50/0.51 | 0.50/0.51 | $81,296 | ✅ right |
| Oct 23 2:00 PM | $81,311 | 48.2% | DOWN (lean) | 0.43/0.43 | 0.43/0.44 | $81,330 | ❌ wrong |
| Oct 23 1:45 PM | $81,387 | 42.5% | DOWN | 0.56/0.57 | 0.57/0.58 | $81,311 | ✅ right |
| Oct 23 1:30 PM | $81,324 | 43.5% | DOWN | 0.49/0.50 | 0.50/0.51 | $81,387 | ❌ wrong |
| Oct 23 1:15 PM | $81,258 | 47.9% | DOWN (lean) | 0.43/0.45 | 0.47/0.48 | $81,324 | ❌ wrong |
| Oct 23 1:00 PM | $81,184 | 50.9% | UP (lean) | 0.62/0.63 | 0.63/0.64 | $81,258 | ✅ right |
| Oct 23 12:45 PM | $81,236 | 49.7% | DOWN (lean) | 0.59/0.60 | 0.57/0.58 | $81,184 | ✅ right |
| Oct 23 12:30 PM | $81,257 | 51.9% | UP (lean) | 0.44/0.45 | 0.48/0.49 | $81,236 | ❌ wrong |
| Oct 23 12:15 PM | $81,199 | 54.8% | UP | 0.56/0.58 | 0.56/0.57 | $81,257 | ✅ right |
| Oct 23 12:00 PM | $81,338 | 51.9% | UP (lean) | 0.56/0.57 | 0.56/0.57 | $81,199 | ❌ wrong |
| Oct 23 11:45 AM | $81,377 | 50.5% | UP (lean) | 0.46/0.47 | 0.46/0.47 | $81,338 | ❌ wrong |
| Oct 23 11:30 AM | $81,449 | 51.9% | UP (lean) | 0.46/0.47 | 0.48/0.49 | $81,377 | ❌ wrong |
| Oct 23 11:15 AM | $81,506 | 49.6% | DOWN (lean) | 0.63/0.64 | 0.65/0.66 | $81,449 | ✅ right |
| Oct 23 11:00 AM | $81,541 | 50.2% | UP (lean) | 0.37/0.38 | 0.38/0.39 | $81,506 | ❌ wrong |
| Oct 23 10:45 AM | $81,475 | 52.1% | UP (lean) | 0.55/0.56 | 0.54/0.55 | $81,541 | ✅ right |
| Oct 23 10:30 AM | $81,539 | 50.3% | UP (lean) | 0.53/0.54 | 0.51/0.52 | $81,475 | ❌ wrong |
| Oct 23 10:15 AM | $81,699 | 48.1% | DOWN (lean) | 0.55/0.58 | 0.52/0.53 | $81,539 | ✅ right |
| Oct 23 10:00 AM | $81,611 | 47.7% | DOWN (lean) | 0.53/0.54 | 0.52/0.53 | $81,699 | ❌ wrong |
| Oct 23 9:45 AM | $81,657 | 48.9% | DOWN (lean) | 0.53/0.54 | 0.00/0.00 | $81,611 | ✅ right |
| Oct 23 9:30 AM | $81,393 | 49.2% | DOWN (lean) | 0.54/0.55 | 0.00/0.00 | $81,657 | ❌ wrong |
| Oct 23 9:15 AM | $81,470 | 51.5% | UP (lean) | 0.37/0.38 | 0.38/0.39 | $81,393 | ❌ wrong |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
