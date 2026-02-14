# agent_graph.py
import os
from typing import TypedDict, Optional, Literal
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

# ---------- Load env ----------
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# ---------- External tools ----------
from src.TavilySearch import TavilySearch
from src.Decider import decide_image_source
from src.GSerper import GoogleSerper
from src.Replicate import replicate
from src.AWS_S3Upload import upload_to_s3
from src.instagram_api import upload_to_instagram

print("🔥 AGENT GRAPH LOADED")

# ---------- LLM ----------
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# ---------- Types ----------
ImageSource = Literal["REPLICATE", "GOOGLE_SERPER"]
Decision = Literal["APPROVE", "EDIT", "REGENERATE", "SWITCH_IMAGE_SOURCE"]

# ---------- State ----------
class AgentState(TypedDict):
    keyword: str
    content: Optional[str]
    image_source: Optional[ImageSource]
    image_path: Optional[str]
    decision: Optional[Decision]
    edited_caption: Optional[str]


# ===================== NODES =====================

def tavily_node(state: AgentState) -> AgentState:
    return {**state, "content": TavilySearch(state["keyword"])}


def summarize_node(state: AgentState) -> AgentState:
    prompt = f"""
Summarize the following news into 3–4 concise Instagram bullet points.

Rules:
- Max 15 words per point
- Neutral tone
- No emojis or hashtags

News:
{state["content"]}
"""
    summary = llm.invoke(prompt).content.strip()
    return {**state, "content": summary}


def decider_node(state: AgentState) -> str:
    return decide_image_source(
        content=state["content"],
        goal="Create an Instagram post"
    )


def replicate_node(state: AgentState) -> AgentState:
    replicate(state["content"])
    return {
        **state,
        "image_source": "REPLICATE",
        "image_path": "output.png"
    }


def gserper_node(state: AgentState) -> AgentState:
    path = GoogleSerper(state["content"])

    if path is None:
        return {
            **state,
            "image_source": "GOOGLE_SERPER",
            "image_path": None
        }

    return {
        **state,
        "image_source": "GOOGLE_SERPER",
        "image_path": path
    }


def image_fallback_router(state: AgentState) -> str:
    if state["image_path"] is None:
        return "REPLICATE"
    return "HUMAN"


def human_node(state: AgentState):
    return interrupt({
        "caption": state["content"],
        "image_path": state["image_path"],
        "image_source": state["image_source"],
        "question": "Approve, edit, regenerate, or switch image source?"
    })


def human_router(state: AgentState) -> str:
    if state["decision"] == "APPROVE":
        return "UPLOAD"
    if state["decision"] == "EDIT":
        return "EDIT"
    if state["decision"] == "SWITCH_IMAGE_SOURCE":
        return "SWITCH_IMAGE"
    return "REGENERATE"


def switch_image_source_node(state: AgentState) -> AgentState:
    new_source = (
        "REPLICATE"
        if state["image_source"] == "GOOGLE_SERPER"
        else "GOOGLE_SERPER"
    )
    return {**state, "image_source": new_source}


def edit_node(state: AgentState) -> AgentState:
    return {**state, "content": state["edited_caption"]}


def s3_node(state: AgentState) -> AgentState:
    url = upload_to_s3("output.png")
    return {**state, "image_path": url}


def instagram_node(state: AgentState) -> AgentState:
    upload_to_instagram(
        image_url=state["image_path"],
        caption=state["content"]
    )
    return state


# ===================== GRAPH =====================

graph = StateGraph(AgentState)

graph.add_node("tavily", tavily_node)
graph.add_node("summarize", summarize_node)

graph.add_node("replicate", replicate_node)
graph.add_node("gserper", gserper_node)

graph.add_node("human", human_node)
graph.add_node("edit", edit_node)
graph.add_node("switch_image", switch_image_source_node)

graph.add_node("s3", s3_node)
graph.add_node("instagram", instagram_node)

graph.set_entry_point("tavily")

graph.add_edge("tavily", "summarize")

graph.add_conditional_edges(
    "summarize",
    decider_node,
    {
        "GOOGLE_SERPER": "gserper",
        "REPLICATE": "replicate"
    }
)

graph.add_conditional_edges(
    "gserper",
    image_fallback_router,
    {
        "REPLICATE": "replicate",
        "HUMAN": "human"
    }
)

graph.add_edge("replicate", "human")

graph.add_conditional_edges(
    "human",
    human_router,
    {
        "UPLOAD": "s3",
        "EDIT": "edit",
        "REGENERATE": "tavily",
        "SWITCH_IMAGE": "switch_image"
    }
)

graph.add_conditional_edges(
    "switch_image",
    lambda s: s["image_source"],
    {
        "GOOGLE_SERPER": "gserper",
        "REPLICATE": "replicate"
    }
)

graph.add_edge("edit", "human")
graph.add_edge("s3", "instagram")
graph.add_edge("instagram", END)

app = graph.compile(checkpointer=MemorySaver())
