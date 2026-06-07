# Local Portfolio Manager Agent

A local AI-powered assistant designed to provide an instant, data-driven pre-market breifing on your stock holdings and watchlist. This agent is designed too deliver actionable portfolio verdicts entirely locally on your machine.

---

##  Why did I make this?

Upon starting my internship I realized quickly that investors lack the time to read through news, analyze charts and do other tasks that represent the bare minimum when managing a self-run investment portfolio.

Most retail stock market trackers rely heavily on financial news headline aggregators. These headlines tend to be engineered for click-through rates rather than actual insight. They use open-ended, emotional hooks that mislead many traditional sentiment analyzing models.

**This Agent solves the problem by:**
* **Eliminating Scraper Noise:** It strips out clickbait hooks and isolates the underlying summary body text.
* **Tracking "Smart Money" Anchors:** It tracks actual structural signals: Form 4 executive insider buying/selling trends, 13F hedge fund concentration, and short interest parameters.
* **10-Second Time-to-Awareness:** It synthesizes raw data streams into a single high-impact **Executive Briefing Matrix** right at the top of your morning dashboard file. If an asset registers no material structural variance, it compresses it into a single line, allowing you to prioritize critical risk items instantly.

---

## Technical Architecture Breakdown

The engine shifts away from broad single-prompt dumps—which easily overwhelm small local neural pathways—and implements a decoupled, sequential extraction loop.

```
                  [ config.json ]
               (Portfolio & Watchlist)
                          |
             [ Sequential Extraction Loop ]
        (Iterates through assets one-by-one)
                          |
     +--------------------+--------------------+
     |                    |                    |
[yfinance API]      [yfinance API]       [yfinance API]
Valuation Target    Insider Form 4       Nested Article
Spreads (Low/High)  & 13F Concentrations Summary Bodies
     |                    |                    |
     +--------------------+--------------------+
                          |
            [ Strict Context Consolidation ]
         (Data isolation to prevent token leak)
                          |
             [ Local Ollama LLM Inference ]
                  (Llama 3.2 3B Model)
                          |
             [ Executive Matrix Assembler ]
        (Global synthesis map via second LLM call)
                          |
              [ ~/Desktop/daily_dashboard.md ]
```

### Architectural Implementations

1. **Sequential Single-Ticker Isolation (MapReduce Design):** Handing multiple assets to a small language model simultaneously causes context-window dilution and variable hallucinations. This agent queries the API, extracts the data matrix, and executes inference for **exactly one ticker at a time**. This guarantees 100% of the model's focus is dedicated to the core asset profile before moving to the next block.
2. **Consensus Target Boundaries:** Price movements are relative to valuation limits. The agent maps out Wall Street's Low, Median, and High target ranges, calculating the exact location percentage of current pricing to anchor its execution verdicts.
3. **Automated macOS State Recovery Execution:** Scheduled natively via operating system calendar configurations, the execution architecture handles system sleep states smoothly. If the computer is closed/off during the target execution time, macOS queues the background daemon, firing the pipeline and refreshing the desktop file within 15 seconds of logging back in.

---

## Installation & Setup Tutorial

Follow these exact steps to clone, configure, and execute the automated intelligence infrastructure locally on your machine.

### 1. Clone the Workspace & Initialize Environment
Clone the repository to your local machine and navigate into the root project directory:
```bash
git clone https://github.com/pranavbhupathiraju/Local-Portfolio-Manager.git
cd Local-Portfolio-Manager
```

Create a secure Python virtual environment to keep your global operating system dependencies completely decoupled and isolated:
```bash
python3 -m venv trading_env
source trading_env/bin/activate
```

### 2. Install Project Dependencies
Install the required analytical and modeling libraries inside your virtual environment:
```bash
pip install yfinance pandas ollama nltk
```

