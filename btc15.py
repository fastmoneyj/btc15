#!/usr/bin/env python3
"""
btc15.py - predict whether BTC-USD will be UP or DOWN 15 minutes from now.

Setup (once):
    pip install pandas numpy scikit-learn requests joblib

Usage:
    python btc15.py train    # download ~90 days of 5-min candles, backtest, save model
    python btc15.py live     # predict at every :00 :15 :30 :45 and score past calls

Data: Coinbase Exchange public candles API (no key needed, works in the US).
A call made at 10:15 means: "BTC's price at 10:30 will be above/below its price at 10:15."
"""
import sys, time, os, datetime as dt
import numpy as np
import pandas as pd
import requests
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, roc_auc_score

API = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
GRAN = 300          # 5-minute candles
HORIZON = 3         # 3 candles ahead = 15 minutes
TRAIN_DAYS = 90
MODEL_FILE = "btc15_model.joblib"
LOG_FILE = "btc15_live_log.csv"
CONF_BAND = 0.03    # "confident" calls are p_up > 0.53 or < 0.47


# ---------------------------------------------------------------- data
def fetch_candles(days):
    """Download `days` of completed 5-min candles, oldest first, on a gap-free grid."""
    now = dt.datetime.now(dt.timezone.utc)
    start_all = now - dt.timedelta(days=days)
    step = dt.timedelta(seconds=GRAN * 300)  # API returns max 300 candles per call
    rows, cur_end, tries = [], now, 0
    while cur_end > start_all:
        cur_start = max(start_all, cur_end - step)
        r = requests.get(API, params={"granularity": GRAN,
                                      "start": cur_start.isoformat(),
                                      "end": cur_end.isoformat()},
                         headers={"User-Agent": "btc15"}, timeout=20)
        if r.status_code == 429 and tries < 5:      # rate limited: back off, retry
            tries += 1
            time.sleep(1.5 * tries)
            continue
        r.raise_for_status()
        rows.extend(r.json())
        cur_end, tries = cur_start, 0
        time.sleep(0.2)
    df = pd.DataFrame(rows, columns=["time", "low", "high", "open", "close", "volume"])
    df = df.drop_duplicates("time").sort_values("time")
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").astype(float)
    # drop the candle still in progress
    df = df[df.index + pd.Timedelta(seconds=GRAN) <= now]
    # fill any missing 5-min slots so shifts mean exactly N*5 minutes
    grid = pd.date_range(df.index[0], df.index[-1], freq=f"{GRAN}s", tz="UTC")
    df = df.reindex(grid)
    df["close"] = df["close"].ffill()
    for col in ["open", "high", "low"]:
        df[col] = df[col].fillna(df["close"])
    df["volume"] = df["volume"].fillna(0.0)
    return df


# ---------------------------------------------------------------- features
def make_features(df):
    c = df["close"]
    lr = np.log(c).diff()
    f = pd.DataFrame(index=df.index)
    for k in [1, 2, 3, 6, 12, 24, 48]:              # returns over 5 min .. 4 hours
        f[f"ret_{k}"] = np.log(c / c.shift(k))
    for k in [6, 12, 48]:                           # realized volatility
        f[f"vol_{k}"] = lr.rolling(k).std()
    f["vol_ratio"] = f["vol_6"] / f["vol_48"]
    v = np.log1p(df["volume"])
    f["volume_z"] = (v - v.rolling(48).mean()) / v.rolling(48).std()
    f["range"] = (df["high"] - df["low"]) / c
    f["body"] = (df["close"] - df["open"]) / c
    for k in [12, 48, 288]:                         # distance from 1h / 4h / 24h average
        f[f"dist_ma{k}"] = c / c.rolling(k).mean() - 1
    d = c.diff()
    up = d.clip(lower=0).rolling(14).mean()
    dn = (-d.clip(upper=0)).rolling(14).mean()
    f["rsi"] = up / (up + dn)
    hour = df.index.hour + df.index.minute / 60
    f["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    f["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    f["weekend"] = (df.index.dayofweek >= 5).astype(float)
    return f.replace([np.inf, -np.inf], np.nan)


def make_target(df):
    future = df["close"].shift(-HORIZON)
    y = (future > df["close"]).astype(float)
    y[future.isna()] = np.nan
    return y


def candidate_models():
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000)),
        "gboost": HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03,
                                                 max_iter=300, min_samples_leaf=200,
                                                 l2_regularization=1.0),
    }


