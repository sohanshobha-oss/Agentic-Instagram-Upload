import os
from tkinter import E
from typing import List, Optional
import requests
from pathlib import Path
from langchain_community.utilities import GoogleSerperAPIWrapper
from PIL import Image
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from typing import List

load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")


DOWNLOAD_LIMIT = 10
OUTPUT_PATH = "output.png"


# IMAGE DOWNLOAD

def download_image_safe(url: str, save_path: str) -> Optional[str]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://www.google.com/"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        img = Image.open(BytesIO(resp.content))
        img = img.convert("RGB")
        img.save(save_path, format="PNG")

        return save_path

    except Exception:
        return None



# LLM IMAGE DECIDER

def decide_best_image(image_urls: List[str], context: str) -> Optional[int]:
    """
    Returns index of best image OR None
    """

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = PromptTemplate.from_template("""
You are an expert image selector.

Given:
- A list of image URLs
- A news context

Task:
- Choose the ONE image that best visually represents the context.

Rules:
- Prefer real photographs (sports/news)
- Avoid posters, memes, logos, graphics
- Avoid social media screenshots
- If none match, return -1

Return ONLY:
- A single number (0-based index)
- OR -1

Image URLs:
{urls}

Context:
{context}
""")

    response = llm.invoke(
        prompt.format(
            urls="\n".join([f"{i}. {u}" for i, u in enumerate(image_urls)]),
            context=context
        )
    ).content.strip()

    try:
        idx = int(response)
        if idx < 0 or idx >= len(image_urls):
            return None
        return idx
    except Exception:
        return None



# GOOGLE SERPER IMAGE SEARCH 

def GoogleSerper(query: str) -> Optional[str]:
    """
    1. Fetch top image URLs
    2. Let LLM choose best
    3. Download chosen image
    4. Fallback safely
    """

    try:
        search = GoogleSerperAPIWrapper(type="images")
        results = search.results(query)

        images = results.get("images", [])
        if not images:
            return None

        image_urls = [
            img.get("imageUrl")
            for img in images[:DOWNLOAD_LIMIT]
            if img.get("imageUrl")
        ]

        if not image_urls:
            return None

        
        best_idx = decide_best_image(image_urls, query)

        if best_idx is not None:
            chosen_url = image_urls[best_idx]
            path = download_image_safe(chosen_url, OUTPUT_PATH)
            if path:
                return path

        
        for url in image_urls:
            path = download_image_safe(url, OUTPUT_PATH)
            if path:
                return path

        return None

    except Exception:
        return None