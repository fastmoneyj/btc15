# BTC 15-Minute Predictor

## Latest call: **DOWN**
Oct 22, 4:15 PM PT at $81,267 · P(up) 47.6% · lean · resolves 4:30 PM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 2/2 (100.0%) | 2/2 (100.0%) | 100.0% over 2 calls | 51.1% |

Model retrained Oct 22 4:01 PM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

**In use:** gboost / base inputs (21 features). Each hour four candidates compete on held-out data and the best is kept:

| Model | Inputs | Features | Holdout AUC | Holdout accuracy |
|---|---|---|---|---|
| logistic | base | 21 | 0.508 | 50.8% |
| gboost | base | 21 | 0.508 | 51.1% |
| logistic | expanded | 36 | 0.497 | 48.0% |
| gboost | expanded | 36 | 0.498 | 49.4% |

Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are recorded with every call so they can be added once enough history builds up.

## Model vs. the market (paper tracking only, nothing is traded)

At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is logged only when the model's probability beats the market's ask by 3+ cents, then settled with the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; Kalshi includes its taker fee, Polymarket fees are not included.

| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |
|---|---|---|---|---|---|---|
| Polymarket | 2 | 0 | — | — | — | — |
| Kalshi | 2 | 1 | 100.0% | 0.49 | +$0.49 | model 0.2158 vs market 0.2652 (1 windows) |

If the market's Brier score stays lower than the model's, the market is the better forecaster and the paper P&L should drift negative. That would mean there's no edge to trade.

## Recent calls

| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |
|---|---|---|---|---|---|---|---|
| Oct 22 4:15 PM | $81,267 | 47.6% | DOWN (lean) | 0.52/0.51 | 0.51/0.52 | pending | pending |
| Oct 22 4:00 PM | $81,246 | 53.5% | UP | 0.50/0.49 | 0.48/0.49 | $81,267 | ✅ right |
| Oct 22 3:15 PM | $81,350 | 45.0% | DOWN | — | — | $81,280 | ✅ right |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
