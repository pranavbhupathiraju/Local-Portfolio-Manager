import ollama
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# 1. SECURE CONFIGURATION LOADER
# ==========================================
def load_secure_config():
    with open("config.json", "r") as f:
        return json.load(f)

CONFIG = load_secure_config()
PORTFOLIO = CONFIG["PORTFOLIO"]
WATCHLIST = CONFIG["WATCHLIST"]

# ==========================================
# 2. RAW INSTITUTIONAL PIPELINE
# ==========================================
def fetch_ticker_intelligence(ticker):
    """Extracts raw pricing metrics, smart money density, and anti-clickbait summaries."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        if not current_price:
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0

        # Wall Street Valuation Spread
        target_low = info.get("targetLowPrice")
        target_base = info.get("targetMedianPrice") or info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        
        valuation_context = f"Price: ${current_price:.2f} | "
        if target_low and target_high:
            total_range = target_high - target_low
            current_pct = ((current_price - target_low) / total_range) * 100 if total_range > 0 else 0
            valuation_context += f"WallSt Ranges -> Low: ${target_low:.2f} | Base: ${target_base:.2f} | High: ${target_high:.2f} (Sitting at {current_pct:.1f}% mark of range)."
        else:
            valuation_context += "Wall Street Target spectrum unavailable."

        # Hedge Fund Concentration (13F) & Short Interest
        held_by_insiders = info.get("heldPercentInsiders", 0) * 100 if info.get("heldPercentInsiders") else 0
        held_by_institutions = info.get("heldPercentInstitutions", 0) * 100 if info.get("heldPercentInstitutions") else 0
        shares_short = info.get("shortPercentOfFloat", 0) * 100 if info.get("shortPercentOfFloat") else 0
        
        institutional_context = f"Insider Hold: {held_by_insiders:.2f}% | Hedge Fund Hold: {held_by_institutions:.2f}% | Short Interest Float: {shares_short:.2f}%"

        # Executive Insider Actions (Form 4)
        try:
            insider_tx = stock.get_insider_transactions()
            if insider_tx is not None and not insider_tx.empty:
                recent_tx = insider_tx.head(3)
                tx_list = [f"Trans: {row.get('Text')} | Shares: {row.get('Shares')} | Title: {row.get('Insider_Position')}" for _, row in recent_tx.iterrows()]
                insider_summary = " & ".join(tx_list)
            else:
                insider_summary = "No material insider tracking registered in this window."
        except:
            insider_summary = "Insider tracking registry offline."

        # Content Summary Extraction (Anti-Clickbait Engine)
        news_stream = stock.news
        deep_news_payload = []
        for item in news_stream[:3]:
            title = item.get('content', {}).get('title') or item.get('title', '')
            summary = item.get('content', {}).get('summary') or item.get('summary', '')
            if title:
                body = summary if len(summary) > 20 else "No summary details."
                deep_news_payload.append(f"[{title} -> Detail Fact: {body}]")
        news_summary = " | ".join(deep_news_payload) if deep_news_payload else "No major news updates."

        return f"""
        * VALUATION SPREAD: {valuation_context}
        * INSTITUTIONAL CONCENTRATION: {institutional_context}
        * RECENT FORM 4 INSIDER MOVES: {insider_summary}
        * UNFILTERED ARTICLE CORPORATE FACTS: {news_summary}
        """
    except Exception as e:
        print(f"Error compiling {ticker}: {str(e)}")
        return None

# ==========================================
# 3. HIGH-VELOCITY REASONING ENGINE
# ==========================================
def query_local_brain(ticker, data_stream):
    """Executes hyper-dense individual ticker assessment."""
    system_prompt = """
    You are an ironclad equity risk officer. Your target reader is a busy summer corporate intern who has exactly 10 seconds to screen their portfolio. 
    
    YOUR UNBENDING ANALYSIS PROTOCOL:
    1. Cross-reference pricing against target limits. If price is near the ceiling and executive insiders are selling, trigger an alert.
    2. Read news details for operational data. Ignore headline clickbait completely.
    3. Output EXACTLY two single-sentence bullet lines for the stock. No introduction, no conversational text, no corporate disclaimers.
    
    EXACT OUTPUT TEMPLATE FORMAT:
    - **Synthesis**: [1-sentence dense fundamental evaluation of insider, institutional, and structural data alignment]
    - **Verdict**: [State either 🟩 **[BUY/ACCUMULATE]**, 🟥 **[SELL/TRIM RISK]**, or 🟨 **[HOLD / DO NOTHING]** followed by a 1-sentence blunt technical reason why]
    """
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Analyze ticker data matrix for {ticker}:\n{data_stream}"}
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"- **Error**: Local model inference failed ({str(e)})"

def generate_global_matrix(ticker_reports):
    """Assembles all ticker verdicts into a high-impact, single-glance dashboard panel."""
    system_prompt = """
    You are a high-speed intelligence compilation officer. Your job is to read individual stock analyst reports and combine them into a single, compact Executive Morning Alert box.
    
    CRITICAL COMPRESS RULE:
    Extract only the stock symbol and its execution verdict emoji block. Group them clearly into three exact lists inside a clean markdown layout block:
    * 🛑 CRITICAL ACTION REQUIRED (List any stocks flagged as BUY or SELL)
    * ⚖️ STEADY POSITIONING STATE (List any stocks flagged as HOLD / DO NOTHING)
    
    Keep it completely brief. No conversational intro or outro.
    """
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Synthesize these ticker files into the matrix:\n{ticker_reports}"}
            ]
        )
        return response['message']['content'].strip()
    except:
        return "### ⚠️ Morning Briefing Matrix Generation Error"

# ==========================================
# 4. CONTROL SYSTEM DISPATCHER
# ==========================================
def generate_executive_dashboard():
    print("⚡ Fetching fundamental coordinates and executing local inference...")
    
    raw_reports_dump = []
    portfolio_output = ""
    watchlist_output = ""

    for ticker in PORTFOLIO["positions"].keys():
        print(f" 📦 Ingesting Core Asset: {ticker}")
        data_stream = fetch_ticker_intelligence(ticker)
        if not data_stream: continue
        analysis = query_local_brain(ticker, data_stream)
        raw_reports_dump.append(f"Asset: {ticker} | Report:\n{analysis}")
        portfolio_output += f"### 📈 {ticker}\n{analysis}\n\n"

    for ticker in WATCHLIST:
        print(f" 🔭 Ingesting Watchlist Target: {ticker}")
        data_stream = fetch_ticker_intelligence(ticker)
        if not data_stream: continue
        analysis = query_local_brain(ticker, data_stream)
        raw_reports_dump.append(f"Asset: {ticker} | Report:\n{analysis}")
        watchlist_output += f"### 🔭 {ticker}\n{analysis}\n\n"

    print("📊 Synthesizing Global Executive Summary Matrix Panel...")
    all_reports_combined = "\n\n".join(raw_reports_dump)
    top_matrix_panel = generate_global_matrix(all_reports_combined)

    final_dashboard = f"""# 🌅 High-Velocity Internship Intelligence Dashboard
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

## 🚨 EXECUTIVE BRIEFING MATRIX
{top_matrix_panel}

---

## 💼 ACTIVE PORTFOLIO ASSESSMENTS
{portfolio_output}

## 🔬 WATCHLIST TARGET SPECTRUMS
{watchlist_output}
"""
    
    output_path = os.path.expanduser("~/Desktop/daily_dashboard.md")
    with open(output_path, "w") as f:
        f.write(final_dashboard)
        
    print(f"\n🎯 Execution Complete! Dashboard dropped cleanly onto your desktop: {output_path}")

if __name__ == "__main__":
    generate_executive_dashboard()