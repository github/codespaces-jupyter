from __future__ import annotations

import typer
from typing import Annotated, Any
from gradio_client import Client
from gradio_client.client import DEFAULT_TEMP_DIR
from gradio_client.utils import traverse
import json

app = typer.Typer()


def _resolve_refs(schema: Any, defs: dict[str, Any] | None = None) -> Any:
    """Recursively resolve $ref references and remove $defs."""
    if not isinstance(schema, dict):
        if isinstance(schema, list):
            return [_resolve_refs(item, defs) for item in schema]
        return schema

    if defs is None:
        defs = schema.get("$defs", {})

    if "$ref" in schema:
        ref_path = schema["$ref"]
        ref_name = ref_path.split("/")[-1]
        if ref_name in defs:
            return _resolve_refs(defs[ref_name], defs)  # type: ignore
        return schema

    resolved = {}
    for key, value in schema.items():
        if key == "$defs":
            continue
        resolved[key] = _resolve_refs(value, defs)
    return resolved


def _is_file_schema(schema: Any) -> bool:
    """Check if a schema represents a file type (has path + meta with gradio.FileData)."""
    if not isinstance(schema, dict):
        return False
    props = schema.get("properties", {})
    if "path" not in props or "meta" not in props:
        return False
    meta = props["meta"]
    meta_props = meta.get("properties", {})
    if "_type" in meta_props:
        return meta_props["_type"].get("const") == "gradio.FileData"
    meta_default = meta.get("default", {})
    if isinstance(meta_default, dict):
        return meta_default.get("_type") == "gradio.FileData"
    return False


def _is_file_dict(d):
    return (
        isinstance(d, dict)
        and isinstance(d.get("path", None), str)
        and d.get("meta") == {"_type": "gradio.FileData"}
    )


def simplify_json_schema(schema: Any, is_input: bool = True, url_only: bool = False):
    schema = _resolve_refs(schema)
    simplifier = _make_file_simplifier(is_input, url_only)
    return traverse(
        schema,
        simplifier,
        _is_file_schema,
    )


def _make_file_simplifier(is_input: bool, url_only: bool = False):
    def _simplify(schema: Any) -> Any:
        props = schema.get("properties", {})
        if "meta" in props and "path" in props:
            if is_input:
                if url_only:
                    desc = 'Must include {"path": "url", "meta": {"_type": "gradio.FileData"}}. '
                else:
                    desc = 'Must include {"path": "<local path or url>", "meta": {"_type": "gradio.FileData"}}. '
                return {
                    "type": "filepath",
                    "description": (
                        desc
                        + "The meta key signals that the file will be uploaded to the remote server."
                    ),
                }
            else:
                if url_only:
                    return {
                        "type": "object",
                        "description": "JSON object with url key to fetch the output",
                    }
                return {
                    "type": "filepath",
                    "description": "The returned file path on disk.",
                }
        return schema

    return _simplify


def _condense_info(info: dict[str, Any], url_only: bool = False):
    condensed_info = {}
    for endpoint, data_format in info["named_endpoints"].items():
        endpoint_info = {
            "parameters": [],
            "returns": [],
            "description": data_format.get("description", ""),
        }
        for param in data_format["parameters"]:
            endpoint_info["parameters"].append(
                {
                    "name": param["parameter_name"],
                    "required": not param["parameter_has_default"],
                    "default": param["parameter_default"],
                    "type": simplify_json_schema(
                        param["type"], is_input=True, url_only=url_only
                    ),
                }
            )
        for output in data_format["returns"]:
            endpoint_info["returns"].append(
                {
                    "name": output["label"],
                    "type": simplify_json_schema(
                        output["type"], is_input=False, url_only=url_only
                    ),
                }
            )
        condensed_info[endpoint] = endpoint_info
    return condensed_info


def _delete_keys(d):
    return {k: v for k, v in d.items() if k in ["path", "meta"]}


def generate_cli_snippet(original_info):
    endpoints = {}
    for endpoint, info in original_info.items():
        params = json.dumps(
            {
                p["parameter_name"]: traverse(
                    p["parameter_default"] or p["example_input"],
                    _delete_keys,
                    _is_file_dict,
                )
                for p in info["parameters"]
            },
            indent=2,
        )
        endpoints[endpoint] = f"""
{{command}} predict {{space_id}} {endpoint} '{params}'
""".lstrip("\n")
    return endpoints


@app.command()
def info(
    space_id_or_url: Annotated[
        str,
        typer.Argument(
            help="The space id, e.g. gradio/calculator or URL of the Gradio application"
        ),
    ],
    token: Annotated[
        str | None,
        typer.Option(
            help="optional Hugging Face token to use to access private Spaces. By default, the locally saved token is used if there is one.",
        ),
    ] = None,
):
    """Fetches the expected JSON payload for all of the app's endpoints."""
    client = Client(src=space_id_or_url, token=token, verbose=False)
    original_info = client.view_api(return_format="dict", print_info=False)
    condensed_info = _condense_info(original_info)  # type: ignore
    print(json.dumps(condensed_info, indent=2))


@app.command()
def predict(
    space_id_or_url: Annotated[
        str,
        typer.Argument(
            help="The space id, e.g. gradio/calculator or URL of the Gradio application"
        ),
    ],
    endpoint: Annotated[str, typer.Argument(help="The endpoint to hit")],
    payload: Annotated[str, typer.Argument(help="The payload to send to the space")],
    download_files: Annotated[
        str,
        typer.Option(
            help="The directory where the files created by the space are downloaded to on your local machine. By default, this is the Gradio temporary directory. If False, a URL pointing to the file on the remote app will be returned instead."
        ),
    ] = DEFAULT_TEMP_DIR,
    token: Annotated[
        str | None,
        typer.Option(
            help="optional Hugging Face token to use to access private Spaces. By default, the locally saved token is used if there is one.",
        ),
    ] = None,
):
    """Sends a prediction request to a Gradio app endpoint."""
    client = Client(
        src=space_id_or_url,
        token=token,
        verbose=False,
        download_files=download_files if download_files != "False" else False,
    )
    payload = json.loads(payload)
    result = client.predict(**payload, api_name=endpoint)  # type: ignore

    original_info = client.view_api(return_format="dict", print_info=False)
    condensed_info = _condense_info(original_info)  # type: ignore
    return_names = [r["name"] for r in condensed_info[endpoint]["returns"]]

    if not isinstance(result, tuple):
        result = (result,)
    output = dict(zip(return_names, result))
    print(json.dumps(output, indent=2))
