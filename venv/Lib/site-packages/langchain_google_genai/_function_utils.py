from __future__ import annotations

import collections
import importlib
import logging
from collections.abc import Callable, Sequence
from typing import (
    Any,
    Literal,
    TypedDict,
    cast,
)

from google.genai import types
from langchain_core.tools import BaseTool
from langchain_core.tools import tool as callable_as_lc_tool
from langchain_core.utils.function_calling import (
    FunctionDescription,
    convert_to_openai_tool,
)
from langchain_core.utils.json_schema import dereference_refs
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1
from typing_extensions import NotRequired

logger = logging.getLogger(__name__)


TYPE_ENUM = {
    "string": types.Type.STRING,
    "number": types.Type.NUMBER,
    "integer": types.Type.INTEGER,
    "boolean": types.Type.BOOLEAN,
    "array": types.Type.ARRAY,
    "object": types.Type.OBJECT,
    "null": None,
}

# Note: For google.genai, we'll use a simplified approach for allowed schema fields
# since the new library doesn't expose protobuf fields in the same way
_ALLOWED_SCHEMA_FIELDS = [
    "type",
    "type_",
    "description",
    "enum",
    "format",
    "items",
    "properties",
    "required",
    "nullable",
    "anyOf",
    "default",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "pattern",
    "minItems",
    "maxItems",
    "title",
]
_ALLOWED_SCHEMA_FIELDS_SET = set(_ALLOWED_SCHEMA_FIELDS)


# Info: This is a FunctionDeclaration(=fc).
_FunctionDeclarationLike = (
    BaseTool | type[BaseModel] | types.FunctionDeclaration | Callable | dict[str, Any]
)
_GoogleSearchRetrievalLike = types.GoogleSearchRetrieval | dict[str, Any]

_GoogleSearchLike = types.GoogleSearch | dict[str, Any]
_GoogleMapsLike = types.GoogleMaps | dict[str, Any]
_CodeExecutionLike = types.ToolCodeExecution | dict[str, Any]
_UrlContextLike = types.UrlContext | dict[str, Any]
_ComputerUseLike = types.ComputerUse | dict[str, Any]


class _ToolDict(TypedDict):
    function_declarations: Sequence[_FunctionDeclarationLike]
    google_search_retrieval: _GoogleSearchRetrievalLike | None
    google_search: NotRequired[_GoogleSearchLike]
    google_maps: NotRequired[_GoogleMapsLike]
    code_execution: NotRequired[_CodeExecutionLike]
    url_context: NotRequired[_UrlContextLike]
    computer_use: NotRequired[_ComputerUseLike]


# Info: This means one tool=Sequence of FunctionDeclaration
# The dict should be Tool like. {"function_declarations": [ { "name": ...}.
# OpenAI like dict is not be accepted. {{'type': 'function', 'function': {'name': ...}
_ToolType = types.Tool | _ToolDict | _FunctionDeclarationLike
_ToolsType = Sequence[_ToolType]


def _format_json_schema_to_gapic(schema: dict[str, Any]) -> dict[str, Any]:
    converted_schema: dict[str, Any] = {}
    for key, value in schema.items():
        if key == "definitions":
            continue
        if key == "items":
            if value is not None:
                converted_schema["items"] = _format_json_schema_to_gapic(value)
        elif key == "properties":
            converted_schema["properties"] = _get_properties_from_schema(value)
            continue
        elif key == "allOf":
            if len(value) > 1:
                logger.warning(
                    "Only first value for 'allOf' key is supported. "
                    f"Got {len(value)}, ignoring other than first value!"
                )
            return _format_json_schema_to_gapic(value[0])
        elif key in ["type", "type_"]:
            if isinstance(value, dict):
                converted_schema["type"] = value["_value_"]
            elif isinstance(value, str):
                converted_schema["type"] = value
            else:
                msg = f"Invalid type: {value}"
                raise ValueError(msg)
        elif key not in _ALLOWED_SCHEMA_FIELDS_SET:
            logger.warning(f"Key '{key}' is not supported in schema, ignoring")
        else:
            converted_schema[key] = value
    return converted_schema


