from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(news_list):
    combined = ". ".join(news_list)
    result = sentiment_pipeline(combined[:512])[0]
    return result