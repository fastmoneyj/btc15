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
COLS = ["made_at", "price", "p_up", "call", "confident", "end_price", "outcome", "correct",
        "model", "book_imbalance", "flow_imbalance"]


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def load_calls():
    if os.path.exists(CALLS):
        df = pd.read_csv(CALLS).reindex(columns=COLS)
        df["outcome"] = df["outcome"].astype(object)
        df["model"] = df["model"].astype(object)
        return df
    return pd.DataFrame(columns=COLS)


def fetch_extras(days):
    out = {}
    for prod in m.EXTRA_PRODUCTS:
        try:
            out[prod] = m.fetch_candles(days, prod)
        except Exception as e:
            print(f"could not fetch {prod}: {e}")
    return out


def build_X(df, extras, use_extra):
    X = m.make_features(df)
    if use_extra:
        X = m.add_extra_features(X, extras)
    return X


def retrain():
    """Fit 4 candidates (base/expanded inputs x logistic/boosted) and keep the best on a holdout."""
    from sklearn.metrics import roc_auc_score
    df = m.fetch_candles(TRAIN_DAYS)
    extras = fetch_extras(TRAIN_DAYS)
    y_all = m.make_target(df)
    results = []
    for use_extra in ([False, True] if len(extras) == len(m.EXTRA_PRODUCTS) else [False]):
        X = build_X(df, extras, use_extra)
        d = X.join(y_all.rename("y")).dropna()
        X, y = d.drop(columns="y"), d["y"]
        split = int(len(X) * 0.8)
        for name in ["logistic", "gboost"]:
            mod = m.candidate_models()[name].fit(X.iloc[:split - m.HORIZON], y.iloc[:split - m.HORIZON])
            p = mod.predict_proba(X.iloc[split:])[:, 1]
            auc = roc_auc_score(y.iloc[split:], p)
            acc = float(((p > 0.5) == y.iloc[split:].values).mean())
            results.append({"name": name, "extra": use_extra, "auc": auc, "acc": acc, "n": len(X), "X": X, "y": y})
            print(f"{name:8s} {'expanded' if use_extra else 'base':8s} auc={auc:.4f} acc={acc:.4f} features={X.shape[1]}")
    best = max(results, key=lambda r: r["auc"])
    model = m.candidate_models()[best["name"]].fit(best["X"], best["y"])
    label = f"{best['name']} / {'expanded' if best['extra'] else 'base'} inputs ({best['X'].shape[1]} features)"
    table = [(r["name"], "expanded" if r["extra"] else "base", r["X"].shape[1], r["auc"], r["acc"]) for r in results]
    return model, list(best["X"].columns), best["extra"], best["acc"], best["n"], label, table


def order_flow():
    """Snapshot of buy/sell pressure right now. Recorded for future training (no free history exists)."""
    import requests
    book = flow = np.nan
    try:
        b = requests.get(f"{m.BASE}/BTC-USD/book", params={"level": 2}, timeout=10).json()
        bids = [(float(p), float(s)) for p, s, _ in b["bids"]]
        asks = [(float(p), float(s)) for p, s, _ in b["asks"]]
        mid = (bids[0][0] + asks[0][0]) / 2
        bv = sum(s for p, s in bids if p >= mid * 0.999)
        av = sum(s for p, s in asks if p <= mid * 1.001)
        book = (bv - av) / (bv + av) if bv + av else np.nan
    except Exception as e:
        print("book snapshot failed:", e)
    try:
        t = requests.get(f"{m.BASE}/BTC-USD/trades", params={"limit": 1000}, timeout=10).json()
        cutoff = pd.Timestamp.utcnow() - pd.Timedelta(minutes=5)
        buy = sell = 0.0
        for tr in t:
            if pd.Timestamp(tr["time"]) < cutoff:
                continue
            # Coinbase "side" is the maker side: maker sell = aggressive buyer
            if tr["side"] == "sell":
                buy += float(tr["size"])
            else:
                sell += float(tr["size"])
        flow = (buy - sell) / (buy + sell) if buy + sell else np.nan
    except Exception as e:
        print("trade snapshot failed:", e)
    return book, flow


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
              f"**In use:** {meta['label']}. Each hour four candidates compete on held-out data and the best is kept:", "",
              "| Model | Inputs | Features | Holdout AUC | Holdout accuracy |", "|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d:.3f} | {e:.1%} |" for a, b, c, d, e in meta["table"]]
    lines += ["", "Inputs: BTC returns, volatility, volume, RSI, moving-average gaps, time of day; expanded adds ETH and SOL "
              "momentum/volatility, day of week, and US/Asia/Europe sessions. Order-book and trade-flow pressure are "
              "recorded with every call so they can be added once enough history builds up.", "",
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
    model, cols, use_extra, acc, n, label, table = retrain()
    meta = {"acc": acc, "n": n, "label": label, "table": table,
            "trained": utcnow().astimezone(ZoneInfo("America/Los_Angeles")).strftime("%b %d %-I:%M %p PT")}
    print(f"using {label}, holdout acc {acc:.3f}")
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
            df = m.fetch_candles(3)
            if (pd.Timestamp(q) - pd.Timedelta(seconds=m.GRAN)) in df.index:
                break
            time.sleep(10)
        k = pd.Timestamp(q) - pd.Timedelta(seconds=m.GRAN)
        calls = load_calls()
        if k in df.index and str(pd.Timestamp(q)) not in set(calls["made_at"].astype(str)):
            extras = fetch_extras(3) if use_extra else {}
            if use_extra and len(extras) < len(m.EXTRA_PRODUCTS):
                print("extra data missing; skipping this call")
                X = df.iloc[:0]
            else:
                X = build_X(df.loc[:k], {p: e.loc[:k] for p, e in extras.items()}, use_extra).reindex(columns=cols).dropna()
            if len(X) and X.index[-1] == k:
                p = float(model.predict_proba(X.iloc[[-1]])[:, 1][0])
                book, flow = order_flow()
                calls.loc[len(calls)] = [str(pd.Timestamp(q)), float(df.at[k, "close"]), round(p, 4),
                                         "UP" if p > 0.5 else "DOWN", abs(p - 0.5) > m.CONF_BAND,
                                         np.nan, np.nan, np.nan, meta["label"],
                                         round(book, 4) if pd.notna(book) else np.nan,
                                         round(flow, 4) if pd.notna(flow) else np.nan]
                print(f"{q}: {'UP' if p > 0.5 else 'DOWN'} p={p:.3f}")
        calls = score(calls, df)
        calls.to_csv(CALLS, index=False)
        write_readme(calls, meta)
        push(f"call {q:%Y-%m-%d %H:%M} UTC")


if __name__ == "__main__":
    main()
