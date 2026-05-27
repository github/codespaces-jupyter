"""Go from v1 content blocks to generativelanguage_v1beta format."""

import json
from typing import Any, cast

from langchain_core.messages import content as types


def translate_citations_to_grounding_metadata(
    citations: list[types.Citation], web_search_queries: list[str] | None = None
) -> dict[str, Any]:
    """Translate LangChain Citations to Google AI grounding metadata format.

    Args:
        citations: List of `Citation` content blocks.
        web_search_queries: Optional list of search queries that generated
            the grounding data.

    Returns:
        Google AI grounding metadata dictionary.

    Example:
        ```python
        citations = [
            create_citation(
                url="https://uefa.com/euro2024",
                title="UEFA Euro 2024 Results",
                start_index=0,
                end_index=47,
                cited_text="Spain won the UEFA Euro 2024 championship",
            )
        ]

        metadata = translate_citations_to_grounding_metadata(citations)
        len(metadata["groundingChunks"])
        # -> 1

        metadata["groundingChunks"][0]["web"]["uri"]
        # -> 'https://uefa.com/euro2024'
        ```
    """
    if not citations:
        return {}

    # Group citations by text segment (start_index, end_index, cited_text)
    segment_to_citations: dict[
        tuple[int | None, int | None, str | None], list[types.Citation]
    ] = {}

    for citation in citations:
        key = (
            citation.get("start_index"),
            citation.get("end_index"),
            citation.get("cited_text"),
        )
        if key not in segment_to_citations:
            segment_to_citations[key] = []
        segment_to_citations[key].append(citation)

    # Build grounding chunks from unique URLs
    url_to_chunk_index: dict[str, int] = {}
    grounding_chunks: list[dict[str, Any]] = []

    for citation in citations:
        url = citation.get("url")
        if url and url not in url_to_chunk_index:
            url_to_chunk_index[url] = len(grounding_chunks)
            grounding_chunks.append(
                {"web": {"uri": url, "title": citation.get("title", "")}}
            )

    # Build grounding supports
    grounding_supports: list[dict[str, Any]] = []

    for (
        start_index,
        end_index,
        cited_text,
    ), citations_group in segment_to_citations.items():
        if start_index is not None and end_index is not None and cited_text:
            chunk_indices = []
            confidence_scores = []

            for citation in citations_group:
                url = citation.get("url")
                if url and url in url_to_chunk_index:
                    chunk_indices.append(url_to_chunk_index[url])

                    # Extract confidence scores from extras if available
                    extras = citation.get("extras", {})
                    google_metadata = extras.get("google_ai_metadata", {})
                    scores = google_metadata.get("confidence_scores", [])
                    confidence_scores.extend(scores)

            support = {
                "segment": {
                    "startIndex": start_index,
                    "endIndex": end_index,
                    "text": cited_text,
                },
                "groundingChunkIndices": chunk_indices,
            }

            if confidence_scores:
                support["confidenceScores"] = confidence_scores

            grounding_supports.append(support)

    # Extract search queries from extras if not provided
    if web_search_queries is None:
        web_search_queries = []
        for citation in citations:
            extras = citation.get("extras", {})
            google_metadata = extras.get("google_ai_metadata", {})
            queries = google_metadata.get("web_search_queries", [])
            web_search_queries.extend(queries)
        # Remove duplicates while preserving order
        web_search_queries = list(dict.fromkeys(web_search_queries))

    return {
        "webSearchQueries": web_search_queries,
        "groundingChunks": grounding_chunks,
        "groundingSupports": grounding_supports,
    }


