import os
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

def query_openrouter(prompt, model=DEFAULT_MODEL):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def fetch_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

def get_financial_ratios(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "PE Ratio": info.get("trailingPE"),
        "Market Cap": info.get("marketCap"),
        "EPS": info.get("trailingEps"),
        "Dividend Yield": info.get("dividendYield"),
    }

def fetch_news(query):
    url = f"https://news.google.com/search?q={query}%20when%3A7d"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [item.text for item in soup.select("article h3")]
    return headlines[:5]

def summarize_news(news_list):
    prompt = "Summarize the following financial news headlines:\n\n" + "\n".join(news_list)
    return query_openrouter(prompt)

def analyze_sentiment(news_list):
    prompt = "Classify the sentiment (Positive, Neutral, Negative) of each headline:\n\n" + "\n".join(news_list)
    return query_openrouter(prompt)

def investment_advice(ticker, ratios, summary, sentiment):
    prompt = f"""
You are a financial analyst. Based on the following data for {ticker}:

- Financial Ratios: {ratios}
- News Summary: {summary}
- Sentiment: {sentiment}

Provide a brief investment recommendation (Buy/Hold/Sell) and your reasoning.
"""
    return query_openrouter(prompt)

def analyze_single_stock(ticker):
    print(f"\n=== Analyzing {ticker} ===")
    data = fetch_stock_data(ticker)
    ratios = get_financial_ratios(ticker)
    news = fetch_news(ticker)
    summary = summarize_news(news)
    sentiment = analyze_sentiment(news)
    advice = investment_advice(ticker, ratios, summary, sentiment)

    print("\nFinancial Ratios:", ratios)
    print("\nNews Headlines:")
    for h in news:
        print("-", h)
    print("\nNews Summary:\n", summary)
    print("\nSentiment Analysis:\n", sentiment)
    print("\nInvestment Recommendation:\n", advice)

def compare_stocks(tickers):
    print(f"\n=== Comparing Stocks: {', '.join(tickers)} ===")

    all_ratios = {}
    all_summaries = {}
    all_sentiments = {}
    all_advices = {}

    for ticker in tickers:
        print(f"\nFetching data for {ticker}...")
        ratios = get_financial_ratios(ticker)
        news = fetch_news(ticker)
        summary = summarize_news(news)
        sentiment = analyze_sentiment(news)
        advice = investment_advice(ticker, ratios, summary, sentiment)

        all_ratios[ticker] = ratios
        all_summaries[ticker] = summary
        all_sentiments[ticker] = sentiment
        all_advices[ticker] = advice

    # Print comparison summary
    print("\n--- Financial Ratios Comparison ---")
    for ticker, ratios in all_ratios.items():
        print(f"{ticker}: {ratios}")

    print("\n--- Investment Recommendations ---")
    for ticker, advice in all_advices.items():
        print(f"{ticker}: {advice}\n")

if __name__ == "__main__":
    choice = input("Analyze (1) Single Stock or (2) Compare Multiple Stocks? Enter 1 or 2: ").strip()
    if choice == "1":
        ticker = input("Enter stock ticker (e.g. AAPL): ").strip().upper()
        analyze_single_stock(ticker)
    elif choice == "2":
        tickers = input("Enter stock tickers separated by commas (e.g. AAPL,MSFT,GOOG): ").strip().upper().split(",")
        tickers = [t.strip() for t in tickers if t.strip()]
        compare_stocks(tickers)
    else:
        print("Invalid choice. Please enter 1 or 2.")