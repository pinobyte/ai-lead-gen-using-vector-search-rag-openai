from fastapi import Request, HTTPException
from app.services.user_service import get_user
import httpx

async def authenticate_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid auth header")

    access_token = auth_header.split(" ")[1]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_info = response.json()
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Email not found in user info")

    request.state.user_email = email
    return user_info
    
async def ensure_authorised_access(action: str, email: str):
    user = await get_user(email)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    if user["api_tokens_analyze_allocated"] == 0 and user["api_tokens_search_allocated"] == 0:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Contact @billsaber123 at Telegram to obtain access."
        )

    check_token_allowance(user, action)

def check_token_allowance(user: object, action: str):
    def check_analyze():
        if (user["api_tokens_analyze_allocated"] - user["api_tokens_analyze_used"]) <= 0:
            raise HTTPException(status_code=401, detail="Analyze API Tokens plan allowance exceeded.")

    def check_search():
        if (user["api_tokens_search_allocated"] - user["api_tokens_search_used"]) <= 0:
            raise HTTPException(status_code=401, detail="Search API Tokens plan allowance exceeded.")

    switch = {
        "analyze": check_analyze,
        "search": check_search,
    }

    if action in switch:
        switch[action]()
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

def extract_user_email(request: Request):
    email = getattr(request.state, "user_email", None)
    if not email:
        raise HTTPException(status_code=401, detail="User email not found in request state")
    return email