Initialize NLTK's local sentiment lexicons (used by the script's semantic evaluation pipelines):
```bash
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 3. Install and Initialize the Local LLM Engine
1. Download and install the open-source **Ollama** framework natively onto your machine from ollama.com.
2. Open your terminal window and fetch the localized, highly optimized **Llama 3.2 (3B)** model weights:
```bash
ollama run llama3.2
```
*(Once the download finishes and the prompt opens, type `/exit` to return to your standard workspace shell).*

### 4. Configure Your Secure Local Parameters
Create your personalized, ignored configurations profile based on the template layout provided:
```bash
cp config.example.json config.json
```

Open `config.json` in your code editor and map out your core portfolio allocation limits and tracking targets:
```json
{
    "PORTFOLIO": {
        "positions": {
            "NVDA": {"shares": 20, "avg_cost": 110.00},
            "HOOD": {"shares": 50, "avg_cost": 18.50},
            "AMD": {"shares": 50, "avg_cost": 140.00}
        }
    },
    "WATCHLIST": ["PLTR", "AMZN", "MSFT", "UUUU", "GEV"]
}
```
*(Note: Because `config.json` is explicitly registered inside the `.gitignore` file, your private capital allocations will never be tracked or exposed online during git push commands).*

---

## Usage & Automated Execution Options

### Manual High-Velocity Run
To manually execute the scraping pipelines and instantly compile your pre-market executive brief on your laptop Desktop, run:
```bash
python agent.py
```

### Creating a Fast-Execution Terminal Alias
To completely bypass navigation strings during your morning routine, you can map a quick command shortcut. Append an alias declaration straight into your local environment run profile:
```bash
echo "alias sifter='source ~/Local-Portfolio-Manager/trading_env/bin/activate && python ~/Local-Portfolio-Manager/agent.py'" >> ~/.zshrc && source ~/.zshrc
```
Now, typing the single keyword `sifter` anywhere in your terminal windows will immediately spin up the local worker pipes and update your dashboard.

### Background Calendar Automation (Internal Systems Daemon)
To have the script run completely hands-off every single day before your corporate alarm fires:
* The system leverages native background system daemons configured via internal task engines.
* If your laptop is asleep or shut down at the exact calendar timestamp, the OS schedules execution to fire **the exact second you wake up and unlock your machine**. 
* A freshly generated `daily_dashboard.md` file will automatically compile right on your Desktop, giving you an immediate 10-second situational awareness vector before you head out the door for your day.

---

## 📊 Sample Executive Dashboard Output Layout

When you open `daily_dashboard.md` on your Desktop, you are met with a structured, noise-free layout:

```markdown
# 🌅 High-Velocity Internship Intelligence Dashboard

## 🚨 EXECUTIVE BRIEFING MATRIX
### 🛑 CRITICAL ACTION REQUIRED
* **PLTR**: 🟩 [BUY/ACCUMULATE] - Major corporate contract validation paired with institutional whale scaling.
* **NVDA**: 🟥 [SELL/TRIM RISK] - Heavy executive insider Form 4 distribution noticed at 97% of Wall Street target ceilings.

### ⚖️ STEADY POSITIONING STATE
* **AMD**: 🟨 [HOLD / DO NOTHING] - No material structural updates or filing modifications.
* **HOOD**: 🟨 [HOLD / DO NOTHING] - Normal volatility within standard target deviations.

---

## 💼 ACTIVE PORTFOLIO ASSESSMENTS
### 📈 NVDA
* **Synthesis**: Executive leadership registered heavy equity sales via Form 4 filings over the past 72 hours as the price hit $132, pushing it directly into the top 3% bound of institutional price consensus targets.
* **Verdict**: 🟥 **[SELL/TRIM RISK]** - Profit-taking is highly recommended as technical parameters show overextension with a complete lack of near-term buying momentum from corporate insiders.
```

---

## 🛡️ License & Disclaimers
This repository is configured entirely for personal software engineering portfolio demonstration and capital monitoring automation uses. 

**Disclaimer:** This software is an experimental local AI data parsing tool. None of the compiled automated output, evaluation vectors, or inferred execution statuses represent official financial, legal, or investment advice. Always double-check raw institutional filings independently. Always double check claims and do not use the outputs of this agent/project as advice or in a suggestive manner in any regard.
