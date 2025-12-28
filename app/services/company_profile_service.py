import uuid
from bson import ObjectId
from typing import List, Optional
from app.db import company_profiles
from app.graphql.types import Profile
import re

async def insert_items(items: List[Profile]):
    try:
        to_update = []
        for item in items:
            existing = await company_profiles.find_one({"url":item["url"]})
            if existing is None:
                item["id"] = str(uuid.uuid4())
                to_update.append(item)
        
        await company_profiles.insert_many(to_update)
    except:
        print('Company profiles can not be inserted...')

async def enrich_reviewer_with_linkedin_url(id: id, reviewer_name: str, reviewer_location: str, linkedin_url: str):
    await company_profiles.update_one(
        {
            "_id": ObjectId(id),
            "reviews.reviewer.name": reviewer_name,
            "reviews.reviewer.location": reviewer_location
        },
        {
            "$set": {"reviews.$.reviewer.linkedinUrl": linkedin_url}
        }
    )

async def search_profiles(
    reviewer_names: Optional[List[str]] = None,
    exclude_anonymous: Optional[bool] = False,
    focus_names: Optional[List[str]] = None,
    project_focus_names: Optional[List[str]] = None,
    min_reviews: Optional[int] = None,
    max_reviews: Optional[int] = None,
    include_only_profiles_with_linkedin_url: Optional[bool] = False,
    include_only_profiles_without_linkedin_url: Optional[bool] = False,
    ids: Optional[List[str]] = None,
    industry_names: Optional[List[str]] = None,
    reviewer_titles: Optional[List[str]] = None,
    background_client_keywords: Optional[List[str]] = None,
    challenge_client_keywords: Optional[List[str]] = None,
    solution_client_keywords: Optional[List[str]] = None,
    feedback_client_keywords: Optional[List[str]] = None,
) -> List[dict]:
    any_filters_applied = any([
        reviewer_names,
        exclude_anonymous,
        focus_names, 
        project_focus_names, 
        min_reviews, 
        max_reviews,
        include_only_profiles_with_linkedin_url, 
        include_only_profiles_without_linkedin_url,
        ids, 
        industry_names,
        reviewer_titles, 
        background_client_keywords, 
        challenge_client_keywords,
        solution_client_keywords, 
        feedback_client_keywords
    ])

    if not any_filters_applied:
        return await company_profiles.find().to_list(length=None)

    query = {}

    if focus_names:
        regex_pattern = "|".join([re.escape(focus_name) for focus_name in focus_names])
        query["focus"] = {"$regex": regex_pattern, "$options": "i"}

    if min_reviews is not None:
        query.setdefault("summary.noOfReviews", {})["$gte"] = min_reviews
    if max_reviews is not None:
        query.setdefault("summary.noOfReviews", {})["$lte"] = max_reviews

    if ids:
        query["_id"] = {"$in": [ObjectId(id) for id in ids]}

    review_query = {}

    if include_only_profiles_with_linkedin_url:
        review_query["reviewer.linkedinUrl"] = {"$exists": True, "$ne": ""}

    if include_only_profiles_without_linkedin_url:
        review_query["reviewer.linkedinUrl"] = {"$exists": False }

    if project_focus_names:
        project_focus_regex_pattern = "|".join([re.escape(name) for name in project_focus_names])
        review_query["project.allCategories"] = {"$regex": project_focus_regex_pattern, "$options": "i"}

    if reviewer_names:
        reviewer_names_regex_pattern = "|".join([re.escape(name) for name in reviewer_names])
        review_query["reviewer.name"] = {"$regex": reviewer_names_regex_pattern, "$options": "i"}

    if industry_names:
        industries_regex_pattern = "|".join([re.escape(name) for name in industry_names])
        review_query["reviewer.industry"] = {"$regex": industries_regex_pattern, "$options": "i"}

    if reviewer_titles:
        titles_regex_pattern = "|".join([re.escape(title) for title in reviewer_titles])
        review_query["reviewer.title"] = {"$regex": titles_regex_pattern, "$options": "i"}

    background_regex = "|".join([re.escape(keyword) for keyword in background_client_keywords]) if background_client_keywords else None
    challenge_regex = "|".join([re.escape(keyword) for keyword in challenge_client_keywords]) if challenge_client_keywords else None
    solution_regex = "|".join([re.escape(keyword) for keyword in solution_client_keywords]) if solution_client_keywords else None
    feedback_regex = "|".join([re.escape(keyword) for keyword in feedback_client_keywords]) if feedback_client_keywords else None
    
    label_conditions = []

    if background_client_keywords:
        label_conditions.append(
            {"content": {"$elemMatch": {"label": "BACKGROUND", "text": {"$regex": background_regex, "$options": "i"}}}}
        )

    if challenge_client_keywords:
        label_conditions.append(
            {"content": {"$elemMatch": {"label": "OPPORTUNITY / CHALLENGE", "text": {"$regex": challenge_regex, "$options": "i"}}}}
        )

    if solution_client_keywords:
        label_conditions.append(
            {"content": {"$elemMatch": {"label": "SOLUTION", "text": {"$regex": solution_regex, "$options": "i"}}}}
        )

    if feedback_client_keywords:
        label_conditions.append(
            {"content": {"$elemMatch": {"label": "RESULTS & FEEDBACK", "text": {"$regex": feedback_regex, "$options": "i"}}}}
        )

    if label_conditions:
        review_query["$or"] = label_conditions

    if review_query:
        query["reviews"] = {"$elemMatch": review_query}

    items = await company_profiles.find(query).to_list(length=None)

    for item in items:
        if "reviews" in item and item["reviews"]:
            filtered_reviews = []

            for review in item["reviews"]:
                reviewer = review.get("reviewer", {})

                matches_reviewer_industry = (
                    not industry_names or any(re.search(rf"{re.escape(industry)}", reviewer.get("industry", ""), re.IGNORECASE) for industry in industry_names)
                )

                matches_reviewer_name = (
                    not reviewer_names or any(re.search(rf"{re.escape(name)}", reviewer.get("name", ""), re.IGNORECASE) for name in reviewer_names)
                )

                matches_reviewer_title = (
                    not reviewer_titles or any(re.search(rf"{re.escape(title)}", reviewer.get("title", ""), re.IGNORECASE) for title in reviewer_titles)
                )

                has_linkedin_url = (
                    not include_only_profiles_with_linkedin_url 
                    or (
                        reviewer.get("linkedinUrl") 
                        and "linkedin.com/in/" in reviewer.get("linkedinUrl")
                    )
                )

                does_not_has_linkedin_url = (
                    not include_only_profiles_without_linkedin_url 
                    or ("linkedinUrl" not in reviewer or not reviewer.get("linkedinUrl"))
                )

                if not (matches_reviewer_name and matches_reviewer_industry and matches_reviewer_title and has_linkedin_url and does_not_has_linkedin_url):
                    continue

                if not (
                    background_client_keywords
                    or challenge_client_keywords
                    or solution_client_keywords
                    or feedback_client_keywords
                ):
                    filtered_reviews.append(review)
                    continue
                    

                matches_content = any(
                    (background_client_keywords and c["label"] == "BACKGROUND" and re.search(background_regex, c["text"], re.IGNORECASE))
                    or (challenge_client_keywords and c["label"] == "OPPORTUNITY / CHALLENGE" and re.search(challenge_regex, c["text"], re.IGNORECASE))
                    or (solution_client_keywords and c["label"] == "SOLUTION" and re.search(solution_regex, c["text"], re.IGNORECASE))
                    or (feedback_client_keywords and c["label"] == "RESULTS & FEEDBACK" and re.search(feedback_regex, c["text"], re.IGNORECASE))
                    for c in review.get("content", [])
                )

                if matches_content:
                    filtered_reviews.append(review)

            item["reviews"] = filtered_reviews

    return [item for item in items if item["reviews"]]

