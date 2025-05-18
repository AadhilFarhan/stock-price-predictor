import csv

def write_report(stock_symbol, last_price, predicted_price, sentiment, decision):
    with open("stock_report.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([stock_symbol, last_price, predicted_price, sentiment['label'], sentiment['score'], decision])