def _dict_to_genai_schema(
    schema: dict[str, Any],
    is_property: bool = False,
    is_any_of_item: bool = False,
) -> types.Schema | None:
    if schema:
        dereferenced_schema = dereference_refs(schema)
        formatted_schema = _format_json_schema_to_gapic(dereferenced_schema)
        # Convert the formatted schema to google.genai.types.Schema
        schema_dict = {}
        # Set type if present
        # Note: Don't set type when anyOf is present, as Gemini requires
        # that when any_of is used, it must be the only field set
        if "type" in formatted_schema and "anyOf" not in formatted_schema:
            type_obj = formatted_schema["type"]
            if isinstance(type_obj, dict):
                type_value = type_obj["_value_"]
            elif isinstance(type_obj, str):
                type_value = type_obj
            else:
                msg = f"Invalid type: {type_obj}"
                raise ValueError(msg)
            schema_dict["type"] = types.Type(type_value)
        if "description" in formatted_schema:
            schema_dict["description"] = formatted_schema["description"]
        # Include title for non-properties and for anyOf items
        # (to identify alternatives)
        if "title" in formatted_schema and (not is_property or is_any_of_item):
            schema_dict["title"] = formatted_schema["title"]
        if "properties" in formatted_schema:
            # Recursively process each property
            properties_dict = {}
            for prop_name, prop_schema in formatted_schema["properties"].items():
                properties_dict[prop_name] = _dict_to_genai_schema(
                    prop_schema, is_property=True
                )
            schema_dict["properties"] = properties_dict  # type: ignore[assignment]
        # Set required field for all schemas
        if "required" in formatted_schema and formatted_schema["required"] is not None:
            schema_dict["required"] = formatted_schema["required"]
        elif not is_property:
            # For backward compatibility, set empty list for non-property schemas
            empty_required: list[str] = []
            schema_dict["required"] = empty_required  # type: ignore[assignment]
        if "items" in formatted_schema:
            # Recursively process items schema
            schema_dict["items"] = _dict_to_genai_schema(
                formatted_schema["items"], is_property=True
            )  # type: ignore[assignment]
        if "enum" in formatted_schema:
            schema_dict["enum"] = formatted_schema["enum"]
        if "nullable" in formatted_schema:
            schema_dict["nullable"] = formatted_schema["nullable"]
        if "anyOf" in formatted_schema:
            # Convert anyOf list to list of Schema objects
            any_of_schemas = []
            for any_of_item in formatted_schema["anyOf"]:
                any_of_schema = _dict_to_genai_schema(
                    any_of_item, is_property=True, is_any_of_item=True
                )
                if any_of_schema:
                    any_of_schemas.append(any_of_schema)
            schema_dict["any_of"] = any_of_schemas  # type: ignore[assignment]
        return types.Schema.model_validate(schema_dict)
    return None


def _format_dict_to_function_declaration(
    tool: FunctionDescription | dict[str, Any],
) -> types.FunctionDeclaration:
    name = tool.get("name") or tool.get("title") or "MISSING_NAME"
    description = tool.get("description") or None
    parameters = _dict_to_genai_schema(tool.get("parameters", {}))
    return types.FunctionDeclaration(
        name=str(name),
        description=description,
        parameters=parameters,
    )


