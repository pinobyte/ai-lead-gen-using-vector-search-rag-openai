from app.config import settings
import asyncio
from typing import List
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI, AzureOpenAI
import re
from datetime import datetime

embedding_client = AzureOpenAI(
    api_version=settings.EMBEDDING_API_VERSION,
    api_key=settings.EMBEDDING_KEY,
    azure_endpoint=settings.EMBEDDING_ENDPOINT
)

search_client = SearchClient(
    endpoint=settings.SEARCH_ENDPOINT,
    index_name=settings.SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(settings.SEARCH_API_KEY)
)

#completion_client = AzureOpenAI(
#    api_version=settings.COMPLETION_API_VERSION,
#    azure_endpoint=settings.AZURE_COMPLETION_ENDPOINT,
#    api_key=settings.AZURE_OPENAI_KEY
#)

completion_client = OpenAI(
    api_key=settings.AZURE_OPENAI_KEY
)

async def analyze(query: str, review_date_from: str, industries: List[str], company_sizes: list, project_budgets: list):
    embedding = embedding_client.embeddings.create(input=query, model=settings.EMBEDDING_MODEL_NAME).data[0].embedding
    
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="embeddings")

    filter_query = build_search_filter(review_date_from, industries, company_sizes, project_budgets)

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=filter_query,
        select=[
            "project_name", "reviewer_industry", "content_background",
            "content_opportunity_challenge", "content_solution", "content_results_feedback"
        ],
        top=25,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='semantic-configuration',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE
    )

    reviews = [
        {
            "project_name": r.get("project_name", ""),
            "reviewer_industry": r.get("reviewer_industry", ""),
            "content_background": r.get("content_background", ""),
            "content_opportunity_challenge": r.get("content_opportunity_challenge", ""),
            "content_solution": r.get("content_solution", ""),
            "content_results_feedback": r.get("content_results_feedback", ""),
        }
        for r in results
    ]

    review_chunks = chunk_list(reviews, 3)

    intermediate_insights = await asyncio.gather(*(get_analysis_internal(chunk) for chunk in review_chunks))

    insights_combined = "\n\n".join(intermediate_insights)

    final_prompt = f"""
    You are an expert in customer feedback analysis specializing in IT services and solutions.
    The user has the following query: "{query}"
    
    Use only the structured review summaries provided below to generate the final analysis:
    
    {insights_combined}
    
    Provide a comprehensive and structured summary, ensuring insights remain objective and data-driven.
    """

    final_response = completion_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in customer feedback analysis."},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0
    )

    return final_response.choices[0].message.content

async def get_analysis_internal(reviews):
    reviews_text = "\n\n".join(
        f"Industry: {r['reviewer_industry']}\n"
        f"Background summary: {r['content_background']}\n"
        f"Challenge/Pain summary: {r['content_opportunity_challenge']}\n"
        f"Solution summary: {r['content_solution']}\n"
        f"Feedback summary: {r['content_results_feedback']}"
        for r in reviews
    )

    prompt = f"""
    You are an expert in customer feedback analysis specializing in IT services and solutions.
    Here are multiple customer reviews:

    {reviews_text}

    Summarize each review separately using the following format (it must be short, only the most important info):
    Industry: 
    Background summary:
    Challenge/Pain summary:
    Solution summary:
    Feedback summary:

    Keep the summaries concise and extract only the most valuable insights.
    """

    response = completion_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in customer feedback analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content

