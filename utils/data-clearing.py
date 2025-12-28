import re
import datetime
from app.db import reviews_with_embeddings, reviews_structured

def parse_reviewer_title(title):
    title = title.strip()
    if "," in title:
        parts = title.split(",", 1)
        return parts[0].strip().lower(), parts[1].strip().lower()
    return title.lower(), None

def parse_project_budget(project_size):
    budget_mapping = {
        "Less than $10,000": (0, 9999, "Less than $10,000"),
        "$10,000 to $49,999": (10000, 49999, "$10,000 to $49,999"),
        "$50,000 to $199,999": (50000, 199999, "$50,000 to $199,999"),
        "$200,000 to $999,999": (200000, 999999, "$200,000 to $999,999"),
        "$1,000,000+": (1000000, None, "Enterprise"),
        "Confidential": (-1, -1, "Confidential"),
    }
    return budget_mapping.get(project_size, (None, None, "Unknown"))

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    "January": 1, "February": 2, "March": 3, "April": 4, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

def normalize_month(month_raw: str):
    return month_raw.replace(".", "").title()

def parse_project_length(length: str):
    now = datetime.datetime.now()
    length = length.strip().replace("–", "-").replace("—", "-")

    match_full = re.match(
        r'(?P<start_month>\w+)\.?\s(?P<start_year>\d{4})\s*-\s*(?P<end_month>\w+)\.?\s(?P<end_year>\d{4})',
        length
    )
    if match_full:
        start_month = normalize_month(match_full.group("start_month"))
        start_year = int(match_full.group("start_year"))
        end_month = normalize_month(match_full.group("end_month"))
        end_year = int(match_full.group("end_year"))

        start_date = datetime.datetime(start_year, MONTHS[start_month], 1)
        end_date = datetime.datetime(end_year, MONTHS[end_month], 1)
        return start_date, end_date

    match_ongoing = re.match(
        r'(?P<start_month>\w+)\.?\s(?P<start_year>\d{4})\s*-\s*Ongoing',
        length,
        re.IGNORECASE
    )
    if match_ongoing:
        start_month = normalize_month(match_ongoing.group("start_month"))
        start_year = int(match_ongoing.group("start_year"))

        start_date = datetime.datetime(start_year, MONTHS[start_month], 1)
        end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) 
        return start_date, end_date

    match_month_range = re.match(
        r'(?P<start_month>\w+)\.?\s*-\s*(?P<end_month>\w+)\.?\s(?P<year>\d{4})',
        length
    )
    if match_month_range:
        year = int(match_month_range.group("year"))
        start_month = normalize_month(match_month_range.group("start_month"))
        end_month = normalize_month(match_month_range.group("end_month"))

        start_date = datetime.datetime(year, MONTHS[start_month], 1)
        end_date = datetime.datetime(year, MONTHS[end_month], 1)
        return start_date, end_date

    return None, None

def parse_company_size(size):
    size_mapping = {
        "1-10 Employees": (1, 10),
        "11-50 Employees": (11, 50),
        "51-200 Employees": (51, 200),
        "201-500 Employees": (201, 500),
        "501-1,000 Employees": (501, 1000),
        "1,001-5,000 Employees": (1001, 5000),
        "5,001-10,000 Employees": (5001, 10000),
        "10,000+ Employees": (10000, None),
    }
    return size_mapping.get(size, (None, None))

def parse_location(location):
    parts = location.split(", ")
    return parts[0], parts[1] if len(parts) > 1 else None


async def process_reviews():
    structured_data = []

    async for doc in reviews_with_embeddings.find():
        reviewer_position, reviewer_company = parse_reviewer_title(doc.get("reviewer_title", ""))
        project_budget_from, project_budget_to, project_budget_label = parse_project_budget(doc.get("project_size", ""))
        project_start_date, project_end_date = parse_project_length(doc.get("project_length", ""))
        reviewer_size_from, reviewer_size_to = parse_company_size(doc.get("reviewer_size", ""))
        reviewer_city, reviewer_country = parse_location(doc.get("reviewer_location", ""))
        tags = doc.get("tags", [])
        if len(tags) > 0:
            tags = [tag for tag in tags if tag not in ['clutch', 'did']]

        structured_doc = {
            "_id": doc["_id"],
            "company_id": doc["company_id"],
            "company_name": doc["company_name"],
            "company_url": doc["company_url"],
            "title": doc["title"],
            "date_published": doc["date_published"],
            "project_name": doc["project_name"],
            "project_category": doc["project_category"],
            "project_all_categories": doc["project_all_categories"],
            "project_start_date": project_start_date,
            "project_end_date": project_end_date,
            "project_length_label": doc["project_length"],
            "project_budget_from": project_budget_from,
            "project_budget_to": project_budget_to,
            "project_budget_label": project_budget_label,
            "reviewer_position": reviewer_position,
            "reviewer_company": reviewer_company,
            "reviewer_industry": doc["reviewer_industry"],
            "reviewer_size_from": reviewer_size_from,
            "reviewer_size_to": reviewer_size_to,
            "reviewer_size_label": doc["reviewer_size"],
            "reviewer_city": reviewer_city,
            "reviewer_country": reviewer_country,
            "reviewer_review_type": doc["reviewer_review_type"],
            "reviewer_is_verified": doc["reviewer_is_verified"],
            "reviewer_linkedin_url": doc["reviewer_linkedin_url"],
            "content_background": doc["content_background"],
            "content_opportunity_challenge": doc["content_opportunity_challenge"],
            "content_solution": doc["content_solution"],
            "content_results_feedback": doc["content_results_feedback"],
            "combined": doc["combined"],
            "embeddings": doc["embeddings"],
            "tags": tags
        }

        structured_data.append(structured_doc)

        if len(structured_data) >= 1000:
            await reviews_structured.insert_many(structured_data)
            print(f"Inserted {len(structured_data)} structured documents...")
            structured_data.clear()

    if structured_data:
        await reviews_structured.insert_many(structured_data)
        print(f"Inserted {len(structured_data)} structured documents successfully!")

import asyncio
asyncio.run(process_reviews())