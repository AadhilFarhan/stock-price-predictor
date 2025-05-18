from stock_predictor import run

def run_multiple():
    stocks = ["COCHINSHIP.NS","RELIANCE.NS", "TCS.NS", "INFY.NS"]
    for stock in stocks:
        print(f"\n===== Analyzing {stock} =====")
        run(stock, capital=10000)

if __name__ == "__main__":
    run_multiple()