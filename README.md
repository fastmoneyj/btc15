# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 23, 2:00 PM PT at $81,311 · P(up) 48.2% · lean · resolves 2:15 PM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 45/87 (51.7%) | 16/27 (59.3%) | 51.7% over 87 calls | 51.4% |

Model retrained Oct 23 1:20 PM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.514 | 51.4% |
| gboost | base | 21 | 0.505 | 50.7% |
| logistic | expanded | 36 | 0.500 | 48.4% |
| gboost | expanded | 36 | 0.498 | 49.3% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 87 | 0 | — | — | — | — |
| Kalshi | 87 | 62 | 43.5% | 0.39 | +$1.66 | model 0.2464 vs market 0.2396 (86 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 23 2:00 PM | $81,311 | 48.2% | DOWN (lean) | 0.43/0.43 | 0.43/0.44 | pending | pending |
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
| Oct 23 9:00 AM | $81,582 | 47.7% | DOWN (lean) | 0.41/0.42 | 0.43/0.44 | $81,470 | ✅ right |
| Oct 23 8:45 AM | $81,380 | 49.7% | DOWN (lean) | 0.49/0.50 | 0.49/0.50 | $81,582 | ❌ wrong |
| Oct 23 8:30 AM | $81,490 | 47.0% | DOWN | 0.57/0.58 | 0.57/0.58 | $81,380 | ✅ right |
| Oct 23 8:15 AM | $81,375 | 50.8% | UP (lean) | 0.53/0.54 | 0.52/0.53 | $81,490 | ✅ right |
| Oct 23 8:00 AM | $81,679 | 49.8% | DOWN (lean) | 0.51/0.52 | 0.50/0.51 | $81,375 | ✅ right |
| Oct 23 7:45 AM | $81,729 | 48.4% | DOWN (lean) | 0.49/0.50 | 0.49/0.50 | $81,679 | ✅ right |
| Oct 23 7:30 AM | $81,339 | 48.3% | DOWN (lean) | 0.72/0.73 | 0.71/0.72 | $81,729 | ❌ wrong |
| Oct 23 7:15 AM | $81,558 | 54.7% | UP | 0.60/0.61 | 0.57/0.58 | $81,339 | ❌ wrong |
| Oct 23 7:00 AM | $81,891 | 47.7% | DOWN (lean) | 0.47/0.48 | 0.51/0.52 | $81,558 | ✅ right |
| Oct 23 6:45 AM | $81,882 | 47.3% | DOWN (lean) | 0.34/0.35 | 0.33/0.34 | $81,891 | ❌ wrong |
| Oct 23 6:30 AM | $81,592 | 51.9% | UP (lean) | 0.55/0.56 | 0.52/0.53 | $81,882 | ✅ right |
| Oct 23 6:15 AM | $81,547 | 49.5% | DOWN (lean) | 0.40/0.42 | 0.39/0.40 | $81,592 | ❌ wrong |
| Oct 23 6:00 AM | $81,637 | 47.9% | DOWN (lean) | 0.41/0.42 | 0.38/0.39 | $81,547 | ✅ right |
| Oct 23 5:45 AM | $81,674 | 48.1% | DOWN (lean) | 0.48/0.49 | 0.50/0.51 | $81,637 | ✅ right |
| Oct 23 5:30 AM | $81,599 | 49.7% | DOWN (lean) | 0.59/0.60 | 0.61/0.62 | $81,674 | ❌ wrong |
| Oct 23 5:15 AM | $81,402 | 52.4% | UP (lean) | 0.48/0.49 | 0.48/0.49 | $81,599 | ✅ right |
| Oct 23 5:00 AM | $81,616 | 48.9% | DOWN (lean) | 0.47/0.49 | 0.00/0.00 | $81,402 | ✅ right |
| Oct 23 4:45 AM | $81,586 | 48.4% | DOWN (lean) | 0.35/0.36 | 0.35/0.36 | $81,616 | ❌ wrong |
| Oct 23 4:30 AM | $81,567 | 50.6% | UP (lean) | 0.56/0.57 | 0.54/0.55 | $81,586 | ✅ right |
| Oct 23 4:15 AM | $81,498 | 48.7% | DOWN (lean) | 0.63/0.64 | 0.60/0.61 | $81,567 | ❌ wrong |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
