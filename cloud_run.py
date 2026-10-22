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
        "model", "book_imbalance", "flow_imbalance",
        "poly_slug", "poly_bid", "poly_ask", "poly_result",
        "kalshi_ticker", "kalshi_bid", "kalshi_ask", "kalshi_result"]
EDGE = 0.03          # paper-bet only when the model beats the market's price by 3+ cents
POLY = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def load_calls():
    if os.path.exists(CALLS):
        df = pd.read_csv(CALLS).reindex(columns=COLS)
        df["outcome"] = df["outcome"].astype(object)
        for col in ["model", "poly_slug", "poly_result", "kalshi_ticker", "kalshi_result"]:
            df[col] = df[col].astype(object)
        for v in ["poly", "kalshi"]:   # repair any rows logged with bid/ask swapped
            bad = df[f"{v}_bid"] > df[f"{v}_ask"]
            df.loc[bad, [f"{v}_bid", f"{v}_ask"]] = df.loc[bad, [f"{v}_ask", f"{v}_bid"]].values
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


def market_odds(q):
    """Read-only snapshot of the Polymarket and Kalshi 'BTC up in this 15 min' prices for the window starting at q.
    Returns (slug, up_bid, up_ask, ticker, yes_bid, yes_ask); missing pieces are NaN."""
    import requests, json
    out = [np.nan] * 6
    ts = int(pd.Timestamp(q).timestamp())
    try:
        slug = f"btc-updown-15m-{ts}"
        mk = requests.get(f"{POLY}/markets", params={"slug": slug}, timeout=10).json()
        if mk:
            mk = mk[0]
            tok = json.loads(mk["clobTokenIds"])[0]          # the "Up" token
            bid = ask = np.nan
            try:
                # CLOB /price: side=buy is the best bid (what buyers pay), side=sell is the best ask
                bid = float(requests.get(f"{CLOB}/price", params={"token_id": tok, "side": "buy"}, timeout=10).json()["price"])
                ask = float(requests.get(f"{CLOB}/price", params={"token_id": tok, "side": "sell"}, timeout=10).json()["price"])
                if bid > ask:
                    bid, ask = ask, bid
            except Exception:
                bid, ask = float(mk.get("bestBid", np.nan)), float(mk.get("bestAsk", np.nan))
            out[0:3] = [slug, bid, ask]
    except Exception as e:
        print("polymarket odds failed:", e)
    try:
        close = ts + 900
        r = requests.get(f"{KALSHI}/markets", params={"series_ticker": "KXBTC15M", "min_close_ts": close - 60,
                                                       "max_close_ts": close + 60, "limit": 10}, timeout=10).json()
        for mk in r.get("markets", []):
            if int(pd.Timestamp(mk["close_time"]).timestamp()) == close:
                out[3:6] = [mk["ticker"], float(mk["yes_bid_dollars"]), float(mk["yes_ask_dollars"])]
                break
    except Exception as e:
        print("kalshi odds failed:", e)
    return out


def market_results(calls):
    """Fill in how each market actually settled (its own price source, not Coinbase)."""
    import requests, json
    for i in calls.index:
        slug = calls.at[i, "poly_slug"]
        if isinstance(slug, str) and pd.isna(calls.at[i, "poly_result"]):
            try:
                mk = requests.get(f"{POLY}/markets", params={"slug": slug}, timeout=10).json()
                if mk and mk[0].get("closed"):
                    prices = [float(x) for x in json.loads(mk[0]["outcomePrices"])]
                    if max(prices) >= 0.99:
                        calls.at[i, "poly_result"] = "UP" if prices[0] > prices[1] else "DOWN"
            except Exception as e:
                print("polymarket result failed:", e)
        tk = calls.at[i, "kalshi_ticker"]
        if isinstance(tk, str) and pd.isna(calls.at[i, "kalshi_result"]):
            try:
                mk = requests.get(f"{KALSHI}/markets/{tk}", timeout=10).json()["market"]
                if mk.get("result") in ("yes", "no"):
                    calls.at[i, "kalshi_result"] = "UP" if mk["result"] == "yes" else "DOWN"
            except Exception as e:
                print("kalshi result failed:", e)
    return calls


def paper_bets(calls, venue):
    """Hypothetical $1 contracts: buy the side the model rates EDGE above its ask. Nothing is traded."""
    bid, ask, res = calls[f"{venue}_bid"], calls[f"{venue}_ask"], calls[f"{venue}_result"]
    rows = []
    for i in calls.index:
        if pd.isna(ask[i]) or pd.isna(bid[i]):
            continue
        p = calls.at[i, "p_up"]
        up_ask, down_ask = ask[i], 1 - bid[i]
        if p - up_ask > EDGE:
            side, price = "UP", up_ask
        elif (1 - p) - down_ask > EDGE:
            side, price = "DOWN", down_ask
        else:
            continue
        if not isinstance(res[i], str):
            rows.append((side, price, np.nan, np.nan))
            continue
        win = side == res[i]
        pnl = (1 - price) if win else -price
        fee = np.ceil(0.07 * price * (1 - price) * 100) / 100 if venue == "kalshi" else 0.0
        rows.append((side, price, float(win), pnl - fee))
    return pd.DataFrame(rows, columns=["side", "price", "win", "pnl"])


