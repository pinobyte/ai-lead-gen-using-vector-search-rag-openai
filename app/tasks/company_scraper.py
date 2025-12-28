# import redis.asyncio as redis
# from apify_client import ApifyClientAsync
# from app.config import settings
# from app.utils.utils import clean_data
# from app.services.company_profile_service import insert_items
# import asyncio
# import jsonata
# from typing import List

# redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
# apify_client = ApifyClientAsync(settings.APIFY_API_KEY)

# async def log_apify_output(run_id):
#     async with apify_client.run(run_id).log().stream() as async_log_stream:
#         if async_log_stream:
#             async for line in async_log_stream.aiter_lines():
#                 print(line)

# async def start_data_collection(start_urls: List[str], max_items: int):
#     """
#     Starts the Apify actor task for data collection and returns the run ID.
#     """
#     input_params = {
#         "includeReviews": True,
#         "excludePortfolio": True,
#         "maxItems": max_items,
#         "mode": "profiles",
#         "proxy": {
#             "useApifyProxy": True
#         },
#         "startUrls": start_urls,
#     }
#     run = await apify_client.actor('epctex/clutchco-scraper').start(run_input=input_params)

#     asyncio.create_task(log_apify_output(run["id"]))

#     return run["id"]


# async def get_checkpoint(run_id: str) -> int:
#     """
#     Get the current checkpoint (offset) for a specific run ID from Redis.
#     """
#     offset = await redis_client.get(run_id)
#     return int(offset) if offset else 0


# async def set_checkpoint(run_id: str, offset: int):
#     """
#     Save the current checkpoint (offset) for a specific run ID to Redis.
#     """
#     await redis_client.set(run_id, offset)


# async def fetch_and_process_results(run_id: str, limit: int = 50):
#     """
#     Fetch results from Apify's dataset and process them incrementally.
#     """
#     run_client = apify_client.run(run_id=run_id)

#     while True:
#         offset = await get_checkpoint(run_id)
#         item_listing = await run_client.dataset().list_items(offset=offset, limit=limit)
#         items = item_listing.items
#         items_count = item_listing.count

#         if items_count > 0:
#             print(f"Fetched {items_count} items from offset: {offset}")
#             jncontext = jsonata.Context()
#             transformed = jncontext(settings.COMPANY_PROFILE_JSON_MAPPING_QUERY.replace("\n", ""), clean_data(items))
#             if not isinstance(transformed, list):
#                 transformed = [transformed]
#             await insert_items(transformed)
#             offset += items_count
#             await set_checkpoint(run_id, offset)
#         else:
#             print(f"No items available at offset {offset}. Waiting for more data...")

#         # Wait for the task to finish or check again
#         run_status = await run_client.wait_for_finish(wait_secs=5)

#         if run_status["status"] in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
#             if run_status["status"] == "SUCCEEDED" and not items:
#                 print("Task completed successfully, and all items have been processed.")
#                 break
#             elif run_status["status"] in ["FAILED", "TIMED_OUT", "ABORTED"]:
#                 raise Exception(f"Task failed with status: {run_status['status']}")

#         # Wait briefly before checking for more items
#         await asyncio.sleep(2)


# async def execute_company_collection(start_urls: List[str], max_items: int):
#     """
#     Orchestrates the entire data collection process:
#     - Starts data collection
#     - Monitors task status
#     - Fetches results incrementally
#     - Saves results into Cosmos DB
#     """
#     run_id = await start_data_collection(start_urls, max_items)
#     print(f"Data collection started with run_id: {run_id}")

#     # Fetch and process results incrementally
#     await fetch_and_process_results(run_id)

#     print("Data collection process completed successfully!")
