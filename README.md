# 🚀 Daily Job Digest Bot

A personalized job digest bot that fetches 20-30 relevant jobs daily, scores them using Claude AI against your resume, and sends the top matches to your Telegram at **8:00 AM IST** every day.

---

## 🏗️ Architecture

```
GitHub Actions (cron: 8AM IST daily)
        ↓
job_fetcher.py  →  SerpAPI (Google Jobs) + Company APIs
        ↓
job_scorer.py   →  Claude AI scores each job against your profile
        ↓
telegram_sender.py  →  Sends top 25 jobs to your Telegram
```

---

## ⚙️ Setup Guide (One-Time, ~15 mins)

### Step 1 — Get your API Keys

#### 🔑 SerpAPI (Google Jobs scraper)
1. Go to [serpapi.com](https://serpapi.com) → Sign up (free)
2. Free tier gives **100 searches/month** (enough for daily runs)
3. Copy your API key from the dashboard

#### 🔑 Anthropic API (Claude job scorer)
1. Go to [console.anthropic.com](https://console.anthropic.com) → Sign up
2. Go to **API Keys** → Create new key
3. Add ~$5 credits (costs ~$0.01/day to run)

#### 🔑 Telegram Bot
1. Open Telegram → search for `@BotFather`
2. Send `/newbot` → follow prompts → copy your **Bot Token**
3. To get your **Chat ID**:
   - Start a chat with your new bot (send any message)
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":XXXXXXX}` — that number is your Chat ID

---

### Step 2 — Set up the GitHub Repository

```bash
# Clone or fork this repo
git clone https://github.com/YOUR_USERNAME/job-digest-bot
cd job-digest-bot

# Create your .env file for local testing
cp .env.example .env
# Fill in your keys in .env
```

---

### Step 3 — Add Secrets to GitHub

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these 4 secrets:

| Secret Name | Value |
|---|---|
| `SERPAPI_KEY` | Your SerpAPI key |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

---

### Step 4 — Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. To test immediately: Go to **Actions** → **Daily Job Digest** → **Run workflow**

---

## 🧪 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run manually
python main.py
```

---

## 🎯 Customizing Your Profile

Edit `utils/job_scorer.py` → `CANDIDATE_PROFILE` section to update:
- Your current role/company
- Skills
- Target roles
- Target companies
- Expected CTC

Edit `scrapers/job_fetcher.py` → `SEARCH_QUERIES` to change job search terms.

---

## 📅 Schedule

The bot runs at **8:00 AM IST (2:30 AM UTC)** daily via GitHub Actions cron.

To change the time, edit `.github/workflows/daily_digest.yml`:
```yaml
- cron: "30 2 * * *"  # Change this (UTC time)
```

IST to UTC converter: IST = UTC + 5:30

| IST Time | UTC Cron |
|---|---|
| 7:00 AM | `30 1 * * *` |
| 8:00 AM | `30 2 * * *` |
| 9:00 AM | `30 3 * * *` |
| 12:00 PM | `30 6 * * *` |

---

## 💰 Cost Estimate

| Service | Cost |
|---|---|
| SerpAPI (100 free/month) | **$0/month** |
| Claude API (~30 jobs/day scored) | **~$0.30/month** |
| GitHub Actions (free tier) | **$0/month** |
| Telegram Bot | **$0/month** |
| **Total** | **~$0.30/month** |

---

## 📲 Sample Telegram Output

```
🚀 Daily Job Digest — 20 Mar 2026
━━━━━━━━━━━━━━━━━━━━
📊 25 curated jobs found
🔴 HIGH priority: 8 | 🟡 MEDIUM: 17

🔴 1. Software Engineer II - Backend
🏢 Uber | 📍 Bangalore, India
⭐ Match Score: 92/100
💡 Perfect match: distributed systems + Java + SDE-2 level
🕐 Posted: 1 day ago
🔗 Apply Here
```

---

## 🛠️ Troubleshooting

**No jobs received?**
- Check GitHub Actions logs under the Actions tab
- Verify all 4 secrets are correctly set
- Test SerpAPI key at serpapi.com/playground

**Telegram messages not arriving?**
- Make sure you've sent at least one message to your bot first
- Double-check your Chat ID (it's a number, not your username)

**Claude scoring not working?**
- Verify ANTHROPIC_API_KEY is valid and has credits
- Jobs will still be sent, just unscored

---

## 📁 Project Structure

```
job-digest-bot/
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # GitHub Actions cron
├── scrapers/
│   └── job_fetcher.py         # Fetches from SerpAPI + company pages
├── utils/
│   ├── job_scorer.py          # Claude AI scoring
│   └── telegram_sender.py     # Telegram delivery
├── main.py                    # Orchestrator
├── requirements.txt
├── .env.example               # Template for your keys
├── .gitignore
└── README.md
```
