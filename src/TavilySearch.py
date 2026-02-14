# src/TavilySearch.py

from dotenv import load_dotenv
import os
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError(
        "TAVILY_API_KEY is missing. "
        "Add it to your .env file or environment variables."
    )

client = TavilyClient(api_key=TAVILY_API_KEY)


def TavilySearch(query: str) -> str:
    result = client.search(
        query=query,
        max_results=1,
        include_raw_content=True,
        search_depth="advanced",
        time_range="week"
    )
    return result["results"][0]["content"]
