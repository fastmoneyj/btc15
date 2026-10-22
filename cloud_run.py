#!/usr/bin/env python3
"""
Hourly cloud job for GitHub Actions.
1. Retrains the model on the latest 60 days (so every new outcome is learned from).
2. Makes a call at each quarter-hour mark for the next hour (:00 :15 :30 :45).
3. Scores past calls and rewrites README.md as a live dashboard, pushing after each call.
"""
import os, time, subprocess, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import btc15 as m

CALLS = "calls.csv"
TRAIN_DAYS = 60
LATE_LIMIT = 240  # skip a call if we reach the mark more than 4 minutes late
COLS = ["made_at", "price", "p_up", "call", "confident", "end_price", "outcome", "correct"]


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def load_calls():
    if os.path.exists(CALLS):
        df = pd.read_csv(CALLS)
        df["outcome"] = df["outcome"].astype(object)
        return df
    return pd.DataFrame(columns=COLS)


def retrain():
    df = m.fetch_candles(TRAIN_DAYS)
    X, y = m.make_features(df), m.make_target(df)
    d = X.join(y.rename("y")).dropna()
    X, y = d.drop(columns="y"), d["y"]
    n = len(X)
    split = int(n * 0.8)
    model = m.candidate_models()["logistic"].fit(X.iloc[:split - m.HORIZON], y.iloc[:split - m.HORIZON])
    p = model.predict_proba(X.iloc[split:])[:, 1]
    holdout_acc = float(((p > 0.5) == y.iloc[split:].values).mean())
    model = m.candidate_models()["logistic"].fit(X, y)
    return model, list(X.columns), holdout_acc, n


def score(calls, df):
    for i in calls.index[calls["outcome"].isna()]:
        made = pd.Timestamp(calls.at[i, "made_at"])
        k = made + pd.Timedelta(minutes=15) - pd.Timedelta(seconds=m.GRAN)
        if k in df.index:
            end = float(df.at[k, "close"])
            calls.at[i, "end_price"] = end
            calls.at[i, "outcome"] = "UP" if end > calls.at[i, "price"] else "DOWN"
            calls.at[i, "correct"] = float(calls.at[i, "call"] == calls.at[i, "outcome"])
    return calls


def write_readme(calls, meta):
    la = "America/Los_Angeles"
    done = calls.dropna(subset=["correct"])
    conf = done[done["confident"] == True]
    rec = f"{int(done.correct.sum())}/{len(done)} ({done.correct.mean():.1%})" if len(done) else "no results yet"
    crec = f"{int(conf.correct.sum())}/{len(conf)} ({conf.correct.mean():.1%})" if len(conf) else "—"
    last24 = done.tail(96)
    r24 = f"{last24.correct.mean():.1%} over {len(last24)} calls" if len(last24) else "—"
    lines = ["# BTC 15-Minute Predictor", ""]
    if len(calls):
        L = calls.iloc[-1]
        t = pd.Timestamp(L["made_at"]).tz_convert(la).strftime("%b %d, %-I:%M %p PT")
        res = pd.Timestamp(L["made_at"]) + pd.Timedelta(minutes=15)
        lines += [f"## Latest call: **{L['call']}**",
                  f"{t} at ${L['price']:,.0f} · P(up) {L['p_up']:.1%} · {'confident' if L['confident'] else 'lean'} · "
                  f"resolves {res.tz_convert(la).strftime('%-I:%M %p')}", ""]
    lines += ["| Live record | Confident calls | Last 24 h | Model holdout accuracy |",
              "|---|---|---|---|",
              f"| {rec} | {crec} | {r24} | {meta['acc']:.1%} |", "",
              f"Model retrained {meta['trained']} on {meta['n']:,} fifteen-minute windows from the last {TRAIN_DAYS} days. "
              "It retrains every hour, so every new outcome feeds the next model.", "",
              "## Recent calls", "", "| Time (PT) | Price | P(up) | Call | 15 min later | Result |", "|---|---|---|---|---|---|"]
    for _, r in calls.tail(40).iloc[::-1].iterrows():
        t = pd.Timestamp(r["made_at"]).tz_convert(la).strftime("%b %d %-I:%M %p")
        end = f"${r['end_price']:,.0f}" if pd.notna(r["end_price"]) else "pending"
        res = "pending" if pd.isna(r["correct"]) else ("✅ right" if r["correct"] else "❌ wrong")
        lines.append(f"| {t} | ${r['price']:,.0f} | {r['p_up']:.1%} | {r['call']}{'' if r['confident'] else ' (lean)'} | {end} | {res} |")
    lines += ["", "Each call compares Coinbase BTC-USD at the quarter-hour mark with the price 15 minutes later. "
              "AUC/accuracy near 50% is a coin flip; a 1–2 point edge can vanish after fees or spreads. Not financial advice."]
    open("README.md", "w").write("\n".join(lines) + "\n")


def push(msg):
    if os.environ.get("BTC15_NO_PUSH"):
        return
    subprocess.run(["git", "add", CALLS, "README.md"], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-q", "-m", msg], check=True)
    for _ in range(3):
        subprocess.run(["git", "pull", "-q", "--rebase", "-X", "theirs"])
        if subprocess.run(["git", "push", "-q"]).returncode == 0:
            return
        time.sleep(5)


def main():
    start = utcnow()
    model, cols, acc, n = retrain()
    meta = {"acc": acc, "n": n, "trained": utcnow().astimezone(ZoneInfo("America/Los_Angeles")).strftime("%b %d %-I:%M %p PT")}
    print(f"retrained on {n} samples, holdout acc {acc:.3f}")
    # quarter marks to cover: from the current one (if still fresh) through ~60 minutes ahead
    q0 = start.replace(second=0, microsecond=0, minute=(start.minute // 15) * 15)
    marks = [q0 + dt.timedelta(minutes=15 * k) for k in range(0, 5)]
    marks = [q for q in marks if q <= start + dt.timedelta(minutes=58)]
    for q in marks:
        wait = (q - utcnow()).total_seconds() + 10
        if wait > 0:
            time.sleep(wait)
        if (utcnow() - q).total_seconds() > LATE_LIMIT + 60:
            print(f"skip {q}: too late")
            continue
        df = None
        for _ in range(8):
            df = m.fetch_candles(2)
            if (pd.Timestamp(q) - pd.Timedelta(seconds=m.GRAN)) in df.index:
                break
            time.sleep(10)
        k = pd.Timestamp(q) - pd.Timedelta(seconds=m.GRAN)
        calls = load_calls()
        if k in df.index and str(pd.Timestamp(q)) not in set(calls["made_at"].astype(str)):
            X = m.make_features(df.loc[:k])[cols].dropna()
            if len(X) and X.index[-1] == k:
                p = float(model.predict_proba(X.iloc[[-1]])[:, 1][0])
                calls.loc[len(calls)] = [str(pd.Timestamp(q)), float(df.at[k, "close"]), round(p, 4),
                                         "UP" if p > 0.5 else "DOWN", abs(p - 0.5) > m.CONF_BAND,
                                         np.nan, np.nan, np.nan]
                print(f"{q}: {'UP' if p > 0.5 else 'DOWN'} p={p:.3f}")
        calls = score(calls, df)
        calls.to_csv(CALLS, index=False)
        write_readme(calls, meta)
        push(f"call {q:%Y-%m-%d %H:%M} UTC")


if __name__ == "__main__":
    main()
