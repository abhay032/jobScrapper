"""
telegram_sender.py
Sends the daily job digest to your Telegram chat.
"""

import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_message(text: str) -> bool:
    """Send a message via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False


def format_job_digest(jobs: list[dict]) -> list[str]:
    """
    Format jobs into Telegram-friendly messages.
    Splits into multiple messages since Telegram has a 4096 char limit.
    """
    today = datetime.now().strftime("%d %b %Y")
    messages = []

    # Header message
    high = [j for j in jobs if j.get("apply_priority") == "HIGH"]
    medium = [j for j in jobs if j.get("apply_priority") == "MEDIUM"]

    header = (
        f"🚀 *Daily Job Digest — {today}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{len(jobs)} curated jobs found*\n"
        f"🔴 HIGH priority: {len(high)} | 🟡 MEDIUM: {len(medium)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_Personalized for Abhay Kumar | SDE-2 target_"
    )
    messages.append(header)

    # Priority emoji map
    priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

    # Send HIGH priority jobs first
    for i, job in enumerate(jobs, 1):
        priority = job.get("apply_priority", "MEDIUM")
        emoji = priority_emoji.get(priority, "🟡")
        score = job.get("score", "N/A")
        link = job.get("link", "")
        posted = job.get("posted", "")
        reason = job.get("reason", "")

        msg = (
            f"{emoji} *{i}. {job['title']}*\n"
            f"🏢 {job['company']} | 📍 {job['location']}\n"
            f"⭐ Match Score: {score}/100\n"
            f"💡 _{reason}_\n"
        )
        if posted:
            msg += f"🕐 Posted: {posted}\n"
        if link:
            msg += f"🔗 [Apply Here]({link})\n"

        messages.append(msg)

    # Footer
    footer = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *Apply to HIGH priority jobs first!*\n"
        "📌 Track your applications in a spreadsheet.\n"
        "🔁 Next digest tomorrow at 8:00 AM IST"
    )
    messages.append(footer)

    return messages


def send_daily_digest(jobs: list[dict]) -> None:
    """Send the full digest to Telegram."""
    if not jobs:
        send_message("⚠️ *Daily Job Digest* — No jobs found today. Will retry tomorrow.")
        return

    messages = format_job_digest(jobs)
    print(f"Sending {len(messages)} messages to Telegram...")

    for i, msg in enumerate(messages):
        success = send_message(msg)
        if success:
            print(f"  ✓ Message {i+1}/{len(messages)} sent")
        else:
            print(f"  ✗ Message {i+1}/{len(messages)} failed")

        # Small delay to avoid Telegram rate limits
        import time
        time.sleep(0.3)


if __name__ == "__main__":
    # Test message
    test_jobs = [
        {
            "title": "Software Engineer II - Backend",
            "company": "Uber",
            "location": "Bangalore, India",
            "score": 92,
            "reason": "Perfect match: distributed systems + Java + SDE-2 level",
            "apply_priority": "HIGH",
            "link": "https://uber.com/careers/example",
            "posted": "1 day ago",
            "source": "Google Jobs",
        },
        {
            "title": "Senior Backend Engineer",
            "company": "Atlassian",
            "location": "Bengaluru, India",
            "score": 87,
            "reason": "Strong match: Java backend, cloud infra, skill-based leveling",
            "apply_priority": "HIGH",
            "link": "https://atlassian.com/careers/example",
            "posted": "3 days ago",
            "source": "Google Jobs",
        },
    ]
    send_daily_digest(test_jobs)
