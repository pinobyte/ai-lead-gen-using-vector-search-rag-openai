from fastapi import APIRouter, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
# from app.tasks.company_scraper import execute_company_collection
# from app.tasks.linkedin_profile_finder import execute_linkedin_profiles_finder_workflows_in_parallel

router = APIRouter()

class EnrichCompanyProfileReviwersRequest(BaseModel):
    ids: Optional[List[str]] = None
    focus_names: Optional[List[str]] = None
    project_focus_names: Optional[List[str]] = None
    min_reviews: Optional[int] = None
    max_reviews: Optional[int] = None
    include_only_profiles_with_linkedin_url: Optional[bool] = False

class ExtractCompanyProfilesRequest(BaseModel):
    StartUrls: List[str]
    MaxItems: int

@router.post("/company-profiles/actions/extract")
async def extract_company_profiles(request: ExtractCompanyProfilesRequest, background_tasks: BackgroundTasks):
    # background_tasks.add_task(execute_company_collection, request.StartUrls, request.MaxItems)
    return {"message": "Data collection task triggered successfully."}

@router.post("/company-profiles/reviewers/actions/enrich-with-linkedin-url")
async def enrich_company_profiles_reviewers(request: EnrichCompanyProfileReviwersRequest, background_tasks: BackgroundTasks):
    # background_tasks.add_task(execute_linkedin_profiles_finder_workflows_in_parallel,
    #                         request.focus_names,
    #                         request.project_focus_names,
    #                         request.min_reviews,
    #                         request.max_reviews,
    #                         request.ids)
    return {"message": "Data collection task triggered successfully."}

@router.post("/company-profiles/reviewers/actions/try-enrich-with-contact-details")
async def enrich_company_profiles_reviewers(request: EnrichCompanyProfileReviwersRequest, background_tasks: BackgroundTasks):
    # background_tasks.add_task(execute_linkedin_profiles_finder_workflows_in_parallel,
    #                         request.focus_names,
    #                         request.project_focus_names,
    #                         request.min_reviews,
    #                         request.max_reviews,
    #                         request.ids)
    return {"message": "Data collection task triggered successfully."}