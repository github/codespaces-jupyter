import os
import re
import string
from typing import Any

from google.genai.client import Client
from google.genai.errors import ClientError
from google.genai.types import EmbedContentConfig, HttpOptions
from langchain_core.embeddings import Embeddings
from langchain_core.utils import from_env, secret_from_env
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

from langchain_google_genai._common import (
    GoogleGenerativeAIError,
    get_user_agent,
)

_MAX_TOKENS_PER_BATCH = 20000
_DEFAULT_BATCH_SIZE = 100


class GoogleGenerativeAIEmbeddings(BaseModel, Embeddings):
    """Google Generative AI Embeddings.

    !!! warning "Text-only"

        While `gemini-embedding-2-preview` natively supports multimodal inputs
        (text, images, video, audio, and PDFs) via the Google GenAI SDK, the
        LangChain `Embeddings` interface (`embed_query` / `embed_documents`)
        currently only accepts text. For multimodal embedding use cases in the
        meantime, use the `Google GenAI SDK directly.

    Setup:
        !!! version-added "Vertex AI Platform Support"

            Added in `langchain-google-genai` 4.0.0.

            `GoogleGenerativeAIEmbeddings` now supports both the **Gemini Developer
            API** and **Vertex AI Platform** as backend options.

        **For Gemini Developer API** (simplest):

        1. Set the `GOOGLE_API_KEY` environment variable (recommended), or
        2. Pass your API key using the `google_api_key` kwarg

        **For Vertex AI**:

        Set `vertexai=True` and provide `project` (and optionally `location`).

        Example:
            ```python
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            # Gemini Developer API
            embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-2-preview"
            )
            embeddings.embed_query("What's our Q1 revenue?")

            # Vertex AI
            embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-2-preview",
                project="my-project",
                vertexai=True,
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
        | `GOOGLE_API_KEY` | API key (primary) | Both |
        | `GEMINI_API_KEY` | API key (fallback) | Both |
        | `GOOGLE_GENAI_USE_VERTEXAI` | Force Vertex AI (`true`/`false`) | Vertex AI |
        | `GOOGLE_CLOUD_PROJECT` | GCP project ID | Vertex AI |
        | `GOOGLE_CLOUD_LOCATION` | GCP region (default: `us-central1`) | Vertex AI |
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

        For SOCKS5 proxies or advanced proxy configuration, use the `client_args`
        parameter:

        ```python
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            client_args={"proxy": "socks5://user:pass@host:port"},
        )
        ```
    """

    client: Any = None
    """The Google GenAI client instance."""

    model: str = Field(...)
    """The name of the embedding model to use."""

    task_type: str | None = Field(
        default=None,
    )
    """The task type.

    Valid options include:

    * `'TASK_TYPE_UNSPECIFIED'`
    * `'RETRIEVAL_QUERY'`
    * `'RETRIEVAL_DOCUMENT'`
    * `'SEMANTIC_SIMILARITY'`
    * `'CLASSIFICATION'`
    * `'CLUSTERING'`
    * `'QUESTION_ANSWERING'`
    * `'FACT_VERIFICATION'`
    * `'CODE_RETRIEVAL_QUERY'`

    See [`TaskType`](https://ai.google.dev/api/embeddings#tasktype) for details.
    """

    google_api_key: SecretStr | None = Field(
        alias="api_key",
        default_factory=secret_from_env(
            ["GOOGLE_API_KEY", "GEMINI_API_KEY"], default=None
        ),
    )
    """The Google API key to use.

    If not provided, will check the env vars `GOOGLE_API_KEY` and `GEMINI_API_KEY`.
    """

    credentials: Any = Field(default=None, exclude=True)
    """Custom credentials for Vertex AI authentication.

    When provided, forces Vertex AI backend.

    Accepts a `google.auth.credentials.Credentials` object.
    """

    vertexai: bool | None = Field(default=None)
    """Whether to use Vertex AI backend.

    If `None` (default), backend is automatically determined:

    1. If `GOOGLE_GENAI_USE_VERTEXAI` env var is set, uses that value
    2. If `credentials` parameter is provided, uses Vertex AI
    3. If `project` parameter is provided, uses Vertex AI
    4. Otherwise, uses Gemini Developer API
    """

    project: str | None = Field(default=None)
    """Google Cloud project ID (Vertex AI only).

    Falls back to `GOOGLE_CLOUD_PROJECT` env var if not provided.
    """

    location: str | None = Field(
        default_factory=from_env("GOOGLE_CLOUD_LOCATION", default=None)
    )
    """Google Cloud region (Vertex AI only).

    Defaults to `GOOGLE_CLOUD_LOCATION` env var, then `'us-central1'`.
    """

    base_url: str | None = Field(
        default=None,
    )
    """The base URL to use for the API client."""

    additional_headers: dict[str, str] | None = Field(
        default=None,
    )
    """Additional HTTP headers to include in API requests."""

    client_args: dict[str, Any] | None = Field(default=None)
    """Additional arguments to pass to the underlying HTTP client.

    Applied to both sync and async clients.
    """

    api_version: str | None = Field(default=None)
    """Override the API version path segment in request URLs.

    By default, the underlying `google-genai` SDK currently uses `v1beta1` for
    Vertex AI and `v1beta` for the Gemini Developer API. Set this when
    targeting a proxy or gateway that expects a different API version segment
    (e.g. `'v1'`).
    """

    request_options: dict | None = Field(
        default=None,
    )
    """A dictionary of request options to pass to the Google API client.

    Example: `{'timeout': 10}`
    """

    output_dimensionality: int | None = Field(default=None)
    """Default output dimensionality for embeddings.

    If set, all embed calls use this dimension unless explicitly overridden.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def _determine_backend(self) -> Self:
        """Determine which backend (Vertex AI or Gemini Developer API) to use."""
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

    @model_validator(mode="after")
    def _initialize_client(self) -> Self:
        """Initialize the Google GenAI client."""
        if isinstance(self.google_api_key, SecretStr):
            google_api_key: str | None = self.google_api_key.get_secret_value()
        else:
            google_api_key = self.google_api_key

        # Build headers with user agent
        _, user_agent = get_user_agent("GoogleGenerativeAIEmbeddings")
        headers = {"user-agent": user_agent}
        if self.additional_headers:
            headers.update(self.additional_headers)

        http_options = HttpOptions(
            base_url=self.base_url,
            api_version=self.api_version,
            headers=headers,
            client_args=self.client_args,
            async_client_args=self.client_args,
        )

        if self._use_vertexai:  # type: ignore[attr-defined]
            # Vertex AI backend
            # Normalize model name - strip 'models/' prefix for Vertex AI
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

    @staticmethod
    def _split_by_punctuation(text: str) -> list[str]:
        """Splits a string by punctuation and whitespace characters."""
        split_by = string.punctuation + "\t\n "
        pattern = f"([{split_by}])"
        # Using re.split to split the text based on the pattern
        return [segment for segment in re.split(pattern, text) if segment]

    @staticmethod
    def _prepare_batches(texts: list[str], batch_size: int) -> list[list[str]]:
        """Splits texts in batches based on current maximum batch size and maximum
        tokens per request.
        """
        text_index = 0
        texts_len = len(texts)
        batch_token_len = 0
        batches: list[list[str]] = []
        current_batch: list[str] = []
        if texts_len == 0:
            return []
        while text_index < texts_len:
            current_text = texts[text_index]
            # Number of tokens per a text is conservatively estimated
            # as 2 times number of words, punctuation and whitespace characters.
            # Using `count_tokens` API will make batching too expensive.
            # Utilizing a tokenizer, would add a dependency that would not
            # necessarily be reused by the application using this class.
            current_text_token_cnt = (
                len(GoogleGenerativeAIEmbeddings._split_by_punctuation(current_text))
                * 2
            )
            end_of_batch = False
            if current_text_token_cnt > _MAX_TOKENS_PER_BATCH:
                # Current text is too big even for a single batch.
                # Such request will fail, but we still make a batch
                # so that the app can get the error from the API.
                if len(current_batch) > 0:
                    # Adding current batch if not empty.
                    batches.append(current_batch)
                current_batch = [current_text]
                text_index += 1
                end_of_batch = True
            elif (
                batch_token_len + current_text_token_cnt > _MAX_TOKENS_PER_BATCH
                or len(current_batch) == batch_size
            ):
                end_of_batch = True
            else:
                if text_index == texts_len - 1:
                    # Last element - even though the batch may be not big,
                    # we still need to make it.
                    end_of_batch = True
                batch_token_len += current_text_token_cnt
                current_batch.append(current_text)
                text_index += 1
            if end_of_batch:
                batches.append(current_batch)
                current_batch = []
                batch_token_len = 0
        return batches

    def _build_config(
        self,
        *,
        task_type: str | None = None,
        title: str | None = None,
        output_dimensionality: int | None = None,
    ) -> EmbedContentConfig:
        """Build an `EmbedContentConfig` for the embed request."""
        effective_task_type = task_type or self.task_type
        if effective_task_type:
            effective_task_type = effective_task_type.upper()

        return EmbedContentConfig(
            task_type=effective_task_type,
            title=title,
            output_dimensionality=output_dimensionality,
        )

    def embed_documents(
        self,
        texts: list[str],
        *,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        task_type: str | None = None,
        titles: list[str] | None = None,
        output_dimensionality: int | None = None,
    ) -> list[list[float]]:
        """Embed a list of strings.

        Google Generative AI currently sets a max batch size of 100 strings.

        Args:
            texts: The list of strings to embed.
            batch_size: Batch size of embeddings to send to the model
            task_type: [`task_type`](https://ai.google.dev/api/embeddings#tasktype)
            titles: Optional list of titles for texts provided.

                Only applicable when `TaskType` is `'RETRIEVAL_DOCUMENT'`.
            output_dimensionality: Optional reduced dimension for the output embedding.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings: list[list[float]] = []
        batch_start_index = 0

        # Use RETRIEVAL_DOCUMENT as default for documents
        effective_task_type = task_type or self.task_type or "RETRIEVAL_DOCUMENT"

        # Use instance default if no explicit value provided
        effective_dimensionality = output_dimensionality or self.output_dimensionality

        for batch in GoogleGenerativeAIEmbeddings._prepare_batches(texts, batch_size):
            # Handle titles for this batch
            if titles:
                titles_batch = titles[
                    batch_start_index : batch_start_index + len(batch)
                ]
                batch_start_index += len(batch)
            else:
                titles_batch = None

            # Build config - title only used if single text or all same title
            # The SDK handles batching internally
            # Title only applies to single-text batches
            title = None
            if titles_batch and len(titles_batch) == 1:
                title = titles_batch[0]

            config = self._build_config(
                task_type=effective_task_type,
                title=title,
                output_dimensionality=effective_dimensionality,
            )

            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=config,
                )
            except ClientError as e:
                msg = f"Error embedding content ({e.status}): {e}"
                raise GoogleGenerativeAIError(msg) from e
            except Exception as e:
                msg = f"Error embedding content: {e}"
                raise GoogleGenerativeAIError(msg) from e

            embeddings.extend([list(e.values) for e in result.embeddings])
        return embeddings

    def embed_query(
        self,
        text: str,
        *,
        task_type: str | None = None,
        title: str | None = None,
        output_dimensionality: int | None = None,
    ) -> list[float]:
        """Embed a single text.

        Args:
            text: The text to embed.
            task_type: [`task_type`](https://ai.google.dev/api/embeddings#tasktype)
            title: Optional title for the text.

                Only applicable when `TaskType` is `'RETRIEVAL_DOCUMENT'`.
            output_dimensionality: Optional reduced dimension for the output embedding.

        Returns:
            Embedding for the text.
        """
        # Use RETRIEVAL_QUERY as default for queries
        effective_task_type = task_type or self.task_type or "RETRIEVAL_QUERY"

        effective_dimensionality = output_dimensionality or self.output_dimensionality

        config = self._build_config(
            task_type=effective_task_type,
            title=title,
            output_dimensionality=effective_dimensionality,
        )

        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=config,
            )
        except ClientError as e:
            msg = f"Error embedding content ({e.status}): {e}"
            raise GoogleGenerativeAIError(msg) from e
        except Exception as e:
            msg = f"Error embedding content: {e}"
            raise GoogleGenerativeAIError(msg) from e

        # Single text returns single embedding
        return list(result.embeddings[0].values)

    async def aembed_documents(
        self,
        texts: list[str],
        *,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        task_type: str | None = None,
        titles: list[str] | None = None,
        output_dimensionality: int | None = None,
    ) -> list[list[float]]:
        """Embed a list of strings asynchronously.

        Google Generative AI currently sets a max batch size of 100 strings.

        Args:
            texts: The list of strings to embed.
            batch_size: The batch size of embeddings to send to the model
            task_type: [`task_type`](https://ai.google.dev/api/embeddings#tasktype)
            titles: Optional list of titles for texts provided.

                Only applicable when `TaskType` is `'RETRIEVAL_DOCUMENT'`.
            output_dimensionality: Optional reduced dimension for the output embedding.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings: list[list[float]] = []
        batch_start_index = 0

        # Use RETRIEVAL_DOCUMENT as default for documents
        effective_task_type = task_type or self.task_type or "RETRIEVAL_DOCUMENT"

        effective_dimensionality = output_dimensionality or self.output_dimensionality

        for batch in GoogleGenerativeAIEmbeddings._prepare_batches(texts, batch_size):
            # Handle titles for this batch
            if titles:
                titles_batch = titles[
                    batch_start_index : batch_start_index + len(batch)
                ]
                batch_start_index += len(batch)
            else:
                titles_batch = None

            # Title only applies to single-text batches
            title = None
            if titles_batch and len(titles_batch) == 1:
                title = titles_batch[0]

            config = self._build_config(
                task_type=effective_task_type,
                title=title,
                output_dimensionality=effective_dimensionality,
            )

            try:
                result = await self.client.aio.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=config,
                )
            except ClientError as e:
                msg = f"Error embedding content ({e.status}): {e}"
                raise GoogleGenerativeAIError(msg) from e
            except Exception as e:
                msg = f"Error embedding content: {e}"
                raise GoogleGenerativeAIError(msg) from e

            embeddings.extend([list(e.values) for e in result.embeddings])
        return embeddings

    async def aembed_query(
        self,
        text: str,
        *,
        task_type: str | None = None,
        title: str | None = None,
        output_dimensionality: int | None = None,
    ) -> list[float]:
        """Embed a single text asynchronously.

        Args:
            text: The text to embed.
            task_type: [`task_type`](https://ai.google.dev/api/embeddings#tasktype)
            title: Optional title for the text.

                Only applicable when `TaskType` is `'RETRIEVAL_DOCUMENT'`.
            output_dimensionality: Optional reduced dimension for the output embedding.

        Returns:
            Embedding for the text.
        """
        # Use RETRIEVAL_QUERY as default for queries
        effective_task_type = task_type or self.task_type or "RETRIEVAL_QUERY"

        effective_dimensionality = output_dimensionality or self.output_dimensionality

        config = self._build_config(
            task_type=effective_task_type,
            title=title,
            output_dimensionality=effective_dimensionality,
        )

        try:
            result = await self.client.aio.models.embed_content(
                model=self.model,
                contents=text,
                config=config,
            )
        except ClientError as e:
            msg = f"Error embedding content ({e.status}): {e}"
            raise GoogleGenerativeAIError(msg) from e
        except Exception as e:
            msg = f"Error embedding content: {e}"
            raise GoogleGenerativeAIError(msg) from e

        # Single text returns single embedding
        return list(result.embeddings[0].values)
