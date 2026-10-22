# BTC 15-Minute Predictor

## Latest call: **UP**
Oct 22, 4:00 PM PT at $81,246 · P(up) 50.6% · lean · resolves 4:15 PM

| Live record | Confident calls | Last 24 h | Model holdout accuracy |
|---|---|---|---|
| 2/3 (66.7%) | 2/2 (100.0%) | 66.7% over 3 calls | 50.8% |

Model retrained Oct 22 3:10 PM PT on 16,989 fifteen-minute windows from the last 60 days. It retrains every hour, so every new outcome feeds the next model.

## Recent calls

| Time (PT) | Price | P(up) | Call | 15 min later | Result |
|---|---|---|---|---|---|
| Oct 22 4:00 PM | $81,246 | 50.6% | UP (lean) | pending | pending |
| Oct 22 3:45 PM | $81,216 | 53.0% | UP | $81,246 | ✅ right |
| Oct 22 3:30 PM | $81,280 | 50.6% | UP (lean) | $81,216 | ❌ wrong |
| Oct 22 3:15 PM | $81,350 | 45.0% | DOWN | $81,280 | ✅ right |

Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice.
