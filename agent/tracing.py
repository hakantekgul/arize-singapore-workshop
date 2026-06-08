"""Arize tracing setup for the workshop agent.

This wires the agent into Arize AX using ``arize-otel`` plus the LangChain
OpenInference instrumentor. Because LangGraph is built on LangChain runnables,
this single instrumentor captures the graph, the LLM calls, and every tool
invocation.

Call :func:`setup_tracing` once, before building the agent. It fails gracefully
(prints a warning and returns ``None``) when credentials are missing, so the
agent still runs without tracing.
"""

from __future__ import annotations

import os

PROJECT_NAME = "arize-singapore-workshop"

_INSTRUMENTED = False


def setup_tracing(
    space_id: str | None = None,
    api_key: str | None = None,
    project_name: str = PROJECT_NAME,
):
    """Register the Arize tracer and instrument LangChain/LangGraph.

    Args:
        space_id: Arize Space ID. Falls back to ``ARIZE_SPACE_ID`` env var.
        api_key: Arize API key. Falls back to ``ARIZE_API_KEY`` env var.
        project_name: Project name shown in the Arize UI.

    Returns:
        The configured tracer provider, or ``None`` if credentials are missing.
    """
    global _INSTRUMENTED

    space_id = space_id or os.getenv("ARIZE_SPACE_ID")
    api_key = api_key or os.getenv("ARIZE_API_KEY")

    if not space_id or not api_key:
        print(
            "[tracing] ARIZE_SPACE_ID / ARIZE_API_KEY not set - skipping Arize "
            "tracing. The agent will still run, but no traces will be sent."
        )
        return None

    from arize.otel import register
    from openinference.instrumentation.langchain import LangChainInstrumentor

    tracer_provider = register(
        space_id=space_id,
        api_key=api_key,
        project_name=project_name,
    )

    if not _INSTRUMENTED:
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        _INSTRUMENTED = True

    print(f"[tracing] Arize tracing enabled -> project '{project_name}'.")
    return tracer_provider