# Info: gapicTool means function_declarations and other tool types
def convert_to_genai_function_declarations(
    tools: _ToolsType,
) -> list[types.Tool]:
    """Convert tools to google-genai `Tool` objects.

    Each special tool type (`google_search`, `google_maps`, `url_context`, etc.) must
    be in its own Tool object due to protobuf oneof constraints.
    """
    if not isinstance(tools, collections.abc.Sequence):
        logger.warning(
            "convert_to_genai_function_declarations expects a Sequence "
            "and not a single tool."
        )
        tools = [tools]

    result_tools: list[types.Tool] = []
    function_declarations: list[types.FunctionDeclaration] = []

    # Special tool types that must be in separate Tool objects
    special_tool_types = [
        "google_search_retrieval",
        "google_search",
        "google_maps",
        "code_execution",
        "url_context",
        "computer_use",
    ]

    for tool in tools:
        if isinstance(tool, types.Tool):
            # Already a Tool object, add it directly
            result_tools.append(tool)
        elif isinstance(tool, dict):
            # Check if this is a special tool type dict
            # Only count keys that have non-None values
            special_keys = [
                k for k in special_tool_types if k in tool and tool.get(k) is not None
            ]

            if len(special_keys) > 1:
                msg = (
                    f"A single tool dict cannot have multiple special tool types. "
                    f"Found: {special_keys}. Each special tool type must be in a "
                    f"separate dict or Tool object."
                )
                raise ValueError(msg)

            if special_keys:
                # This is a special tool type - create a separate Tool for it
                special_key = special_keys[0]
                tool = cast("_ToolDict", tool)

                if special_key == "google_search_retrieval":
                    if isinstance(tool["google_search_retrieval"], dict):
                        tool_obj = types.Tool(
                            google_search_retrieval=types.GoogleSearchRetrieval(
                                **tool["google_search_retrieval"]
                            )
                        )
                    else:
                        tool_obj = types.Tool(
                            google_search_retrieval=tool["google_search_retrieval"]
                        )
                elif special_key == "google_search":
                    if isinstance(tool["google_search"], dict):
                        tool_obj = types.Tool(
                            google_search=types.GoogleSearch(**tool["google_search"])
                        )
                    else:
                        tool_obj = types.Tool(google_search=tool["google_search"])
                elif special_key == "google_maps":
                    if isinstance(tool["google_maps"], dict):
                        tool_obj = types.Tool(
                            google_maps=types.GoogleMaps(**tool["google_maps"])
                        )
                    else:
                        tool_obj = types.Tool(google_maps=tool["google_maps"])
                elif special_key == "code_execution":
                    if isinstance(tool["code_execution"], dict):
                        tool_obj = types.Tool(
                            code_execution=types.ToolCodeExecution(
                                **tool["code_execution"]
                            )
                        )
                    else:
                        tool_obj = types.Tool(code_execution=tool["code_execution"])
                elif special_key == "url_context":
                    if isinstance(tool["url_context"], dict):
                        tool_obj = types.Tool(
                            url_context=types.UrlContext(**tool["url_context"])
                        )
                    else:
                        tool_obj = types.Tool(url_context=tool["url_context"])
                elif special_key == "computer_use":
                    if isinstance(tool["computer_use"], dict):
                        # Handle enum conversion - extract string values from
                        # Environment enums
                        computer_use_config = dict(tool["computer_use"])
                        if "environment" in computer_use_config:
                            env = computer_use_config["environment"]
                            # Handle serialized enum (dict with _value_ key)
                            if isinstance(env, dict) and "_value_" in env:
                                computer_use_config["environment"] = env["_value_"]
                            # Handle enum instance
                            elif hasattr(env, "value"):
                                computer_use_config["environment"] = env.value
                        tool_obj = types.Tool(
                            computer_use=types.ComputerUse(**computer_use_config)
                        )
                    else:
                        tool_obj = types.Tool(computer_use=tool["computer_use"])

                result_tools.append(tool_obj)
            elif (
                "function_declarations" in tool
                and tool["function_declarations"] is not None
            ):
                # Has function_declarations - add to our collection
                tool = cast("_ToolDict", tool)
                tool_function_declarations = tool["function_declarations"]
                if tool_function_declarations is not None and not isinstance(
                    tool_function_declarations, collections.abc.Sequence
                ):
                    msg = (
                        "function_declarations should be a list, "
                        f"got '{type(tool_function_declarations)}'"
                    )
                    raise ValueError(msg)
                if tool_function_declarations:
                    fds = [
                        _format_to_genai_function_declaration(fd)
                        for fd in tool_function_declarations
                    ]
                    function_declarations.extend(fds)
            else:
                # Regular function declaration dict
                fd = _format_to_genai_function_declaration(tool)  # type: ignore[arg-type]
                function_declarations.append(fd)
        else:
            # Other tool type - convert to function declaration
            fd = _format_to_genai_function_declaration(tool)
            function_declarations.append(fd)

    # If we have function_declarations, create a Tool for them
    if function_declarations:
        result_tools.append(types.Tool(function_declarations=function_declarations))

    # Validate that we don't have multiple google_search_retrieval tools
    google_search_retrieval_count = sum(
        1
        for tool in result_tools
        if hasattr(tool, "google_search_retrieval") and tool.google_search_retrieval
    )
    if google_search_retrieval_count > 1:
        msg = (
            "Providing multiple google_search_retrieval tools is not supported. "
            "Only one google_search_retrieval tool can be used at a time."
        )
        raise ValueError(msg)

    return result_tools


