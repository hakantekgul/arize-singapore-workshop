"""LangGraph customer-support agent for Sunrise Outfitters.

Uses LangGraph's prebuilt ReAct agent with ChatOpenAI and the mock support
tools. Because LangGraph runs on LangChain runnables, the single LangChain
OpenInference instrumentor (see ``agent/tracing.py``) captures the graph, the
LLM calls, and every tool invocation as spans in Arize.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agent.tools import SUPPORT_TOOLS

SYSTEM_PROMPT = (
    "You are Sunny, the customer-support assistant for Sunrise Outfitters, an "
    "online outdoor-apparel retailer based in Singapore. Be warm, concise, and "
    "helpful.\n\n"
    "Guidelines:\n"
    "- Use the tools to look up real order details before answering; never "
    "invent order statuses, tracking numbers, or prices.\n"
    "- For refund or return questions, check eligibility with the tool before "
    "promising anything.\n"
    "- Use the FAQ tool for general shipping, sizing, returns, and payment "
    "questions.\n"
    "- If the customer is upset or you cannot resolve the issue, escalate to a "
    "human.\n"
    "- Keep replies friendly and under ~120 words."
)

DEFAULT_MODEL = "gpt-4o-mini"


def build_agent(model: str = DEFAULT_MODEL, temperature: float = 0.0):
    """Build and return the compiled LangGraph ReAct agent.

    Args:
        model: OpenAI chat model name.
        temperature: Sampling temperature.

    Returns:
        A compiled LangGraph agent that accepts ``{"messages": [...]}``.
    """
    llm = ChatOpenAI(model=model, temperature=temperature)
    return create_react_agent(llm, tools=SUPPORT_TOOLS, prompt=SYSTEM_PROMPT)


def run_agent(agent, user_message: str) -> str:
    """Run one turn of the agent and return the final assistant reply text.

    Args:
        agent: A compiled agent from :func:`build_agent`.
        user_message: The customer's message.

    Returns:
        The agent's final text reply.
    """
    result = agent.invoke({"messages": [HumanMessage(content=user_message)]})
    messages = result["messages"]
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return messages[-1].content if messages else ""
