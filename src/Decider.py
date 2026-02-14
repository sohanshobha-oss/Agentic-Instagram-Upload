from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def decide_image_source(content: str, goal: str) -> str:
    prompt = f"""
You are an expert visual editor.

Goal:
{goal}

News content:
{content}

Decide the BEST image source.

Rules:
- Use GOOGLE_SERPER if a real photograph best serves the goal
- Use REPLICATE if a conceptual or illustrative image is better
- Respond with ONLY one word

Allowed responses:
REPLICATE
GOOGLE_SERPER
"""

    response = llm.invoke(prompt).content.strip().upper()

    if response not in {"REPLICATE", "GOOGLE_SERPER"}:
        return "GOOGLE_SERPER"

    return response
