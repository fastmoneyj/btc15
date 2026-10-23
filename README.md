# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 22, 6:45 PM PT at $81,380 · P(up) 45.9% · confident · resolves 7:00 PM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 7/11 (63.6%) | 4/6 (66.7%) | 63.6% over 11 calls | 50.7% |

Model retrained Oct 22 6:33 PM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** gboost / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.509 | 50.7% |
| gboost | base | 21 | 0.509 | 50.7% |
| logistic | expanded | 36 | 0.498 | 47.8% |
| gboost | expanded | 36 | 0.501 | 50.3% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 11 | 0 | — | — | — | — |
| Kalshi | 11 | 10 | 40.0% | 0.39 | −$0.10 | model 0.2330 vs market 0.1928 (10 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 22 6:45 PM | $81,380 | 45.9% | DOWN | 0.61/0.62 | 0.60/0.61 | pending | pending |
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
