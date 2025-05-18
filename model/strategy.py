def decide_action(current_price, predicted_price, sentiment_label):
    diff = predicted_price - current_price
    percent_change = (diff / current_price) * 100

    if sentiment_label == "NEGATIVE":
        return "❌ SELL or WAIT (negative sentiment)"

    if percent_change > 2:
        return f"✅ BUY (Expected ↑ {percent_change:.2f}%)"
    elif percent_change < -2:
        return f"❌ SELL (Expected ↓ {abs(percent_change):.2f}%)"
    else:
        return "⚠️ HOLD (No strong movement expected)"