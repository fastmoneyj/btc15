# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 23, 1:30 AM PT at $81,711 · P(up) 47.2% · lean · resolves 1:45 AM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 19/37 (51.4%) | 10/18 (55.6%) | 51.4% over 37 calls | 50.8% |

Model retrained Oct 23 12:37 AM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.508 | 50.8% |
| gboost | base | 21 | 0.506 | 50.2% |
| logistic | expanded | 36 | 0.496 | 48.1% |
| gboost | expanded | 36 | 0.491 | 49.4% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 37 | 0 | — | — | — | — |
| Kalshi | 37 | 30 | 40.0% | 0.41 | −$0.75 | model 0.2465 vs market 0.2242 (36 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 23 1:30 AM | $81,711 | 47.2% | DOWN (lean) | 0.38/0.39 | 0.38/0.39 | pending | pending |
| Oct 23 1:15 AM | $81,651 | 47.1% | DOWN (lean) | 0.61/0.62 | 0.64/0.65 | $81,711 | ❌ wrong |
| Oct 23 1:00 AM | $81,462 | 54.4% | UP | 0.45/0.46 | 0.42/0.43 | $81,651 | ✅ right |
| Oct 23 12:45 AM | $81,573 | 52.6% | UP (lean) | 0.43/0.44 | 0.44/0.45 | $81,462 | ❌ wrong |
| Oct 23 12:15 AM | $81,694 | 46.3% | DOWN | 0.40/0.41 | 0.39/0.40 | $81,615 | ✅ right |
| Oct 23 12:00 AM | $81,774 | 47.6% | DOWN (lean) | 0.48/0.49 | 0.49/0.50 | $81,694 | ✅ right |
| Oct 22 11:45 PM | $81,772 | 44.7% | DOWN | 0.45/0.46 | 0.46/0.47 | $81,774 | ❌ wrong |
| Oct 22 11:30 PM | $81,724 | 50.8% | UP (lean) | 0.59/0.60 | 0.59/0.60 | $81,772 | ✅ right |
| Oct 22 11:15 PM | $81,787 | 48.9% | DOWN (lean) | 0.51/0.52 | 0.55/0.56 | $81,724 | ✅ right |
| Oct 22 11:00 PM | $81,715 | 45.9% | DOWN | 0.39/0.40 | 0.38/0.39 | $81,787 | ❌ wrong |
| Oct 22 10:45 PM | $81,690 | 46.2% | DOWN | 0.61/0.62 | 0.64/0.65 | $81,715 | ❌ wrong |
| Oct 22 10:30 PM | $81,516 | 53.9% | UP | 0.39/0.42 | 0.39/0.40 | $81,690 | ✅ right |
| Oct 22 10:15 PM | $81,724 | 47.8% | DOWN (lean) | 0.48/0.49 | 0.52/0.53 | $81,516 | ✅ right |
| Oct 22 10:00 PM | $81,471 | 54.9% | UP | 0.61/0.61 | 0.60/0.61 | $81,724 | ✅ right |
| Oct 22 9:45 PM | $81,558 | 50.7% | UP (lean) | 0.52/0.53 | 0.53/0.54 | $81,471 | ❌ wrong |
| Oct 22 9:30 PM | $81,573 | 51.0% | UP (lean) | 0.49/0.50 | 0.48/0.49 | $81,558 | ❌ wrong |
| Oct 22 9:15 PM | $81,628 | 51.6% | UP (lean) | 0.51/0.52 | 0.52/0.53 | $81,573 | ❌ wrong |
| Oct 22 9:00 PM | $81,769 | 51.7% | UP (lean) | 0.43/0.44 | 0.47/0.48 | $81,628 | ❌ wrong |
| Oct 22 8:45 PM | $81,806 | 47.6% | DOWN (lean) | 0.68/0.69 | 0.67/0.68 | $81,769 | ✅ right |
| Oct 22 8:30 PM | $81,665 | 44.8% | DOWN | 0.54/0.55 | 0.52/0.53 | $81,806 | ❌ wrong |
| Oct 22 8:15 PM | $81,763 | 42.5% | DOWN | 0.46/0.47 | 0.47/0.48 | $81,665 | ✅ right |
| Oct 22 8:00 PM | $81,850 | 48.1% | DOWN (lean) | 0.42/0.43 | 0.43/0.44 | $81,763 | ✅ right |
| Oct 22 7:45 PM | $81,753 | 47.0% | DOWN | 0.49/0.50 | 0.53/0.54 | $81,850 | ❌ wrong |
| Oct 22 7:30 PM | $81,516 | 46.4% | DOWN | 0.84/0.85 | 0.83/0.84 | $81,753 | ❌ wrong |
| Oct 22 7:15 PM | $81,291 | 48.8% | DOWN (lean) | 0.45/0.47 | 0.46/0.47 | $81,516 | ❌ wrong |
| Oct 22 7:00 PM | $81,233 | 48.9% | DOWN (lean) | 0.46/0.47 | 0.42/0.43 | $81,291 | ❌ wrong |
| Oct 22 6:45 PM | $81,380 | 45.9% | DOWN | 0.61/0.62 | 0.60/0.61 | $81,233 | ✅ right |
| Oct 22 6:30 PM | $81,371 | 46.4% | DOWN | 0.21/0.22 | 0.21/0.22 | $81,380 | ❌ wrong |
| Oct 22 6:15 PM | $81,325 | 46.3% | DOWN | 0.38/0.39 | 0.42/0.43 | $81,371 | ❌ wrong |
| Oct 22 6:00 PM | $81,343 | 49.9% | DOWN (lean) | 0.54/0.55 | 0.54/0.55 | $81,325 | ✅ right |
| Oct 22 5:45 PM | $81,372 | 45.1% | DOWN | 0.54/0.55 | 0.58/0.59 | $81,343 | ✅ right |
| Oct 22 5:30 PM | $81,101 | 50.8% | UP (lean) | 0.67/0.68 | 0.66/0.67 | $81,372 | ✅ right |
| Oct 22 5:15 PM | $81,137 | 52.3% | UP (lean) | 0.61/0.62 | 0.62/0.63 | $81,101 | ❌ wrong |
| Oct 22 5:00 PM | $81,307 | 44.5% | DOWN | 0.31/0.32 | 0.35/0.36 | $81,137 | ✅ right |
| Oct 22 4:45 PM | $81,244 | 48.8% | DOWN (lean) | 0.68/0.69 | 0.69/0.70 | $81,307 | ❌ wrong |
| Oct 22 4:15 PM | $81,267 | 47.6% | DOWN (lean) | 0.51/0.52 | 0.51/0.52 | $81,212 | ✅ right |
| Oct 22 4:00 PM | $81,246 | 53.5% | UP | 0.49/0.50 | 0.48/0.49 | $81,267 | ✅ right |
| Oct 22 3:15 PM | $81,350 | 45.0% | DOWN | — | — | $81,280 | ✅ right |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