# ---------------------------------------------------------------- train + backtest
def train():
    print(f"Downloading {TRAIN_DAYS} days of 5-min BTC-USD candles from Coinbase...")
    df = fetch_candles(TRAIN_DAYS)
    X, y = make_features(df), make_target(df)
    data = X.join(y.rename("y")).dropna()
    X, y = data.drop(columns="y"), data["y"]
    print(f"{len(X):,} samples, {y.mean():.1%} of 15-min windows went UP\n")

    # walk-forward: train on everything before each fold, test on the fold
    n, folds = len(X), 5
    edges = np.linspace(int(n * 0.4), n, folds + 1).astype(int)
    results = {name: [] for name in list(candidate_models()) + ["momentum", "always_up"]}
    gap = HORIZON  # skip rows whose target overlaps the test period
    for i in range(folds):
        tr_end, te_start, te_end = edges[i] - gap, edges[i], edges[i + 1]
        Xtr, ytr = X.iloc[:tr_end], y.iloc[:tr_end]
        Xte, yte = X.iloc[te_start:te_end], y.iloc[te_start:te_end]
        for name, m in candidate_models().items():
            m.fit(Xtr, ytr)
            p = m.predict_proba(Xte)[:, 1]
            conf = np.abs(p - 0.5) > CONF_BAND
            results[name].append({
                "acc": accuracy_score(yte, p > 0.5),
                "auc": roc_auc_score(yte, p),
                "conf_acc": accuracy_score(yte[conf], p[conf] > 0.5) if conf.any() else np.nan,
                "coverage": conf.mean(),
            })
        mom = (Xte["ret_3"] > 0).astype(float)
        results["momentum"].append({"acc": accuracy_score(yte, mom), "auc": np.nan,
                                    "conf_acc": np.nan, "coverage": np.nan})
        results["always_up"].append({"acc": yte.mean(), "auc": 0.5,
                                     "conf_acc": np.nan, "coverage": np.nan})

    print("Walk-forward backtest (out-of-sample, 5 folds)")
    print(f"{'model':<11}{'accuracy':>10}{'AUC':>8}{'conf. acc':>11}{'% calls conf.':>15}")
    summary = {}
    for name, rs in results.items():
        r = pd.DataFrame(rs).mean()
        summary[name] = r
        fmt = lambda v, pct=True: "   -" if pd.isna(v) else (f"{v:.1%}" if pct else f"{v:.3f}")
        print(f"{name:<11}{fmt(r.acc):>10}{fmt(r.auc, False):>8}"
              f"{fmt(r.conf_acc):>11}{fmt(r.coverage):>15}")

    best = max(candidate_models(), key=lambda k: summary[k]["auc"])
    print(f"\nBest by AUC: {best}. Refitting on all data and saving to {MODEL_FILE}.")
    model = candidate_models()[best].fit(X, y)
    joblib.dump({"model": model, "features": list(X.columns), "name": best,
                 "trained_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                 "backtest": {k: v.to_dict() for k, v in summary.items()}}, MODEL_FILE)
    print("Reality check: AUC 0.50 = coin flip. Anything under ~0.53 is mostly noise,")
    print("and a small edge can vanish entirely after fees or market spreads.")


# ---------------------------------------------------------------- live
def next_quarter_hour(now):
    q = (now.minute // 15 + 1) * 15
    base = now.replace(minute=0, second=0, microsecond=0)
    return base + dt.timedelta(minutes=q)


def score_log(df):
    if not os.path.exists(LOG_FILE):
        return None
    log = pd.read_csv(LOG_FILE, parse_dates=["made_at", "resolve_candle"])
    log["outcome"] = log["outcome"].astype(object)
    open_ = log["outcome"].isna()
    for i in log[open_].index:
        t = log.at[i, "resolve_candle"]
        if t in df.index:
            end_price = df.at[t, "close"]
            went_up = end_price > log.at[i, "price"]
            log.at[i, "end_price"] = end_price
            log.at[i, "outcome"] = "UP" if went_up else "DOWN"
            log.at[i, "correct"] = float(log.at[i, "call"] == log.at[i, "outcome"])
    log.to_csv(LOG_FILE, index=False)
    return log


def live():
    if not os.path.exists(MODEL_FILE):
        sys.exit("No model yet. Run:  python btc15.py train")
    bundle = joblib.load(MODEL_FILE)
    model, cols = bundle["model"], bundle["features"]
    print(f"Loaded {bundle['name']} model trained {bundle['trained_at'][:16]} UTC. Ctrl+C to stop.\n")
    while True:
        target = next_quarter_hour(dt.datetime.now(dt.timezone.utc))
        wait = (target - dt.datetime.now(dt.timezone.utc)).total_seconds() + 8  # let candle close
        print(f"Next call at {target.astimezone().strftime('%H:%M')} local "
              f"(waiting {wait/60:.1f} min)...", flush=True)
        time.sleep(max(wait, 0))
        try:
            df = fetch_candles(days=2)
        except Exception as e:
            print(f"  data error: {e}; retrying next window")
            continue
        X = make_features(df)[cols].dropna()
        t = X.index[-1]
        p_up = float(model.predict_proba(X.iloc[[-1]])[:, 1][0])
        price = df.at[t, "close"]
        call = "UP" if p_up > 0.5 else "DOWN"
        strength = "confident" if abs(p_up - 0.5) > CONF_BAND else "lean"
        # the candle at index t closes at t+5min; that's the "now" price
        made_at = t + pd.Timedelta(seconds=GRAN)
        resolves_at = made_at + pd.Timedelta(minutes=15)
        row = pd.DataFrame([{"made_at": made_at, "resolve_candle": resolves_at - pd.Timedelta(seconds=GRAN),
                             "price": price, "p_up": round(p_up, 4), "call": call,
                             "strength": strength, "end_price": np.nan,
                             "outcome": np.nan, "correct": np.nan}])
        row.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)
        log = score_log(df)
        local = made_at.to_pydatetime().astimezone().strftime("%H:%M")
        print(f"  {local}  BTC ${price:,.0f}  ->  {call}  (P(up)={p_up:.1%}, {strength})")
        if log is not None:
            done = log.dropna(subset=["correct"])
            if len(done):
                conf = done[done["strength"] == "confident"]
                msg = f"  record: {int(done.correct.sum())}/{len(done)} = {done.correct.mean():.1%}"
                if len(conf):
                    msg += f"  | confident calls {conf.correct.mean():.1%} ({len(conf)})"
                print(msg)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "train":
        train()
    elif cmd == "live":
        live()
    else:
        print(__doc__)
