import matplotlib.pyplot as plt

def plot_price(df, forecast, stock_symbol):
    plt.figure(figsize=(10, 4))
    plt.plot(df['Close'], label='Actual')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast')
    plt.title(f"{stock_symbol} Price Prediction")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{stock_symbol}_forecast.png")
    plt.close()