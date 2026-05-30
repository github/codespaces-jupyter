"""Utility functions for LangChain Google GenAI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from google.genai import types
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from langchain_google_genai._function_utils import (
    _ToolChoiceType,
    convert_to_genai_function_declarations,
)
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAI,
    _parse_chat_history,
)


def create_context_cache(
    model: ChatGoogleGenerativeAI,
    messages: list[BaseMessage],
    *,
    ttl: str | None = None,
    expire_time: str | None = None,
    tools: list[BaseTool | type[BaseModel] | dict | Callable] | None = None,
    tool_choice: _ToolChoiceType | bool | None = None,
) -> str:
    """Creates a context cache for the specified model and content.

    Context caching allows you to store and reuse content (e.g., PDFs, images) for
    faster processing. This is useful when you have large amounts of context that
    you want to reuse across multiple requests.

    !!! warning "Important Constraint"
        When using cached content, you **cannot** specify `system_instruction`,
        `tools`, or `tool_config` in subsequent API requests. These must be part
        of the cached content. Do not call `.bind_tools()` when using a model with
        cached content that already includes tools.

    Args:
        model: `ChatGoogleGenerativeAI` model instance.

            Must be a model that supports context caching.
        messages: List of `BaseMessage` objects to cache.

            Can include system messages, human messages, and multimodal content
            (images, PDFs, etc.).
        ttl: Time-to-live for the cache in seconds (e.g., `'300'` for 5 minutes).

            At most one of `ttl` or `expire_time` can be specified.
        expire_time: Absolute expiration time (ISO 8601 format).

            At most one of `ttl` or `expire_time` can be specified.
        tools: Optional list of tools to bind to the cached context. Can be:
            - `BaseTool` instances
            - Pydantic models (converted to JSON schema)
            - Dict representations of tools
            - Callable functions
        tool_choice: Optional tool choice configuration.

    Returns:
        Cache name (string identifier) that can be passed to `cached_content`
            parameter in subsequent API calls.

    Raises:
        ValueError: If the model client is not initialized or if the model is not
            specified.

    Example:
        ```python
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI, create_context_cache

        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

        # Example 1: Cache with text content
        cache = create_context_cache(
            model,
            messages=[
                SystemMessage(content="You are an expert researcher."),
                HumanMessage(content="Large document content here..."),
            ],
            ttl="3600s",  # 1 hour
        )

        # Example 2: Cache with uploaded files (Gemini API)
        # Note: gs:// URIs are NOT supported with Gemini API.
        # Files must be uploaded first using client.files.upload()
        file = model.client.files.upload(file="document.pdf")
        cache = create_context_cache(
            model,
            messages=[
                SystemMessage(content="You are an expert researcher."),
                HumanMessage(
                    content=[
                        {
                            "type": "media",
                            "file_uri": file.uri,  # Use the uploaded file's URI
                            "mime_type": "application/pdf",
                        }
                    ]
                ),
            ],
            ttl="3600s",
        )

        # Use the cache in subsequent requests
        response = model.invoke(
            "Summarize the document.",
            cached_content=cache,
        )

        # Example 3: Cache with tools (correct usage)
        from langchain_core.tools import tool


        @tool
        def search_database(query: str) -> str:
            '''Search the database.'''
            return f"Results for: {query}"


        # Create cache WITH tools
        cache_with_tools = create_context_cache(
            model,
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Large context here..."),
            ],
            tools=[search_database],
            ttl="3600s",
        )

        # When using the cache, do NOT bind tools again
        # The tools are already in the cache
        model_with_cache = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            cached_content=cache_with_tools,
        )
        # DON'T do this: .bind_tools([search_database])

        response = model_with_cache.invoke("Search for X")
        ```
    """
    if model.client is None:
        msg = "Model client must be initialized to create cached content."
        raise ValueError(msg)

    if not model.model:
        msg = "Model name must be specified to create cached content."
        raise ValueError(msg)

    # Parse messages into system instruction and content
    system_instruction, contents = _parse_chat_history(messages, model=model.model)

    # Convert tools to Tool objects if provided
    tool_list = None
    if tools:
        tool_list = convert_to_genai_function_declarations(tools)

    # Build the cache config
    cache_config_kwargs: dict[str, Any] = {}

    if system_instruction:
        cache_config_kwargs["system_instruction"] = system_instruction

    if contents:
        cache_config_kwargs["contents"] = contents

    if ttl:
        cache_config_kwargs["ttl"] = ttl

    if expire_time:
        cache_config_kwargs["expire_time"] = expire_time

    if tool_list:
        cache_config_kwargs["tools"] = tool_list

    # Create the cache
    cache = model.client.caches.create(
        model=model.model,
        config=types.CreateCachedContentConfig(**cache_config_kwargs),
    )

    if cache.name is None:
        msg = "Cache name was not set after creation."
        raise ValueError(msg)

    return cache.name
