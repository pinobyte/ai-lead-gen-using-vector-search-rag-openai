from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
database = client[settings.MONGO_DB_NAME]
company_profiles = database["company_profiles"]
reviews = database["reviews"]
reviews_with_embeddings = database["reviews_with_embeddings"]
new_reviews = database["new_reviews"]
company_profiles_v2 = database["company_profiles_v2"]
users = database["users"]
user_requests = database["user_requests"]
reviews_structured = database["reviews_structured"]