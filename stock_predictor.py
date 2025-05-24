from utils.news_scraper import fetch_news
from utils.sentiment import analyze_sentiment
from model.price_predictor import train_predict_price
from model.price_predictor import train_predict_price_new
from model.price_predictor import  train_xgb_predict_next_day
from model.strategy import decide_action
from utils.buy_quantity import suggest_quantity
from utils.data_fetcher import get_minute_data_from_source
import pandas as pd
import yfinance as yf
import csv

from utils.news_scraper import fetch_news
from utils.sentiment import analyze_sentiment
from model.price_predictor import train_predict_price
from model.strategy import decide_action
from utils.buy_quantity import suggest_quantity



def run(stock_symbol="RELIANCE.NS", capital=10000, source="fyers", api_keys=None, date="2024-05-17",days=7):
    print(f"\n📊 Fetching minute-level historical data for {stock_symbol} from {source}...")
    
    # if api_keys is None:
    #     api_keys = {}

    # data = get_minute_data_from_source(source, stock_symbol, date=date, api_keys=api_keys)

    # if not data:
    #     print("❌ No data found for this stock.")
    #     return

    print(f"Fetching historical data for {stock_symbol}")
    df = yf.download(stock_symbol, interval=f"5m", period=f"60d")
    df = df.reset_index().rename(columns={"Datetime": "Date"})

    print(df)
    df.to_csv("data.csv")

    if df.empty:
        print("❌ No data found for this stock.")
        return

    print(f"✅ Fetched {len(df)} rows of stock data")

    print(f"\n🗞️ Fetching recent news for {stock_symbol}...")
    news_list = fetch_news(stock_symbol.replace(".NS", "").replace("NSE:", ""))
    print(f"✅ Got {len(news_list)} news articles")

    sentiments = analyze_sentiment(news_list)
    print(f"🧠 Sentiment: {sentiments['label']} ({sentiments['score']:.2f})")

    print(f"DAYS IS: {days}")

    if days == 8:
        predicted_price = train_xgb_predict_next_day(df)
        print(f"📈 XGB Predicted next price: ₹{predicted_price:.2f}")
    elif days ==7:
        predicted_price = train_predict_price(df)
        print(f"📈 Prophet Predicted next price: ₹{predicted_price:.2f}")
    elif days == 6:
        predicted_price = train_predict_price_new(df)
        print(f"📈 Prophet NEW Predicted next price: ₹{predicted_price:.2f}")

    

    last_close = df['Close'].iloc[-1]
    decision = decide_action(last_close, predicted_price, sentiments['label'])
    print(f"\n🤖 Final Recommendation: {decision}")

    if 'BUY' in decision:
        qty = suggest_quantity(capital, last_close)
        print(f"💰 Suggested Quantity to Buy: {qty} shares (Capital: ₹{capital})")


if __name__ == "__main__":
    run(
        stock_symbol="COCHINSHIP.NS",
        capital=20000,
        source="twelve",
        api_keys={
            "fyers": "YOUR_FYERS_ACCESS_TOKEN",
            "alpha": "YOUR_ALPHA_KEY",
            "twelve": "e4ceee6b9c384dc1b99e438d2e3d7a90"
        },
        date="2024-05-17"
    )
