import requests
from bs4 import BeautifulSoup
from feedparser import parse

def fetch_news(query):
    query = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}+stock+site:moneycontrol.com&hl=en-IN&gl=IN&ceid=IN:en"
    r = requests.get(url)
    feed = parse(r.text)
    return [entry.title for entry in feed.entries[:10000]]