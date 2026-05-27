from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import mimetypes
import os
import re
import uuid
import warnings
import wave
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from difflib import get_close_matches
from operator import itemgetter
from typing import (
    Any,
    Literal,
    cast,
)

import filetype  # type: ignore[import-untyped]
from google.genai.client import Client
from google.genai.errors import ClientError
from google.genai.types import (
    Blob,
    Candidate,
    CodeExecutionResult,
    Content,
    ExecutableCode,
    FileData,
    FunctionCall,
    FunctionDeclaration,
    FunctionResponse,
    GenerateContentConfig,
    GenerateContentResponse,
    GenerationConfig,
    HttpOptions,
    HttpRetryOptions,
    ImageConfig,
    Part,
    PrebuiltVoiceConfig,
    SafetySetting,
    SpeechConfig,
    ThinkingConfig,
    ToolCodeExecution,
    ToolConfig,
    VideoMetadata,
    VoiceConfig,
)
from google.genai.types import (
    Outcome as CodeExecutionResultOutcome,
)
from google.genai.types import Tool as GoogleTool
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.exceptions import ContextOverflowError
from langchain_core.language_models import (
    LangSmithParams,
    LanguageModelInput,
    ModelProfile,
    ModelProfileRegistry,
    is_openai_data_block,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    is_data_content_block,
)
from langchain_core.messages import content as types
from langchain_core.messages.ai import UsageMetadata, add_usage, subtract_usage
from langchain_core.messages.tool import invalid_tool_call, tool_call, tool_call_chunk
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
    parse_tool_calls,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.utils import get_pydantic_field_names
from langchain_core.utils.function_calling import (
    convert_to_json_schema,
    convert_to_openai_tool,
)
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_core.utils.utils import _build_model_kwargs
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from pydantic.v1 import BaseModel as BaseModelV1
from typing_extensions import Self, is_typeddict

from langchain_google_genai._common import (
    GoogleGenerativeAIError,
    SafetySettingDict,
    _BaseGoogleGenerativeAI,
    get_user_agent,
)
from langchain_google_genai._compat import (
    _convert_from_v1_to_generativelanguage_v1beta,
)
from langchain_google_genai._function_utils import (
    _tool_choice_to_tool_config,
    _ToolChoiceType,
    _ToolDict,
    convert_to_genai_function_declarations,
    is_basemodel_subclass_safe,
    tool_to_dict,
)
from langchain_google_genai._image_utils import (
    ImageBytesLoader,
    image_bytes_to_b64_string,
)
from langchain_google_genai.data._profiles import _PROFILES

logger = logging.getLogger(__name__)

_FunctionDeclarationType = FunctionDeclaration | dict[str, Any] | Callable[..., Any]

_FUNCTION_CALL_THOUGHT_SIGNATURES_MAP_KEY = (
    "__gemini_function_call_thought_signatures__"
)

_MODEL_PROFILES = cast("ModelProfileRegistry", _PROFILES)


class GoogleContextOverflowError(ClientError, ContextOverflowError):
    """ClientError raised when input exceeds Google's context limit."""


def _handle_client_error(e: ClientError, request: dict[str, Any]) -> None:
    """Convert `ClientError` to a more specific exception when possible.

    Raises `GoogleContextOverflowError` (a `ContextOverflowError` subclass)
    when the error indicates that the input exceeded the model's token limit,
    so that upstream middleware (e.g. `SummarizationMiddleware`) can catch it
    and fall back to context compaction.

    Args:
        e: The `ClientError` exception to handle.
        request: The request dict containing model info.

    Raises:
        GoogleContextOverflowError: When the error indicates a context overflow.
        ChatGoogleGenerativeAIError: For all other client errors.
    """
    error_str = str(e)
    if (
        "exceeds the maximum number of tokens allowed" in error_str
        or "token limit" in error_str.lower()
    ):
        raise GoogleContextOverflowError(
            code=e.code,
            response_json=e.details,
            response=e.response,
        ) from e
    model_name = request.get("model", "unknown")
    msg = f"Error calling model '{model_name}' ({e.status}): {e}"
    raise ChatGoogleGenerativeAIError(msg) from e


def _get_default_model_profile(model_name: str) -> ModelProfile:
    default = _MODEL_PROFILES.get(model_name) or {}
    return default.copy()


def _bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _base64_to_bytes(input_str: str) -> bytes:
    return base64.b64decode(input_str.encode("utf-8"))


class ChatGoogleGenerativeAIError(GoogleGenerativeAIError):
    """Wrapper exception class for errors associated with the `Google GenAI` API.

    Raised when there are specific issues related to the Google GenAI API usage in the
    `ChatGoogleGenerativeAI` class, such as unsupported message types or roles.
    """


def _is_gemini_3_or_later(model_name: str) -> bool:
    """Checks if the model is a pre-Gemini 3 model."""
    if not model_name:
        return False
    model_name = model_name.lower().replace("models/", "")
    return "gemini-3" in model_name


def _is_gemini_25_model(model_name: str) -> bool:
    """Checks if the model is a Gemini 2.5 model."""
    if not model_name:
        return False
    model_name = model_name.lower().replace("models/", "")
    return "gemini-2.5" in model_name


def _validate_video_metadata(video_metadata: object) -> None:
    """Validate user-supplied video metadata before sending to the API.

    The Gemini API surfaces an opaque `500 Internal error` when video
    offsets are negative or `start_offset` exceeds `end_offset`. This
    helper checks the obvious cases up front and raises a clearer error
    so callers do not have to debug the underlying API response.

    Args:
        video_metadata: Raw `video_metadata` from a media part. Accepts
            a `Mapping` (e.g. `dict`) keyed by either `start_offset`/
            `end_offset` or their camelCase aliases, or a `VideoMetadata`
            Pydantic instance. Each offset may be a duration string like
            `"10s"`, a number of seconds, or a `{"seconds": int, "nanos":
            int}` mapping.

    Raises:
        ValueError: If an offset is negative, `start_offset` is greater
            than `end_offset`, or `video_metadata` is not a mapping or
            object exposing offset fields.
    """

    def _to_seconds(value: object) -> float | None:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if not value.endswith("s"):
                return None
            try:
                return float(value[:-1])
            except (TypeError, ValueError):
                return None
        if isinstance(value, Mapping):
            mapping = cast("Mapping[str, Any]", value)
            try:
                return (
                    float(mapping.get("seconds", 0))
                    + float(mapping.get("nanos", 0)) / 1e9
                )
            except (TypeError, ValueError):
                return None
        return None

    if isinstance(video_metadata, Mapping):
        mapping = cast("Mapping[str, Any]", video_metadata)
        raw_start = mapping.get("start_offset", mapping.get("startOffset"))
        raw_end = mapping.get("end_offset", mapping.get("endOffset"))
    elif hasattr(video_metadata, "start_offset") or hasattr(
        video_metadata, "end_offset"
    ):
        # Pydantic `VideoMetadata` instance — read fields via attribute
        # access so callers passing a constructed model don't regress.
        raw_start = getattr(video_metadata, "start_offset", None)
        raw_end = getattr(video_metadata, "end_offset", None)
    else:
        msg = (
            "video_metadata must be a mapping or a VideoMetadata-like object "
            f"with start_offset/end_offset, got {type(video_metadata).__name__}"
        )
        raise ValueError(msg)

    start = _to_seconds(raw_start)
    end = _to_seconds(raw_end)

    if start is not None and start < 0:
        msg = f"video_metadata.start_offset must be non-negative, got {start}s"
        raise ValueError(msg)
    if end is not None and end < 0:
        msg = f"video_metadata.end_offset must be non-negative, got {end}s"
        raise ValueError(msg)
    if start is not None and end is not None and start > end:
        msg = (
            f"video_metadata.start_offset ({start}s) must not exceed "
            f"video_metadata.end_offset ({end}s)"
        )
        raise ValueError(msg)


