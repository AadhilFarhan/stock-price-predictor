from flask import Flask, request, jsonify, render_template
# from your_module import run  # Import your run function properly
import io
import sys
from stock_predictor import run

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # This serves index.html from templates/

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    stocks = data.get('stocks', [])
    days = data.get('days', 7)
    capital = data.get('capital', 10000)
    
    results = []
    for stock in stocks:
        # We'll capture print output from run to collect messages
        buffer = io.StringIO()
        sys.stdout = buffer

        try:
            # Call run with modified parameters - you need to adjust run to accept 'days'
            run(stock_symbol=stock, capital=capital, date=None, days=days) 
        except Exception as e:
            sys.stdout = sys.__stdout__
            results.append({'stock': stock, 'error': str(e)})
            continue
        
        sys.stdout = sys.__stdout__
        output = buffer.getvalue()
        results.append({'stock': stock, 'output': output})
    
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
