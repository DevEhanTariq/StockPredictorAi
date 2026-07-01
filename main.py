import yfinance as yf
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LOOKBACK = 20


# ============================
# FALLBACK TICKERS
# ============================
def get_fallback_tickers():
    return [
        "AAPL","MSFT","NVDA","AMZN","TSLA",
        "META","GOOGL","AMD","INTC","NFLX",
        "JPM","V","MA","BAC","DIS"
    ]


# ============================
# LOAD NASDAQ UNIVERSE
# ============================
def load_large_universe():
    try:
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        df = pd.read_csv(url, sep="|")

        tickers = df["Symbol"].dropna().tolist()

        # clean junk
        tickers = [
            t for t in tickers
            if isinstance(t, str)
            and t.isalpha()
            and len(t) <= 5
        ]

        print("\n📊 NASDAQ UNIVERSE LOADED:", len(tickers))

        return tickers

    except Exception as e:
        print("⚠️ NASDAQ load failed:", e)
        return get_fallback_tickers()


# ============================
# SAMPLE UNIVERSE (NEW CONTROL)
# ============================
def build_universe(random_count):

    base = get_fallback_tickers()
    full = load_large_universe()

    full = list(set(full) - set(base))

    if random_count > len(full):
        print(f"⚠️ Requested {random_count}, but only {len(full)} available. Clamping.")
        random_count = len(full)

    random_sample = list(np.random.choice(full, random_count, replace=False))

    universe = base + random_sample

    print("\n📊 UNIVERSE READY")
    print("Base:", len(base))
    print("Random:", len(random_sample))
    print("Total:", len(universe))
    print("Sample:", universe[:10])

    return universe


# ============================
# DOWNLOAD SAFE
# ============================
def download(ticker):
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        if df is None or df.empty or len(df) < 80:
            return None
        return df
    except:
        return None


# ============================
# INDICATORS
# ============================
def ema(arr, span):
    arr = np.asarray(arr).reshape(-1)
    alpha = 2 / (span + 1)

    out = np.zeros_like(arr, dtype=float)
    out[0] = arr[0]

    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]

    return out


def rsi(arr, period=14):
    arr = np.asarray(arr).reshape(-1)
    delta = np.diff(arr, prepend=arr[0])

    gain = np.maximum(delta, 0)
    loss = np.maximum(-delta, 0)

    avg_gain = np.zeros_like(arr)
    avg_loss = np.zeros_like(arr)

    for i in range(period, len(arr)):
        avg_gain[i] = np.mean(gain[i-period:i])
        avg_loss[i] = np.mean(loss[i-period:i])

    rs = avg_gain / (avg_loss + 1e-8)
    return 100 - (100 / (1 + rs))


# ============================
# FEATURES
# ============================
def make_features(df):

    close = np.asarray(df["Close"].values).reshape(-1)
    close = np.nan_to_num(close)

    if len(close) < 100:
        return None, None

    ret = np.zeros_like(close)
    ret[1:] = (close[1:] - close[:-1]) / (close[:-1] + 1e-8)

    vol = np.zeros_like(close)
    for i in range(10, len(close)):
        vol[i] = np.std(ret[i-10:i])

    ema20 = ema(close, 20)
    ema50 = ema(close, 50)

    trend = (ema20 - ema50) / (close + 1e-8)

    momentum = np.zeros_like(close)
    momentum[5:] = (close[5:] / (close[:-5] + 1e-8)) - 1

    rsi_val = rsi(close)

    feat = np.stack([ret, vol, trend, momentum, rsi_val], axis=1)
    feat = np.nan_to_num(feat)

    return feat[60:], close[60:]


# ============================
# DATASET
# ============================
def build_dataset(tickers):

    X, y = [], []

    for t in tickers:

        df = download(t)
        if df is None:
            continue

        feat, close = make_features(df)
        if feat is None:
            continue

        min_len = min(len(feat), len(close))

        for i in range(LOOKBACK, min_len - 1):
            X.append(feat[i-LOOKBACK:i].reshape(-1))
            y.append((close[i+1] - close[i]) / (close[i] + 1e-8))

    return np.array(X), np.array(y)


# ============================
# MODEL
# ============================
class Net(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)


# ============================
# TRAIN
# ============================
def train(X, y):

    X = torch.tensor(X, dtype=torch.float32).to(DEVICE)
    y = torch.tensor(y, dtype=torch.float32).view(-1,1).to(DEVICE)

    model = Net(X.shape[1]).to(DEVICE)

    opt = optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    for epoch in range(10):
        opt.zero_grad()
        loss = loss_fn(model(X), y)
        loss.backward()
        opt.step()

        print(f"Epoch {epoch+1} | Loss: {loss.item():.6f}")

    return model


# ============================
# PREDICT
# ============================
def predict(model, tickers):

    results = {}

    for t in tickers:

        df = download(t)
        if df is None:
            continue

        feat, _ = make_features(df)
        if feat is None or len(feat) < LOOKBACK:
            continue

        x = torch.tensor(
            feat[-LOOKBACK:].reshape(-1),
            dtype=torch.float32
        ).unsqueeze(0).to(DEVICE)

        results[t] = model(x).item()

    return results


# ============================
# SIGNAL
# ============================
def signal_to_pct(x):
    return np.tanh(x) * 5


# ============================
# PORTFOLIO
# ============================
def allocate(preds, budget):

    ranked = sorted(preds.items(), key=lambda x: x[1], reverse=True)[:10]

    positive = [(t, s) for t, s in ranked if signal_to_pct(s) > 0]

    if len(positive) == 0:
        print("\n📊 No positive signals.")
        return

    weights = np.array([abs(s) for _, s in positive])
    weights = weights / np.sum(weights)

    print("\n📊 PORTFOLIO (POSITIVES ONLY)\n")

    total = 0

    for i, (t, signal) in enumerate(positive):

        pct = signal_to_pct(signal)
        alloc = budget * weights[i]
        profit = alloc * (pct / 100)

        total += profit

        print(
            f"{t} | Alloc £{alloc:.2f} | "
            f"%Move {pct:+.2f}% | "
            f"Profit £{profit:.2f}"
        )

    print("\n💰 TOTAL P&L:", f"£{total:.2f}")
    print("📈 FINAL VALUE:", f"£{budget + total:.2f}")


# ============================
# MAIN
# ============================
if __name__ == "__main__":

    random_count = int(input("🎲 How many random NASDAQ stocks? "))

    tickers = build_universe(random_count)

    print("\nBuilding dataset...")
    X, y = build_dataset(tickers)

    print("Samples:", len(X))

    print("\nTraining model...")
    model = train(X, y)

    print("\nPredicting...\n")
    preds = predict(model, tickers)

    budget = float(input("💰 Enter investment budget: "))

    allocate(preds, budget)