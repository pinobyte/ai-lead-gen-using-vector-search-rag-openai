from fastapi import APIRouter, Request, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.chat_service import search, analyze
from app.services.user_service import update_analyze_api_tokens_usage
from app.services.user_service import update_search_api_tokens_usage
from app.services.user_service import log_user_api_request
from app.utils.auth import authenticate_user
from app.utils.auth import ensure_authorised_access
from app.utils.auth import extract_user_email

router = APIRouter(
    dependencies=[Depends(authenticate_user)]
)

class SearchRequest(BaseModel):
    query: str
    review_date_from: Optional[str] = None,
    industries: Optional[List[str]] = None,
    company_sizes: Optional[List[str]] = None,
    project_budgets: Optional[List[str]] = None,
    limit:Optional[int]=500

@router.post("/search/")
async def chat(request: SearchRequest, httpRequest: Request, _: None = Depends(authenticate_user)):
    email = extract_user_email(httpRequest)
    await ensure_authorised_access("search", email)
    results = await search(
        query=request.query,
        review_date_from=request.review_date_from,
        industries=request.industries,
        company_sizes=request.company_sizes,
        project_budgets=request.project_budgets,
        limit=request.limit
    )
    await update_search_api_tokens_usage(email)
    await log_user_api_request(email, "Search", request)
    return {"response": results}

@router.post("/analyze/")
async def chat(request: SearchRequest, httpRequest: Request, _: None = Depends(authenticate_user)):
    email = extract_user_email(httpRequest)
    await ensure_authorised_access("analyze", email)
    results = await analyze(
        query=request.query,
        review_date_from=request.review_date_from,
        industries=request.industries,
        company_sizes=request.company_sizes,
        project_budgets=request.project_budgets
    )
    await update_analyze_api_tokens_usage(email)
    await log_user_api_request(email, "Analyze", request)
    return {"response": results}