async def search_profiles_v2(
    reviewer_names: Optional[List[str]] = None,
    exclude_anonymous: Optional[bool] = False,
    focus_names: Optional[List[str]] = None,
    project_focus_names: Optional[List[str]] = None,
    min_reviews: Optional[int] = None,
    max_reviews: Optional[int] = None,
    include_only_profiles_with_linkedin_url: Optional[bool] = False,
    include_only_profiles_without_linkedin_url: Optional[bool] = False,
    ids: Optional[List[str]] = None,
    industry_names: Optional[List[str]] = None,
    reviewer_titles: Optional[List[str]] = None,
    background_client_keywords: Optional[List[str]] = None,
    challenge_client_keywords: Optional[List[str]] = None,
    solution_client_keywords: Optional[List[str]] = None,
    feedback_client_keywords: Optional[List[str]] = None,
) -> List[dict]:

    query = {}

    if focus_names:
        query["$text"] = {"$search": " ".join(focus_names)}

    if min_reviews is not None:
        query["summary.noOfReviews"] = {"$gte": min_reviews}
    if max_reviews is not None:
        query["summary.noOfReviews"] = {"$lte": max_reviews}

    if ids:
        query["_id"] = {"$in": [ObjectId(id) for id in ids]}

    review_query = {}

    if include_only_profiles_with_linkedin_url:
        review_query["reviewer.linkedinUrl"] = {"$regex": "linkedin.com/in/"}

    if include_only_profiles_without_linkedin_url:
        review_query["reviewer.linkedinUrl"] = {"$exists": False}

    if industry_names:
        review_query["reviewer.industry"] = {"$in": industry_names}

    if reviewer_titles:
        review_query["reviewer.title"] = {"$in": reviewer_titles}

    # Keyword Searches for Reviews
    keyword_conditions = []
    if background_client_keywords:
        keyword_conditions.append({"$text": {"$search": " ".join(background_client_keywords)}})
    if challenge_client_keywords:
        keyword_conditions.append({"$text": {"$search": " ".join(challenge_client_keywords)}})
    if solution_client_keywords:
        keyword_conditions.append({"$text": {"$search": " ".join(solution_client_keywords)}})
    if feedback_client_keywords:
        keyword_conditions.append({"$text": {"$search": " ".join(feedback_client_keywords)}})

    if keyword_conditions:
        review_query["$or"] = keyword_conditions

    pipeline = [
        {"$match": query},
        {"$unwind": "$reviews"},
        {"$match": review_query},
        {"$group": {"_id": "$_id", "reviews": {"$push": "$reviews"}}},
        {"$match": {"reviews": {"$ne": []}}},
        {"$addFields": {"text_score": {"$meta": "textScore"}}},
        {"$sort": {"text_score": -1, "summary.noOfReviews": -1}},
        {"$limit": 100}
    ]

    return await company_profiles.aggregate(pipeline).to_list(length=None)