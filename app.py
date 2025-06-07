import streamlit as st
import os
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

def query_openrouter_chat(messages, model=DEFAULT_MODEL):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages
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

def main():
    st.title("Financial Stock Analysis")

    mode = st.radio("Choose mode:", ("Single Stock Analysis", "Compare Multiple Stocks", "Conversational Chat"))

    predefined_tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA", "NVDA"]

    if mode == "Single Stock Analysis":
        ticker = st.selectbox("Select Stock Ticker", predefined_tickers, index=0)
        if st.button("Analyze Single Stock") and ticker:
            st.subheader(f"Analysis for {ticker}")
            data = fetch_stock_data(ticker)
            st.line_chart(data['Close'])

            ratios = get_financial_ratios(ticker)
            st.write("### Financial Ratios:")
            st.json(ratios)

            news = fetch_news(ticker)
            st.write("### News Headlines:")
            for h in news:
                st.write("-", h)

            if "summary" not in st.session_state:
                st.session_state.summary = query_openrouter_chat([{"role":"user","content":"Summarize these news headlines:\n" + "\n".join(news)}])

            if "sentiment" not in st.session_state:
                st.session_state.sentiment = query_openrouter_chat([{"role":"user","content":"Classify the sentiment (Positive, Neutral, Negative) of these headlines:\n" + "\n".join(news)}])

            if "advice" not in st.session_state:
                advice_prompt = f"""
                You are a financial analyst. Based on the following data for {ticker}:
                - Financial Ratios: {ratios}
                - News Summary: {st.session_state.summary}
                - Sentiment: {st.session_state.sentiment}
                Provide a brief investment recommendation (Buy/Hold/Sell) and reasoning.
                """
                st.session_state.advice = query_openrouter_chat([{"role":"user","content":advice_prompt}])

            st.write("##### News Summary: \n", st.session_state.summary)
            st.write("### Sentiment:\n", st.session_state.sentiment)
            st.markdown(f"### Investment Recommendation:\n{st.session_state.advice}")

            df_ratios = pd.DataFrame([ratios])
            csv_data = df_ratios.to_csv(index=False)
            # Store analysis TXT in session state
            if "txt_data" not in st.session_state:
                st.session_state.txt_data = (
                    f"News Headlines:\n" + "\n".join(news) +
                    f"\n\nSummary:\n{st.session_state.summary}" +
                    f"\n\nSentiment:\n{st.session_state.sentiment}" +
                    f"\n\nRecommendation:\n{st.session_state.advice}"
                )

            st.download_button("Download Ratios CSV", csv_data, file_name=f"{ticker}_ratios.csv")
            st.download_button("Download Analysis TXT", st.session_state.txt_data, file_name=f"{ticker}_analysis.txt")

    elif mode == "Compare Multiple Stocks":
        popular_stocks = {
            "Apple Inc. (AAPL)": "AAPL",
            "Microsoft Corp. (MSFT)": "MSFT",
            "Alphabet Inc. (GOOGL)": "GOOGL",
            "Amazon.com Inc. (AMZN)": "AMZN",
            "Tesla Inc. (TSLA)": "TSLA",
            "NVIDIA Corp. (NVDA)": "NVDA",
            "Meta Platforms Inc. (META)": "META",
            "Netflix Inc. (NFLX)": "NFLX",
            "Berkshire Hathaway Inc. (BRK-B)": "BRK-B",
            "Johnson & Johnson (JNJ)": "JNJ",
        }

        selected_companies = st.multiselect("Select companies to compare", options=list(popular_stocks.keys()), default=["Apple Inc. (AAPL)", "Microsoft Corp. (MSFT)"])

        if st.button("Compare Selected Companies") and selected_companies:
            tickers = [popular_stocks[name] for name in selected_companies]
            
            if len(tickers) < 2:
                st.error("Enter at least two tickers for comparison.")
                return

            st.subheader("Closing Price Trends")
            price_data = {}
            for ticker in tickers:
                df = fetch_stock_data(ticker)
                price_data[ticker] = df['Close']

            prices_df = pd.DataFrame(price_data)
            st.line_chart(prices_df)

            all_ratios = {}
            all_advices = {}

            for ticker in tickers:
                st.write(f"### {ticker}")
                ratios = get_financial_ratios(ticker)
                all_ratios[ticker] = ratios
                st.json(ratios)

                news = fetch_news(ticker)
                with st.spinner(f"Analyzing {ticker}..."):
                    summary = query_openrouter_chat([{"role":"user","content":"Summarize these news headlines:\n" + "\n".join(news)}])
                    sentiment = query_openrouter_chat([{"role":"user","content":"Classify the sentiment (Positive, Neutral, Negative) of these headlines:\n" + "\n".join(news)}])
                    advice_prompt = f"""
                    You are a financial analyst. Based on the following data for {ticker}:
                    - Financial Ratios: {ratios}
                    - News Summary: {summary}
                    - Sentiment: {sentiment}
                    Provide a brief investment recommendation (Buy/Hold/Sell) and reasoning.
                    """
                    advice = query_openrouter_chat([{"role":"user","content":advice_prompt}])
                    all_advices[ticker] = advice

                st.write("#### News Headlines:")
                for h in news:
                    st.write("-", h)
                st.write("#### Summary:\n", summary)
                st.write("#### Sentiment:\n", sentiment)
                st.markdown(f"#### Investment Advice: \n{advice}")
                st.write("---")

            df_ratios = pd.DataFrame(all_ratios).T
            st.download_button("Download All Ratios CSV", df_ratios.to_csv().encode('utf-8'), file_name="stocks_ratios.csv")

            advices_text = "\n\n".join([f"{ticker}:\n{advice}" for ticker, advice in all_advices.items()])
            st.download_button("Download All Recommendations TXT", advices_text, file_name="stocks_recommendations.txt")

    else:
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": "You are a helpful financial analyst assistant."}]

        ticker = st.selectbox("Select Stock Ticker for context (optional)", [""] + predefined_tickers)
        if ticker:
            ratios = get_financial_ratios(ticker)
            news = fetch_news(ticker)

            st.sidebar.header(f"Stock Info: {ticker}")
            st.sidebar.write("### Financial Ratios:")
            st.sidebar.json(ratios)
            st.sidebar.write("### News Headlines:")
            for h in news:
                st.sidebar.write("-", h)

            context = f"Stock ticker: {ticker}\nFinancial Ratios: {ratios}\nRecent News Headlines: {news}"
            if st.session_state.messages[0]["role"] == "system":
                st.session_state.messages[0]["content"] = f"You are a helpful financial analyst assistant.\n{context}"

        st.write("### Chat:")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown("---")
                st.markdown(f"### You: \n{msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"### Assistant: \n{msg['content']}")

        user_input = st.text_input("Enter message:", key="")

        if st.button("Send") and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Waiting for assistant response..."):
                response = query_openrouter_chat(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()