import ollama
import yfinance as yf
import pandas as pd
import feedparser
import json  # <-- Added standard library to parse JSON
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

# Initialize local NLP sentiment analyzer
sia = SentimentIntensityAnalyzer()

# ==========================================
# 1. DYNAMIC SECURE CONFIGURATION LOADER
# ==========================================
def load_secure_config():
    """Loads private portfolio configuration details dynamically from local storage."""
    config_path = "config.json"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            "CRITICAL ERROR: 'config.json' not found! Please create it locally. "
            "Refer to config.example.json for the correct formatting structure."
        )
        
    with open(config_path, "r") as f:
        return json.load(f)

# Load data dynamically into the execution context
CONFIG = load_secure_config()
PORTFOLIO = CONFIG["PORTFOLIO"]
RISK_PROFILE = CONFIG["RISK_PROFILE"]

# ==========================================
# 2. UPGRADED NEWS & NLP PIPELINE (Keeps identical to your prior script)
# ==========================================

def get_stock_news_and_sentiment(ticker):
    """Fetches real-time RSS news headlines and runs local NLP sentiment analysis."""
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    
    analyzed_headlines = []
    
    # Process the top 4 latest live headlines
    for entry in feed.entries[:4]:
        title = entry.title
        # Calculate local NLP scores (-1.0 to +1.0)
        scores = sia.polarity_scores(title)
        compound = scores['compound']
        
        # Classify the sentiment based on standard VADER thresholds
        if compound >= 0.05:
            sentiment = "POSITIVE 🟩"
        elif compound <= -0.05:
            sentiment = "NEGATIVE 🟥"
        else:
            sentiment = "NEUTRAL 🟨"
            
        analyzed_headlines.append(f"'{title}' ({sentiment} | Score: {compound:.2f})")
        
    return analyzed_headlines if analyzed_headlines else ["No recent major RSS headlines found."]

def fetch_market_context(ticker):
    """Gathers dense market metrics and combines them with NLP news metrics."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get("currentPrice" if "currentPrice" in info else "regularMarketPrice", 0)
        sma_50 = info.get("fiftyDayAverage", 0)
        sma_200 = info.get("twoHundredDayAverage", 0)
        
        # Hit our new RSS + NLP pipeline
        headlines_with_sentiment = get_stock_news_and_sentiment(ticker)
        
        return {
            "current_price": price,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "news_analysis": headlines_with_sentiment
        }
    except Exception as e:
        return {"current_price": 0, "sma_50": 0, "sma_200": 0, "news_analysis": [f"Pipeline Error: {str(e)}"]}

# ==========================================
# 3. AGENT ORCHESTRATION ENGINE
# ==========================================
def generate_morning_briefing():
    print("🤖 Scraping live RSS feeds, running local NLP sentiment, and prompting Ollama...")
    
    portfolio_summary = ""
    for ticker, details in PORTFOLIO["positions"].items():
        ctx = fetch_market_context(ticker)
        current_val = ctx['current_price'] * details['shares']
        pnl = (ctx['current_price'] - details['avg_cost']) * details['shares']
        
        portfolio_summary += f"""
        - Ticker: {ticker}
          Current Price: ${ctx['current_price']:.2f} | Avg Cost: ${details['avg_cost']:.2f}
          Total Value: ${current_val:,.2f} | Unrealized PnL: ${pnl:,.2f}
          Technicals: 50MA: ${ctx['sma_50']:.2f} | 200MA: ${ctx['sma_200']:.2f}
          Processed News Feed:
          * {chr(10).join(ctx['news_analysis'])}
        """

    system_prompt = f"""
    You are an elite, concise quantitative trading assistant. Your task is to output a scannable Pre-Market Intelligence Dashboard.
    You are provided with raw mathematical data and news titles that have ALREADY been evaluated by a local NLP engine for sentiment.
    
    User Context:
    - Philosophy: {RISK_PROFILE['philosophy']}
    - Risk Stance: {RISK_PROFILE['tolerance']}
    Current Cash Available: ${PORTFOLIO['free_cash']:,}
    """

    user_prompt = f"""
    Analyze the raw portfolio data and NLP sentiment summaries below. Synthesize everything into a clean markdown dashboard with exactly these three bold headers:
    1. 🚨 **Risk & Breakdown Alerts** (Flag positions if price breaks below MAs or if the NLP score highlights consistent NEGATIVE headlines)
    2. 🎯 **Asymmetric Setups** (Look for technical setups or positive sentiment momentum that aligns with the strategy)
    3. 📊 **Capital Allocation Blueprint** (Provide dynamic instructions on cash deployment based on current market signals)

    Data Input:
    {portfolio_summary}
    """

    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    markdown_output = f"""# 🌅 Pre-Market Trading Dashboard
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{response['message']['content']}
"""
    
    with open("daily_dashboard.md", "w") as f:
        f.write(markdown_output)
        
    print("\n🎯 Dashboard updated successfully with live NLP data!")

if __name__ == "__main__":
    generate_morning_briefing()