def tool_to_dict(tool: types.Tool) -> _ToolDict:
    def _traverse_values(raw: Any) -> Any:
        if isinstance(raw, list):
            return [_traverse_values(v) for v in raw]
        if isinstance(raw, dict):
            return {k: _traverse_values(v) for k, v in raw.items()}
        if hasattr(raw, "__dict__"):
            return _traverse_values(raw.__dict__)
        return raw

    if hasattr(tool, "model_dump"):
        raw_result = tool.model_dump()
    else:
        raw_result = tool.__dict__

    return _traverse_values(raw_result)


def _format_to_genai_function_declaration(
    tool: _FunctionDeclarationLike,
) -> types.FunctionDeclaration:
    if isinstance(tool, BaseTool):
        return _format_base_tool_to_function_declaration(tool)
    if isinstance(tool, type) and is_basemodel_subclass_safe(tool):
        return _convert_pydantic_to_genai_function(tool)
    if isinstance(tool, dict):
        if all(k in tool for k in ("type", "function")) and tool["type"] == "function":
            function = tool["function"]
        elif (
            all(k in tool for k in ("name", "description")) and "parameters" not in tool
        ):
            function = cast("dict", tool)
        elif "parameters" in tool and tool["parameters"].get("properties"):
            function = convert_to_openai_tool(cast("dict", tool))["function"]
        else:
            function = cast("dict", tool)
        function["parameters"] = function.get("parameters") or {}
        # Empty 'properties' field not supported.
        if not function["parameters"].get("properties"):
            function["parameters"] = {}
        return _format_dict_to_function_declaration(
            cast("FunctionDescription", function)
        )
    if callable(tool):
        return _format_base_tool_to_function_declaration(callable_as_lc_tool()(tool))
    msg = f"Unsupported tool type {tool}"
    raise ValueError(msg)


def _format_base_tool_to_function_declaration(
    tool: BaseTool,
) -> types.FunctionDeclaration:
    if not tool.args_schema:
        return types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "__arg1": types.Schema(type=types.Type.STRING),
                },
                required=["__arg1"],
            ),
        )

    if isinstance(tool.args_schema, dict):
        schema = tool.args_schema
    elif isinstance(tool.args_schema, type) and issubclass(tool.args_schema, BaseModel):
        schema = tool.args_schema.model_json_schema()
    elif isinstance(tool.args_schema, type) and issubclass(
        tool.args_schema, BaseModelV1
    ):
        schema = tool.args_schema.schema()
    else:
        msg = (
            "args_schema must be a Pydantic BaseModel or JSON schema, "
            f"got {tool.args_schema}."
        )
        raise NotImplementedError(msg)
    parameters = _dict_to_genai_schema(schema)

    return types.FunctionDeclaration(
        name=tool.name or schema.get("title"),
        description=tool.description or schema.get("description"),
        parameters=parameters,
    )


