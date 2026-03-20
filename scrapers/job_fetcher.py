"""
job_fetcher.py
Fetches jobs from SerpAPI (Google Jobs) and direct company career pages.
"""

import os
import requests
from datetime import datetime

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# Your profile keywords — edit these anytime
SEARCH_QUERIES = [
    "Software Engineer backend distributed systems Bangalore",
    "Software Engineer GenAI LLM Bangalore",
    "Cloud Engineer AWS DevOps Bangalore",
    "SDE 2 backend Java Python Bangalore",
    "AI Engineer LLM backend Bangalore",
]

COMPANY_CAREER_PAGES = [
    {
        "company": "Uber",
        "url": "https://www.uber.com/api/loadfe/jobs/search?query=software+engineer&location=bangalore&department=engineering",
    },
    {
        "company": "Atlassian",
        "url": "https://careers.atlassian.com/api/jobs?search=software+engineer&location=bangalore",
    },
]


def fetch_via_serpapi(query: str) -> list[dict]:
    """Fetch jobs from Google Jobs via SerpAPI."""
    if not SERPAPI_KEY:
        print("Warning: SERPAPI_KEY not set, skipping SerpAPI fetch.")
        return []

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": "Bangalore, India",
        "api_key": SERPAPI_KEY,
        "chips": "date_posted:week",  # only last 7 days
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs_results", [])

        parsed = []
        for job in jobs:
            parsed.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "description_snippet": job.get("description", "")[:300],
                "link": job.get("share_link") or job.get("related_links", [{}])[0].get("link", ""),
                "posted": job.get("detected_extensions", {}).get("posted_at", ""),
                "source": "Google Jobs / SerpAPI",
            })
        return parsed

    except Exception as e:
        print(f"SerpAPI error for query '{query}': {e}")
        return []


def fetch_company_pages() -> list[dict]:
    """Directly hit company career page APIs where available."""
    jobs = []

    # Uber public jobs API
    try:
        uber_url = "https://api.uber.com/v1/careers/jobs?location=bangalore&department=engineering"
        # Uber doesn't have a clean public API — fallback to SerpAPI for them
        # Placeholder: extend this with BeautifulSoup scraping if needed
        pass
    except Exception as e:
        print(f"Company page fetch error: {e}")

    return jobs


def deduplicate(jobs: list[dict]) -> list[dict]:
    """Remove duplicate jobs based on title + company."""
    seen = set()
    unique = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


def fetch_all_jobs() -> list[dict]:
    """Main entry point — fetches from all sources."""
    all_jobs = []

    print(f"[{datetime.now().isoformat()}] Fetching jobs from SerpAPI...")
    for query in SEARCH_QUERIES:
        results = fetch_via_serpapi(query)
        print(f"  → '{query}': {len(results)} jobs found")
        all_jobs.extend(results)

    print(f"[{datetime.now().isoformat()}] Fetching from company career pages...")
    all_jobs.extend(fetch_company_pages())

    all_jobs = deduplicate(all_jobs)
    print(f"[{datetime.now().isoformat()}] Total unique jobs: {len(all_jobs)}")
    return all_jobs


if __name__ == "__main__":
    jobs = fetch_all_jobs()
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']} @ {job['company']}")
        print(f"   {job['location']} | {job['posted']}")
        print(f"   {job['link']}")
