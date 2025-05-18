import pandas as pd

def compute_indicators(df):
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['RSI'] = compute_rsi(df['Close'], 14)
    df['Upper'] = df['Close'].rolling(window=20).mean() + 2*df['Close'].rolling(window=20).std()
    df['Lower'] = df['Close'].rolling(window=20).mean() - 2*df['Close'].rolling(window=20).std()
    return df

def compute_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))