def _convert_pydantic_to_genai_function(
    pydantic_model: type[BaseModel],
    tool_name: str | None = None,
    tool_description: str | None = None,
) -> types.FunctionDeclaration:
    if issubclass(pydantic_model, BaseModel):
        schema = pydantic_model.model_json_schema()
    elif issubclass(pydantic_model, BaseModelV1):
        schema = pydantic_model.schema()
    else:
        msg = f"pydantic_model must be a Pydantic BaseModel, got {pydantic_model}"
        raise NotImplementedError(msg)
    schema.pop("definitions", None)

    # Convert to google.genai Schema format - remove title/description for parameters
    schema_for_params = schema.copy()
    schema_for_params.pop("title", None)
    schema_for_params.pop("description", None)
    parameters = _dict_to_genai_schema(schema_for_params)
    return types.FunctionDeclaration(
        name=tool_name or schema.get("title"),
        description=tool_description or schema.get("description"),
        parameters=parameters,
    )


def _get_properties_from_schema_any(schema: Any) -> dict[str, Any]:
    if isinstance(schema, dict):
        return _get_properties_from_schema(schema)
    return {}


def _get_properties_from_schema(schema: dict) -> dict[str, Any]:
    properties: dict[str, dict[str, str | int | dict | list]] = {}
    for k, v in schema.items():
        if not isinstance(k, str):
            logger.warning(f"Key '{k}' is not supported in schema, type={type(k)}")
            continue
        if not isinstance(v, dict):
            logger.warning(f"Value '{v}' is not supported in schema, ignoring v={v}")
            continue
        properties_item: dict[str, str | int | dict | list] = {}

        # Preserve description and other schema properties before manipulation
        original_description = v.get("description")
        original_enum = v.get("enum")
        original_items = v.get("items")

        if v.get("anyOf") and all(
            anyOf_type.get("type") != "null" for anyOf_type in v.get("anyOf", [])
        ):
            properties_item["anyOf"] = [
                _format_json_schema_to_gapic(anyOf_type)
                for anyOf_type in v.get("anyOf", [])
            ]
            # Don't set type_ when anyOf is present as they're mutually exclusive
        elif v.get("type") or v.get("anyOf") or v.get("type_"):
            item_type_ = _get_type_from_schema(v)
            properties_item["type"] = item_type_
            if _is_nullable_schema(v):
                properties_item["nullable"] = True

            # Replace `v` with chosen definition for array / object json types
            any_of_types = v.get("anyOf")
            if any_of_types and item_type_ in [types.Type.ARRAY, types.Type.OBJECT]:
                json_type_ = "array" if item_type_ == types.Type.ARRAY else "object"
                # Use Index -1 for consistency with `_get_nullable_type_from_schema`
                filtered_schema = [
                    val for val in any_of_types if val.get("type") == json_type_
                ][-1]
                # Merge filtered schema with original properties to preserve enum/items
                v = filtered_schema.copy()
                if original_enum and not v.get("enum"):
                    v["enum"] = original_enum
                if original_items and not v.get("items"):
                    v["items"] = original_items
            elif any_of_types:
                # For other types (like strings with enums), find the non-null schema
                # and preserve enum/items from the original anyOf structure
                non_null_schemas = [
                    val for val in any_of_types if val.get("type") != "null"
                ]
                if non_null_schemas:
                    filtered_schema = non_null_schemas[-1]
                    v = filtered_schema.copy()
                    if original_enum and not v.get("enum"):
                        v["enum"] = original_enum
                    if original_items and not v.get("items"):
                        v["items"] = original_items

        if v.get("enum"):
            properties_item["enum"] = v["enum"]

        # Prefer description from the filtered schema, fall back to original
        description = v.get("description") or original_description
        if description and isinstance(description, str):
            properties_item["description"] = description

        if properties_item.get("type") == types.Type.ARRAY and v.get("items"):
            properties_item["items"] = _get_items_from_schema_any(v.get("items"))

        if properties_item.get("type") == types.Type.OBJECT:
            if (
                v.get("anyOf")
                and isinstance(v["anyOf"], list)
                and isinstance(v["anyOf"][0], dict)
            ):
                v = v["anyOf"][0]
            v_properties = v.get("properties")
            if v_properties:
                properties_item["properties"] = _get_properties_from_schema_any(
                    v_properties
                )
                if isinstance(v_properties, dict):
                    properties_item["required"] = [
                        k for k, v in v_properties.items() if "default" not in v
                    ]
            elif not v.get("additionalProperties"):
                # Only provide dummy type for object without properties AND without
                # additionalProperties
                properties_item["type"] = types.Type.STRING

        if k == "title" and "description" not in properties_item:
            properties_item["description"] = k + " is " + str(v)

        properties[k] = properties_item

    return properties


