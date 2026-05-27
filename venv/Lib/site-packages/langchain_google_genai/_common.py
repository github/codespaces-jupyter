import os
from importlib import metadata
from typing import Any

from langchain_core.utils import from_env, secret_from_env
from pydantic import BaseModel, Field, SecretStr, model_validator
from typing_extensions import Self

from langchain_google_genai._enums import (
    HarmBlockThreshold,
    HarmCategory,
    MediaResolution,
    Modality,
)

_TELEMETRY_TAG = "remote_reasoning_engine"
_TELEMETRY_ENV_VARIABLE_NAME = "GOOGLE_CLOUD_AGENT_ENGINE_ID"

# Cache package version at module import time to avoid blocking I/O in async contexts
try:
    LC_GOOGLE_GENAI_VERSION = metadata.version("langchain-google-genai")
except metadata.PackageNotFoundError:
    LC_GOOGLE_GENAI_VERSION = "0.0.0"


class GoogleGenerativeAIError(Exception):
    """Custom exception class for errors associated with the `Google GenAI` API."""


SafetySettingDict = dict[HarmCategory, HarmBlockThreshold]


class _BaseGoogleGenerativeAI(BaseModel):
    """Base class for Google Generative AI LLMs.

    !!! version-added "Vertex AI Platform Support"

        Added in `langchain-google-genai` 4.0.0.

        `ChatGoogleGenerativeAI` and `GoogleGenerativeAIEmbeddings` now supports both
        the **Gemini Developer API** and **Vertex AI Platform** as backend options.

        The backend is selected **automatically** based on your configuration, or can be
        set explicitly using the `vertexai` parameter.

    **Automatic backend detection** (when `vertexai=None` / unspecified):

    1. If `GOOGLE_GENAI_USE_VERTEXAI` env var is set, uses that value
    2. If `credentials` parameter is provided, uses Vertex AI
    3. If `project` parameter is provided, uses Vertex AI
    4. Otherwise, uses Gemini Developer API

    **Authentication options:**

    | Backend | Authentication Methods |
    |---------|------------------------|
    | **Gemini Developer API** | API key (via `api_key` param or `GOOGLE_API_KEY`/`GEMINI_API_KEY` env var) |
    | **Vertex AI** | API key, service account credentials, or [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) |

    !!! tip "Quick Start"

        **Gemini Developer API** (simplest):

        ```python
        # Either set GOOGLE_API_KEY env var or pass api_key directly
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key="MY_API_KEY")
        ```

        **Vertex AI with API key**:

        ```bash
        export GEMINI_API_KEY='your-api-key'
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT='your-project-id'
        ```

        ```python
        # Automatically uses Vertex AI with API key
        llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")
        ```

        Or programmatically:

        ```python
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            api_key="your-api-key",
            project="your-project-id",
            vertexai=True,  # Explicitly use Vertex AI
        )
        ```

        **Vertex AI with credentials**:

        ```python
        # Ensure ADC is configured: gcloud auth application-default login
        # Either set GOOGLE_CLOUD_PROJECT env var or pass project directly
        # Location defaults to global or can be set via GOOGLE_CLOUD_LOCATION
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            project="my-project",
            # location="global",
        )
        ```

    ## Environment variables

    | Variable | Purpose | Backend |
    |----------|---------|---------|
    | `GOOGLE_API_KEY` | API key (primary) | Both (see `GOOGLE_GENAI_USE_VERTEXAI`) |
    | `GEMINI_API_KEY` | API key (fallback) | Both (see `GOOGLE_GENAI_USE_VERTEXAI`) |
    | `GOOGLE_GENAI_USE_VERTEXAI` | Force Vertex AI backend (`true`/`false`) | Vertex AI |
    | `GOOGLE_CLOUD_PROJECT` | GCP project ID | Vertex AI |
    | `GOOGLE_CLOUD_LOCATION` | GCP region (default: `global`) | Vertex AI |
    | `HTTPS_PROXY` | HTTP/HTTPS proxy URL | Both |
    | `SSL_CERT_FILE` | Custom SSL certificate file | Both |

    `GOOGLE_API_KEY` is checked first for backwards compatibility. (`GEMINI_API_KEY` was
    introduced later to better reflect the API's branding.)

    ## Proxy configuration

    Set these before initializing:

    ```bash
    export HTTPS_PROXY='http://username:password@proxy_uri:port'
    export SSL_CERT_FILE='path/to/cert.pem'  # Optional: custom SSL certificate
    ```

    For SOCKS5 proxies or advanced proxy configuration, use the `client_args` parameter:

    ```python
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        client_args={"proxy": "socks5://user:pass@host:port"},
    )
    ```
    """  # noqa: E501

    # This class is used by ChatGoogleGenerativeAI and GoogleGenerativeAI (LLM)

    # --- Client params ---

    google_api_key: SecretStr | None = Field(
        alias="api_key",
        default_factory=secret_from_env(
            ["GOOGLE_API_KEY", "GEMINI_API_KEY"], default=None
        ),
    )
    """API key for authentication.

    If not specified, will check the env vars `GOOGLE_API_KEY` and `GEMINI_API_KEY` with
    precedence given to `GOOGLE_API_KEY`.

    - **Gemini Developer API**: API key is required (default when no `project` is set)
    - **Vertex AI**: API key is optional (set `vertexai=True` or provide `project`)
        - If provided, uses API key for authentication
        - If not provided, uses [Application Default Credentials (ADC)](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
            or `credentials` parameter

    !!! tip "Vertex AI with API key"

        You can now use Vertex AI with API key authentication instead of service account
        credentials. Set `GOOGLE_GENAI_USE_VERTEXAI=true` or `vertexai=True` along with
        your API key and project.
    """

    credentials: Any = None
    """Custom credentials for Vertex AI authentication.

    When provided, forces Vertex AI backend (regardless of API key presence in
    `google_api_key`/`api_key`).

    Accepts a [`google.auth.credentials.Credentials`](https://googleapis.dev/python/google-auth/latest/reference/google.auth.credentials.html#google.auth.credentials.Credentials)
    object.

    If omitted and no API key is found, the SDK uses
    [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials).

    !!! example "Service account credentials"

        ```python
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            "path/to/service-account.json",
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            credentials=credentials,
            project="my-project-id",
        )
        ```
    """

    vertexai: bool | None = Field(default=None)
    """Whether to use Vertex AI backend.

    If `None` (default), backend is automatically determined as follows:

    1. If the `GOOGLE_GENAI_USE_VERTEXAI` env var is set, uses Vertex AI
    2. If the [`credentials`][langchain_google_genai.ChatGoogleGenerativeAI.credentials]
        parameter is provided, uses Vertex AI
    3. If the [`project`][langchain_google_genai.ChatGoogleGenerativeAI.project]
        parameter is provided, uses Vertex AI
    4. Otherwise, uses Gemini Developer API

    Set explicitly to `True` or `False` to override auto-detection.

    !!! tip "Vertex AI with API key"

        You can use Vertex AI with API key authentication by setting:

        ```bash
        export GEMINI_API_KEY='your-api-key'
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT='your-project-id'
        ```

        Or programmatically:

        ```python
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            api_key="your-api-key",
            project="your-project-id",
            vertexai=True,
        )
        ```

        This allows for simpler authentication compared to service account JSON files.
    """

    project: str | None = Field(default=None)
    """Google Cloud project ID (**Vertex AI only**).

    Required when using Vertex AI.

    Falls back to `GOOGLE_CLOUD_PROJECT` env var if not provided.
    """

    location: str | None = Field(
        default_factory=from_env("GOOGLE_CLOUD_LOCATION", default=None)
    )
    """Google Cloud region (**Vertex AI only**).

    If not provided, falls back to the `GOOGLE_CLOUD_LOCATION` env var, then
    `'global'`.
    """

    base_url: str | dict | None = Field(default=None, alias="client_options")
    """Custom base URL for the API client.

    If not provided, defaults depend on the API being used:

    - **Gemini Developer API** (
        [`api_key`][langchain_google_genai.ChatGoogleGenerativeAI.google_api_key]/
        [`google_api_key`][langchain_google_genai.ChatGoogleGenerativeAI.google_api_key]
        ): `https://generativelanguage.googleapis.com/`
    - **Vertex AI** (
        [`credentials`][langchain_google_genai.ChatGoogleGenerativeAI.credentials]):
        `https://{location}-aiplatform.googleapis.com/`

    !!! note "Backwards compatibility"

        Typed to accept `dict` to support backwards compatibility for the (now removed)
        `client_options` param.

        If a `dict` is passed in, it will **only** extract the `'api_endpoint'` key.
    """

    additional_headers: dict[str, str] | None = Field(
        default=None,
    )
    """Additional HTTP headers to include in API requests.

    Passed as `headers` to `HttpOptions` when creating the client.

    !!! example

        ```python
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            additional_headers={
                "X-Custom-Header": "value",
            },
        )
        ```
    """

    client_args: dict[str, Any] | None = Field(default=None)
    """Additional arguments to pass to the underlying HTTP client.

    Applied to both sync and async clients.

    !!! example "SOCKS5 proxy"

        ```python
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            client_args={"proxy": "socks5://user:pass@host:port"},
        )
        ```
    """

    api_version: str | None = Field(default=None)
    """Override the API version path segment in request URLs.

    By default, the underlying `google-genai` SDK currently uses `v1beta1` for
    Vertex AI and `v1beta` for the Gemini Developer API. Set this when
    targeting a proxy or gateway that expects a different API version segment
    (e.g. `'v1'`).

    !!! example "Custom API gateway"

        ```python
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            vertexai=True,
            base_url="https://my-gateway.example.com/api/gemini",
            api_version="v1",
            additional_headers={"Authorization": "Bearer <token>"},
        )
        ```
    """

    # --- Model / invocation params ---

    model: str = Field(...)
    """Model name to use."""

    temperature: float = 0.7
    """Run inference with this temperature.

    Must be within `[0.0, 2.0]`.

    !!! note "Automatic override for Gemini 3.0+ models"

        If `temperature` is not explicitly set and the model is Gemini 3.0 or later,
        it will be automatically set to `1.0` instead of the default `0.7` per the
        Google GenAI API best practices, as it can cause infinite loops, degraded
        reasoning performance, and failure on complex tasks.

    """

    top_p: float | None = None
    """Decode using nucleus sampling.

    Consider the smallest set of tokens whose probability sum is at least `top_p`.

    Must be within `[0.0, 1.0]`.
    """

    top_k: int | None = None
    """Decode using top-k sampling: consider the set of `top_k` most probable tokens.

    Must be positive.
    """

    max_output_tokens: int | None = Field(default=None, alias="max_tokens")
    """Maximum number of tokens to include in a candidate.

    Must be greater than zero.

    If unset, will use the model's default value, which varies by model.

    See [docs](https://ai.google.dev/gemini-api/docs/models) for model-specific limits.

    To constrain the number of thinking tokens to use when generating a response, see
    the `thinking_budget` parameter.
    """

    n: int = 1
    """Number of chat completions to generate for each prompt.

    Note that the API may not return the full `n` completions if duplicates are
    generated.
    """

    max_retries: int = Field(default=6, alias="retries")
    """The maximum number of retries to make when generating.

    !!! warning "Disabling retries"

        To disable retries, set `max_retries=1` (not `0`) due to a quirk in the
        underlying Google SDK. `max_retries=0` is interpreted as "use the (Google)
        default" (5 retries).

        Setting `max_retries=1` means only the initial request is made with no retries.

    !!! warning "Handling rate limits (429 errors)"

        When you exceed quota limits, the API returns a 429 error with a suggested
        `retry_delay`. The SDK's built-in retry logic ignores this value and uses fixed
        exponential backoff instead. This is a known issue in Google's SDK and an issue
        has been [raised upstream](https://github.com/googleapis/python-genai/issues/1875).
        We plan to implement proper handling once it's supported.

        If you need to respect the server's suggested retry delay, disable SDK retries
        with `max_retries=1` and implement custom retry logic:

        ```python
        import re
        import time

        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", max_retries=1)

        try:
            response = llm.invoke("Hello")
        except ChatGoogleGenerativeAIError as e:
            if "429" in str(e):
                # Parse retry_delay from error: "[retry_delay { seconds: N }]"
                match = re.search(r"retry_delay\\s*\\{\\s*seconds:\\s*(\\d+)", str(e))
                delay = int(match.group(1)) if match else 60
                time.sleep(delay)
                # Retry...
        ```
    """

    timeout: float | None = Field(default=None, alias="request_timeout")
    """The maximum number of seconds to wait for a response."""

    response_modalities: list[Modality] | None = Field(
        default=None,
    )
    """A list of modalities of the response"""

    media_resolution: MediaResolution | None = Field(
        default=None,
    )
    """Media resolution for the input media.

    May be defined at the individual part level, allowing for mixed-resolution requests
    (e.g., images and videos of different resolutions in the same request).

    May be `'low'`, `'medium'`, or `'high'`.

    Can be set either per-part or globally for all media inputs in the request. To set
    globally, set in the `generation_config`.

    !!! warning "Model compatibility"

        Setting per-part media resolution requests to Gemini 2.5 models is not
        supported.
    """

    image_config: dict[str, Any] | None = Field(
        default=None,
    )
    """Configuration for image generation.

    Provides control over generated image dimensions and quality for image generation
    models.

    See [`genai.types.ImageConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.ImageConfig)
    for a list of supported fields and their values.

    !!! note "Model compatibility"

        This parameter only applies to image generation models. Supported parameters
        vary by model and backend (Gemini Developer API and Vertex AI each support
        different subsets of parameters and models).

    See [the docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#image-generation)
    for more details and examples.
    """

    thinking_budget: int | None = Field(
        default=None,
    )
    """Indicates the thinking budget in tokens.

    Used to disable thinking for supported models (when set to `0`) or to constrain
    the number of tokens used for thinking.

    Dynamic thinking (allowing the model to decide how many tokens to use) is
    enabled when set to `-1`.

    More information, including per-model limits, can be found in the
    [Gemini API docs](https://ai.google.dev/gemini-api/docs/thinking#set-budget).
    """

    include_thoughts: bool | None = Field(
        default=None,
    )
    """Indicates whether to include thoughts in the response.

    !!! note

        This parameter is only applicable for models that support thinking.

        This does not disable thinking; to disable thinking, set `thinking_budget` to
        `0`. for supported models. See the `thinking_budget` parameter for more details.
    """

    safety_settings: SafetySettingDict | None = None
    """Default safety settings to use for all generations.

        !!! example

            ```python
            from google.genai.types import HarmBlockThreshold, HarmCategory

            safety_settings = {
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
            ```
    """  # noqa: E501

    seed: int | None = Field(default=None)
    """Seed used in decoding for reproducible generations.

    By default, a random number is used.

    !!! note

        Using the same seed does not guarantee identical outputs, but makes them more
        deterministic. Reproducibility is "best effort" based on the model and
        infrastructure.
    """

    labels: dict[str, str] | None = Field(default=None)
    """User-defined key-value metadata for organizing and filtering billing reports.

    Attach labels to categorize API usage by team, environment, or feature.

    Can be overridden per-request via invoke kwargs.

    See: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/add-labels-to-api-calls
    """

    @model_validator(mode="after")
    def _resolve_project_from_credentials(self) -> Self:
        """Extract project from credentials if not explicitly set.

        For backward compatibility with `langchain-google-vertexai`, which extracts
        `project_id` from credentials when not explicitly provided.
        """
        if self.project is None:
            if self.credentials and hasattr(self.credentials, "project_id"):
                self.project = self.credentials.project_id
        return self

    @model_validator(mode="after")
    def _determine_backend(self) -> Self:
        """Determine which backend (Vertex AI or Gemini Developer API) to use.

        The backend is determined by the following priority:
        1. Explicit `vertexai` parameter value (if not None)
        2. `GOOGLE_GENAI_USE_VERTEXAI` environment variable
        3. Presence of `credentials` parameter (forces Vertex AI)
        4. Presence of `project` parameter (implies Vertex AI)
        5. Default to Gemini Developer API (False)

        Stores result in `_use_vertexai` attribute for use in client initialization.
        """
        use_vertexai = self.vertexai

        if use_vertexai is None:
            # Check environment variable
            env_var = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower()
            if env_var in ("true", "1", "yes"):
                use_vertexai = True
            elif env_var in ("false", "0", "no"):
                use_vertexai = False
            # Check for credentials (forces Vertex AI)
            elif self.credentials is not None:
                use_vertexai = True
            # Check for project (implies Vertex AI)
            elif self.project is not None:
                use_vertexai = True
            else:
                # Default to Gemini Developer API
                use_vertexai = False

        # Store the determined backend in a private attribute
        object.__setattr__(self, "_use_vertexai", use_vertexai)
        return self

    @property
    def lc_secrets(self) -> dict[str, str]:
        # Either could contain the API key
        return {
            "google_api_key": "GOOGLE_API_KEY",
            "gemini_api_key": "GEMINI_API_KEY",
        }

    @property
    def _identifying_params(self) -> dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
            "candidate_count": self.n,
            "image_config": self.image_config,
        }


def get_user_agent(module: str | None = None) -> tuple[str, str]:
    r"""Returns a custom user agent header.

    Args:
        module: The module for a custom user agent header.
    """
    client_library_version = (
        f"{LC_GOOGLE_GENAI_VERSION}-{module}" if module else LC_GOOGLE_GENAI_VERSION
    )
    if os.environ.get(_TELEMETRY_ENV_VARIABLE_NAME):
        client_library_version += f"+{_TELEMETRY_TAG}"
    return client_library_version, f"langchain-google-genai/{client_library_version}"