def brier(calls, venue):
    d = calls.dropna(subset=[f"{venue}_bid", f"{venue}_ask"])
    d = d[d[f"{venue}_result"].isin(["UP", "DOWN"])]
    if not len(d):
        return None
    y = (d[f"{venue}_result"] == "UP").astype(float)
    mid = (d[f"{venue}_bid"] + d[f"{venue}_ask"]) / 2
    return len(d), float(((d["p_up"] - y) ** 2).mean()), float(((mid - y) ** 2).mean())


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
              "## Model vs. the market (paper tracking only, nothing is traded)", "",
              f"At each call the job records the Polymarket and Kalshi prices for that same 15-minute window. A paper bet is "
              f"logged only when the model's probability beats the market's ask by {EDGE*100:.0f}+ cents, then settled with "
              "the market's own result (Polymarket uses Chainlink, Kalshi uses CF Benchmarks). P&L is per $1 contract; "
              "Kalshi includes its taker fee, Polymarket fees are not included.", "",
              "| Market | Windows priced | Paper bets settled | Win rate | Avg price paid | Total P&L per $1 contract | Model vs market accuracy (Brier, lower is better) |",
              "|---|---|---|---|---|---|---|"]
    for venue, name in [("poly", "Polymarket"), ("kalshi", "Kalshi")]:
        priced = int(calls[f"{venue}_ask"].notna().sum())
        b = paper_bets(calls, venue)
        s_ = b.dropna(subset=["win"])
        br = brier(calls, venue)
        brs = f"model {br[1]:.4f} vs market {br[2]:.4f} ({br[0]} windows)" if br else "—"
        if len(s_):
            lines.append(f"| {name} | {priced} | {len(s_)} | {s_.win.mean():.1%} | {s_.price.mean():.2f} | "
                         f"{'+' if s_.pnl.sum() >= 0 else '−'}${abs(s_.pnl.sum()):.2f} | {brs} |")
        else:
            lines.append(f"| {name} | {priced} | 0 | — | — | — | {brs} |")
    lines += ["", "If the market's Brier score stays lower than the model's, the market is the better forecaster and "
              "the paper P&L should drift negative. That would mean there's no edge to trade.", "",
              "## Recent calls", "", "| Time (PT) | Price | P(up) | Call | Polymarket UP bid/ask | Kalshi YES bid/ask | 15 min later | Result |", "|---|---|---|---|---|---|---|---|"]
    for _, r in calls.tail(40).iloc[::-1].iterrows():
        t = pd.Timestamp(r["made_at"]).tz_convert(la).strftime("%b %d %-I:%M %p")
        end = f"${r['end_price']:,.0f}" if pd.notna(r["end_price"]) else "pending"
        res = "pending" if pd.isna(r["correct"]) else ("✅ right" if r["correct"] else "❌ wrong")
        pm = f"{r['poly_bid']:.2f}/{r['poly_ask']:.2f}" if pd.notna(r["poly_ask"]) else "—"
        ks = f"{r['kalshi_bid']:.2f}/{r['kalshi_ask']:.2f}" if pd.notna(r["kalshi_ask"]) else "—"
        lines.append(f"| {t} | ${r['price']:,.0f} | {r['p_up']:.1%} | {r['call']}{'' if r['confident'] else ' (lean)'} | {pm} | {ks} | {end} | {res} |")
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
                odds = market_odds(q)
                calls.loc[len(calls)] = [str(pd.Timestamp(q)), float(df.at[k, "close"]), round(p, 4),
                                         "UP" if p > 0.5 else "DOWN", abs(p - 0.5) > m.CONF_BAND,
                                         np.nan, np.nan, np.nan, meta["label"],
                                         round(book, 4) if pd.notna(book) else np.nan,
                                         round(flow, 4) if pd.notna(flow) else np.nan,
                                         odds[0], odds[1], odds[2], np.nan, odds[3], odds[4], odds[5], np.nan]
                print(f"{q}: {'UP' if p > 0.5 else 'DOWN'} p={p:.3f}")
        calls = score(calls, df)
        calls = market_results(calls)
        calls.to_csv(CALLS, index=False)
        write_readme(calls, meta)
        push(f"call {q:%Y-%m-%d %H:%M} UTC")


if __name__ == "__main__":
    main()
