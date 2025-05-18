import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt


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


def get_fyers_minute_data(symbol="NSE:RELIANCE-EQ", resolution="1", date="2024-05-17", token=""):
    print("📡 Fetching FYERS data...")
    endpoint = "https://api.fyers.in/data-rest/v2/history/"
    headers = {"Authorization": f"Bearer {token}"}

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

    data = [{
        "datetime": datetime.datetime.fromtimestamp(candle[0]),
        "open": candle[1],
        "high": candle[2],
        "low": candle[3],
        "close": candle[4],
        "volume": candle[5]
    } for candle in candles]

    save_and_plot(data, symbol.replace(":", "_"), "FYERS")
    return data


def get_alpha_minute_data(symbol="AAPL", interval="1min", key=""):
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

    data = [{
        "datetime": pd.to_datetime(dt_str),
        "open": float(values["1. open"]),
        "high": float(values["2. high"]),
        "low": float(values["3. low"]),
        "close": float(values["4. close"]),
        "volume": int(values["5. volume"])
    } for dt_str, values in ts_data.items()]

    save_and_plot(data, symbol, "AlphaVantage")
    return data


# def get_twelve_minute_data(symbol="RELIANCE.NS", interval="1min", key=""):
#     print("📡 Fetching Twelve Data...")
#     endpoint = f"https://api.twelvedata.com/time_series"
#     params = {
#         "symbol": symbol,
#         "interval": interval,
#         "outputsize": 30,
#         "apikey": key
#     }

#     response = requests.get(endpoint, params=params)
#     json_data = response.json()
#     values = json_data.get("values", [])

#     data = [{
#         "datetime": pd.to_datetime(entry["datetime"]),
#         "open": float(entry["open"]),
#         "high": float(entry["high"]),
#         "low": float(entry["low"]),
#         "close": float(entry["close"]),
#         "volume": float(entry["volume"])
#     } for entry in values]

#     save_and_plot(data, symbol.replace(".", "_"), "TwelveData")
#     return data

def get_twelve_minute_data(symbol="RELIANCE.NS", interval="1min", key="", outputsize=1000, start_date=None, end_date=None):
    print("📡 Fetching Twelve Data...")

    endpoint = "https://api.twelvedata.com/time_series"
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": key,
        "outputsize": outputsize
    }

    # Add optional date filters
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = requests.get(endpoint, params=params)
    json_data = response.json()

    # Handle errors
    if "status" in json_data and json_data["status"] == "error":
        print(f"❌ Error from Twelve Data: {json_data.get('message')}")
        return []

    values = json_data.get("values", [])

    if not values:
        print("❌ No data received from Twelve Data.")
        return []

    # Process data
    data = [{
        "datetime": pd.to_datetime(entry["datetime"]),
        "open": float(entry["open"]),
        "high": float(entry["high"]),
        "low": float(entry["low"]),
        "close": float(entry["close"]),
        "volume": float(entry["volume"])
    } for entry in values]

    save_and_plot(data, symbol.replace(".", "_"), "TwelveData")
    return data

def get_minute_data_from_source(source, symbol, date=None, api_keys={}):
    if source == "fyers":
        return get_fyers_minute_data(symbol, date=date, token=api_keys.get("fyers", ""))
    elif source == "alpha":
        return get_alpha_minute_data(symbol, key=api_keys.get("alpha", ""))
    elif source == "twelve":
        return get_twelve_minute_data(symbol, key=api_keys.get("twelve", ""))
    else:
        raise ValueError(f"Unsupported source: {source}")