def _convert_to_parts(
    raw_content: str | Sequence[str | dict],
    model: str | None = None,
) -> list[Part]:
    """Converts LangChain message content into `generativelanguage_v1beta` parts.

    Used when preparing Human, System and AI messages for sending to the API.

    Handles both legacy (pre-v1) dict-based content blocks and v1 `ContentBlock`
    objects.
    """
    content = [raw_content] if isinstance(raw_content, str) else raw_content
    image_loader = ImageBytesLoader()

    parts = []
    # Iterate over each item in the content list, constructing a list of Parts
    for part in content:
        if isinstance(part, str):
            parts.append(Part(text=part))
        elif isinstance(part, Mapping):
            if "type" in part:
                if part["type"] == "text":
                    # Either old dict-style CC text block or new TextContentBlock
                    # Check if there's a signature attached to this text block
                    thought_sig = None
                    if "extras" in part and isinstance(part["extras"], dict):
                        sig = part["extras"].get("signature")
                        if sig and isinstance(sig, str):
                            # Decode base64-encoded signature back to bytes
                            thought_sig = base64.b64decode(sig)
                    if thought_sig:
                        parts.append(
                            Part(text=part["text"], thought_signature=thought_sig)
                        )
                    else:
                        parts.append(Part(text=part["text"]))
                elif part.get("type") == "file" and "file_id" in part:
                    # Handle FileContentBlock with file_id (uploaded file reference)
                    mime_type = part.get("mime_type", "application/octet-stream")
                    parts.append(
                        Part(
                            file_data=FileData(
                                file_uri=part["file_id"], mime_type=mime_type
                            )
                        )
                    )
                elif is_data_content_block(part):
                    # Handle both legacy LC blocks (with `source_type`) and blocks >= v1

                    if "source_type" in part:
                        # Catch legacy v0 formats
                        # Safe since v1 content blocks don't have `source_type` key
                        if part["source_type"] == "url":
                            bytes_ = image_loader._bytes_from_url(part["url"])
                        elif part["source_type"] == "base64":
                            bytes_ = base64.b64decode(part["data"])
                        else:
                            # Unable to support IDContentBlock
                            msg = "source_type must be url or base64."
                            raise ValueError(msg)
                    elif "url" in part:
                        # v1 multimodal block w/ URL
                        bytes_ = image_loader._bytes_from_url(part["url"])
                    elif "base64" in part:
                        # v1 multimodal block w/ base64
                        bytes_ = base64.b64decode(part["base64"])
                    else:
                        msg = (
                            "Data content block must contain 'url', 'base64', or "
                            "'data' field."
                        )
                        raise ValueError(msg)

                    mime_type = part.get("mime_type")
                    if not mime_type:
                        # Guess MIME type based on data field if not provided
                        source = cast(
                            "str",
                            part.get("url") or part.get("base64") or part.get("data"),
                        )
                        mime_type, _ = mimetypes.guess_type(source)
                        if not mime_type:
                            # Last resort - try to guess based on file bytes
                            kind = filetype.guess(bytes_)
                            if kind:
                                mime_type = kind.mime
                    blob_kwargs: dict[str, Any] = {
                        "data": bytes_,
                    }
                    if mime_type:
                        blob_kwargs["mime_type"] = mime_type

                    part_kwargs: dict[str, Any] = {
                        "inline_data": Blob(**blob_kwargs),
                    }
                    if "media_resolution" in part:
                        if model and _is_gemini_25_model(model):
                            warnings.warn(
                                "Setting per-part media resolution requests to "
                                "Gemini 2.5 models and older is not supported. The "
                                "media_resolution parameter will be ignored.",
                                UserWarning,
                                stacklevel=2,
                            )
                        elif model and _is_gemini_3_or_later(model):
                            part_kwargs["media_resolution"] = {
                                "level": part["media_resolution"]
                            }
                    if "extras" in part and isinstance(part["extras"], dict):
                        sig = part["extras"].get("signature")
                        if sig and isinstance(sig, str):
                            part_kwargs["thought_signature"] = base64.b64decode(sig)

                    parts.append(Part(**part_kwargs))
                elif part["type"] == "image_url":
                    # Chat Completions image format
                    img_url = part["image_url"]
                    if isinstance(img_url, dict):
                        if "url" not in img_url:
                            msg = f"Unrecognized message image format: {img_url}"
                            raise ValueError(msg)
                        img_url = img_url["url"]
                    # Check for thought_signature in extras
                    # (needed for multi-turn image editing/usage)
                    thought_sig = None
                    if "extras" in part and isinstance(part["extras"], dict):
                        sig = part["extras"].get("signature")
                        if sig and isinstance(sig, str):
                            thought_sig = base64.b64decode(sig)
                    image_part = image_loader.load_part(img_url)
                    if thought_sig:
                        image_part.thought_signature = thought_sig
                    parts.append(image_part)
                elif part["type"] == "media":
                    # Handle `media` following pattern established in LangChain.js
                    # https://github.com/langchain-ai/langchainjs/blob/e536593e2585f1dd7b0afc187de4d07cb40689ba/libs/langchain-google-common/src/utils/gemini.ts#L93-L106
                    if "mime_type" not in part:
                        msg = f"Missing mime_type in media part: {part}"
                        raise ValueError(msg)
                    mime_type = part["mime_type"]
                    media_part_kwargs: dict[str, Any] = {}

                    if "data" in part:
                        # Embedded media
                        media_part_kwargs["inline_data"] = Blob(
                            data=part["data"], mime_type=mime_type
                        )
                    elif "file_uri" in part:
                        # Referenced files (e.g. stored in GCS)
                        media_part_kwargs["file_data"] = FileData(
                            file_uri=part["file_uri"], mime_type=mime_type
                        )
                    else:
                        msg = f"Media part must have either data or file_uri: {part}"
                        raise ValueError(msg)
                    if "video_metadata" in part:
                        _validate_video_metadata(part["video_metadata"])
                        metadata = VideoMetadata.model_validate(part["video_metadata"])
                        media_part_kwargs["video_metadata"] = metadata

                    if "media_resolution" in part:
                        if model and _is_gemini_25_model(model):
                            warnings.warn(
                                "Setting per-part media resolution requests to "
                                "Gemini 2.5 models and older is not supported. The "
                                "media_resolution parameter will be ignored.",
                                UserWarning,
                                stacklevel=2,
                            )
                        elif model and _is_gemini_3_or_later(model):
                            media_part_kwargs["media_resolution"] = {
                                "level": part["media_resolution"]
                            }
                    if "extras" in part and isinstance(part["extras"], dict):
                        sig = part["extras"].get("signature")
                        if sig and isinstance(sig, str):
                            media_part_kwargs["thought_signature"] = base64.b64decode(
                                sig
                            )

                    parts.append(Part(**media_part_kwargs))
                elif part["type"] == "thinking":
                    # Pre-existing thinking block format that we continue to store as
                    thought_sig = None
                    if "signature" in part:
                        sig = part["signature"]
                        if sig and isinstance(sig, str):
                            # Decode base64-encoded signature back to bytes
                            thought_sig = base64.b64decode(sig)
                    parts.append(
                        Part(
                            text=part["thinking"],
                            thought=True,
                            thought_signature=thought_sig,
                        )
                    )
                elif part["type"] == "reasoning":
                    # ReasoningContentBlock (when output_version = "v1")
                    extras = part.get("extras", {}) or {}
                    sig = extras.get("signature")
                    thought_sig = None
                    if sig and isinstance(sig, str):
                        # Decode base64-encoded signature back to bytes
                        thought_sig = base64.b64decode(sig)
                    parts.append(
                        Part(
                            text=part["reasoning"],
                            thought=True,
                            thought_signature=thought_sig,
                        )
                    )
                elif part["type"] == "server_tool_call":
                    if part.get("name") == "code_interpreter":
                        args = part.get("args", {})
                        code = args.get("code", "")
                        language = args.get("language", "python")
                        executable_code_part = Part(
                            executable_code=ExecutableCode(language=language, code=code)
                        )
                        parts.append(executable_code_part)
                    else:
                        warnings.warn(
                            f"Server tool call with name '{part.get('name')}' is not "
                            "currently supported by Google GenAI. Only "
                            "'code_interpreter' is supported.",
                            stacklevel=2,
                        )
                elif part["type"] == "executable_code":
                    # Legacy executable_code format (backward compat)
                    if "executable_code" not in part or "language" not in part:
                        msg = (
                            "Executable code part must have 'code' and 'language' "
                            f"keys, got {part}"
                        )
                        raise ValueError(msg)
                    executable_code_part = Part(
                        executable_code=ExecutableCode(
                            language=part["language"], code=part["executable_code"]
                        )
                    )
                    parts.append(executable_code_part)
                elif part["type"] == "server_tool_result":
                    output = part.get("output", "")
                    status = part.get("status", "success")
                    outcome = (
                        CodeExecutionResultOutcome.OUTCOME_OK
                        if status == "success"
                        else CodeExecutionResultOutcome.OUTCOME_FAILED
                    )
                    # Check extras for original outcome if available
                    if "extras" in part and "outcome" in part["extras"]:
                        outcome = part["extras"]["outcome"]
                    code_execution_result_part = Part(
                        code_execution_result=CodeExecutionResult(
                            output=str(output), outcome=outcome
                        )
                    )
                    parts.append(code_execution_result_part)
                elif part["type"] == "code_execution_result":
                    # Legacy code_execution_result format (backward compat)
                    if "code_execution_result" not in part:
                        msg = (
                            "Code execution result part must have "
                            f"'code_execution_result', got {part}"
                        )
                        raise ValueError(msg)
                    if "outcome" in part:
                        raw_outcome = part["outcome"]
                        # Convert integer outcome to enum if needed
                        # (for backward compat)
                        if isinstance(raw_outcome, int):
                            if raw_outcome == 1:
                                outcome = CodeExecutionResultOutcome.OUTCOME_OK
                            elif raw_outcome == 2:
                                outcome = CodeExecutionResultOutcome.OUTCOME_FAILED
                            else:
                                outcome = CodeExecutionResultOutcome.OUTCOME_UNSPECIFIED
                        else:
                            outcome = raw_outcome
                    else:
                        # Backward compatibility
                        outcome = CodeExecutionResultOutcome.OUTCOME_OK
                    code_execution_result_part = Part(
                        code_execution_result=CodeExecutionResult(
                            outcome=outcome,
                            output=part["code_execution_result"],
                        )
                    )
                    parts.append(code_execution_result_part)
                else:
                    msg = f"Unrecognized message part type: {part['type']}."
                    raise ValueError(msg)
            else:
                # Yolo. The input message content doesn't have a `type` key
                logger.warning(
                    "Unrecognized message part format. Assuming it's a text part."
                )
                parts.append(Part(text=str(part)))
        else:
            msg = "Unknown error occurred while converting LC message content to parts."
            raise ChatGoogleGenerativeAIError(msg)
    return parts


def _convert_tool_message_to_parts(
    message: ToolMessage | FunctionMessage,
    name: str | None = None,
    model: str | None = None,
) -> list[Part]:
    """Converts a tool or function message to a Google `Part`."""
    # Legacy agent stores tool name in message.additional_kwargs instead of message.name
    name = message.name or name or message.additional_kwargs.get("name")
    response: Any
    parts: list[Part] = []
    if isinstance(message.content, list):
        media_blocks = []
        other_blocks = []
        for block in message.content:
            if isinstance(block, dict) and (
                is_data_content_block(block) or is_openai_data_block(block)
            ):
                media_blocks.append(block)
            else:
                other_blocks.append(block)
        parts.extend(_convert_to_parts(media_blocks, model=model))
        response = other_blocks

    elif not isinstance(message.content, str):
        response = message.content
    else:
        try:
            response = json.loads(message.content)
        except json.JSONDecodeError:
            response = message.content  # leave as str representation
    part = Part(
        function_response=FunctionResponse(
            name=name,
            response=(
                {"output": response} if not isinstance(response, dict) else response
            ),
        )
    )
    parts.append(part)
    return parts


def _get_ai_message_tool_messages_parts(
    tool_messages: Sequence[ToolMessage],
    ai_message: AIMessage,
    model: str | None = None,
) -> list[Part]:
    """Conversion.

    Finds relevant tool messages for the AI message and converts them to a single list
    of `Part`s.
    """
    # We are interested only in the tool messages that are part of the AI message
    tool_calls_ids = {tool_call["id"]: tool_call for tool_call in ai_message.tool_calls}
    parts = []
    for _i, message in enumerate(tool_messages):
        if not tool_calls_ids:
            break
        if message.tool_call_id in tool_calls_ids:
            tool_call = tool_calls_ids[message.tool_call_id]
            message_parts = _convert_tool_message_to_parts(
                message, name=tool_call.get("name"), model=model
            )
            parts.extend(message_parts)
            # remove the id from the dict, so that we do not iterate over it again
            tool_calls_ids.pop(message.tool_call_id)
    return parts


# To generate the below thought signature:

# from langchain_google_genai import ChatGoogleGenerativeAI
#
# def generate_placeholder_thoughts(value: int) -> str:
#     """Placeholder tool."""
#     pass
#
# model = ChatGoogleGenerativeAI(
#     model="gemini-3.1-pro-preview"
# ).bind_tools([generate_placeholder_thoughts])
#
# response = model.invoke("Generate a placeholder tool invocation.")

DUMMY_THOUGHT_SIGNATURE = _base64_to_bytes(
    "ErQCCrECAdHtim8MtxgeMCRCiNiyoyImxtYAEDzz4NXOr/HSL3rA7rPPvHWZCm+T9VSDYh/mt9lESoH4wQh"
    "/ca1zDtWTN6XOL1+S3krYLQeqp47RV/b1eSq5jdZF28S4Lb7w4A3/EFdybc4SFb2/YhMm+CulYLmLA4Tr4V"
    "Su0eMWgxM3HVt6u0jECf5BbXzj0qjJ32tEQYJvKvV8H1tCHvB6J+RZhsDr+TcyOCaqxDoR4WKxXYxNRZb3h"
    "YTuCnBEDPhn1lROumVaghi9nEIgc17z002zLoyqIptlLfIVw70FXkCLsPUSL1SjPQYtGL8PVncVajeqGogR"
    "D/eZSVZ1Zr5tshxh3DQ+JAYNcrHaRHWC4Hg0H6oftYx+JdJD9B/81NYV9jyGxP7zHKFHOELl0IUP5GEXP9I"
    "="
)


