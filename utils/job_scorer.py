"""
job_scorer.py
Uses Claude API to score and rank jobs against your resume profile.
Filters down to the top 25 most relevant jobs.
"""

import os
import json
import requests

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Your profile — update this if your resume changes
CANDIDATE_PROFILE = """
Name: Abhay Kumar
Current Role: System Development Engineer I at Amazon (Aug 2025 - Present)
Previous: Developer Intern at SAP Labs (Aug 2024 - Jun 2025)
Education: M.Tech Cyber Security, NIT Kurukshetra (CGPA 8.71) | B.Tech IT, GBU (CGPA 8.36)

Skills:
- Languages: Java, Python, C, C++
- Cloud & DevOps: AWS (EC2, S3, Lambda, CloudWatch), CI/CD, Infrastructure Operations
- Frameworks: Spring Boot, Kafka, Microservices, RESTful APIs
- AI/ML: TensorFlow, LLMs, GenAI, Prompt Engineering
- Concepts: Distributed Systems, DSA, OS, Network Security, Cyber Security

Key Achievements:
- Migrated large-scale distributed data platform at Amazon
- Built pre-deployment integration testing workflows
- Research paper on Medical Image Segmentation (Springer ISMS)
- GATE 2023 Qualified

Target Roles: Backend SDE-2, GenAI/AI Engineer, Cloud/DevOps Engineer, Distributed Systems
Target Companies: Uber, Atlassian, Salesforce, Adobe, Flipkart, Meesho, Swiggy, Google, Microsoft
Target Location: Anywhere in India (prefer Bangalore)
Expected CTC: 20+ LPA
"""


def score_jobs_with_claude(jobs: list[dict]) -> list[dict]:
    """Send jobs to Claude API for scoring and ranking."""
    if not CLAUDE_API_KEY:
        print("Warning: ANTHROPIC_API_KEY not set. Returning unscored jobs.")
        for job in jobs:
            job["score"] = 50
            job["reason"] = "Unscored (API key missing)"
        return jobs[:25]

    # Batch jobs into groups of 20 to avoid token limits
    scored_jobs = []
    batch_size = 20
    batches = [jobs[i:i+batch_size] for i in range(0, len(jobs), batch_size)]

    for batch_num, batch in enumerate(batches):
        print(f"  Scoring batch {batch_num + 1}/{len(batches)} ({len(batch)} jobs)...")

        jobs_text = json.dumps([{
            "id": i,
            "title": j["title"],
            "company": j["company"],
            "location": j["location"],
            "description": j["description_snippet"],
        } for i, j in enumerate(batch)], indent=2)

        prompt = f"""You are a job matching assistant. Given a candidate profile and a list of job postings, 
score each job from 0-100 based on how well it matches the candidate.

CANDIDATE PROFILE:
{CANDIDATE_PROFILE}

JOB LISTINGS:
{jobs_text}

Return ONLY a JSON array (no markdown, no explanation) with this structure:
[
  {{
    "id": 0,
    "score": 85,
    "reason": "Strong match: Java backend + distributed systems at scale, targets SDE-2 level",
    "apply_priority": "HIGH"
  }},
  ...
]

Scoring criteria:
- 80-100: Excellent match (role, level, company tier, tech stack all align)
- 60-79: Good match (most criteria align, minor gaps)
- 40-59: Decent match (role fits but company/level/stack may differ)
- Below 40: Weak match (skip)

apply_priority: HIGH (80+), MEDIUM (60-79), LOW (below 60)
"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["content"][0]["text"].strip()

            # Clean JSON if wrapped in markdown
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            scores = json.loads(content)

            for score_item in scores:
                job_idx = score_item["id"]
                if job_idx < len(batch):
                    batch[job_idx]["score"] = score_item.get("score", 0)
                    batch[job_idx]["reason"] = score_item.get("reason", "")
                    batch[job_idx]["apply_priority"] = score_item.get("apply_priority", "LOW")

            scored_jobs.extend(batch)

        except Exception as e:
            print(f"  Scoring error for batch {batch_num + 1}: {e}")
            for job in batch:
                job["score"] = 50
                job["reason"] = "Scoring unavailable"
                job["apply_priority"] = "MEDIUM"
            scored_jobs.extend(batch)

    # Sort by score descending and return top 25
    scored_jobs.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_jobs = [j for j in scored_jobs if j.get("score", 0) >= 40][:25]

    print(f"  Top {len(top_jobs)} jobs selected after scoring.")
    return top_jobs


if __name__ == "__main__":
    # Test with dummy data
    test_jobs = [
        {
            "title": "Software Engineer II - Backend",
            "company": "Uber",
            "location": "Bangalore",
            "description_snippet": "Distributed systems, Java, Python, microservices at scale.",
            "link": "https://uber.com/careers/test",
            "posted": "2 days ago",
            "source": "Test",
        }
    ]
    result = score_jobs_with_claude(test_jobs)
    print(json.dumps(result, indent=2))
