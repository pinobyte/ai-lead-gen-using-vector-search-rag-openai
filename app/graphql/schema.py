import strawberry
from typing import List, Optional
from collections import Counter
from app.graphql.types import Profile
from app.services.company_profile_service import search_profiles, search_profiles_v2

@strawberry.type
class KeyValue:
    key: str
    value: int

@strawberry.type
class AggregatedData:
    company_count: int
    reviews_count: int
    by_industries: List[KeyValue]
    by_locations: List[KeyValue]
    by_project_sizes: List[KeyValue]
    by_project_categories: List[KeyValue]

@strawberry.type
class SearchProfilesResponse:
    profiles: List[Profile]
    aggregates: AggregatedData

@strawberry.type
class Query:
    @strawberry.field
    async def get_profiles(
        self,
        reviewer_names: Optional[List[str]] = None,
        competitors_focus_names: Optional[List[str]] = None,
        project_focus_names: Optional[List[str]] = None,
        min_reviews: Optional[int] = None,
        max_reviews: Optional[int] = None,
        include_only_profiles_without_linkedin_url: Optional[bool] = False,
        include_only_profiles_with_linkedin_url: Optional[bool] = False,
        ids: Optional[List[str]] = None,
        industry_names: Optional[List[str]] = None,
        reviewer_titles: Optional[List[str]] = None,
        background_client_keywords: Optional[List[str]] = None,
        challenge_client_keywords: Optional[List[str]] = None, 
        solution_client_keywords: Optional[List[str]] = None,
        feedback_client_keywords: Optional[List[str]] = None
    ) -> SearchProfilesResponse:
        result = await search_profiles(
                    reviewer_names=reviewer_names,
                    focus_names=competitors_focus_names,
                    project_focus_names=project_focus_names,
                    min_reviews=min_reviews,
                    max_reviews=max_reviews,
                    include_only_profiles_with_linkedin_url=include_only_profiles_with_linkedin_url,
                    include_only_profiles_without_linkedin_url=include_only_profiles_without_linkedin_url,
                    ids=ids,
                    industry_names=industry_names,
                    reviewer_titles=reviewer_titles,
                    background_client_keywords=background_client_keywords,
                    challenge_client_keywords=challenge_client_keywords,
                    solution_client_keywords=solution_client_keywords,
                    feedback_client_keywords=feedback_client_keywords
                )

        profiles = result
        reviews_counter = 0
        industries_counter = Counter()
        locations_counter = Counter()
        sizes_counter = Counter()
        categories_counter = Counter()

        for profile in profiles:
            if "reviews" in profile and profile["reviews"]:
                for review in profile["reviews"]:
                    industry = review.get("reviewer", {}).get("industry")
                    location = review.get("reviewer", {}).get("location")
                    size = review.get("project", {}).get("size")
                    category = review.get("project", {}).get("category")
                    reviews_counter += 1

                    if industry:
                        industries_counter[industry] += 1
                    if location:
                        country = location.split(",")[-1].strip()
                        locations_counter[country] += 1
                    if size:
                        sizes_counter[size] += 1
                    if category:
                        categories_counter[category] += 1

        industry_counts_sorted = sorted(industries_counter.items(), key=lambda x: x[1], reverse=True)
        location_counts_sorted = sorted(locations_counter.items(), key=lambda x: x[1], reverse=True)
        project_size_counts_sorted = sorted(sizes_counter.items(), key=lambda x: x[1], reverse=True)
        categories_counts_sorted = sorted(categories_counter.items(), key=lambda x: x[1], reverse=True)

        return SearchProfilesResponse(
            profiles=[Profile(**profile) for profile in profiles],
            aggregates=AggregatedData(
                reviews_count=reviews_counter,
                company_count=len(profiles),
                by_industries=[KeyValue(key=k, value=v) for k, v in industry_counts_sorted],
                by_locations=[KeyValue(key=k, value=v) for k, v in location_counts_sorted],
                by_project_sizes=[KeyValue(key=k, value=v) for k, v in project_size_counts_sorted],
                by_project_categories=[KeyValue(key=k, value=v) for k, v in categories_counts_sorted]
            )
        )

schema = strawberry.Schema(query=Query)