def _parse_chat_history(
    input_messages: Sequence[BaseMessage],
    convert_system_message_to_human: bool = False,
    model: str | None = None,
) -> tuple[Content | None, list[Content]]:
    """Parses sequence of `BaseMessage` into system instruction and formatted messages.

    Args:
        input_messages: Sequence of `BaseMessage` objects representing the chat history.
        convert_system_message_to_human: Deprecated, use system instructions instead.

            Whether to convert the first system message into a `HumanMessage`.
        model: The model name, used for version-specific logic.

    Returns:
        A tuple containing:

            - An optional `generativelanguage_v1beta` `Content` representing the system
                instruction (if any).
            - A list of `generativelanguage_v1beta` `Content` representing the formatted
                messages.
    """
    if convert_system_message_to_human:
        warnings.warn(
            "The 'convert_system_message_to_human' parameter is deprecated and will be "
            "removed in a future version. Use system instructions instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    input_messages = list(input_messages)  # Make a mutable copy

    # Case where content was serialized to v1 format
    for idx, message in enumerate(input_messages):
        if (
            isinstance(message, AIMessage)
            and message.response_metadata.get("output_version") == "v1"
        ):
            # Unpack known v1 content to v1beta format for the request
            #
            # Old content types and any previously serialized messages passed back in to
            # history will skip this, but hit and processed in `_convert_to_parts`
            input_messages[idx] = message.model_copy(
                update={
                    "content": _convert_from_v1_to_generativelanguage_v1beta(
                        cast("list[types.ContentBlock]", message.content),
                        message.response_metadata.get("model_provider"),
                    )
                }
            )

    formatted_messages: list[Content] = []

    system_instruction: Content | None = None
    messages_without_tool_messages = [
        message for message in input_messages if not isinstance(message, ToolMessage)
    ]
    tool_messages = [
        message for message in input_messages if isinstance(message, ToolMessage)
    ]
    for i, message in enumerate(messages_without_tool_messages):
        if isinstance(message, SystemMessage):
            system_parts = _convert_to_parts(message.content, model=model)
            if i == 0:
                system_instruction = Content(parts=system_parts)
            elif system_instruction is not None:
                if system_instruction.parts is None:
                    system_instruction.parts = system_parts
                else:
                    system_instruction.parts.extend(system_parts)
            else:
                pass
            continue
        if isinstance(message, AIMessage):
            role = "model"
            if message.tool_calls:
                ai_message_parts = []

                # First, include thinking blocks from content if present.
                # When include_thoughts=True, thinking blocks need to be preserved
                # when passing messages back to the API.
                if isinstance(message.content, list):
                    for content_block in message.content:
                        if isinstance(content_block, dict):
                            block_type = content_block.get("type")
                            if block_type == "thinking":
                                # v0 output_format thinking block
                                thought_sig = None
                                if "signature" in content_block:
                                    sig = content_block["signature"]
                                    if sig and isinstance(sig, str):
                                        thought_sig = base64.b64decode(sig)
                                ai_message_parts.append(
                                    Part(
                                        text=content_block["thinking"],
                                        thought=True,
                                        thought_signature=thought_sig,
                                    )
                                )
                            elif block_type == "reasoning":
                                # v1 output_format reasoning block
                                # (Stored in extras, and different type key)
                                extras = content_block.get("extras", {}) or {}
                                sig = extras.get("signature")
                                thought_sig = None
                                if sig and isinstance(sig, str):
                                    thought_sig = base64.b64decode(sig)
                                ai_message_parts.append(
                                    Part(
                                        text=content_block["reasoning"],
                                        thought=True,
                                        thought_signature=thought_sig,
                                    )
                                )

                # Then, add function call parts
                function_call_sigs: dict[Any, str] = message.additional_kwargs.get(
                    _FUNCTION_CALL_THOUGHT_SIGNATURES_MAP_KEY, {}
                )
                for tool_call_idx, tool_call in enumerate(message.tool_calls):
                    function_call = FunctionCall(
                        name=tool_call["name"],
                        args=tool_call["args"],
                    )
                    # Check if there's a signature for this function call
                    sig = function_call_sigs.get(tool_call.get("id"))
                    if sig:
                        ai_message_parts.append(
                            Part(
                                function_call=function_call,
                                thought_signature=_base64_to_bytes(sig),
                            )
                        )
                    else:
                        ai_message_parts.append(Part(function_call=function_call))
                tool_messages_parts = _get_ai_message_tool_messages_parts(
                    tool_messages=tool_messages, ai_message=message, model=model
                )
                formatted_messages.append(Content(role=role, parts=ai_message_parts))
                # Only append tool response message if there are actual tool responses.
                # The Gemini API requires every Content message to have at least one
                # Part. If there are no ToolMessages in the conversation history for
                # this AI message's tool_calls, tool_messages_parts will be empty, and
                # we must not create an empty Content message.
                if tool_messages_parts:
                    formatted_messages.append(
                        Content(role="user", parts=tool_messages_parts)
                    )
                continue
            if raw_function_call := message.additional_kwargs.get("function_call"):
                function_call = FunctionCall(
                    name=raw_function_call["name"],
                    args=json.loads(raw_function_call["arguments"]),
                )
                parts = [Part(function_call=function_call)]
            elif message.response_metadata.get("output_version") == "v1":
                # Already converted to v1beta format above
                parts = message.content  # type: ignore[assignment]
            else:
                # Prepare request content parts from message.content field
                parts = _convert_to_parts(message.content, model=model)
        elif isinstance(message, HumanMessage):
            role = "user"
            parts = _convert_to_parts(message.content, model=model)
            if i == 1 and convert_system_message_to_human and system_instruction:
                parts = list(system_instruction.parts or []) + parts
                system_instruction = None
        elif isinstance(message, FunctionMessage):
            role = "user"
            parts = _convert_tool_message_to_parts(message, model=model)
        else:
            msg = f"Unexpected message with type {type(message)} at the position {i}."
            raise ValueError(msg)

        # Final step; assemble the Content object to pass to the API
        # If version = "v1", the parts are already in v1beta format and will be
        # automatically converted using protobuf's auto-conversion
        formatted_messages.append(Content(role=role, parts=parts))

    # Enforce thought signatures for new Gemini models
    #
    # These models require a 'thought_signature' field in function calls for the
    # current active conversation loop. If missing (e.g., from older history or
    # manual construction), the API may reject the request.
    if model and _is_gemini_3_or_later(model):
        # 1. Identify the "Active Loop":
        # Scan backwards to find the most recent User message that initiated he current
        # interaction (i.e., contains text/media, not just a tool response).
        # This defines the scope where we must ensure compliance.
        active_loop_start_idx = -1
        for i in range(len(formatted_messages) - 1, -1, -1):
            content_msg = formatted_messages[i]
            if content_msg.role == "user":
                has_function_response = False
                has_standard_content = False
                for part in content_msg.parts or []:
                    if part.function_response:
                        has_function_response = True
                    if part.text or part.inline_data:
                        has_standard_content = True

                # Found the user message that started this turn
                if has_standard_content and not has_function_response:
                    active_loop_start_idx = i
                    break

        # 2. Patch Missing Signatures:
        # Iterate through the active loop. If a model message contains a function call
        # but lacks a thought signature, inject a dummy value. This satisfies the
        # API's schema validation without requiring the original internal thought data.
        start_idx = active_loop_start_idx + 1 if active_loop_start_idx != -1 else 0
        for i in range(start_idx, len(formatted_messages)):
            content_msg = formatted_messages[i]
            if content_msg.role == "model":
                first_fc_seen = False
                for part in content_msg.parts or []:
                    if part.function_call:
                        if not first_fc_seen:
                            if not part.thought_signature:
                                part.thought_signature = DUMMY_THOUGHT_SIGNATURE
                            first_fc_seen = True

    return system_instruction, formatted_messages


# Helper function to append content consistently
def _append_to_content(
    current_content: str | list[Any] | None, new_item: Any
) -> str | list[Any]:
    """Appends a new item to the content, handling different initial content types."""
    if current_content is None and isinstance(new_item, str):
        return new_item
    if current_content is None:
        return [new_item]
    if isinstance(current_content, str):
        return [current_content, new_item]
    if isinstance(current_content, list):
        current_content.append(new_item)
        return current_content
    # This case should ideally not be reached with proper type checking,
    # but it catches any unexpected types that might slip through.
    msg = f"Unexpected content type: {type(current_content)}"
    raise TypeError(msg)


def _convert_integer_like_floats(obj: Any) -> Any:
    """Convert integer-like floats to integers recursively.

    Addresses a protobuf issue where integers are converted to floats when using
    `proto.Message.to_dict()`.

    Args:
        obj: The object to process (can be `dict`, `list`, or primitive)

    Returns:
        The object with integer-like floats converted to integers
    """
    if isinstance(obj, dict):
        return {k: _convert_integer_like_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_integer_like_floats(item) for item in obj]
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    return obj


def _parse_response_candidate(
    response_candidate: Candidate,
    streaming: bool = False,
    model_name: str | None = None,
    *,
    model_name_for_content: str | None = None,
) -> AIMessage:
    """Parse a response candidate from Google into an `AIMessage`.

    Args:
        response_candidate: The candidate from the API response.
        streaming: Whether this is a streaming response.
        model_name: Model name to include in `response_metadata` (`None` for
            intermediate streaming chunks to avoid duplication when concatenating).
        model_name_for_content: Model name to use for determining content format.

            For Gemini 3+, this determines whether to use list-based content blocks
            or string content. Must be consistent across all streaming chunks to
            enable proper concatenation. If not provided, falls back to `model_name`.

    Returns:
        The parsed `AIMessage` or `AIMessageChunk`.

    Note:
        During streaming, we want to avoid duplicating `model_name` in
        `response_metadata` for intermediate chunks (only include it in the final
        chunk), but we need the model name consistently across all chunks to determine
        the content format. This is why `model_name` and `model_name_for_content` are
        separate parameters.
    """
    content: None | str | list[str | dict] = None
    additional_kwargs: dict[str, Any] = {}
    response_metadata: dict[str, Any] = {"model_provider": "google_genai"}
    if model_name:
        response_metadata["model_name"] = model_name
    tool_calls = []
    invalid_tool_calls = []
    tool_call_chunks = []

    # Use model_name_for_content if provided, otherwise fall back to model_name.
    # This ensures consistent content format across all streaming chunks while
    # only including model_name in response_metadata for the final chunk.
    effective_model_name = model_name_for_content or model_name

    parts = response_candidate.content.parts or [] if response_candidate.content else []
    for part in parts:
        text: str | None = None
        try:
            if hasattr(part, "text") and part.text is not None:
                text = part.text
                # Remove erroneous newline character if present
                if not streaming:
                    text = text.rstrip("\n")
        except AttributeError:
            pass

        # Extract thought signature if present (can be on any Part type)
        # Signatures are binary data, encode to base64 string for JSON serialization
        thought_sig: str | None = None
        if hasattr(part, "thought_signature") and part.thought_signature:
            try:
                # Encode binary signature to base64 string
                thought_sig = base64.b64encode(part.thought_signature).decode("ascii")
                if not thought_sig:  # Empty string
                    thought_sig = None
            except (AttributeError, TypeError):
                thought_sig = None

        if hasattr(part, "thought") and part.thought:
            thinking_message = {
                "type": "thinking",
                "thinking": part.text,
            }
            # Include signature if present
            if thought_sig:
                thinking_message["signature"] = thought_sig
            content = _append_to_content(content, thinking_message)
        elif (
            (text is not None and text)  # text part with non-empty string
            or (part.text is not None and thought_sig)  # text part w/ thought sig
        ):
            text_block: dict[str, Any] = {"type": "text", "text": text or ""}
            if thought_sig:
                text_block["extras"] = {"signature": thought_sig}
            if thought_sig or _is_gemini_3_or_later(effective_model_name or ""):
                # append blocks if there's a signature or new Gemini model
                content = _append_to_content(content, text_block)
            elif isinstance(content, list) and any(
                isinstance(item, dict) and item.get("type") == "thinking"
                for item in content
            ):
                # if there's thinking blocks, keep content as dicts
                content = _append_to_content(content, text_block)
            else:
                # otherwise, append text
                content = _append_to_content(content, text or "")

        if hasattr(part, "executable_code") and part.executable_code is not None:
            if part.executable_code.code and part.executable_code.language:
                code_id = str(uuid.uuid4())  # Generate ID if not present, needed later
                code_message = {
                    "type": "executable_code",
                    "executable_code": part.executable_code.code,
                    "language": part.executable_code.language,
                    "id": code_id,
                }
                content = _append_to_content(content, code_message)

        if (
            hasattr(part, "code_execution_result")
            and part.code_execution_result is not None
        ) and part.code_execution_result.output:
            # outcome: 1 = OUTCOME_OK (success), 2 = error
            # Convert enum to int for compatibility with langchain_core
            if part.code_execution_result.outcome is None:
                outcome = 1  # Default to OUTCOME_OK
            elif (
                part.code_execution_result.outcome
                == CodeExecutionResultOutcome.OUTCOME_OK
            ):
                outcome = 1
            else:
                outcome = 2
            execution_result = {
                "type": "code_execution_result",
                "code_execution_result": part.code_execution_result.output,
                "outcome": outcome,
                "tool_call_id": "",  # Linked via block translator
            }
            content = _append_to_content(content, execution_result)

        if part.inline_data and part.inline_data.data and part.inline_data.mime_type:
            if part.inline_data.mime_type.startswith("audio/"):
                buffer = io.BytesIO()

                with wave.open(buffer, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    # TODO: Read Sample Rate from MIME content type.
                    wf.setframerate(24000)
                    wf.writeframes(part.inline_data.data)

                audio_data = buffer.getvalue()
                additional_kwargs["audio"] = audio_data

                # For backwards compatibility, audio stays in additional_kwargs by
                # default and is accessible via .content_blocks property

            if part.inline_data.mime_type.startswith("image/"):
                image_format = part.inline_data.mime_type[6:]
                image_message: dict[str, Any] = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_bytes_to_b64_string(
                            part.inline_data.data,
                            image_format=image_format,
                        )
                    },
                }
                if thought_sig:
                    image_message["extras"] = {"signature": thought_sig}
                content = _append_to_content(content, image_message)

        if part.function_call:
            function_call = {"name": part.function_call.name}
            # dump to match other function calling llm for now
            # Convert function call args to dict first, then fix integer-like floats
            args_dict = dict(part.function_call.args) if part.function_call.args else {}
            function_call_args_dict = _convert_integer_like_floats(args_dict)
            function_call["arguments"] = json.dumps(
                {k: function_call_args_dict[k] for k in function_call_args_dict}
            )
            additional_kwargs["function_call"] = function_call

            tool_call_id = function_call.get("id", str(uuid.uuid4()))
            if streaming:
                tool_call_chunks.append(
                    tool_call_chunk(
                        name=function_call.get("name"),
                        args=function_call.get("arguments"),
                        id=tool_call_id,
                        index=function_call.get("index"),  # type: ignore
                    )
                )
            else:
                try:
                    tool_call_dict = parse_tool_calls(
                        [{"function": function_call}],
                        return_id=False,
                    )[0]
                except Exception as e:
                    invalid_tool_calls.append(
                        invalid_tool_call(
                            name=function_call.get("name"),
                            args=function_call.get("arguments"),
                            id=tool_call_id,
                            error=str(e),
                        )
                    )
                else:
                    tool_calls.append(
                        tool_call(
                            name=tool_call_dict["name"],
                            args=tool_call_dict["args"],
                            id=tool_call_id,
                        )
                    )

            # If this function_call Part has a signature, track it separately
            if thought_sig:
                if _FUNCTION_CALL_THOUGHT_SIGNATURES_MAP_KEY not in additional_kwargs:
                    additional_kwargs[_FUNCTION_CALL_THOUGHT_SIGNATURES_MAP_KEY] = {}
                additional_kwargs[_FUNCTION_CALL_THOUGHT_SIGNATURES_MAP_KEY][
                    tool_call_id
                ] = (
                    _bytes_to_base64(thought_sig)
                    if isinstance(thought_sig, bytes)
                    else thought_sig
                )

    if content is None:
        if _is_gemini_3_or_later(effective_model_name or ""):
            content = []
        else:
            content = ""
    if isinstance(content, list) and any(
        isinstance(item, dict) and "executable_code" in item for item in content
    ):
        warnings.warn(
            """
        Warning: Output may vary each run.
        - 'executable_code': Always present.
        - 'execution_result' & 'image_url': May be absent for some queries.

        Validate before using in production.
"""
        )
    if streaming:
        return AIMessageChunk(
            content=content,
            additional_kwargs=additional_kwargs,
            response_metadata=response_metadata,
            tool_call_chunks=tool_call_chunks,
        )

    return AIMessage(
        content=content,
        additional_kwargs=additional_kwargs,
        response_metadata=response_metadata,
        tool_calls=tool_calls,
        invalid_tool_calls=invalid_tool_calls,
    )


