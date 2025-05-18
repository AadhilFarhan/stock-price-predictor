import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# === UTILITY ===
def save_and_plot(data, symbol, source):
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime", inplace=True)

    filename = f"{symbol}_{source}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Saved {filename}")

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(df["datetime"], df["close"], label="Close Price")
    plt.title(f"{symbol} ({source}) Minute Chart")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ========== FYERS API ==========
def get_fyers_minute_data(symbol="NSE:RELIANCE-EQ", resolution="1", date="2024-05-17", token="YOUR_FYERS_ACCESS_TOKEN"):
    print("📡 Fetching FYERS data...")
    endpoint = "https://api.fyers.in/data-rest/v2/history/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    from_ts = int(datetime.datetime.strptime(f"{date} 09:15", "%Y-%m-%d %H:%M").timestamp())
    to_ts = int(datetime.datetime.strptime(f"{date} 15:30", "%Y-%m-%d %H:%M").timestamp())

    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": "1",
        "range_from": from_ts,
        "range_to": to_ts,
        "cont_flag": "1"
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    json_data = response.json()

    candles = json_data.get("candles", [])
    data = []
    for candle in candles:
        dt = datetime.datetime.fromtimestamp(candle[0])
        data.append({
            "datetime": dt,
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            "volume": candle[5]
        })

    save_and_plot(data, symbol.replace(":", "_"), "FYERS")
    return data


# ========== ALPHA VANTAGE ==========
def get_alpha_minute_data(symbol="AAPL", interval="1min", key="YOUR_ALPHA_KEY"):
    print("📡 Fetching Alpha Vantage data...")
    endpoint = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": key,
        "outputsize": "compact"
    }

    response = requests.get(endpoint, params=params)
    json_data = response.json()
    ts_data = json_data.get(f"Time Series ({interval})", {})

    data = []
    for dt_str, values in ts_data.items():
        data.append({
            "datetime": pd.to_datetime(dt_str),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"])
        })

    save_and_plot(data, symbol, "AlphaVantage")
    return data


# ========== TWELVE DATA ==========
def get_twelve_minute_data(symbol="RELIANCE.NS", interval="1min", key="YOUR_TWELVE_KEY"):
    print("📡 Fetching Twelve Data...")
    endpoint = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 30,
        "apikey": key
    }

    response = requests.get(endpoint, params=params)
    json_data = response.json()
    values = json_data.get("values", [])

    data = []
    for entry in values:
        data.append({
            "datetime": pd.to_datetime(entry["datetime"]),
            "open": float(entry["open"]),
            "high": float(entry["high"]),
            "low": float(entry["low"]),
            "close": float(entry["close"]),
            "volume": float(entry["volume"])
        })

    save_and_plot(data, symbol.replace(".", "_"), "TwelveData")
    return data


# ========== MAIN ==========
if __name__ == "__main__":
    # 🔑 Replace these with actual keys
    FYERS_TOKEN = "YOUR_FYERS_ACCESS_TOKEN"
    ALPHA_KEY = "YOUR_ALPHA_KEY"
    TWELVE_KEY = "YOUR_TWELVE_KEY"

    # 🔁 Fetch and store data from each provider
    try:
        get_fyers_minute_data(token=FYERS_TOKEN)
    except Exception as e:
        print("❌ FYERS error:", e)

    try:
        get_alpha_minute_data(symbol="AAPL", key=ALPHA_KEY)
    except Exception as e:
        print("❌ Alpha Vantage error:", e)

    try:
        get_twelve_minute_data(symbol="RELIANCE.NS", key=TWELVE_KEY)
    except Exception as e:
        print("❌ Twelve Data error:", e)