def _get_items_from_schema_any(schema: Any) -> dict[str, Any]:
    if isinstance(schema, (dict, list, str)):
        return _get_items_from_schema(schema)
    return {}


def _get_items_from_schema(schema: dict | list | str) -> dict[str, Any]:
    items: dict = {}
    if isinstance(schema, list):
        for i, v in enumerate(schema):
            items[f"item{i}"] = _get_properties_from_schema_any(v)
    elif isinstance(schema, dict):
        items["type"] = _get_type_from_schema(schema)
        if items["type"] == types.Type.OBJECT and "properties" in schema:
            items["properties"] = _get_properties_from_schema_any(schema["properties"])
        if items["type"] == types.Type.ARRAY and "items" in schema:
            items["items"] = _format_json_schema_to_gapic(schema["items"])
        if "title" in schema or "description" in schema:
            items["description"] = schema.get("description") or schema.get("title")
        if "enum" in schema:
            items["enum"] = schema["enum"]
        if _is_nullable_schema(schema):
            items["nullable"] = True
        if "required" in schema:
            items["required"] = schema["required"]
        if "enum" in schema:
            items["enum"] = schema["enum"]
    else:
        # str
        items["type"] = _get_type_from_schema({"type": schema})
        if _is_nullable_schema({"type": schema}):
            items["nullable"] = True

    return items


def _get_type_from_schema(schema: dict[str, Any]) -> types.Type:
    type_ = _get_nullable_type_from_schema(schema)
    return type_ if type_ is not None else types.Type.STRING


def _get_nullable_type_from_schema(schema: dict[str, Any]) -> types.Type | None:
    if "anyOf" in schema:
        schema_types = [
            _get_nullable_type_from_schema(sub_schema) for sub_schema in schema["anyOf"]
        ]
        schema_types = [t for t in schema_types if t is not None]  # Remove None values
        # TODO: update FunctionDeclaration and pass all types?
        if schema_types:
            return schema_types[-1]
    elif "type" in schema or "type_" in schema:
        type_ = schema["type"] if "type" in schema else schema["type_"]
        if isinstance(type_, types.Type):
            return type_
        if isinstance(type_, int):
            msg = f"Invalid type, int not supported: {type_}"
            raise ValueError(msg)
        if isinstance(type_, dict):
            return types.Type(type_["_value_"])
        if isinstance(type_, str):
            if type_ == "null":
                return None
            return types.Type(type_)
        return None
    else:
        pass
    return None  # No valid types found


def _is_nullable_schema(schema: dict[str, Any]) -> bool:
    if "anyOf" in schema:
        schema_types = [
            _get_nullable_type_from_schema(sub_schema) for sub_schema in schema["anyOf"]
        ]
        return any(t is None for t in schema_types)
    if "type" in schema or "type_" in schema:
        type_ = schema["type"] if "type" in schema else schema["type_"]
        if isinstance(type_, types.Type):
            return False
        if isinstance(type_, int):
            # Handle integer type values (from tool_to_dict serialization)
            # Integer types are never null (except for NULL type handled separately)
            return type_ == 7  # 7 corresponds to NULL type
    else:
        pass
    return False