def _response_to_result(
    response: GenerateContentResponse,
    stream: bool = False,
    prev_usage: UsageMetadata | None = None,
) -> ChatResult:
    """Converts a Google AI response into a LangChain `ChatResult`."""
    llm_output = (
        {"prompt_feedback": response.prompt_feedback.model_dump()}
        if response.prompt_feedback
        else {}
    )

    # Get usage metadata
    try:
        if response.usage_metadata is None:
            msg = "Usage metadata is None"
            raise AttributeError(msg)
        input_tokens = response.usage_metadata.prompt_token_count or 0
        thought_tokens = response.usage_metadata.thoughts_token_count or 0
        output_tokens = (
            response.usage_metadata.candidates_token_count or 0
        ) + thought_tokens
        total_tokens = response.usage_metadata.total_token_count or 0
        cache_read_tokens = response.usage_metadata.cached_content_token_count or 0
        if input_tokens + output_tokens + cache_read_tokens + total_tokens > 0:
            if thought_tokens > 0:
                cumulative_usage = UsageMetadata(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    input_token_details={"cache_read": cache_read_tokens},
                    output_token_details={"reasoning": thought_tokens},
                )
            else:
                cumulative_usage = UsageMetadata(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    input_token_details={"cache_read": cache_read_tokens},
                )
            # previous usage metadata needs to be subtracted because gemini api returns
            # already-accumulated token counts with each chunk
            lc_usage = subtract_usage(cumulative_usage, prev_usage)
            if prev_usage and cumulative_usage["input_tokens"] < prev_usage.get(
                "input_tokens", 0
            ):
                # Gemini 2.0 returns a lower cumulative count of prompt tokens
                # in the final chunk. We take this count to be ground truth because
                # it's consistent with the reported total tokens. So we need to
                # ensure this chunk compensates (the subtract_usage funcction floors
                # at zero).
                lc_usage["input_tokens"] = cumulative_usage[
                    "input_tokens"
                ] - prev_usage.get("input_tokens", 0)
        else:
            lc_usage = None
    except AttributeError:
        lc_usage = None

    generations: list[ChatGeneration] = []

    for candidate in response.candidates or []:
        generation_info: dict[str, Any] = {}
        # Only include model_name in response_metadata for the last chunk
        # (when finish_reason exists)
        # to avoid duplication when chunks are concatenated with +=
        model_name_for_metadata = None
        if candidate.finish_reason:
            # Handle finish_reason that may be an enum or raw integer
            if hasattr(candidate.finish_reason, "name"):
                generation_info["finish_reason"] = candidate.finish_reason.name
            elif isinstance(candidate.finish_reason, int):
                generation_info["finish_reason"] = f"UNKNOWN_{candidate.finish_reason}"
            # Add model_name in last chunk
            generation_info["model_name"] = response.model_version or ""
            # Set for final chunk
            model_name_for_metadata = response.model_version
        generation_info["safety_ratings"] = (
            [safety_rating.model_dump() for safety_rating in candidate.safety_ratings]
            if candidate.safety_ratings
            else []
        )
        # Pass model_version for content format determination (Gemini 3+ needs
        # consistent list-based content across all chunks), but only include
        # model_name in response_metadata for the final chunk to avoid duplication
        # when chunks are concatenated.
        message = _parse_response_candidate(
            candidate,
            streaming=stream,
            model_name=model_name_for_metadata,  # None for intermediate chunks
            model_name_for_content=response.model_version,  # Always set
        )

        if not hasattr(message, "response_metadata"):
            message.response_metadata = {}

        try:
            if candidate.grounding_metadata:
                grounding_metadata = candidate.grounding_metadata.model_dump()
                # Ensure None fields that are expected to be lists become empty lists
                # to prevent errors in downstream processing
                if (
                    "grounding_supports" in grounding_metadata
                    and grounding_metadata["grounding_supports"] is None
                ):
                    grounding_metadata["grounding_supports"] = []
                if (
                    "grounding_chunks" in grounding_metadata
                    and grounding_metadata["grounding_chunks"] is None
                ):
                    grounding_metadata["grounding_chunks"] = []
                if (
                    "web_search_queries" in grounding_metadata
                    and grounding_metadata["web_search_queries"] is None
                ):
                    grounding_metadata["web_search_queries"] = []
                if (
                    "image_search_queries" in grounding_metadata
                    and grounding_metadata["image_search_queries"] is None
                ):
                    grounding_metadata["image_search_queries"] = []
                generation_info["grounding_metadata"] = grounding_metadata
                message.response_metadata["grounding_metadata"] = grounding_metadata
        except AttributeError:
            pass

        message.usage_metadata = lc_usage

        if stream:
            generations.append(
                ChatGenerationChunk(
                    message=cast("AIMessageChunk", message),
                    generation_info=generation_info,
                )
            )
        else:
            generations.append(
                ChatGeneration(message=message, generation_info=generation_info)
            )
    if not response.candidates:
        # Likely a "prompt feedback" violation (e.g., toxic input)
        # Raising an error would be different than how OpenAI handles it,
        # so we'll just log a warning and continue with an empty message.
        logger.warning(
            "Gemini produced an empty response. Continuing with empty message\n"
            f"Feedback: {response.prompt_feedback}"
        )
        if stream:
            response_metadata = (
                {"prompt_feedback": response.prompt_feedback.model_dump()}
                if response.prompt_feedback
                else {}
            )
            generations = [
                ChatGenerationChunk(
                    message=AIMessageChunk(
                        content="",
                        response_metadata=response_metadata,
                    ),
                    generation_info={},
                )
            ]
        else:
            generations = [ChatGeneration(message=AIMessage(""), generation_info={})]
    return ChatResult(generations=generations, llm_output=llm_output)


