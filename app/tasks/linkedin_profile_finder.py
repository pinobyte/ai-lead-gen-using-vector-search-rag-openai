# import redis.asyncio as redis
# from apify_client import ApifyClientAsync
# from app.config import settings
# from app.services.company_profile_service import search_profiles, enrich_reviewer_with_linkedin_url
# import asyncio
# import json
# import os
# from typing import List, Optional

# redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
# apify_client = ApifyClientAsync(settings.APIFY_API_KEY)

# async def start_data_collection(query: str):
#     """
#     Starts the Apify actor task for data collection and returns the run ID.
#     """
#     input_params = {
#         "forceExactMatch": False,
#         "includeIcons": False,
#         "includeUnfilteredResults": False,
#         "languageCode": "en",
#         "maxPagesPerQuery": 1,
#         "mobileResults": False,
#         "queries": query,
#         "resultsPerPage": 3,
#         "saveHtml": False,
#         "saveHtmlToKeyValueStore": True,
#         "wordsInTitle": [],
#         "wordsInText": []
#     }
#     run = await apify_client.actor('apify/google-search-scraper').start(run_input=input_params)
#     return run["id"]

# async def fetch_and_process_result(session_id: str, run_id: str, company_profile_id: str, reviewer_name: str, reviewer_location: str):
#     """
#     Fetch results from Apify's dataset and process them incrementally.
#     """
#     if not os.path.exists(session_id):
#         os.makedirs(session_id)

#     run_client = apify_client.run(run_id=run_id)

#     while True:
#         run_status = await run_client.wait_for_finish(wait_secs=5)

#         if run_status["status"] in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
#             if run_status["status"] == "SUCCEEDED":
                
#                 for attempt in range(3):
#                     item_listing = await run_client.dataset().list_items()
#                     items = item_listing.items
#                     items_count = item_listing.count

#                     if items_count > 0:
#                         orgranic_results = items[0]["organicResults"]
#                         if (len(orgranic_results) > 0):
#                             url = orgranic_results[0]["url"]
#                             await enrich_reviewer_with_linkedin_url(company_profile_id, reviewer_name, reviewer_location, url)
#                             print(f"Fetched url: {url} for reviewer name: {reviewer_name} and reviwere location: {reviewer_location}")
#                             return
#                         else:
#                             url=""
#                             await enrich_reviewer_with_linkedin_url(company_profile_id, reviewer_name, reviewer_location, url)
#                             return
#                     else:
#                         print(f"Attempt {attempt + 1}/3: No items found. Retrying...")
#                         await asyncio.sleep(2)
#                         return
#             elif run_status["status"] in ["FAILED", "TIMED_OUT", "ABORTED"]:
#                 raise Exception(f"Task failed with status: {run_status['status']}")
#         else:
#             await asyncio.sleep(2)

# async def execute_linkedin_profile_finder_workflow(company_profile, semaphore):
#     async with semaphore:
#         reviewers_to_enrich = []
#         reviews = company_profile.get('reviews', [])
#         for review in reviews:
#             reviewer = review.get('reviewer', {})
#             if reviewer.get('name') and reviewer.get('name') != "Anonymous" and reviewer.get('linkedinUrl') == None and reviewer.get('linkedinUrl') != "":
#                 reviewers_to_enrich.append(reviewer)
        
#         if len(reviewers_to_enrich) == 0:
#             return
        
#         for reviewer in reviewers_to_enrich:
#             query = f"{reviewer['name']}, {reviewer.get('title', '')}, {reviewer.get('location', '')}, {reviewer.get('industry', '')}"
#             run_id = await start_data_collection(query=query)
#             await fetch_and_process_result(
#                 session_id="poc",
#                 run_id=run_id, 
#                 company_profile_id=str(company_profile["_id"]),
#                 reviewer_name=reviewer['name'],
#                 reviewer_location=reviewer['location'])

# async def execute_linkedin_profiles_finder_workflows_in_parallel(
#     focus_names: Optional[List[str]] = None,
#     project_focus_names: Optional[List[str]] = None,
#     min_reviews: Optional[int] = None,
#     max_reviews: Optional[int] = None,
#     ids: Optional[List[str]] = None):
#     semaphore = asyncio.Semaphore(10)
#     company_profiles = await search_profiles(
#         focus_names=focus_names, 
#         project_focus_names=project_focus_names,
#         min_reviews=min_reviews,
#         max_reviews=max_reviews,
#         include_only_profiles_without_linkedin_url=True,
#         ids=ids)
#     tasks = [execute_linkedin_profile_finder_workflow(company_profile, semaphore) for company_profile in company_profiles]
#     await asyncio.gather(*tasks)