_ToolChoiceType = (
    Literal["auto", "none", "any", "required", True] | dict | list[str] | str
)


def _tool_choice_to_tool_config(
    tool_choice: _ToolChoiceType,
    all_names: list[str],
) -> types.ToolConfig:
    """Convert `tool_choice` to Google's `ToolConfig` format.

    Maps LangChain/OpenAI-style `tool_choice` values to Google's function calling modes:

    - `'auto'` -> `AUTO`: Model decides whether to call functions or generate text
    - `'any'` / `'required'` / `True` -> `ANY`: Model must call one of the provided
        functions.

        Both `'any'` and `'required'` map to the same Google API mode for compatibility
        (OpenAI uses `'required'`)
    - `'none'` -> `NONE`: Model cannot call functions
    - `'function_name'` -> `ANY` with specific function: Model must call the named
        function
    - `['fn1', 'fn2']` -> `ANY` with specific functions: Model must call one of the
        listed functions

    Args:
        tool_choice: The tool choice specification.
        all_names: List of all available function names.

    Returns:
        `ToolConfig` object for the Google API.
    """
    allowed_function_names: list[str] | None = None
    if tool_choice is True or tool_choice == "any":
        mode = "ANY"
        allowed_function_names = all_names
    elif tool_choice == "required":
        # OpenAI-compatible alias for "any"
        mode = "ANY"
        allowed_function_names = all_names
    elif tool_choice == "auto":
        mode = "AUTO"
    elif tool_choice == "none":
        mode = "NONE"
    elif isinstance(tool_choice, str):
        mode = "ANY"
        allowed_function_names = [tool_choice]
    elif isinstance(tool_choice, list):
        mode = "ANY"
        allowed_function_names = tool_choice
    elif isinstance(tool_choice, dict):
        if "mode" in tool_choice:
            mode = tool_choice["mode"]
            allowed_function_names = tool_choice.get("allowed_function_names")
        elif "function_calling_config" in tool_choice:
            mode = tool_choice["function_calling_config"]["mode"]
            allowed_function_names = tool_choice["function_calling_config"].get(
                "allowed_function_names"
            )
        else:
            msg = (
                f"Unrecognized tool choice format:\n\n{tool_choice=}\n\nShould match "
                f"Google GenerativeAI ToolConfig or FunctionCallingConfig format."
            )
            raise ValueError(msg)
    else:
        msg = f"Unrecognized tool choice format:\n\n{tool_choice=}"
        raise ValueError(msg)
    return types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode=types.FunctionCallingConfigMode(mode),
            allowed_function_names=allowed_function_names,
        )
    )


def is_basemodel_subclass_safe(tool: type) -> bool:
    if safe_import("langchain_core.utils.pydantic", "is_basemodel_subclass"):
        from langchain_core.utils.pydantic import (
            is_basemodel_subclass,
        )

        return is_basemodel_subclass(tool)
    return issubclass(tool, BaseModel)


def safe_import(module_name: str, attribute_name: str = "") -> bool:
    try:
        module = importlib.import_module(module_name)
        if attribute_name:
            return hasattr(module, attribute_name)
        return True
    except ImportError:
        return False


def _get_def_key_from_schema_path(schema_path: str) -> str:
    error_message = f"Malformed schema reference path {schema_path}"

    if not isinstance(schema_path, str) or not schema_path.startswith("#/$defs/"):
        raise ValueError(error_message)

    # Schema has to have only one extra level.
    parts = schema_path.split("/")
    if len(parts) != 3:
        raise ValueError(error_message)

    return parts[-1]


# Backward compatibility alias
_dict_to_gapic_schema = _dict_to_genai_schema