class ChatGoogleGenerativeAI(_BaseGoogleGenerativeAI, BaseChatModel):
    r"""Google GenAI chat model integration.

    Setup:
        !!! version-added "Vertex AI Platform Support"

            Added in `langchain-google-genai` 4.0.0.

            `ChatGoogleGenerativeAI` now supports both the **Gemini Developer API** and
            **Vertex AI Platform** as backend options.

        **For Gemini Developer API** (simplest):

        1. Set the `GOOGLE_API_KEY` environment variable (recommended), or
        2. Pass your API key using the [`api_key`][langchain_google_genai.ChatGoogleGenerativeAI.google_api_key]
            parameter

        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", api_key="...")
        ```

        **For Vertex AI Platform with API key**:

        ```bash
        export GEMINI_API_KEY='your-api-key'
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT='your-project-id'
        ```

        ```python
        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
        # Or explicitly:
        model = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            api_key="...",
            project="your-project-id",
            vertexai=True,
        )
        ```

        **For Vertex AI with credentials**:

        ```python
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            project="your-project-id",
            # Uses Application Default Credentials (ADC)
        )
        ```

        **Automatic backend detection** (when `vertexai=None` / unspecified):

        1. If `GOOGLE_GENAI_USE_VERTEXAI` env var is set, uses that value
        2. If `credentials` parameter is provided, uses Vertex AI
        3. If `project` parameter is provided, uses Vertex AI
        4. Otherwise, uses Gemini Developer API

    Environment variables:
        | Variable | Purpose | Backend |
        |----------|---------|---------|
        | `GOOGLE_API_KEY` | API key (primary) | Both (see `GOOGLE_GENAI_USE_VERTEXAI`) |
        | `GEMINI_API_KEY` | API key (fallback) | Both (see `GOOGLE_GENAI_USE_VERTEXAI`) |
        | `GOOGLE_GENAI_USE_VERTEXAI` | Force Vertex AI backend (`true`/`false`) | Vertex AI |
        | `GOOGLE_CLOUD_PROJECT` | GCP project ID | Vertex AI |
        | `GOOGLE_CLOUD_LOCATION` | GCP region (default: `global`) | Vertex AI |
        | `HTTPS_PROXY` | HTTP/HTTPS proxy URL | Both |
        | `SSL_CERT_FILE` | Custom SSL certificate file | Both |

        `GOOGLE_API_KEY` is checked first for backwards compatibility. (`GEMINI_API_KEY`
        was introduced later to better reflect the API's branding.)

    Proxy configuration:
        Set these before initializing:

        ```bash
        export HTTPS_PROXY='http://username:password@proxy_uri:port'
        export SSL_CERT_FILE='path/to/cert.pem'  # Optional: custom SSL certificate
        ```

        For SOCKS5 proxies or advanced proxy configuration, use the
        [`client_args`][langchain_google_genai.ChatGoogleGenerativeAI.client_args]
        parameter:

        ```python
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            client_args={"proxy": "socks5://user:pass@host:port"},
        )
        ```

    ???+ example "Instantiation"

        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
        model.invoke("Write me a ballad about LangChain")
        ```

    ???+ example "Invoke"

        ```python
        messages = [
            ("system", "Translate the user sentence to French."),
            ("human", "I love programming."),
        ]
        model.invoke(messages)
        ```

        ```python
        AIMessage(
            content=[
                {
                    "type": "text",
                    "text": "**J'adore la programmation.**\n\nYou can also say:...",
                    "extras": {"signature": "Eq0W..."},
                }
            ],
            additional_kwargs={},
            response_metadata={
                "prompt_feedback": {"block_reason": 0, "safety_ratings": []},
                "finish_reason": "STOP",
                "model_name": "gemini-3.1-pro-preview",
                "safety_ratings": [],
                "model_provider": "google_genai",
            },
            id="lc_run--63a04ced-6b63-4cf6-86a1-c32fa565938e-0",
            usage_metadata={
                "input_tokens": 12,
                "output_tokens": 826,
                "total_tokens": 838,
                "input_token_details": {"cache_read": 0},
                "output_token_details": {"reasoning": 777},
            },
        )
        ```

        !!! note "`content` format"

            The shape of `content` may differ based on the model chosen. See
            [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#invocation)
            for more info.

    ???+ example "Stream"

        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

        for chunk in model.stream(messages):
            print(chunk)
        ```

        ```python
        AIMessageChunk(
            content="J",
            response_metadata={"finish_reason": "STOP", "safety_ratings": []},
            id="run-e905f4f4-58cb-4a10-a960-448a2bb649e3",
            usage_metadata={
                "input_tokens": 18,
                "output_tokens": 1,
                "total_tokens": 19,
            },
        )
        AIMessageChunk(
            content="'adore programmer. \\n",
            response_metadata={
                "finish_reason": "STOP",
                "safety_ratings": [
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                ],
            },
            id="run-e905f4f4-58cb-4a10-a960-448a2bb649e3",
            usage_metadata={
                "input_tokens": 18,
                "output_tokens": 5,
                "total_tokens": 23,
            },
        )
        ```

        To assemble a full [`AIMessage`][langchain.messages.AIMessage] message from a
        stream of chunks:

        ```python
        stream = model.stream(messages)
        full = next(stream)
        for chunk in stream:
            full += chunk
        full
        ```

        ```python
        AIMessageChunk(
            content="J'adore programmer. \\n",
            response_metadata={
                "finish_reason": "STOPSTOP",
                "safety_ratings": [
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "probability": "NEGLIGIBLE",
                        "blocked": False,
                    },
                ],
            },
            id="run-3ce13a42-cd30-4ad7-a684-f1f0b37cdeec",
            usage_metadata={
                "input_tokens": 36,
                "output_tokens": 6,
                "total_tokens": 42,
            },
        )
        ```

        !!! note "`content` format"

            The shape of `content` may differ based on the model chosen. See
            [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#invocation)
            for more info.

    ???+ example "Async invocation"

        ```python
        await model.ainvoke(messages)

        # stream:
        async for chunk in (await model.astream(messages))

        # batch:
        await model.abatch([messages])
        ```

    ???+ example "Tool calling"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#tool-calling)
        for more info.

        ```python
        from pydantic import BaseModel, Field


        class GetWeather(BaseModel):
            '''Get the current weather in a given location'''

            location: str = Field(
                ..., description="The city and state, e.g. San Francisco, CA"
            )


        class GetPopulation(BaseModel):
            '''Get the current population in a given location'''

            location: str = Field(
                ..., description="The city and state, e.g. San Francisco, CA"
            )


        llm_with_tools = llm.bind_tools([GetWeather, GetPopulation])
        ai_msg = llm_with_tools.invoke(
            "Which city is hotter today and which is bigger: LA or NY?"
        )
        ai_msg.tool_calls
        ```

        ```python
        [
            {
                "name": "GetWeather",
                "args": {"location": "Los Angeles, CA"},
                "id": "c186c99f-f137-4d52-947f-9e3deabba6f6",
            },
            {
                "name": "GetWeather",
                "args": {"location": "New York City, NY"},
                "id": "cebd4a5d-e800-4fa5-babd-4aa286af4f31",
            },
            {
                "name": "GetPopulation",
                "args": {"location": "Los Angeles, CA"},
                "id": "4f92d897-f5e4-4d34-a3bc-93062c92591e",
            },
            {
                "name": "GetPopulation",
                "args": {"location": "New York City, NY"},
                "id": "634582de-5186-4e4b-968b-f192f0a93678",
            },
        ]
        ```

    ???+ example "Structured output"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#structured-output)
        for more info.

        ```python
        from typing import Optional

        from pydantic import BaseModel, Field


        class Joke(BaseModel):
            '''Joke to tell user.'''

            setup: str = Field(description="The setup of the joke")
            punchline: str = Field(description="The punchline to the joke")
            rating: Optional[int] = Field(
                description="How funny the joke is, from 1 to 10"
            )


        # Default method uses json_schema for reliable structured output
        structured_model = model.with_structured_output(Joke)
        structured_model.invoke("Tell me a joke about cats")

        # Alternative: use function_calling method (less reliable)
        structured_model_fc = model.with_structured_output(
            Joke, method="function_calling"
        )
        ```

        ```python
        Joke(
            setup="Why are cats so good at video games?",
            punchline="They have nine lives on the internet",
            rating=None,
        )
        ```

        Two methods are supported for structured output:

        * `method='json_schema'` (default): Uses Gemini's native structured output API.

            The Google GenAI SDK automatically transforms schemas to ensure
            compatibility with Gemini. This includes:

            - Inlining `$defs` definitions (Union types work correctly)
            - Resolving `$ref` references for nested schemas
            - Property ordering preservation
            - Support for streaming partial JSON chunks

            Uses Gemini's `response_json_schema` API param. Refer to the Gemini API
            [docs](https://ai.google.dev/gemini-api/docs/structured-output) for more
            details. This method is recommended for better reliability as it
            constrains the model's generation process directly.

        * `method='function_calling'`: Uses tool calling to extract structured data.
            Less reliable than `json_schema` but compatible with all models.

    ???+ example "Image input"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#image-input)
        for more info.

        ```python
        import base64
        import httpx
        from langchain.messages import HumanMessage

        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
        message = HumanMessage(
            content=[
                {"type": "text", "text": "describe the weather in this image"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ]
        )
        ai_msg = model.invoke([message])
        ai_msg.content
        ```

        ```txt
        The weather in this image appears to be sunny and pleasant. The sky is a bright
        blue with scattered white clouds, suggesting fair weather. The lush green grass
        and trees indicate a warm and possibly slightly breezy day. There are no...
        ```

    ???+ example "PDF input"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#pdf-input)
        for more info.

        ```python
        import base64
        from langchain.messages import HumanMessage

        pdf_bytes = open("/path/to/your/test.pdf", "rb").read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": "describe the document in a sentence"},
                {
                    "type": "file",
                    "source_type": "base64",
                    "mime_type": "application/pdf",
                    "data": pdf_base64,
                },
            ]
        )
        ai_msg = model.invoke([message])
        ```

    ???+ example "Audio input"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#audio-input)
        for more info.

        ```python
        import base64
        from langchain.messages import HumanMessage

        audio_bytes = open("/path/to/your/audio.mp3", "rb").read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": "summarize this audio in a sentence"},
                {
                    "type": "file",
                    "source_type": "base64",
                    "mime_type": "audio/mp3",
                    "data": audio_base64,
                },
            ]
        )
        ai_msg = model.invoke([message])
        ```

    ???+ example "Video input"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#video-input)
        for more info.

        ```python
        import base64
        from langchain.messages import HumanMessage

        video_bytes = open("/path/to/your/video.mp4", "rb").read()
        video_base64 = base64.b64encode(video_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "describe what's in this video in a sentence",
                },
                {
                    "type": "file",
                    "source_type": "base64",
                    "mime_type": "video/mp4",
                    "data": video_base64,
                },
            ]
        )
        ai_msg = model.invoke([message])
        ```

        You can also pass YouTube URLs directly:

        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

        message = HumanMessage(
            content=[
                {"type": "text", "text": "Summarize the video in 3 sentences."},
                {
                    "type": "media",
                    "file_uri": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "mime_type": "video/mp4",
                },
            ]
        )
        response = model.invoke([message])
        print(response.text)
        ```

    ???+ example "Image generation"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#image-generation)
        for more info.

    ???+ example "Audio generation"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#audio-generation)
        for more info.

        !!! note "Vertex compatibility"

            Audio generation models (TTS) are currently in preview on Vertex AI
            and may require allowlist access. If you receive an `INVALID_ARGUMENT`
            error when using TTS models with `vertexai=True`, your project may need to
            be allowlisted.

            See this post on the [Google AI forum](https://discuss.ai.google.dev/t/request-allowlist-access-for-audio-output-in-gemini-2-5-pro-flash-tts-vertex-ai/108067)
            for more details.

    ???+ example "File upload"

        You can also upload files to Google's servers and reference them by URI.

        This works for PDFs, images, videos, and audio files.

        ```python
        import time
        from google import genai
        from langchain.messages import HumanMessage

        client = genai.Client()

        myfile = client.files.upload(file="/path/to/your/sample.pdf")
        while myfile.state.name == "PROCESSING":
            time.sleep(2)
            myfile = client.files.get(name=myfile.name)

        message = HumanMessage(
            content=[
                {"type": "text", "text": "What is in the document?"},
                {
                    "type": "media",
                    "file_uri": myfile.uri,
                    "mime_type": "application/pdf",
                },
            ]
        )
        ai_msg = model.invoke([message])
        ```

    ???+ example "Thinking"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#thinking-support)
        for more info.

        Gemini 3+ models use [`thinking_level`][langchain_google_genai.ChatGoogleGenerativeAI.thinking_level]
        (`'low'`, `'medium'`, or `'high'`) to control reasoning depth. If not specified,
        defaults to `'high'`.

        ```python
        model = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            thinking_level="low",  # For faster, lower-latency responses
        )
        ```

        Gemini 2.5 models use [`thinking_budget`][langchain_google_genai.ChatGoogleGenerativeAI.thinking_budget]
        (an integer token count) to control reasoning. Set to `0` to disable thinking
        (where supported), or `-1` for dynamic thinking.

        See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/thinking) for
        more details on thinking models.

        To see a thinking model's thoughts, set [`include_thoughts=True`][langchain_google_genai.ChatGoogleGenerativeAI.include_thoughts]
        to have the model's reasoning summaries included in the response.

        ```python
        model = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            include_thoughts=True,
        )
        ai_msg = model.invoke("How many 'r's are in the word 'strawberry'?")
        ```

    ???+ example "Thought signatures"

        Gemini 3+ models return *thought signatures*—encrypted representations of
        the model's internal reasoning.

        For multi-turn conversations involving tool calls, you must pass the full
        [`AIMessage`][langchain.messages.AIMessage] back to the model so that these
        signatures are preserved. This happens automatically when you append the
        [`AIMessage`][langchain.messages.AIMessage] to your message list.

        See the [LangChain docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#thought-signatures) for more info as well as a code example.

        See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/thinking)
        for more details on thought signatures.

    ???+ example "Google search"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#google-search)
        for more info.

        ```python
        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
        response = model.invoke(
            "When is the next total solar eclipse in US?",
            tools=[{"google_search": {}}],
        )
        response.content_blocks
        ```

        Alternatively, you can bind the tool to the model for easier reuse across calls:

        ```python
        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

        model_with_search = model.bind_tools([{"google_search": {}}])
        response = model_with_search.invoke(
            "When is the next total solar eclipse in US?"
        )

        response.content_blocks
        ```

    ???+ example "Google Maps"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#google-maps)
        for more info.

    ???+ example "Code execution"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#code-execution)
        for more info.

        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

        model_with_code_interpreter = model.bind_tools([{"code_execution": {}}])
        response = model_with_code_interpreter.invoke("Use Python to calculate 3^3.")

        response.content_blocks
        ```

        ```output
        [{'type': 'server_tool_call',
          'name': 'code_interpreter',
          'args': {'code': 'print(3**3)', 'language': <Language.PYTHON: 1>},
          'id': '...'},
         {'type': 'server_tool_result',
          'tool_call_id': '',
          'status': 'success',
          'output': '27\n',
          'extras': {'block_type': 'code_execution_result',
           'outcome': 1}},
         {'type': 'text', 'text': 'The calculation of 3 to the power of 3 is 27.'}]
        ```

    ???+ example "Computer use"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#computer-use)
        for more info.

        !!! warning "Preview model limitations"

            The Computer Use model is in preview and may produce unexpected behavior.

            Always supervise automated tasks and avoid use with sensitive data or
            critical operations. See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/computer-use)
            for safety best practices.

    ???+ example "Token usage"
        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#token-usage-tracking)
        for more info.

        ```python
        ai_msg = model.invoke(messages)
        ai_msg.usage_metadata
        ```

        ```python
        {"input_tokens": 18, "output_tokens": 5, "total_tokens": 23}
        ```

    ???+ example "Safety settings"

        Gemini models have default safety settings that can be overridden. If you
        are receiving lots of "Safety Warnings" from your models, you can try
        tweaking the `safety_settings` attribute of the model. For example, to
        turn off safety blocking for dangerous content, you can construct your
        LLM as follows:

        ```python
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            HarmBlockThreshold,
            HarmCategory,
        )

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
        ```

        For an enumeration of the categories and thresholds available, see Google's
        [safety settings](https://ai.google.dev/gemini-api/docs/safety-settings).

    ???+ example "Context caching"

        See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#context-caching)
        for more info.

        Context caching allows you to store and reuse content (e.g., PDFs, images) for
        faster processing. The [`cached_content`][langchain_google_genai.ChatGoogleGenerativeAI.cached_content]
        parameter accepts a cache name created via the Google Generative AI API.

        See the Gemini docs for more details on [cached content](https://ai.google.dev/gemini-api/docs/caching?lang=python).

        Below are two examples: caching a single file directly and caching multiple
        files using `Part`.

        ???+ example "Single file example"

            This caches a single file and queries it.

            ```python
            from google import genai
            from google.genai import types
            import time
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.messages import HumanMessage

            client = genai.Client()

            # Upload file
            file = client.files.upload(file="path/to/your/file")
            while file.state.name == "PROCESSING":
                time.sleep(2)
                file = client.files.get(name=file.name)

            # Create cache
            model = "gemini-3.1-pro-preview"
            cache = client.caches.create(
                model=model,
                config=types.CreateCachedContentConfig(
                    display_name="Cached Content",
                    system_instruction=(
                        "You are an expert content analyzer, and your job is to answer "
                        "the user's query based on the file you have access to."
                    ),
                    contents=[file],
                    ttl="300s",
                ),
            )

            # Query with LangChain
            llm = ChatGoogleGenerativeAI(
                model=model,
                cached_content=cache.name,
            )
            message = HumanMessage(content="Summarize the main points of the content.")
            llm.invoke([message])
            ```

        ??? example "Multiple files example"

            This caches two files using `Part` and queries them together.

            ```python
            from google import genai
            from google.genai.types import CreateCachedContentConfig, Content, Part
            import time
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.messages import HumanMessage

            client = genai.Client()

            # Upload files
            file_1 = client.files.upload(file="./file1")
            while file_1.state.name == "PROCESSING":
                time.sleep(2)
                file_1 = client.files.get(name=file_1.name)

            file_2 = client.files.upload(file="./file2")
            while file_2.state.name == "PROCESSING":
                time.sleep(2)
                file_2 = client.files.get(name=file_2.name)

            # Create cache with multiple files
            contents = [
                Content(
                    role="user",
                    parts=[
                        Part.from_uri(file_uri=file_1.uri, mime_type=file_1.mime_type),
                        Part.from_uri(file_uri=file_2.uri, mime_type=file_2.mime_type),
                    ],
                )
            ]
            model = "gemini-3.1-pro-preview"
            cache = client.caches.create(
                model=model,
                config=CreateCachedContentConfig(
                    display_name="Cached Contents",
                    system_instruction=(
                        "You are an expert content analyzer, and your job is to answer "
                        "the user's query based on the files you have access to."
                    ),
                    contents=contents,
                    ttl="300s",
                ),
            )

            # Query with LangChain
            llm = ChatGoogleGenerativeAI(
                model=model,
                cached_content=cache.name,
            )
            message = HumanMessage(
                content="Provide a summary of the key information across both files."
            )
            llm.invoke([message])
            ```

    ???+ example "Response metadata"

        ```python
        ai_msg = model.invoke(messages)
        ai_msg.response_metadata
        ```

        ```python
        {
            "model_name": "gemini-3.1-pro-preview",
            "model_provider": "google_genai",
            "prompt_feedback": {"block_reason": 0, "safety_ratings": []},
            "finish_reason": "STOP",
            "safety_ratings": [
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "probability": "NEGLIGIBLE",
                    "blocked": False,
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "probability": "NEGLIGIBLE",
                    "blocked": False,
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "probability": "NEGLIGIBLE",
                    "blocked": False,
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "probability": "NEGLIGIBLE",
                    "blocked": False,
                },
            ],
        }
        ```
    """  # noqa: E501

    client: Client | None = Field(
        default=None,
        exclude=True,  # Excluded from serialization
    )

    default_metadata: Sequence[tuple[str, str]] | None = Field(
        default=None,
        alias="default_metadata_input",
    )

    model_kwargs: dict[str, Any] = Field(default_factory=dict)
    """Holds any unexpected initialization parameters."""

    streaming: bool | None = None
    """Whether to stream responses from the model."""

    convert_system_message_to_human: bool = False
    """Whether to merge any leading `SystemMessage` into the following `HumanMessage`.

    Gemini does not support system messages; any unsupported messages will raise an
    error.
    """

    stop: list[str] | None = None
    """Stop sequences for the model."""

    response_mime_type: str | None = None
    """Output response MIME type of the generated candidate text.

    Supported MIME types:
        * `'text/plain'`: (default) Text output.
        * `'application/json'`: JSON response in the candidates.
        * `'text/x.enum'`: Enum in plain text. (legacy; use JSON schema output instead)

    !!! note

        The model also needs to be prompted to output the appropriate response type,
        otherwise the behavior is undefined.

        (In other words, simply setting this param doesn't force the model to comply;
        it only tells the model the kind of output expected. You still need to prompt it
        correctly.)
    """

    response_schema: dict[str, Any] | None = None
    """Enforce a schema to the output.

    The format of the dictionary should follow JSON Schema specification.

    !!! note "Schema Transformation"

        The Google GenAI SDK automatically transforms schemas for Gemini compatibility:

        - Inlines `$defs` definitions (enables Union types with `anyOf`)
        - Resolves `$ref` pointers for nested/recursive schemas
        - Preserves property ordering
        - Supports constraints like `minimum`/`maximum`, `minItems`/`maxItems`

    !!! tip "Using Union Types"

        Union types in Pydantic models (e.g., `field: Union[TypeA, TypeB]`) are
        automatically converted to `anyOf` schemas and work correctly with the
        `json_schema` method.

    Refer to the Gemini API [docs](https://ai.google.dev/gemini-api/docs/structured-output)
    for more details on supported JSON Schema features.
    """

    thinking_level: Literal["minimal", "low", "medium", "high"] | None = Field(
        default=None,
    )
    """Indicates the thinking level.

    Supported values:
        * `'low'`: Minimizes latency and cost.
        * `'medium'`: Balances latency/cost with reasoning depth.
        * `'high'`: Maximizes reasoning depth.

    !!! note "Replaces `thinking_budget`"

        `thinking_budget` is deprecated for Gemini 3+ models. If both parameters are
        provided, `thinking_level` takes precedence.

        If left unspecified, the model's default thinking level is used. For Gemini 3+,
        this defaults to `'high'`.
    """

    cached_content: str | None = None
    """The name of the cached content used as context to serve the prediction.

    !!! note

        Only used in explicit caching, where users can have control over caching (e.g.
        what content to cache) and enjoy guaranteed cost savings. Format:
        `cachedContents/{cachedContent}`.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Needed for arg validation."""
        # Get all valid field names, including aliases
        valid_fields = set()
        for field_name, field_info in self.__class__.model_fields.items():
            valid_fields.add(field_name)
            if hasattr(field_info, "alias") and field_info.alias is not None:
                valid_fields.add(field_info.alias)

        # Check for unrecognized arguments
        for arg in kwargs:
            if arg not in valid_fields:
                suggestions = get_close_matches(arg, valid_fields, n=1)
                suggestion = (
                    f" Did you mean: '{suggestions[0]}'?" if suggestions else ""
                )
                logger.warning(
                    f"Unexpected argument '{arg}' "
                    f"provided to ChatGoogleGenerativeAI.{suggestion}"
                )
        super().__init__(**kwargs)

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @property
    def _llm_type(self) -> str:
        return "chat-google-generative-ai"

    @property
    def _supports_code_execution(self) -> bool:
        """Whether the model supports code execution.

        See [Gemini models](https://ai.google.dev/gemini-api/docs/models) for a list.
        """
        # TODO: Refactor to use `capabilities` property when supported upstream
        # (or done via augmentation)
        return "gemini-2" in self.model or "gemini-3" in self.model

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in.

        (In other words, handle additional params that aren't explicitly defined as
        model fields. Used to pass extra config to underlying APIs without defining them
        all here.)
        """
        all_required_field_names = get_pydantic_field_names(cls)
        return _build_model_kwargs(values, all_required_field_names)

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validates params and builds client.

        We override `temperature` to `1.0` for Gemini 3+ models if not explicitly set.
        This is to prevent infinite loops and degraded performance that can occur with
        `temperature < 1.0` on these models.
        """
        if self.temperature is not None and not 0 <= self.temperature <= 2.0:
            msg = "temperature must be in the range [0.0, 2.0]"
            raise ValueError(msg)

        if "temperature" not in self.model_fields_set and _is_gemini_3_or_later(
            self.model
        ):
            self.temperature = 1.0

        if self.top_p is not None and not 0 <= self.top_p <= 1:
            msg = "top_p must be in the range [0.0, 1.0]"
            raise ValueError(msg)

        if self.top_k is not None and self.top_k <= 0:
            msg = "top_k must be positive"
            raise ValueError(msg)

        additional_headers = self.additional_headers or {}
        self.default_metadata = tuple(additional_headers.items())

        _, user_agent = get_user_agent("ChatGoogleGenerativeAI")
        headers = {"user-agent": user_agent, **additional_headers}

        google_api_key = None
        if not self.credentials:
            if isinstance(self.google_api_key, SecretStr):
                google_api_key = self.google_api_key.get_secret_value()
            else:
                google_api_key = self.google_api_key

        base_url = self.base_url
        if isinstance(self.base_url, dict):
            # Handle case where base_url is provided as a dict
            # (Backwards compatibility for deprecated client_options field)
            if keys := list(self.base_url.keys()):
                if "api_endpoint" in keys and len(keys) == 1:
                    base_url = self.base_url["api_endpoint"]
                elif "api_endpoint" in keys and len(keys) > 1:
                    msg = (
                        "When providing base_url as a dict, it can only contain the "
                        "api_endpoint key. Extra keys found: "
                        f"{[k for k in keys if k != 'api_endpoint']}"
                    )
                    raise ValueError(msg)
                else:
                    msg = (
                        "When providing base_url as a dict, it must only contain the "
                        "api_endpoint key."
                    )
                    raise ValueError(msg)
            else:
                msg = (
                    "base_url must be a string or a dict containing the "
                    "api_endpoint key."
                )
                raise ValueError(msg)

        http_options = HttpOptions(
            base_url=cast("str", base_url),
            api_version=self.api_version,
            headers=headers,
            client_args=self.client_args,
            async_client_args=self.client_args,
        )

        if self._use_vertexai:  # type: ignore[attr-defined]
            # Vertex AI backend - supports both API key and credentials
            # Note: The google-genai SDK requires API keys to be passed via environment
            # variables when using Vertex AI, not via the api_key parameter.
            # If an API key is provided programmatically, we set it in the environment
            # temporarily for the Client initialization.

            # Normalize model name for Vertex AI - strip 'models/' prefix
            # Vertex AI expects model names without the prefix
            # (e.g., "gemini-2.5-flash") while Google AI accepts both formats
            if self.model.startswith("models/"):
                object.__setattr__(self, "model", self.model.replace("models/", "", 1))

            api_key_env_set = False

            if (
                google_api_key
                and not os.getenv("GOOGLE_API_KEY")
                and not os.getenv("GEMINI_API_KEY")
            ):
                # Set the API key in environment for Client initialization
                os.environ["GOOGLE_API_KEY"] = google_api_key
                api_key_env_set = True

            try:
                self.client = Client(
                    vertexai=True,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                    http_options=http_options,
                )
            finally:
                # Clean up the temporary environment variable if we set it
                if api_key_env_set:
                    os.environ.pop("GOOGLE_API_KEY", None)
        else:
            # Gemini Developer API - requires API key
            if not google_api_key:
                msg = (
                    "API key required for Gemini Developer API. Provide api_key "
                    "parameter or set GOOGLE_API_KEY/GEMINI_API_KEY environment "
                    "variable."
                )
                raise ValueError(msg)
            self.client = Client(api_key=google_api_key, http_options=http_options)
        return self

    @model_validator(mode="after")
    def _set_model_profile(self) -> Self:
        """Set model profile if not overridden."""
        if self.profile is None:
            model_id = re.sub(r"-\d{3}$", "", self.model.replace("models/", ""))
            self.profile = _get_default_model_profile(model_id)
        return self

    def __del__(self) -> None:
        """Clean up the client on deletion."""
        if not hasattr(self, "client") or self.client is None:
            return

        try:
            # Close the sync client
            self.client.close()

            # Attempt to close the async client
            # Note: The SDK's close() doesn't close the async client automatically
            if hasattr(self.client, "aio") and self.client.aio is not None:
                try:
                    # Check if there's a running event loop
                    loop = asyncio.get_running_loop()
                    if not loop.is_closed():
                        # Schedule the close
                        # Wrap in ensure_future to avoid "coroutine never awaited"
                        task = asyncio.ensure_future(
                            self.client.aio.aclose(), loop=loop
                        )
                        # Add a done callback to suppress any exceptions
                        task.add_done_callback(
                            lambda t: t.exception() if not t.cancelled() else None
                        )
                except RuntimeError:
                    # No running loop - create a new one for cleanup
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(self.client.aio.aclose())
                        finally:
                            loop.close()
                            asyncio.set_event_loop(None)
                    except Exception:
                        # Suppress errors during shutdown
                        pass
        except Exception:
            # Suppress all errors during cleanup
            pass

    @property
    def async_client(self) -> Any:
        """Async client for Google GenAI operations..

        Returns:
            The async client interface that exposes async versions of all client
                methods.

        Raises:
            ValueError: If the client has not been initialized.
        """
        if self.client is None:
            msg = "Client not initialized. Initialize the model first."
            raise ValueError(msg)
        return self.client.aio

    @property
    def _identifying_params(self) -> dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
            "n": self.n,
            "safety_settings": self.safety_settings,
            "response_modalities": self.response_modalities,
            "media_resolution": self.media_resolution,
            "thinking_budget": self.thinking_budget,
            "include_thoughts": self.include_thoughts,
            "thinking_level": self.thinking_level,
            "image_config": self.image_config,
        }

    def invoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        code_execution: bool | None = None,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        """Override `invoke` on `ChatGoogleGenerativeAI` to add `code_execution`."""
        if code_execution is not None:
            if not self._supports_code_execution:
                msg = (
                    "Code execution is only supported on Gemini 2.0, and 2.5 models. "
                    f"Current model: {self.model}"
                )
                raise ValueError(msg)
            if "tools" not in kwargs:
                code_execution_tool = GoogleTool(code_execution=ToolCodeExecution())
                kwargs["tools"] = [code_execution_tool]

            else:
                msg = "Tools are already defined.code_execution tool can't be defined"
                raise ValueError(msg)

        return super().invoke(input, config, stop=stop, **kwargs)

    def _get_ls_params(
        self, stop: list[str] | None = None, **kwargs: Any
    ) -> LangSmithParams:
        """Get standard params for tracing."""
        params = self._get_invocation_params(stop=stop, **kwargs)
        models_prefix = "models/"
        raw_model = params.get("model") or self.model
        ls_model_name = (
            raw_model[len(models_prefix) :]
            if raw_model and raw_model.startswith(models_prefix)
            else raw_model
        )
        ls_params = LangSmithParams(
            ls_provider="google_genai",
            ls_model_name=ls_model_name,
            ls_model_type="chat",
            ls_temperature=params.get("temperature", self.temperature),
        )
        if ls_max_tokens := params.get("max_output_tokens", self.max_output_tokens):
            ls_params["ls_max_tokens"] = ls_max_tokens
        if ls_stop := stop or params.get("stop", None):
            ls_params["ls_stop"] = ls_stop
        return ls_params

    def _supports_thinking(self) -> bool:
        """Check if the current model supports thinking capabilities."""
        return self.profile.get("reasoning_output", False) if self.profile else False

    def _prepare_params(
        self,
        stop: list[str] | None,
        generation_config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> GenerationConfig:
        """Prepare generation parameters with config logic."""
        gen_config = self._build_base_generation_config(stop, **kwargs)
        if generation_config:
            gen_config = self._merge_generation_config(gen_config, generation_config)

        # Handle response-specific kwargs (MIME type and structured output)
        gen_config = self._add_response_parameters(gen_config, **kwargs)

        return GenerationConfig.model_validate(gen_config)

    def _build_base_generation_config(
        self, stop: list[str] | None, **kwargs: Any
    ) -> dict[str, Any]:
        """Build the base generation configuration from instance attributes."""
        config: dict[str, Any] = {
            "candidate_count": self.n,
            "temperature": kwargs.get("temperature", self.temperature),
            "stop_sequences": stop,
            "max_output_tokens": kwargs.get(
                "max_output_tokens", self.max_output_tokens
            ),
            "top_k": kwargs.get("top_k", self.top_k),
            "top_p": kwargs.get("top_p", self.top_p),
            "response_modalities": kwargs.get(
                "response_modalities", self.response_modalities
            ),
            "seed": kwargs.get("seed", self.seed),
        }

        # Convert response modalities
        config["response_modalities"] = (
            [m.value for m in config["response_modalities"]]
            if config["response_modalities"]
            else None
        )

        # Auto-set audio output and speech_config for TTS models
        # if not explicitly configured
        if self.model.endswith("-tts") or "-tts-" in self.model:
            if config["response_modalities"] is None:
                config["response_modalities"] = ["AUDIO"]
            if config.get("speech_config") is None:
                voice_name = config.pop("voice_name", "Kore")
                config["speech_config"] = SpeechConfig(
                    voice_config=VoiceConfig(
                        prebuilt_voice_config=PrebuiltVoiceConfig(voice_name=voice_name)
                    )
                )

        thinking_config = self._build_thinking_config(**kwargs)
        if thinking_config is not None:
            config["thinking_config"] = thinking_config

        return {k: v for k, v in config.items() if v is not None}

    def _build_thinking_config(self, **kwargs: Any) -> ThinkingConfig | None:
        """Build thinking configuration if supported by the model."""
        thinking_level = kwargs.get("thinking_level", self.thinking_level)
        thinking_budget = kwargs.get("thinking_budget", self.thinking_budget)
        include_thoughts = kwargs.get("include_thoughts", self.include_thoughts)

        has_thinking_params = (
            thinking_level is not None
            or thinking_budget is not None
            or include_thoughts is not None
        )
        if not has_thinking_params:
            return None

        config: dict[str, Any] = {}

        # thinking_level takes precedence over thinking_budget for Gemini 3+ models
        if thinking_level is not None:
            if thinking_budget is not None:
                warnings.warn(
                    "Both 'thinking_level' and 'thinking_budget' were provided. "
                    "'thinking_level' takes precedence for Gemini 3+ models; "
                    "'thinking_budget' will be ignored.",
                    UserWarning,
                    stacklevel=2,
                )
            config["thinking_level"] = thinking_level
        elif thinking_budget is not None:
            config["thinking_budget"] = thinking_budget

        if include_thoughts is not None:
            config["include_thoughts"] = include_thoughts

        return ThinkingConfig(**config)

    def _merge_generation_config(
        self, base_config: dict[str, Any], generation_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge user-provided generation config with base config."""
        processed_config = dict(generation_config)
        # Convert string response_modalities to Modality enums if needed
        if "response_modalities" in processed_config:
            modalities = processed_config["response_modalities"]
            if (
                isinstance(modalities, list)
                and modalities
                and isinstance(modalities[0], str)
            ):
                from langchain_google_genai import Modality

                try:
                    processed_config["response_modalities"] = [
                        getattr(Modality, modality) for modality in modalities
                    ]
                except AttributeError as e:
                    msg = f"Invalid response modality: {e}"
                    raise ValueError(msg) from e
        return {**base_config, **processed_config}

    def _add_response_parameters(
        self, gen_config: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]:
        """Add response-specific parameters to generation config.

        Includes `response_mime_type`, `response_schema`, and `response_json_schema`.
        """
        # Handle response mime type
        response_mime_type = kwargs.get("response_mime_type", self.response_mime_type)
        if response_mime_type is not None:
            gen_config["response_mime_type"] = response_mime_type

        response_schema = kwargs.get("response_schema", self.response_schema)
        response_json_schema = kwargs.get("response_json_schema")  # If passed as kwarg

        # Handle both response_schema and response_json_schema
        # (Regardless, we use `response_json_schema` in the request)
        schema_to_use = (
            response_json_schema
            if response_json_schema is not None
            else response_schema
        )
        if schema_to_use:
            self._validate_and_add_response_schema(
                gen_config=gen_config,
                response_schema=schema_to_use,
                response_mime_type=response_mime_type,
            )

        return gen_config

    def _validate_and_add_response_schema(
        self,
        gen_config: dict[str, Any],
        response_schema: dict[str, Any],
        response_mime_type: str | None,
    ) -> None:
        """Validate and add response schema to generation config."""
        if response_mime_type != "application/json":
            error_message = (
                "JSON schema structured output is only supported when "
                "response_mime_type is set to 'application/json'"
            )
            if response_mime_type == "text/x.enum":
                error_message += (
                    ". Instead of 'text/x.enum', define enums using your JSON schema."
                )
            raise ValueError(error_message)

        gen_config["response_json_schema"] = response_schema

    def _prepare_request(
        self,
        messages: list[BaseMessage],
        *,
        stop: list[str] | None = None,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
        safety_settings: SafetySettingDict | None = None,
        tool_config: dict | ToolConfig | None = None,
        tool_choice: _ToolChoiceType | bool | None = None,
        generation_config: dict[str, Any] | None = None,
        cached_content: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Prepare the request configuration for the API call."""
        # Process tools and functions
        formatted_tools = self._format_tools(tools, functions)

        # Remove any messages with empty content
        filtered_messages = self._filter_messages(messages)

        # Parse chat history into Gemini Content
        system_instruction, history = _parse_chat_history(
            filtered_messages,
            convert_system_message_to_human=self.convert_system_message_to_human,
            model=self.model,
        )

        # Process tool configuration
        formatted_tool_config = self._process_tool_config(
            tool_choice, tool_config, formatted_tools
        )

        # Process safety settings
        formatted_safety_settings = self._format_safety_settings(
            safety_settings if safety_settings is not None else self.safety_settings
        )

        timeout = kwargs.pop("timeout", None)
        if timeout is not None:
            timeout = int(timeout * 1000)
        elif self.timeout is not None:
            timeout = int(self.timeout * 1000)

        max_retries = kwargs.pop("max_retries", None)
        if max_retries is None:
            max_retries = self.max_retries

        # Handle OpenAI-style `strict` kwarg (used by langchain.agents.create_agent)
        # Google's json_schema is inherently strict, so we just consume this.
        kwargs.pop("strict", None)

        # Handle OpenAI-style `response_format` kwarg
        # Ref: https://platform.openai.com/docs/guides/structured-outputs
        # Compatible with langchain.agents.create_agent ProviderStrategy
        response_format = kwargs.pop("response_format", None)
        if response_format is not None and isinstance(response_format, dict):
            rf_type = response_format.get("type")
            if rf_type in ("json_object", "json_schema"):
                if "response_mime_type" not in kwargs:
                    kwargs["response_mime_type"] = "application/json"
                json_schema = response_format.get("json_schema", {})
                schema = json_schema.get("schema")
                if schema and "response_json_schema" not in kwargs:
                    kwargs["response_json_schema"] = schema

        # Get generation parameters
        # (consumes thinking kwargs into params.thinking_config)
        params: GenerationConfig = self._prepare_params(
            stop, generation_config=generation_config, **kwargs
        )

        image_config = kwargs.pop("image_config", None)

        labels = kwargs.pop("labels", None)
        if labels is None:
            labels = self.labels

        _consumed_kwargs = {
            "thinking_budget",
            "thinking_level",
            "include_thoughts",
            "response_schema",
            "response_json_schema",
            "response_mime_type",
        }
        _consumed_kwargs.update(params.model_fields_set)
        # Filter out kwargs already consumed by _prepare_params.
        # These are handled via params and aren't direct fields
        # on GenerateContentConfig or would cause duplicate argument errors.
        remaining_kwargs = {
            k: v for k, v in kwargs.items() if k not in _consumed_kwargs
        }

        # Build request configuration
        request = self._build_request_config(
            formatted_tools,
            formatted_tool_config,
            formatted_safety_settings,
            params,
            cached_content,
            system_instruction,
            timeout=timeout,
            max_retries=max_retries,
            image_config=image_config,
            labels=labels,
            **remaining_kwargs,
        )

        # Return config and additional params needed for API call
        return {"model": self.model, "contents": history, "config": request}

    def _format_tools(
        self,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
    ) -> list | None:
        """Format tools and functions for the API."""
        code_execution_tool = GoogleTool(code_execution=ToolCodeExecution())
        if tools == [code_execution_tool]:
            return list(tools)
        if tools:
            return convert_to_genai_function_declarations(tools)
        if functions:
            return convert_to_genai_function_declarations(functions)
        return None

    def _filter_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """Filter out messages with empty content."""
        filtered_messages = []
        for message in messages:
            if isinstance(message, HumanMessage) and not message.content:
                warnings.warn(
                    "HumanMessage with empty content was removed to prevent API error"
                )
            else:
                filtered_messages.append(message)
        return filtered_messages

    def _process_tool_config(
        self,
        tool_choice: _ToolChoiceType | bool | None,
        tool_config: dict | ToolConfig | None,
        formatted_tools: list | None,
    ) -> ToolConfig | None:
        """Process tool configuration and choice.

        Merges `tool_choice` and `tool_config` when both are provided.

        `tool_choice` controls `function_calling_config` while `tool_config` can provide
        retrieval_config (for Maps/Search grounding) and other configurations.
        """
        # Normalize tool_config to ToolConfig object if dict
        normalized_config: ToolConfig | None = None
        if tool_config:
            normalized_config = (
                ToolConfig.model_validate(tool_config)
                if isinstance(tool_config, dict)
                else tool_config
            )

        # Check for conflicts
        if tool_choice and normalized_config:
            if normalized_config.function_calling_config:
                msg = (
                    "Cannot specify both tool_choice and "
                    "tool_config.function_calling_config. "
                    f"Received {tool_choice=} and "
                    f"tool_config.function_calling_config="
                    f"{normalized_config.function_calling_config}"
                )
                raise ValueError(msg)

        # Process tool_choice
        if tool_choice:
            if not formatted_tools:
                msg = (
                    f"Received {tool_choice=} but no {formatted_tools=}. "
                    "'tool_choice' can only be specified if 'tools' is specified."
                )
                raise ValueError(msg)
            all_names = self._extract_tool_names(formatted_tools)

            # Only set function_calling_config if there are actual callable functions
            # (built-in tools like google_maps don't have function_declarations)
            if not all_names:
                # No callable functions, only built-in tools like Maps/Search
                # Just pass through tool_config without function_calling_config
                if normalized_config:
                    return normalized_config
                return None

            choice_config = _tool_choice_to_tool_config(tool_choice, all_names)

            # Merge with tool_config if it exists
            if normalized_config:
                # Merge: take function_calling_config from choice_config
                # and other fields from normalized_config
                return ToolConfig(
                    function_calling_config=choice_config.function_calling_config,
                    retrieval_config=normalized_config.retrieval_config,
                )
            return choice_config

        # Only tool_config provided
        if normalized_config:
            return normalized_config

        return None

    def _extract_tool_names(self, formatted_tools: list) -> list[str]:
        """Extract tool names from formatted tools."""
        all_names: list[str] = []
        for t in formatted_tools:
            if hasattr(t, "function_declarations") and t.function_declarations:
                t_with_declarations = cast("Any", t)
                all_names.extend(
                    f.name for f in t_with_declarations.function_declarations
                )
            elif isinstance(t, GoogleTool):
                # Built-in tools like code_execution, google_search, google_maps
                # don't have function_declarations
                continue
            else:
                msg = f"Tool {t} doesn't have function_declarations attribute"
                raise TypeError(msg)
        return all_names

    def _format_safety_settings(
        self, safety_settings: SafetySettingDict | None
    ) -> list[SafetySetting]:
        """Format safety settings for the API."""
        if not safety_settings:
            return []
        if isinstance(safety_settings, dict):
            return [
                SafetySetting(category=category, threshold=threshold)
                for category, threshold in safety_settings.items()
            ]
        msg = "safety_settings must be: dict[HarmCategory, HarmBlockThreshold]"
        raise TypeError(msg)

    def _build_request_config(
        self,
        formatted_tools: list | None,
        formatted_tool_config: ToolConfig | None,
        formatted_safety_settings: list[SafetySetting],
        params: GenerationConfig,
        cached_content: str | None,
        system_instruction: Content | None,
        timeout: int | None = None,
        max_retries: int | None = None,
        image_config: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> GenerateContentConfig:
        """Build the final request configuration."""

        retry_options = None
        if max_retries is not None:
            retry_options = HttpRetryOptions(attempts=max_retries)

        http_options = None
        if timeout is not None or retry_options is not None:
            http_options = HttpOptions(
                timeout=timeout,
                retry_options=retry_options,
            )

        image_config_dict = (
            image_config if image_config is not None else self.image_config
        )
        image_config_obj = None
        if image_config_dict is not None:
            image_config_obj = ImageConfig(**image_config_dict)

        return GenerateContentConfig(
            tools=list(formatted_tools) if formatted_tools else None,
            tool_config=formatted_tool_config,
            safety_settings=formatted_safety_settings,
            cached_content=cached_content,
            system_instruction=system_instruction,
            http_options=http_options,
            image_config=image_config_obj,
            labels=labels,
            **params.model_dump(exclude_unset=True),
            **kwargs,
        )

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        *,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
        safety_settings: SafetySettingDict | None = None,
        tool_config: dict | ToolConfig | None = None,
        generation_config: dict[str, Any] | None = None,
        cached_content: str | None = None,
        tool_choice: _ToolChoiceType | bool | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.client is None:
            msg = "Client not initialized."
            raise ValueError(msg)

        request = self._prepare_request(
            messages,
            stop=stop,
            tools=tools,
            functions=functions,
            safety_settings=safety_settings,
            tool_config=tool_config,
            generation_config=generation_config,
            cached_content=cached_content or self.cached_content,
            tool_choice=tool_choice,
            **kwargs,
        )
        try:
            response: GenerateContentResponse = self.client.models.generate_content(
                **request,
            )
        except ClientError as e:
            _handle_client_error(e, request)

        return _response_to_result(response)

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        *,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
        safety_settings: SafetySettingDict | None = None,
        tool_config: dict | ToolConfig | None = None,
        generation_config: dict[str, Any] | None = None,
        cached_content: str | None = None,
        tool_choice: _ToolChoiceType | bool | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.client is None:
            msg = "Client not initialized."
            raise ValueError(msg)

        request = self._prepare_request(
            messages,
            stop=stop,
            tools=tools,
            functions=functions,
            safety_settings=safety_settings,
            tool_config=tool_config,
            generation_config=generation_config,
            cached_content=cached_content or self.cached_content,
            tool_choice=tool_choice,
            **kwargs,
        )
        try:
            response: GenerateContentResponse = (
                await self.client.aio.models.generate_content(
                    **request,
                )
            )
        except ClientError as e:
            _handle_client_error(e, request)

        return _response_to_result(response)

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        *,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
        safety_settings: SafetySettingDict | None = None,
        tool_config: dict | ToolConfig | None = None,
        generation_config: dict[str, Any] | None = None,
        cached_content: str | None = None,
        tool_choice: _ToolChoiceType | bool | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        if self.client is None:
            msg = "Client not initialized."
            raise ValueError(msg)

        request = self._prepare_request(
            messages,
            stop=stop,
            tools=tools,
            functions=functions,
            safety_settings=safety_settings,
            tool_config=tool_config,
            generation_config=generation_config,
            cached_content=cached_content or self.cached_content,
            tool_choice=tool_choice,
            **kwargs,
        )
        try:
            response: Iterator[GenerateContentResponse] = (
                self.client.models.generate_content_stream(
                    **request,
                )
            )
        except ClientError as e:
            _handle_client_error(e, request)

        prev_usage_metadata: UsageMetadata | None = None  # Cumulative usage
        index = -1
        index_type = ""
        for chunk in response:
            if chunk:
                _chat_result = _response_to_result(
                    chunk, stream=True, prev_usage=prev_usage_metadata
                )
                gen = cast("ChatGenerationChunk", _chat_result.generations[0])
                message = cast("AIMessageChunk", gen.message)

            # Populate index if missing
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and "type" in block:
                        if block["type"] != index_type:
                            index_type = block["type"]
                            index = index + 1
                        if "index" not in block:
                            block["index"] = index

            prev_usage_metadata = (
                message.usage_metadata
                if prev_usage_metadata is None
                else add_usage(prev_usage_metadata, message.usage_metadata)
            )

            if run_manager:
                run_manager.on_llm_new_token(gen.text, chunk=gen)
            yield gen

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        *,
        tools: Sequence[_ToolDict | GoogleTool] | None = None,
        functions: Sequence[_FunctionDeclarationType] | None = None,
        safety_settings: SafetySettingDict | None = None,
        tool_config: dict | ToolConfig | None = None,
        generation_config: dict[str, Any] | None = None,
        cached_content: str | None = None,
        tool_choice: _ToolChoiceType | bool | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        if self.client is None:
            msg = "Client not initialized."
            raise ValueError(msg)

        request = self._prepare_request(
            messages,
            stop=stop,
            tools=tools,
            functions=functions,
            safety_settings=safety_settings,
            tool_config=tool_config,
            generation_config=generation_config,
            cached_content=cached_content or self.cached_content,
            tool_choice=tool_choice,
            **kwargs,
        )
        prev_usage_metadata: UsageMetadata | None = None  # Cumulative usage
        index = -1
        index_type = ""
        try:
            stream = await self.client.aio.models.generate_content_stream(
                **request,
            )
        except ClientError as e:
            _handle_client_error(e, request)

        async for chunk in stream:
            _chat_result = _response_to_result(
                chunk, stream=True, prev_usage=prev_usage_metadata
            )
            gen = cast("ChatGenerationChunk", _chat_result.generations[0])
            message = cast("AIMessageChunk", gen.message)

            # populate index if missing
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and "type" in block:
                        if block["type"] != index_type:
                            index_type = block["type"]
                            index = index + 1
                        if "index" not in block:
                            block["index"] = index

            prev_usage_metadata = (
                message.usage_metadata
                if prev_usage_metadata is None
                else add_usage(prev_usage_metadata, message.usage_metadata)
            )

            if run_manager:
                await run_manager.on_llm_new_token(gen.text, chunk=gen)
            yield gen

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text. Uses the model's tokenizer.

        Useful for checking if an input will fit in a model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.

        Example:
            ```python
            llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
            num_tokens = llm.get_num_tokens("Hello, world!")
            print(num_tokens)
            # -> 4
            ```
        """
        if self.client is None:
            msg = "Client not initialized."
            raise ValueError(msg)

        result = self.client.models.count_tokens(
            model=self.model, contents=[Content(parts=[Part(text=text)])]
        )
        return result.total_tokens if result and result.total_tokens is not None else 0

    def with_structured_output(
        self,
        schema: dict | type[BaseModel],
        method: Literal["function_calling", "json_mode", "json_schema"]
        | None = "json_schema",
        *,
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, dict | BaseModel]:
        """Return a `Runnable` that constrains model output to a given schema.

        Constrains the model to return output conforming to the provided schema.

        Supports Pydantic models, `TypedDict`, and JSON schema dictionaries.

        Args:
            schema: The output schema as a Pydantic `BaseModel` class, a `TypedDict`
                class, or a JSON schema dictionary.
            method: The method to use for structured output.

                Options:

                - `'json_schema'` (recommended): Uses native JSON schema support for
                    reliable structured output. Supports streaming with fully-parsed
                    Pydantic objects.
                - `'json_mode'`: Deprecated alias for `'json_schema'`.
                - `'function_calling'`: Uses tool/function calling. Less reliable than
                    `'json_schema'` and not recommended for new code.
            include_raw: If `True`, returns a dict with both the raw model output
                and the parsed structured output.

        Returns:
            A `Runnable` that takes the same input as the chat model but returns the
                structured output. When streaming, emits fully-parsed objects of the
                specified schema type (not incremental JSON strings).

        Example:
            ```python title="Basic usage with Pydantic model"
            from pydantic import BaseModel
            from langchain_google_genai import ChatGoogleGenerativeAI


            class Person(BaseModel):
                name: str
                age: int


            model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
            structured_model = model.with_structured_output(
                Person,
                method="json_schema",
            )

            result = structured_model.invoke(
                "Tell me about a person named Alice, age 30"
            )
            print(result)  # Person(name="Alice", age=30)
            ```

            ```python title="Streaming structured output"
            from pydantic import BaseModel
            from langchain_google_genai import ChatGoogleGenerativeAI


            class Recipe(BaseModel):
                name: str
                ingredients: list[str]
                steps: list[str]


            model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
            structured_model = model.with_structured_output(
                Recipe, method="json_schema"
            )

            # Emits fully-parsed Recipe objects, not incremental JSON strings
            for chunk in structured_model.stream(
                "Give me a recipe for chocolate chip cookies"
            ):
                print(chunk)  # Recipe(name=..., ingredients=[...], steps=[...])
            ```

            ```python title="Using with dict schema"
            model = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "priority": {"type": "integer"},
                },
                "required": ["title", "priority"],
            }

            structured_model = model.with_structured_output(
                schema, method="json_schema"
            )
            result = structured_model.invoke("Create a task: finish report, priority 1")
            print(result)  # {"title": "finish report", "priority": 1}
            ```

            ```python title="Including raw output"
            structured_model = model.with_structured_output(
                Person, method="json_schema", include_raw=True
            )

            result = structured_model.invoke("Tell me about Bob, age 25")
            print(result["parsed"])  # Person(name="Bob", age=25)
            print(result["raw"])  # AIMessage with full model response
            ```
        """
        _ = kwargs.pop("strict", None)
        if kwargs:
            msg = f"Received unsupported arguments {kwargs}"
            raise ValueError(msg)

        parser: OutputParserLike
        llm: Runnable[LanguageModelInput, AIMessage]

        # `json_mode` kept for backwards compatibility; shouldn't be used in new code
        if method in ("json_mode", "json_schema"):
            # For ls_structured_output_format, we use convert_to_json_schema for
            # Pydantic/TypedDict/dict-with-title schemas to match langchain standard
            # tests. Raw dicts without titles are passed through as-is.
            if isinstance(schema, type) and is_basemodel_subclass(schema):
                # Handle Pydantic models
                if issubclass(schema, BaseModelV1):
                    # Use legacy schema generation for pydantic v1 models
                    schema_json = schema.schema()
                else:
                    schema_json = schema.model_json_schema()
                parser = PydanticOutputParser(pydantic_object=schema)
                ls_schema = convert_to_json_schema(schema)
            elif is_typeddict(schema):
                schema_json = convert_to_json_schema(schema)
                parser = JsonOutputParser()
                ls_schema = schema_json
            elif isinstance(schema, dict):
                schema_json = schema
                parser = JsonOutputParser()
                # Dicts with title can be converted; raw dicts pass through as-is
                ls_schema = (
                    convert_to_json_schema(schema) if "title" in schema else schema
                )
            else:
                msg = f"Unsupported schema type {type(schema)}"
                raise ValueError(msg)

            # Note: The Google GenAI SDK automatically handles schema transformation
            # (inlining $defs, resolving $ref) via its process_schema() function.
            # This ensures Union types and nested schemas work correctly.
            llm = self.bind(
                response_mime_type="application/json",
                response_json_schema=schema_json,
                ls_structured_output_format={
                    "kwargs": {"method": method},
                    "schema": ls_schema,
                },
            )
        else:
            # LangChain tool calling structured output method (discouraged)
            tool_name = _get_tool_name(schema)  # type: ignore[arg-type]
            if isinstance(schema, type) and is_basemodel_subclass_safe(schema):
                parser = PydanticToolsParser(tools=[schema], first_tool_only=True)
            else:
                parser = JsonOutputKeyToolsParser(
                    key_name=tool_name, first_tool_only=True
                )
            tool_choice = tool_name if self._supports_tool_choice else None
            try:
                llm = self.bind_tools(
                    [schema],
                    tool_choice=tool_choice,
                    ls_structured_output_format={
                        "kwargs": {"method": "function_calling"},
                        "schema": convert_to_openai_tool(schema),
                    },
                )
            except Exception:
                llm = self.bind_tools([schema], tool_choice=tool_choice)
        if include_raw:
            parser_with_fallback = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | parser, parsing_error=lambda _: None
            ).with_fallbacks(
                [RunnablePassthrough.assign(parsed=lambda _: None)],
                exception_key="parsing_error",
            )
            return {"raw": llm} | parser_with_fallback
        return llm | parser

    def bind_tools(
        self,
        tools: Sequence[
            dict[str, Any] | type | Callable[..., Any] | BaseTool | GoogleTool
        ],
        tool_config: dict | ToolConfig | None = None,
        *,
        tool_choice: _ToolChoiceType | bool | None = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, AIMessage]:
        """Bind tool-like objects to this chat model.

        Args:
            tools: A list of tool definitions to bind to this chat model.

                Can be a pydantic model, `Callable`, or `BaseTool`. Pydantic models,
                `Callable`, and `BaseTool` objects will be automatically converted to
                their schema dictionary representation.

                Tools with Union types in their arguments are now supported and
                converted to `anyOf` schemas.
            tool_config: Optional tool configuration for additional settings like
                `retrieval_config` (for Google Maps/Google Search grounding).

                Can be used together with `tool_choice`, but cannot specify
                `function_calling_config` in `tool_config` if `tool_choice` is also
                provided (they would conflict).

                !!! example "Example with Google Maps grounding"

                    ```python
                    from langchain_google_genai import ChatGoogleGenerativeAI

                    model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

                    response = model.invoke(
                        "What Italian restaurants are near here?",
                        tools=[{"google_maps": {}}],
                        tool_choice="required",
                        tool_config={
                            "retrieval_config": {
                                "lat_lng": {
                                    "latitude": 48.858844,
                                    "longitude": 2.294351,
                                }
                            }
                        },
                    )
                    ```
            tool_choice: Control how the model uses tools.

                Options:

                - `'auto'` (default): Model decides whether to call functions
                - `'any'` or `'required'`: Model must call a function (both are
                    equivalent)
                - `'none'`: Model cannot call functions
                - `'function_name'`: Model must call the specified function
                - `['fn1', 'fn2']`: Model must call one of the specified functions
                - `True`: Same as `'any'`

                Can be used together with `tool_config` to control function calling
                while also providing additional configuration like `retrieval_config`.
            **kwargs: Any additional parameters to pass to the `Runnable` constructor.
        """
        try:
            formatted_tools: list = [convert_to_openai_tool(tool) for tool in tools]  # type: ignore[arg-type]
        except Exception:
            formatted_tools = [
                tool_to_dict(t) for t in convert_to_genai_function_declarations(tools)
            ]
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        if tool_config:
            kwargs["tool_config"] = tool_config
        return self.bind(tools=formatted_tools, **kwargs)

    @property
    def _supports_tool_choice(self) -> bool:
        """Whether the model supports the `tool_choice` parameter.

        See the [Gemini models docs](https://ai.google.dev/gemini-api/docs/models) for a
        full list. Gemini calls this "function calling".
        """
        return self.profile.get("tool_choice", True) if self.profile else True


def _get_tool_name(
    tool: _ToolDict | GoogleTool | dict,
) -> str:
    try:
        genai_tools = convert_to_genai_function_declarations([tool])
        genai_tool = tool_to_dict(genai_tools[0])
        return next(f["name"] for f in genai_tool["function_declarations"])  # type: ignore[index]
    except ValueError:  # other TypedDict
        if is_typeddict(tool):
            return convert_to_openai_tool(cast("dict", tool))["function"]["name"]
        raise