def _convert_from_v1_to_generativelanguage_v1beta(
    content: list[types.ContentBlock], model_provider: str | None
) -> list[dict[str, Any]]:
    """Convert v1 content blocks to `generativelanguage_v1beta` `Content`.

    Args:
        content: List of v1 `ContentBlock` objects.
        model_provider: The model provider name that generated the v1 content.

    Returns:
        List of dictionaries in `generativelanguage_v1beta` `Content` format, ready to
            be sent to the API.
    """
    new_content: list = []
    for block in content:
        if not isinstance(block, dict) or "type" not in block:
            continue

        block_dict = dict(block)  # (For typing)

        # TextContentBlock
        if block_dict["type"] == "text":
            new_block = {"text": block_dict.get("text", "")}
            if (
                thought_signature := (block_dict.get("extras") or {}).get("signature")  # type: ignore[attr-defined]
            ) and model_provider == "google_genai":
                new_block["thought_signature"] = thought_signature
            new_content.append(new_block)
            # Citations are only handled on output. Can't pass them back :/

        # ReasoningContentBlock -> thinking
        elif block_dict["type"] == "reasoning" and model_provider == "google_genai":
            # Google requires passing back the thought_signature when available.
            # Signatures are only provided when function calling is enabled.
            if "extras" in block_dict and isinstance(block_dict["extras"], dict):
                extras = block_dict["extras"]
                if "signature" in extras:
                    new_block = {
                        "thought": True,
                        "text": block_dict.get("reasoning", ""),
                        "thought_signature": extras["signature"],
                    }
                    new_content.append(new_block)
                # else: skip reasoning blocks without signatures
                # TODO: log a warning?
            # else: skip reasoning blocks without extras
            # TODO: log a warning?

        # ImageContentBlock
        elif block_dict["type"] == "image":
            if base64 := block_dict.get("base64"):
                new_block = {
                    "inline_data": {
                        "mime_type": block_dict.get("mime_type", "image/jpeg"),
                        "data": base64.encode("utf-8")
                        if isinstance(base64, str)
                        else base64,
                    }
                }
                new_content.append(new_block)
            elif url := block_dict.get("url") and model_provider == "google_genai":
                # Google file service
                new_block = {
                    "file_data": {
                        "mime_type": block_dict.get("mime_type", "image/jpeg"),
                        "file_uri": block_dict[str(url)],
                    }
                }
                new_content.append(new_block)

        # TODO: AudioContentBlock -> audio once models support passing back in

        # FileContentBlock (documents)
        elif block_dict["type"] == "file":
            if base64 := block_dict.get("base64"):
                new_block = {
                    "inline_data": {
                        "mime_type": block_dict.get(
                            "mime_type", "application/octet-stream"
                        ),
                        "data": base64.encode("utf-8")
                        if isinstance(base64, str)
                        else base64,
                    }
                }
                new_content.append(new_block)
            elif file_id := block_dict.get("file_id"):
                # File ID from uploaded file
                new_block = {
                    "file_data": {
                        "mime_type": block_dict.get(
                            "mime_type", "application/octet-stream"
                        ),
                        "file_uri": file_id,
                    }
                }
                new_content.append(new_block)
            elif url := block_dict.get("url") and model_provider == "google_genai":
                # Google file service
                new_block = {
                    "file_data": {
                        "mime_type": block_dict.get(
                            "mime_type", "application/octet-stream"
                        ),
                        "file_uri": block_dict[str(url)],
                    }
                }
                new_content.append(new_block)

        # ToolCall -> FunctionCall
        elif block_dict["type"] == "tool_call":
            function_call = {
                "function_call": {
                    "name": block_dict.get("name", ""),
                    "args": block_dict.get("args", {}),
                }
            }
            new_content.append(function_call)

        # ToolCallChunk -> FunctionCall
        elif block_dict["type"] == "tool_call_chunk":
            try:
                args_str = block_dict.get("args") or "{}"
                input_ = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                input_ = {}

            function_call = {
                "function_call": {
                    "name": block_dict.get("name", "no_tool_name_present"),
                    "args": input_,
                }
            }
            new_content.append(function_call)

        elif block_dict["type"] == "server_tool_call":
            if block_dict.get("name") == "code_interpreter":
                # LangChain v0 format
                args = cast("dict", block_dict.get("args", {}))
                executable_code = {
                    "type": "executable_code",
                    "executable_code": args.get("code", ""),
                    "language": args.get("language", ""),
                    "id": block_dict.get("id", ""),
                }
                # Google generativelanguage format
                new_content.append(
                    {
                        "executable_code": {
                            "language": executable_code["language"],
                            "code": executable_code["executable_code"],
                        }
                    }
                )

        elif block_dict["type"] == "server_tool_result":
            extras = cast("dict", block_dict.get("extras", {}))
            if extras.get("block_type") == "code_execution_result":
                # LangChain v0 format
                raw_outcome = extras.get("outcome", "")
                if isinstance(raw_outcome, int):
                    if raw_outcome == 1:
                        outcome = "OUTCOME_OK"
                    elif raw_outcome == 2:
                        outcome = "OUTCOME_FAILED"
                    else:
                        outcome = "OUTCOME_UNSPECIFIED"
                else:
                    outcome = raw_outcome
                # Google generativelanguage format
                new_content.append(
                    {
                        "code_execution_result": {
                            "outcome": outcome,
                            "output": block_dict.get("output", ""),
                        }
                    }
                )

        elif block_dict["type"] == "non_standard":
            new_content.append(block_dict["value"])

    return new_content
