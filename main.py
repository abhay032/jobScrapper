"""
main.py
Orchestrates the full daily job digest pipeline:
1. Fetch jobs from all sources
2. Score & rank with Claude AI
3. Send top 25 to Telegram

Run manually: python main.py
Automated: GitHub Actions runs this daily at 8:00 AM IST (2:30 AM UTC)
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.job_fetcher import fetch_all_jobs
from utils.job_scorer import score_jobs_with_claude
from utils.telegram_sender import send_daily_digest


def main():
    print("=" * 50)
    print("🚀 Job Digest Bot — Starting Daily Run")
    print("=" * 50)

    # Step 1: Fetch jobs
    print("\n📡 Step 1: Fetching jobs from all sources...")
    jobs = fetch_all_jobs()

    if not jobs:
        print("❌ No jobs fetched. Check API keys and network.")
        send_daily_digest([])
        return

    print(f"✅ Fetched {len(jobs)} total jobs")

    # Step 2: Score with Claude
    print("\n🤖 Step 2: Scoring jobs with Claude AI...")
    top_jobs = score_jobs_with_claude(jobs)
    print(f"✅ Top {len(top_jobs)} jobs selected")

    # Step 3: Send to Telegram
    print("\n📲 Step 3: Sending digest to Telegram...")
    send_daily_digest(top_jobs)

    print("\n✅ Done! Digest sent successfully.")
    print("=" * 50)


if __name__ == "__main__":
    main()
