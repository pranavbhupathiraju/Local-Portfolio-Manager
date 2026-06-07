import ollama
import yfinance as yf
import pandas as pd
import feedparser
import json
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

sia = SentimentIntensityAnalyzer()

# ==========================================
# 1. DATA & SECURITY CONFIG LOADER
# ==========================================
def load_secure_config():
    with open("config.json", "r") as f:
        return json.load(f)

CONFIG = load_secure_config()
PORTFOLIO = CONFIG["PORTFOLIO"]
WATCHLIST = CONFIG["WATCHLIST"]
RISK_PROFILE = CONFIG["RISK_PROFILE"]

# ==========================================
# 2. ADVANCED DATA PROCESSING PIPELINE
# ==========================================
def analyze_news_sentiment(ticker):
    """Aggregates RSS news feed metrics into a dense headline profile and sentiment velocity."""
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    
    headlines = []
    total_score = 0
    count = 0
    
    for entry in feed.entries[:5]:
        title = entry.title
        score = sia.polarity_scores(title)['compound']
        total_score += score
        count += 1
        headlines.append(f"- {title} (Score: {score:.2f})")
        
    avg_sentiment = total_score / count if count > 0 else 0.0
    return {"headlines": "\n".join(headlines), "avg_sentiment": avg_sentiment}

def calculate_composite_setup(ticker):
    """
    Computes an Asymmetric Edge Score (AES) from 0 to 100 based on structure.
    Balances distance to moving averages, recent volatility, and news momentum.
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch historical daily data for tracking structural moves
        hist = stock.history(period="60d")
        if hist.empty: return None
        
        current_price = hist['Close'].iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # 1. Volume Accumulation Check
        avg_vol = hist['Volume'].tail(20).mean()
        recent_vol = hist['Volume'].iloc[-1]
        volume_multiplier = recent_vol / avg_vol if avg_vol > 0 else 1.0
        
        # 2. News Catalyst Check
        news = analyze_news_sentiment(ticker)
        
        # 3. Structural Setup Scoring Algorithm
        score = 50 # Base neutral score
        
        # Add score if pulling back cleanly toward institutional support (50 MA) without breaking it
        if current_price > sma_50 and (current_price / sma_50) < 1.05:
            score += 20  # Strong structural location
        elif current_price < sma_50:
            score -= 20  # Under water / Overhead resistance heavy
            
        # Add score if volume expands on massive accumulation
        if volume_multiplier > 1.5 and hist['Close'].iloc[-1] > hist['Open'].iloc[-1]:
            score += 15
            
        # Add score for positive sentiment velocity
        if news['avg_sentiment'] > 0.2:
            score += 15
        elif news['avg_sentiment'] < -0.2:
            score -= 25
            
        return {
            "price": current_price,
            "score": max(0, min(100, score)), # Clamp score between 0 and 100
            "volume_mult": volume_multiplier,
            "news_summary": news['headlines'],
            "avg_sentiment": news['avg_sentiment']
        }
    except Exception as e:
        return None

# ==========================================
# 3. EXECUTIVE REASONING ENGINE
# ==========================================
def generate_executive_dashboard():
    print("🧠 Sifting through market structure and running catalyst filters...")
    
    portfolio_input = ""
    for ticker, details in PORTFOLIO["positions"].items():
        analysis = calculate_composite_setup(ticker)
        if not analysis: continue
        
        pnl = (analysis['price'] - details['avg_cost']) * details['shares']
        portfolio_input += f"""
        TICKER: {ticker} (Position Size: {details['shares']} shares | PnL: ${pnl:,.2f})
        Current Price: ${analysis['price']:.2f}
        News Catalyst Profile:\n{analysis['news_summary']}
        """

    watchlist_input = ""
    for ticker in WATCHLIST:
        analysis = calculate_composite_setup(ticker)
        if not analysis: continue
        
        watchlist_input += f"""
        TICKER: {ticker}
        Composite Asymmetry Score: {analysis['score']}/100 (Volume Momentum: {analysis['volume_mult']:.2f}x)
        News Sentiment Context Score: {analysis['avg_sentiment']:.2f}
        Latest Context:\n{analysis['news_summary']}
        """

    system_prompt = f"""
    You are a completely blunt, high-conviction personal portfolio risk manager. Your objective is to save the trader time by slashing market noise and delivering strict macro situational awareness.
    
    You follow this protocol:
    - For Core Portfolio Holdings: Actively search for underlying threats, major technical damage, or key structural catalysts. Skip general price summaries.
    - For Watchlist Tickers: Evaluate the Composite Asymmetry Score. If a score is exceptionally high (> 75), outline the tactical entry setup. If the score is low or mediocre (< 70), explicitly tell the user to "Fuck off and wait for a cleaner setup," explaining exactly why the current environment lacks an edge.
    
    Style Directives: Raw, hyper-concise, analytical, zero corporate fluff. Use markdown layout formatting.
    """

    user_prompt = f"""
    Process these current market metrics and news catalogs into an executive pre-market briefing.
    
    ### Core Positions Catalyst Review:
    {portfolio_input}
    
    ### Watchlist Filtering & Tactical Setup Scan:
    {watchlist_input}
    """

    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    dashboard_output = f"""# 🌅 High-Conviction Intelligence Dashboard
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{response['message']['content']}
"""
    
    with open("daily_dashboard.md", "w") as f:
        f.write(dashboard_output)
        
    print("\n🎯 Executive briefing compiled! Check daily_dashboard.md.")

if __name__ == "__main__":
    generate_executive_dashboard()