# 📊 Financial Stock Analysis using LLMs

A powerful and interactive stock analysis tool that uses real-time market data, news headlines, and AI-generated insights. Built with **Streamlit**, **OpenRouter LLMs** (e.g., Mistral), and **Yahoo Finance API**, this app helps you explore and compare stocks easily.

---

## Features

### Single Stock Analysis
- View stock price history chart
- Analyze financial ratios (PE, EPS, Dividend Yield, Market Cap)
- Fetch latest news headlines from Google News
- Get LLM-generated:
  - News Summary
  - Sentiment Analysis
  - Investment Advice (Buy / Hold / Sell)

### Compare Multiple Stocks
- Select multiple companies
- Visualize price trends together
- View side-by-side financial metrics
- Get separate AI insights and recommendations

### Conversational Chat
- Ask financial questions via chat
- Optionally add stock context
- Assistant responds using open-source LLMs (via OpenRouter)

### Export Options
- Download CSV (ratios)
- Download TXT (summary + advice)

---

## Project Structure

```
financial-stock-analysis/
│
├── app.py                      # Main Streamlit app file
├── requirements.txt            # Python dependencies
├── .env                        # API key (OPENROUTER_API_KEY)
├── README.md                   # This documentation
└── stock.py                    # It can run on the terminal
```    


---

## Installation

1. **Clone the repo**
```bash
git clone https://github.com/krishna4002/Financial-Stock-Analysis.git
cd Financial-Stock-Analysis
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up OpenRouter API key**

Create a `.env` file:
```
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

## Run the App

```bash
streamlit run app.py
```

Visit: [http://localhost:8501](http://localhost:8501)

---

## Powered by OpenRouter

Using the free, open-source model:
```
mistralai/mistral-7b-instruct:free
```

You can also use any other model available on [https://openrouter.ai](https://openrouter.ai)

---

## Example Use Cases

- Analyze sentiment around **Apple** or **Tesla**
- Compare **Microsoft vs Google** financials
- Ask: _“Is it a good time to buy NVIDIA?”_
- Export insights to include in your reports or presentations

---

## Screenshots (Coming Soon)

- Stock price comparison chart
- Chat interface with LLM
- Downloadable insights file

---

## Requirements

```
streamlit
yfinance
beautifulsoup4
pandas
requests
python-dotenv
```

Install via:

```bash
pip install -r requirements.txt
```

---

## About This Project

This project demonstrates how **Generative AI can assist in real-world finance**. Whether you're a learner, investor, analyst, or developer — you’ll find value in combining:
- Traditional financial metrics
- Real-time news
- AI intelligence (LLMs)

---

## Roadmap

- Add real-time chart comparisons
- Generate downloadable insights
- Add technical indicators (e.g., RSI, MACD)
- Deploy to Streamlit Cloud / Hugging Face
- Add historical sentiment tracking
- Build a portfolio tracker feature

---
