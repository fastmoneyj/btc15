# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 23, 6:00 AM PT at $81,637 · P(up) 47.9% · lean · resolves 6:15 AM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 29/55 (52.7%) | 13/22 (59.1%) | 52.7% over 55 calls | 50.8% |

Model retrained Oct 23 5:22 AM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.512 | 50.8% |
| gboost | base | 21 | 0.505 | 49.9% |
| logistic | expanded | 36 | 0.500 | 48.1% |
| gboost | expanded | 36 | 0.499 | 49.8% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 55 | 0 | — | — | — | — |
| Kalshi | 55 | 42 | 40.5% | 0.40 | −$0.47 | model 0.2445 vs market 0.2229 (54 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 23 6:00 AM | $81,637 | 47.9% | DOWN (lean) | 0.41/0.42 | 0.38/0.39 | pending | pending |
| Oct 23 5:45 AM | $81,674 | 48.1% | DOWN (lean) | 0.48/0.49 | 0.50/0.51 | $81,637 | ✅ right |
| Oct 23 5:30 AM | $81,599 | 49.7% | DOWN (lean) | 0.59/0.60 | 0.61/0.62 | $81,674 | ❌ wrong |
| Oct 23 5:15 AM | $81,402 | 52.4% | UP (lean) | 0.48/0.49 | 0.48/0.49 | $81,599 | ✅ right |
| Oct 23 5:00 AM | $81,616 | 48.9% | DOWN (lean) | 0.47/0.49 | 0.00/0.00 | $81,402 | ✅ right |
| Oct 23 4:45 AM | $81,586 | 48.4% | DOWN (lean) | 0.35/0.36 | 0.35/0.36 | $81,616 | ❌ wrong |
| Oct 23 4:30 AM | $81,567 | 50.6% | UP (lean) | 0.56/0.57 | 0.54/0.55 | $81,586 | ✅ right |
| Oct 23 4:15 AM | $81,498 | 48.7% | DOWN (lean) | 0.63/0.64 | 0.60/0.61 | $81,567 | ❌ wrong |
| Oct 23 4:00 AM | $81,594 | 47.7% | DOWN (lean) | 0.48/0.49 | 0.48/0.49 | $81,498 | ✅ right |
| Oct 23 3:45 AM | $81,586 | 47.0% | DOWN (lean) | 0.44/0.46 | 0.44/0.45 | $81,594 | ❌ wrong |
| Oct 23 3:30 AM | $81,613 | 50.3% | UP (lean) | 0.34/0.35 | 0.33/0.34 | $81,586 | ❌ wrong |
| Oct 23 3:15 AM | $81,705 | 46.6% | DOWN | 0.56/0.57 | 0.55/0.56 | $81,613 | ✅ right |
| Oct 23 3:00 AM | $81,553 | 51.2% | UP (lean) | 0.45/0.46 | 0.45/0.46 | $81,705 | ✅ right |
| Oct 23 2:45 AM | $81,566 | 50.3% | UP (lean) | 0.50/0.51 | 0.50/0.51 | $81,553 | ❌ wrong |
| Oct 23 2:30 AM | $81,535 | 54.0% | UP | 0.68/0.69 | 0.67/0.68 | $81,566 | ✅ right |
| Oct 23 2:15 AM | $81,677 | 44.4% | DOWN | 0.40/0.41 | 0.40/0.41 | $81,535 | ✅ right |
| Oct 23 2:00 AM | $81,645 | 46.7% | DOWN | 0.40/0.41 | 0.40/0.41 | $81,677 | ❌ wrong |
| Oct 23 1:45 AM | $81,729 | 48.1% | DOWN (lean) | 0.44/0.45 | 0.46/0.47 | $81,645 | ✅ right |
| Oct 23 1:30 AM | $81,711 | 47.2% | DOWN (lean) | 0.45/0.46 | 0.46/0.47 | $81,729 | ❌ wrong |
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

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
