import ollama
import yfinance as yf
import pandas as pd
import json
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

sia = SentimentIntensityAnalyzer()

# ==========================================
# 1. DATA CONFIGURATION LOADER
# ==========================================
def load_secure_config():
    with open("config.json", "r") as f:
        return json.load(f)

CONFIG = load_secure_config()
PORTFOLIO = CONFIG["PORTFOLIO"]
WATCHLIST = CONFIG["WATCHLIST"]
RISK_PROFILE = CONFIG["RISK_PROFILE"]

# ==========================================
# 2. DEEP DATA & CATALYST PIPELINE
# ==========================================
def fetch_ticker_intelligence(ticker):
    """
    Extracts deep consensus valuation metrics (Low/Base/High cases),
    fixes news parsing boundaries, and structures clear context variables.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Historical price metrics for tracking momentum vectors
        hist = stock.history(period="5d")
        if hist.empty: return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        daily_perf = ((current_price - prev_close) / prev_close) * 100
        
        # Categorize immediate price shocks
        if daily_perf >= 3.5: price_shock = f"💥 PARABOLIC SURGE (+{daily_perf:.2f}%)"
        elif daily_perf <= -3.5: price_shock = f"🩸 SEVERE DROP ({daily_perf:.2f}%)"
        else: price_shock = f"⚖️ Normal Volatility Noise ({daily_perf:.2f}%)"

        # Extract Valuation Anchors (Low / Median / High Wall Street cases)
        target_low = info.get("targetLowPrice")
        target_base = info.get("targetMedianPrice") or info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        forward_pe = info.get("forwardPE")
        trailing_pe = info.get("trailingPE")
        
        valuation_context = f"- **Current Price:** ${current_price:.2f} | **Forward P/E:** {f'{forward_pe:.1f}x' if forward_pe else 'N/A'} | **Trailing P/E:** {f'{trailing_pe:.1f}x' if trailing_pe else 'N/A'}\n"
        if target_low and target_base and target_high:
            total_range = target_high - target_low
            current_pct = ((current_price - target_low) / total_range) * 100 if total_range > 0 else 0
            valuation_context += f"  - **Wall Street Targets:** Low: ${target_low:.2f} | Base: ${target_base:.2f} | High: ${target_high:.2f}\n"
            valuation_context += f"  - **Range Location:** Price is sitting at the **{current_pct:.1f}%** mark of the consensus target range."
        else:
            valuation_context += "  - **Wall Street Targets:** Forward target spectrum unavailable for this ticker."

        # FIXED NEWS PARSING ENGINE (Navigating yfinance payload structural updates)
        news_stream = stock.news
        catalysts = []
        sentiment_scores = []
        
        # Keywords determining high-impact macro shifts
        target_keywords = ["target", "upgrade", "downgrade", "partnership", "deal", "earnings", "guidance", "acquisition", "insider", "sell", "buy"]
        
        for item in news_stream[:6]:
            # DRILL DEEP: Try new payload location, fall back to root
            title = item.get('content', {}).get('title') or item.get('title', '')
            summary = item.get('content', {}).get('summary') or item.get('summary', '')
            
            if not title:
                continue
                
            combined_text = f"{title} {summary}".lower()
            
            # Execute local NLTK processing on non-empty strings
            score = sia.polarity_scores(title)['compound']
            sentiment_scores.append(score)
            
            tag = "🔹 [NEWS]"
            if any(k in combined_text for k in ["target", "upgrade", "downgrade"]):
                tag = "🎯 [ANALYST ACTION]"
            elif any(k in combined_text for k in ["partnership", "deal", "acquisition"]):
                tag = "🤝 [STRATEGIC CATALYST]"
            elif any(k in combined_text for k in ["earnings", "guidance"]):
                tag = "📊 [FUNDAMENTAL SHIFT]"

            catalysts.append(f"  {tag} {title} (Sentiment Vane: {score:.2f})")

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        if avg_sentiment >= 0.10: refined_sentiment = "Bullish Sentiment Accel 🟩"
        elif avg_sentiment <= -0.10: refined_sentiment = "Bearish Distress Overhang 🟥"
        else: refined_sentiment = "Mixed/Horizontal Noise 🟨"

        return {
            "price_shock": price_shock,
            "valuation_context": valuation_context,
            "refined_sentiment": f"{refined_sentiment} (Index: {avg_sentiment:.2f})",
            "catalysts": "\n".join(catalysts) if catalysts else "  No explicit fundamental milestones isolated in this news cycle."
        }
    except Exception as e:
        return None
# ==========================================
# 3. HIGH-VELOCITY REASONING ENGINE (UPGRADED)
# ==========================================
def query_local_brain(ticker, block_type, data_stream):
    """Feeds Ollama exactly ONE stock at a time to prevent token confusion and maximize depth."""
    
    system_prompt = f"""
    You are an expert, brutally honest institutional equity research analyst. Your primary goal is to save a high-conviction trader time by aggressively cutting out fluff and identifying structural anomalies.
    
    YOUR PROTOCOL:
    1. Look at the Price Shocks and Valuation Location. Evaluate if the stock has run completely parabolic into its high-case target ceiling (signaling a dangerous overextended entry point) or if it's dropping into its low-case valuation floor.
    2. Sift through the Catalyst stream. Isolate concrete structural shifts: analyst target revisions, strategic corporate partnerships, or fundamental guidance changes.
    3. Be completely direct. If it's a watchlist item, weigh the valuation range against recent sentiment velocity. Give an explicit, unmistakable verdict: either map out the asymmetric entry playbook, or explicitly tell them to "Sit tight, don't chase, or fuck off and wait for a pullback," detailing exactly why the current positioning lacks a statistical edge.
    
    Style: Raw, data-driven, analytical, completely blunt, zero generic filler. Use clean Markdown headers.
    """

    user_prompt = f"""
    Perform a deep, granular review on this specific {block_type} target: **{ticker}**.
    Focus heavily on pulling out partnerships, analyst target changes, structural price drops/surges, and current cycle location.

    RAW PIPELINE INPUTS FOR {ticker}:
    {data_stream}
    """

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"### {ticker}\nError executing local LLM inference: {str(e)}"

def generate_executive_dashboard():
    print("⚡ Cracking nested news structures, mapping valuation spreads...")
    
    compiled_reports = []

    # Process Core Positions Individually
    for ticker, details in PORTFOLIO["positions"].items():
        print(f" 📦 Analyzing Core Holding: {ticker}")
        intel = fetch_ticker_intelligence(ticker)
        if not intel: continue
        
        raw_stream = f"""
        - Immediate Vector: {intel['price_shock']}
        - Valuation Matrix: {intel['valuation_context']}
        - Refined Sentiment: {intel['refined_sentiment']}
        - Active Catalyst Stream:
        {intel['catalysts']}
        """
        
        report = query_local_brain(ticker, "Core Portfolio Holding", raw_stream)
        compiled_reports.append(f"## 📈 Core Holding: {ticker}\n{report}\n\n---")

    # Process Watchlist Tickers Individually
    for ticker in WATCHLIST:
        print(f" 🔭 Analyzing Watchlist Target: {ticker}")
        intel = fetch_ticker_intelligence(ticker)
        if not intel: continue
        
        raw_stream = f"""
        - Immediate Vector: {intel['price_shock']}
        - Valuation Matrix: {intel['valuation_context']}
        - Refined Sentiment: {intel['refined_sentiment']}
        - Active Catalyst Stream:
        {intel['catalysts']}
        """
        
        report = query_local_brain(ticker, "Watchlist Target", raw_stream)
        compiled_reports.append(f"## 🔭 Watchlist Element: {ticker}\n{report}\n\n---")

    # Combine all individual dense reports into the final daily dashboard
    final_dashboard_content = f"""# 🌅 High-Velocity Market Intelligence Dashboard
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{"\n".join(compiled_reports)}
"""
    
    with open("daily_dashboard.md", "w") as f:
        f.write(final_dashboard_content)
        
    print("\n🎯 Complete target-aware intelligence dashboard successfully generated!")

if __name__ == "__main__":
    generate_executive_dashboard()
