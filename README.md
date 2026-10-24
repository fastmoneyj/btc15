# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 24, 11:00 AM PT at $80,167 · P(up) 49.8% · lean · resolves 11:15 AM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 86/170 (50.6%) | 33/64 (51.6%) | 49.0% over 96 calls | 51.3% |

Model retrained Oct 24 10:19 AM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** logistic / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.516 | 51.3% |
| gboost | base | 21 | 0.506 | 50.4% |
| logistic | expanded | 36 | 0.502 | 48.8% |
| gboost | expanded | 36 | 0.500 | 50.1% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 170 | 0 | — | — | — | — |
| Kalshi | 170 | 113 | 40.7% | 0.39 | −$0.37 | model 0.2495 vs market 0.2393 (169 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 24 11:00 AM | $80,167 | 49.8% | DOWN (lean) | 0.53/0.54 | 0.52/0.53 | pending | pending |
| Oct 24 10:45 AM | $80,042 | 50.6% | UP (lean) | 0.50/0.51 | 0.49/0.50 | $80,167 | ✅ right |
| Oct 24 10:30 AM | $80,091 | 51.5% | UP (lean) | 0.43/0.44 | 0.44/0.45 | $80,042 | ❌ wrong |
| Oct 24 10:15 AM | $80,044 | 50.4% | UP (lean) | 0.54/0.55 | 0.55/0.56 | $80,091 | ✅ right |
| Oct 24 10:00 AM | $80,111 | 48.7% | DOWN (lean) | 0.47/0.48 | 0.49/0.50 | $80,044 | ✅ right |
| Oct 24 9:45 AM | $79,778 | 50.0% | DOWN (lean) | 0.50/0.51 | 0.54/0.55 | $80,111 | ❌ wrong |
| Oct 24 9:30 AM | $79,555 | 50.6% | UP (lean) | 0.56/0.57 | 0.54/0.55 | $79,778 | ✅ right |
| Oct 24 9:15 AM | $79,739 | 52.3% | UP (lean) | 0.40/0.41 | 0.40/0.41 | $79,555 | ❌ wrong |
| Oct 24 9:00 AM | $79,691 | 51.0% | UP (lean) | 0.34/0.35 | 0.35/0.36 | $79,739 | ✅ right |
| Oct 24 8:45 AM | $79,343 | 56.2% | UP | 0.50/0.51 | 0.50/0.51 | $79,691 | ✅ right |
| Oct 24 8:30 AM | $79,255 | 55.3% | UP | 0.50/0.51 | 0.49/0.50 | $79,343 | ✅ right |
| Oct 24 8:15 AM | $79,614 | 58.9% | UP | 0.55/0.56 | 0.00/0.00 | $79,255 | ❌ wrong |
| Oct 24 8:00 AM | $80,100 | 56.4% | UP | 0.54/0.55 | 0.52/0.53 | $79,614 | ❌ wrong |
| Oct 24 7:45 AM | $80,143 | 58.9% | UP | 0.56/0.57 | 0.00/0.00 | $80,100 | ❌ wrong |
| Oct 24 7:30 AM | $80,175 | 58.6% | UP | 0.59/0.60 | 0.00/0.00 | $80,143 | ❌ wrong |
| Oct 24 7:15 AM | $80,436 | 61.3% | UP | 0.26/0.27 | 0.27/0.28 | $80,175 | ❌ wrong |
| Oct 24 7:00 AM | $80,593 | 56.1% | UP | 0.61/0.62 | 0.62/0.63 | $80,436 | ❌ wrong |
| Oct 24 6:45 AM | $80,602 | 54.5% | UP | 0.49/0.50 | 0.49/0.50 | $80,593 | ❌ wrong |
| Oct 24 6:30 AM | $80,666 | 51.4% | UP (lean) | 0.49/0.50 | 0.50/0.51 | $80,602 | ❌ wrong |
| Oct 24 6:15 AM | $80,669 | 49.8% | DOWN (lean) | 0.45/0.46 | 0.48/0.49 | $80,666 | ✅ right |
| Oct 24 6:00 AM | $80,677 | 49.2% | DOWN (lean) | 0.46/0.47 | 0.48/0.49 | $80,669 | ✅ right |
| Oct 24 5:45 AM | $80,675 | 48.3% | DOWN (lean) | 0.48/0.49 | 0.49/0.50 | $80,677 | ❌ wrong |
| Oct 24 5:30 AM | $80,673 | 49.0% | DOWN (lean) | 0.46/0.47 | 0.49/0.50 | $80,675 | ❌ wrong |
| Oct 24 5:15 AM | $80,524 | 54.3% | UP | 0.44/0.45 | 0.44/0.45 | $80,673 | ✅ right |
| Oct 24 5:00 AM | $80,487 | 55.6% | UP | 0.34/0.35 | 0.35/0.36 | $80,524 | ✅ right |
| Oct 24 4:45 AM | $80,514 | 55.4% | UP | 0.44/0.45 | 0.46/0.47 | $80,487 | ❌ wrong |
| Oct 24 4:30 AM | $80,470 | 52.1% | UP (lean) | 0.51/0.52 | 0.50/0.51 | $80,514 | ✅ right |
| Oct 24 4:15 AM | $80,556 | 52.8% | UP (lean) | 0.51/0.52 | 0.52/0.53 | $80,470 | ❌ wrong |
| Oct 24 4:00 AM | $80,558 | 49.5% | DOWN (lean) | 0.52/0.53 | 0.55/0.56 | $80,556 | ✅ right |
| Oct 24 3:45 AM | $80,569 | 51.7% | UP (lean) | 0.50/0.51 | 0.50/0.51 | $80,558 | ❌ wrong |
| Oct 24 3:30 AM | $80,509 | 50.8% | UP (lean) | 0.53/0.54 | 0.52/0.53 | $80,569 | ✅ right |
| Oct 24 3:15 AM | $80,497 | 53.4% | UP | 0.48/0.49 | 0.47/0.48 | $80,509 | ✅ right |
| Oct 24 3:00 AM | $80,516 | 52.9% | UP (lean) | 0.54/0.55 | 0.44/0.45 | $80,497 | ❌ wrong |
| Oct 24 2:45 AM | $80,378 | 59.3% | UP | 0.53/0.54 | 0.53/0.54 | $80,516 | ✅ right |
| Oct 24 2:30 AM | $80,484 | 55.6% | UP | 0.56/0.57 | 0.54/0.55 | $80,378 | ❌ wrong |
| Oct 24 2:15 AM | $80,535 | 53.3% | UP | 0.44/0.45 | 0.44/0.45 | $80,484 | ❌ wrong |
| Oct 24 2:00 AM | $80,604 | 54.7% | UP | 0.45/0.46 | 0.48/0.49 | $80,535 | ❌ wrong |
| Oct 24 1:45 AM | $80,531 | 58.1% | UP | 0.46/0.47 | 0.47/0.48 | $80,604 | ✅ right |
| Oct 24 1:30 AM | $80,698 | 54.3% | UP | 0.48/0.49 | 0.50/0.51 | $80,531 | ❌ wrong |
| Oct 24 1:15 AM | $80,687 | 53.4% | UP | 0.56/0.57 | 0.57/0.58 | $80,698 | ✅ right |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
