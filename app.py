"""Gradio chat app for the Sunrise Outfitters support agent.

Run locally:

    cp .env.example .env   # fill in your keys
    pip install -r requirements.txt
    python app.py

Only OPENAI_API_KEY is strictly required. If ARIZE_SPACE_ID and ARIZE_API_KEY
are also set, every conversation is traced into Arize.
"""

from __future__ import annotations

import os

import gradio as gr
from dotenv import load_dotenv

from agent.graph import build_agent, run_agent
from agent.tracing import setup_tracing

load_dotenv()


def _require_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your "
            "OpenAI API key, or export OPENAI_API_KEY before running."
        )


_require_openai_key()
setup_tracing()
AGENT = build_agent()

EXAMPLES = [
    "Where is my order A1001?",
    "Can I get a refund on order A1002?",
    "How long does shipping take to Singapore?",
    "Order A1003 hasn't arrived and I'm frustrated. Help!",
]


def respond(message: str, history: list) -> str:
    """Gradio ChatInterface callback: run the agent on the latest message."""
    try:
        return run_agent(AGENT, message)
    except Exception as exc:  # surface errors in the UI instead of crashing
        return f"Sorry, something went wrong: {exc}"


demo = gr.ChatInterface(
    fn=respond,
    title="Sunrise Outfitters Support",
    description=(
        "A LangGraph customer-support agent, traced with Arize. Ask about "
        "orders A1001, A1002, or A1003, shipping, returns, or sizing."
    ),
    examples=EXAMPLES,
)


if __name__ == "__main__":
    demo.launch()