async def search(query: str, review_date_from: str, industries: list, company_sizes: list, project_budgets: list, limit: int):
    embedding = embedding_client.embeddings.create(input=query, model=settings.EMBEDDING_MODEL_NAME).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="embeddings")
        
    filter_query = build_search_filter(review_date_from, industries, company_sizes, project_budgets)
        
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=filter_query,
        select=[
            "id",
            "company_name",
            "date_published",
            "tags",
            "project_name",
            "project_budget_label",
            "reviewer_industry",
            "reviewer_size_label",
            "reviewer_location",
            "reviewer_linkedin_url",
            "content_background",
            "content_opportunity_challenge",
            "content_solution",
            "content_results_feedback",
            "reviewer_position"
        ],
        top=limit,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='semantic-configuration',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE
    )

    final_results = []
    for result in results:
        formatted_result = {
            "Position": format_position(result["reviewer_position"]),
            "LinkedIn": result["reviewer_linkedin_url"] if "linkedin.com/in" in result["reviewer_linkedin_url"] else '',
            "Industry": result["reviewer_industry"],
            "Company Size": result["reviewer_size_label"],
            "Location": result["reviewer_location"],
            "Project Name": result["project_name"],
            "Project Budget": result["project_budget_label"],
            "Project Finished Date": datetime.strptime(
                result["date_published"], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%B, %Y"),
            "Project Tags": [tag.lower() for tag in result["tags"]],
            "Vendor Name": result["company_name"],
            "Background": extract_qna(result["content_background"], [
                r"Please describe your company and your position there.",
                r"Introduce your business and what you do there.",
                r"Please describe your company and position.",
                r"Please briefly describe what your company does.",
                f"Please describe your organization.",
                f"Describe what your company does in a single sentence."
            ]),
            "Solution": extract_qna(result["content_solution"], [
                r"How did you select * and what were the deciding factors?",
                r"Describe the scope of work in detail, including the project steps, key deliverables, and technologies used.",
                r"What was the scope of their involvement?",
                r"How did you find *?",
                r"How did you select *?",
                r"How did you select this *?",
                r"How did you come to work with *?"
                r"How many people from *'s team worked with you, and what were their positions?",
                r"What is the team composition?",
                r"What was the team composition?",
                r"How did you come to work with *?",
                r"How much have you invested with them?",
                r"What is the status of this engagement?",
                r"Why did you select *?",
                r"Could you provide a sense of the size of this initiative in financial terms?",
                r"How many teammates from *?",
                r"Describe the scope of work in detail. Please include a summary of key deliverables.",
                r"How many resources from *?",
                r"Describe the project and the services they provided in detail.",
                r"Please describe the scope of their work.",
                r"What was your process in selecting *?"
                r"Can you provide a ballpark figure for the size of the work that *?",
                r"What's the status of this engagement?"
            ]),
            "Opportunity & Challenge": extract_qna(result["content_opportunity_challenge"], [
                r"For what projects/services did your company hire *, and what were your goals?",
                r"What specific goals or objectives did you hire *?",
                r"What challenge were you trying to address with *?",
                r"For what projects/services did your company hire *?",
                r"What was the business challenge that you were trying to address when you approached *?",
                r"What business challenge were you trying to address with *?",
                r"What was your goal in working with *?",
                r"What were your goals for this project?",
                r"What specific goals or objectives did you hire *",
                r"What specific goals or objectives did you hire * to accomplish?",
                r"What challenge were you addressing when you hired *?"
            ]),
            "Feedback": extract_qna(result["content_results_feedback"], [
                r"What evidence can you share that demonstrates the impact of the engagement?",
                r"Are there any areas they could improve?",
                r"What did you find most impressive about them?",
                r"Can you share any outcomes from the project that demonstrate progress or success?",
                r"How effective was the workflow between your team and theirs?",
                r"What did you find most impressive or unique about this company?",
                r"Can you share any information that demonstrates the impact that this project has had on your business?",
                r"Could you share any evidence that would demonstrate the productivity, quality of work, or the impact of the engagement?",
                r"Can you share any measurable outcomes of the project or general feedback about the deliverables?",
                r"Describe their project management style, including communication tools and timeliness.",
                r"Are there any areas for improvement or something they could have done differently?",
                r"What were the measurable outcomes from the project that demonstrate progress or success?",
                r"Did they deliver items on time?",
                r"How did they respond to your needs?",
                r"What was your primary form of communication with *?",
                r"How satisfied are you with the work of *?",
                r"Is there anything unique about *?",
                r"Looking back on the work so far, is there any area that you think they could improve upon or something that you might do differently?",
                r"What advice would you give a future client of theirs?",
                r"Describe their project management",
                r"How was project management arranged and how effective was it\?",
                r"What stood out to you about their communication or project delivery\?",
                r"What made you happiest working with \*?",
                r"What aspect of their performance did you appreciate the most\?",
                r"What impressed you most about \*?",
                r"What improvements would you suggest for \*?",
                r"What’s one thing \* could do better\?",
                r"What has been the greatest result of the work done by \*?",
                r"What has your experience been like collaborating with the team at \*?",
                r"Do you have any advice for potential customers?",
                r"What kind of impact did this project have on your company?",
                r"What could have been done differently on this project?",
                r"What sets \* apart from other vendors you’ve worked with?",
                r"Are there any areas for improvement",
                r"Do you have any advice for potential customers\?",
                r"How was project management arranged and how effective was it\?",
                r"How did your relationship with your partner evolve\?",
                r"What advice do you have for clients with similar needs to yours\?",
                r"In what ways can they improve\?"
            ])
        }

        final_results.append(formatted_result)

    return final_results

def build_search_filter(review_date_from: str, industries: list, company_sizes: list, project_budgets: list):
    filter_clauses = []
    if review_date_from:
        filter_clauses.append(f"date_published ge {review_date_from}")
    
    if industries:
        industry_filter = " or ".join(
            [f"reviewer_industry eq '{industry}'" for industry in industries if industry]
        )
        if industry_filter:
            filter_clauses.append(f"({industry_filter})")
        
    if company_sizes:
        company_size_filter = " or ".join(
            [f"reviewer_size_label eq '{size}'" for size in company_sizes if size]
        )
        if company_size_filter:
            filter_clauses.append(f"({company_size_filter})")
    
    if project_budgets:
        project_budget_filter = " or ".join(
            [f"project_budget_label eq '{budget}'" for budget in project_budgets if budget]
        )
        if project_budget_filter:
            filter_clauses.append(f"({project_budget_filter})")

    return " and ".join(filter_clauses) if filter_clauses else None

async def _search(query: str, review_date_from: str, industries: str):
    open_ai_client = AzureOpenAI(
        api_key = settings.AZURE_OPENAI_KEY,  
        api_version = settings.API_VERSION,
        azure_endpoint = settings.AZURE_OPENAI_ENDPOINT)
    embedding = open_ai_client.embeddings.create(input=query, model=settings.EMBEDDING_MODEL_NAME).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="embeddings")
    filter_clauses = []
    
    if review_date_from:
        filter_clauses.append(f"date_published ge {review_date_from}")

    if industries:
        industry_filter = " or ".join([f"reviewer_industry eq '{industry}'" for industry in industries])
        filter_clauses.append(f"({industry_filter})")

    filter_query = " and ".join(filter_clauses) if filter_clauses else None

    results = search_client.search(  
        search_text=query,   
        vector_queries= [vector_query],
        filter=filter_query,
        select=["id", "company_name", "date_published", "tags", "project_name", "project_size", "reviewer_industry", "reviewer_size", "reviewer_location", "reviewer_linkedin_url", "content_background", "content_opportunity_challenge", "content_solution", "content_results_feedback"],
        top=100,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='semantic-configuration',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        #query_rewrites="generative|count-3",
        #query_language="en"
    )

    results = [   
        {
            "Vendor Name": result["company_name"],
            "Project Finished Date": datetime.strptime(result["date_published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%B, %Y"),
            "Project Name": result["project_name"],
            "Project Budget": result["project_size"] if result["project_size"] != "Confidential" else 'Confidential',
            "Industry": result["reviewer_industry"],
            "Company size": result["reviewer_size"],
            "Location": result["reviewer_location"],
            "Linkedin": result["reviewer_linkedin_url"] if "linkedin.com/in" in result["reviewer_linkedin_url"] else '',
            # "Backgound Formatted": extract_qna(result["content_background"], [
            #     r"Please describe your company and your position there.",
            #     r"Introduce your business and what you do there.",
            #     r"Please describe your company and position.",
            #     r"Please briefly describe what your company does.",
            #     f"Please describe your organization.",
            #     f"Describe what your company does in a single sentence."
            # ]),
            # "Backgound": result["content_background"],
            # "Project Challenge Formatted": extract_qna(result["content_opportunity_challenge"], [
            #     r"For what projects/services did your company hire *, and what were your goals?",
            #     r"What specific goals or objectives did you hire *?",
            #     r"What challenge were you trying to address with *?",
            #     r"For what projects/services did your company hire *?",
            #     r"What was the business challenge that you were trying to address when you approached *?",
            #     r"What business challenge were you trying to address with *?",
            #     r"What was your goal in working with *?"
            # ]),
            #"Project Challenge": result["content_opportunity_challenge"],
            "Company Review": extract_qna(result["content_solution"], [
                r"How did you select * and what were the deciding factors?",
                r"Describe the scope of work in detail, including the project steps, key deliverables, and technologies used.",
                r"What was the scope of their involvement?",
                r"How did you find *?",
                r"How did you select *?",
                r"How did you select this *?",
                r"How did you come to work with *?"
                r"How many people from *'s team worked with you, and what were their positions?",
                r"What is the team composition?",
                r"What was the team composition?",
                r"How did you come to work with *?",
                r"How much have you invested with them?",
                r"What is the status of this engagement?",
                r"Why did you select *?",
                r"Could you provide a sense of the size of this initiative in financial terms?",
                r"How many teammates from *?",
                r"Describe the scope of work in detail. Please include a summary of key deliverables.",
                r"How many resources from *?",
                r"Describe the project and the services they provided in detail.",
                r"Please describe the scope of their work.",
                r"What was your process in selecting *?"
                r"Can you provide a ballpark figure for the size of the work that *?"
            ]),
            #"Solution": result["content_solution"],
            # "Feedback Formatted": extract_qna(result["content_results_feedback"], [
            #     r"What evidence can you share that demonstrates the impact of the engagement?",
            #     r"Are there any areas they could improve?",
            #     r"What did you find most impressive about them?",
            #     r"Can you share any outcomes from the project that demonstrate progress or success?",
            #     f"How effective was the workflow between your team and theirs?",
            #     r"What did you find most impressive or unique about this company?",
            #     r"Can you share any information that demonstrates the impact that this project has had on your business?",
            #     r"Could you share any evidence that would demonstrate the productivity, quality of work, or the impact of the engagement?",
            #     r"Can you share any measurable outcomes of the project or general feedback about the deliverables?",
            #     r"Describe their project management style, including communication tools and timeliness.",
            #     r"Are there any areas for improvement or something they could have done differently?",
            #     r"What were the measurable outcomes from the project that demonstrate progress or success?",
            #     r"Did they deliver items on time?",
            #     r"How did they respond to your needs?",
            #     r"What was your primary form of communication with *?",
            #     r"How satisfied are you with the work of *?",
            #     r"Is there anything unique about *?",
            #     r"Looking back on the work so far, is there any area that you think they could improve upon or something that you might do differently?",
            #     r"What advice would you give a future client of theirs?"

            # ]),
            # "Feedback": result["content_results_feedback"],
            "Technologies": [tag.lower() for tag in result["tags"] if tag.lower() not in ["did", "clutch"]]
        } 
        for result in results
    ]

    return results

def format_qna(text):
    qa_pairs = re.findall(r"([^?]+\?)\s*([^?]+)", text)
    formatted_text = "\n\n".join(
        [f"- Q: {q.strip()}\n- A: {a.strip()}" for q, a in qa_pairs]
    )

    return formatted_text

def clean_vendor_name(answer):
    """Removes any leading text that ends with '?' from the beginning of the answer."""
    return re.sub(r"^.*?\?\s*", "", answer).strip()

def extract_qna(text, question_patterns):
    question_regex = "|".join(question_patterns)
    matches = re.split(rf"({question_regex})", text)

    result = []
    current_question = None
    current_answer = []

    for segment in matches:
        segment = segment.strip()
        if not segment:
            continue

        if re.match(question_regex, segment):
            if current_question and current_answer:
                clean_answer = clean_vendor_name(segment.lstrip("?").strip())
                result.append(f"A: {' '.join(current_answer)}")
                result.append("")

            current_question = segment.strip()

            if not current_question.endswith("?") and not current_question.endswith("."):
                current_question += "?"

            result.append(f"Q: {current_question}")
            current_answer = []
        else:
            clean_answer = clean_vendor_name(segment.lstrip("?").strip())  # Apply vendor name cleanup
            current_answer.append(clean_answer)

    if current_question and current_answer:
        result.append(f"A: {' '.join(current_answer)}")

    return "\n".join(result) if result else ""

def chunk_list(lst, n):
    avg = len(lst) // n
    return [lst[i * avg: (i + 1) * avg] for i in range(n - 1)] + [lst[(n - 1) * avg:]]

def format_position(role: str) -> str:
    acronyms = {
        "ceo", "cto", "cfo", "coo", "cmo",
        "cio", "chro", "cpo", "cso", "cdo", "vp"
    }

    def format_word(word):
        return word.upper() if word.lower() in acronyms else word.capitalize()

    return " & ".join(
        " ".join(format_word(w) for w in part.strip().split())
        for part in role.strip().split("&")
    )