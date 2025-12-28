import strawberry
from typing import List, Optional

@strawberry.type
class Address:
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postalCode: Optional[str]
    phone: Optional[str]

@strawberry.type
class Reviewer:
    title: Optional[str]
    name: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    location: Optional[str]
    reviewType: Optional[str]
    isVerified: Optional[bool]
    linkedinUrl: Optional[str]

@strawberry.type
class Project:
    name: str
    category: Optional[str]
    allCategories: Optional[List[str]]
    size: Optional[str]
    length: Optional[str]
    description: Optional[str]

@strawberry.type
class Content:
    label: str
    text: str

@strawberry.type
class ReviewDetails:
    rating: Optional[int]
    quality: Optional[int]
    schedule: Optional[int]
    cost: Optional[int]
    willingToRefer: Optional[int]
    comments: Optional[str]

@strawberry.type
class Review:
    name: str
    datePublished: Optional[str]
    project: Optional[Project]
    reviewer: Optional[Reviewer]
    review: Optional[ReviewDetails]
    content: Optional[List[Content]]

@strawberry.type
class Summary:
    name: str
    rating: Optional[float]
    noOfReviews: Optional[int]
    description: Optional[str]
    minProjectSize: Optional[str]
    averageHourlyRate: Optional[str]
    employees: Optional[str]

@strawberry.type
class Service:
    name: str
    percent: float

@strawberry.type
class Profile:
    _id: str
    url: Optional[str]
    servicesProvided: Optional[List[Service]]
    summary: Optional[Summary]
    focus: Optional[List[str]]
    reviews: Optional[List[Review]]

    def __init__(self, _id, url=None, servicesProvided=None, summary=None, focus=None, reviews=None, **kwargs):
        self._id = _id
        self.url = url
        self.servicesProvided = [Service(
            name=service.get("name"),
            percent=service.get("percent")
        ) for service in servicesProvided] if servicesProvided else None
        self.summary = Summary(**summary) if summary else None
        self.focus = focus
        self.reviews = [Review(
            name=review.get("name"),
            datePublished=review.get("datePublished"),
            project=Project(**review["project"]) if review.get("project") else None,
            reviewer=Reviewer(
                    title=review["reviewer"].get("title"),
                    name=review["reviewer"].get("name"),
                    industry=review["reviewer"].get("industry"),
                    size=review["reviewer"].get("size"),
                    location=review["reviewer"].get("location"),
                    reviewType=review["reviewer"].get("reviewType"),
                    isVerified=review["reviewer"].get("isVerified"),
                    linkedinUrl=review["reviewer"].get("linkedinUrl")  # Ensure this is explicitly handled
                ) if review.get("reviewer") else None,
            review=ReviewDetails(**review["review"]) if review.get("review") else None,
            content=[Content(**content) for content in review["content"]] if review.get("content") else None
        ) for review in reviews] if reviews else None
