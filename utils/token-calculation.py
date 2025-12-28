import os
from pymongo import MongoClient
from dotenv import load_dotenv
from app.db import company_profiles
from app.db import company_profiles_v2
from app.config import settings
from openai import OpenAI
import tiktoken
import asyncio

SECTIONS = ["BACKGROUND", "OPPORTUNITY / CHALLENGE", "SOLUTION", "RESULTS & FEEDBACK"]

encoding = tiktoken.encoding_for_model("text-embedding-3-large")

def count_tokens(text):
    """Returns the number of tokens in a given text."""
    return len(encoding.encode(text))

def extract_review_sections(document):
    """
    Extracts relevant sections from all reviews in a document and organizes them for batch processing.
    Returns a list of (review_id, section_label, text) tuples.
    """
    review_texts = []
    
    company_id = document.get("url", [])

    for review in document.get("reviews", []):
        review_id = f'{review["reviewer"]["name"]}_{review["reviewer"]["location"]}'
        for content_item in review.get("content", []):
            if content_item["label"] in SECTIONS:
                item = {
                    "company_id": company_id,
                    "review_id": review_id,
                    "label": content_item["label"],
                    "text": content_item["text"]
                }
                review_texts.append(item)

    return review_texts

async def fetch_documents():
    return await company_profiles.find({}).limit(10000).to_list(None)

async def main():
    documents = await fetch_documents()
    total_companies = len(documents)
    total_reviews = sum(len(document["reviews"]) for document in documents)
    avg_reviews = total_reviews/ total_companies
    total_tokens = 0
    for doc in documents:
        texts = extract_review_sections(doc)
        for text_item in texts:
            total_tokens += count_tokens(text_item["text"])
    print(f"Total tokens for {total_reviews} reviews across {total_companies} companies: {total_tokens}")
    print(f"AVG reviews per company: {avg_reviews:.2f}")
    estimated_cost = (total_tokens / 1_000_000) * 1.25
    print(f"Estimated Price: ${estimated_cost:.6f}") 

asyncio.run(main())
