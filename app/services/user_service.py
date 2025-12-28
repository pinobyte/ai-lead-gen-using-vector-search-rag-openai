from app.db import users
from app.db import user_requests
import uuid
import datetime

async def log_user_api_request(email: str, requestType: str, request):
    document = {
        "id": str(uuid.uuid4()),
        "email": email,
        "request_type": requestType,
        "request": request.dict(),
        "createdAt": datetime.datetime.now(datetime.UTC)
    }
    await user_requests.insert_one(document)

async def get_user(email: str):
    user = await users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

async def create_user(email: str):
    document = {
        "id": str(uuid.uuid4()),
        "email": email,
        "api_tokens_analyze_allocated": 10,
        "api_tokens_analyze_used": 0,
        "api_tokens_search_allocated": 15,
        "api_tokens_search_used": 0
    }
    await users.insert_one(document)

async def update_search_api_tokens_usage(email: str, count: int = 1):
    result = await users.update_one(
        {"email": email},
        {"$inc": {"api_tokens_search_used": count}}
    )
    return result

async def update_analyze_api_tokens_usage(email: str, count: int = 1):
    result = await users.update_one(
        {"email": email},
        {"$inc": {"api_tokens_analyze_used": count}}
    )
    return result