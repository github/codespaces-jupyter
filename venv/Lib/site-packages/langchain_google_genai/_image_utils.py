from __future__ import annotations

import base64
import mimetypes
import os
import re
from enum import Enum
from urllib.parse import urlparse

import filetype  # type: ignore[import-untyped]
import requests
from google.genai.types import Blob, FileData, Part

# Note: noticed the previous generativelanguage_v1beta Part has a `part_metadata` field
# that is not present in the genai.types.Part.


class Route(Enum):
    """Image loading route.

    Determines how media content is loaded and processed based on the input
    string format.
    """

    URL = 1
    """HTTP/HTTPS URL. Downloads content via HTTP request."""

    BASE64 = 2
    """Base64 encoded data URI (e.g., `data:image/png;base64,...`)."""

    GCS_URI = 3
    """Google Cloud Storage URI (e.g., `gs://bucket/path`)."""

    LOCAL_FILE = 4
    """Local file path. Deprecated for security reasons."""


class ImageBytesLoader:
    """Loads media bytes from multiple sources given a string.

    (Despite the class name, this loader supports multiple media types including
    images, PDFs, audio, and video files.)

    Currently supported:

    - Base64 encoded data URIs (e.g., `data:image/jpeg;base64,...` or
        `data:application/pdf;base64,...`)
    - HTTP/HTTPS URLs
    - Google Cloud Storage URIs (gs://) passed directly to the API as file
        references
    """

    def load_bytes(self, image_string: str) -> bytes:
        """Routes to the correct loader based on the `'image_string'`.

        Args:
            image_string: Can be either:

                - Base64 encoded data URI (e.g., `data:image/jpeg;base64,...` or
                    `data:application/pdf;base64,...`)
                - HTTP/HTTPS URL

        Returns:
            Media bytes (images, PDFs, audio, video, etc.).
        """
        route = self._route(image_string)

        if route == Route.BASE64:
            return self._bytes_from_b64(image_string)

        if route == Route.URL:
            return self._bytes_from_url(image_string)

        if route == Route.GCS_URI:
            msg = (
                "Cannot load raw bytes from GCS URIs. "
                "Use `load_part()` instead, which returns a Part with file_data "
                "that references the GCS URI directly."
            )
            raise ValueError(msg)

        if route == Route.LOCAL_FILE:
            msg = (
                "Loading from local files is no longer supported for security reasons. "
                "Please pass in media as Google Cloud Storage URI, "
                "base64 encoded data URI (e.g., data:image/..., "
                "data:application/pdf;base64,...), or valid HTTP/HTTPS URL."
            )
            raise ValueError(msg)

        msg = (
            "Media string must be one of: Google Cloud Storage URI, "
            "base64 encoded data URI (e.g., data:image/..., "
            "data:application/pdf;base64,...), or valid HTTP/HTTPS URL. "
            f"Instead got '{image_string}'."
        )
        raise ValueError(msg)

    def load_part(self, image_string: str) -> Part:
        """Gets Part for loading from Gemini.

        Args:
            image_string: Can be either:

                - Base64 encoded data URI (e.g., `data:image/jpeg;base64,...` or
                    `data:application/pdf;base64,...`)
                - HTTP/HTTPS URL
                - Google Cloud Storage URI (gs://bucket/path)

        Returns:
            Part object with either `inline_data` containing the media bytes, or
                `file_data` for GCS URIs.
        """
        route = self._route(image_string)

        if route == Route.GCS_URI:
            # For GCS URIs, pass directly to the API as a file reference
            mime_type, _ = mimetypes.guess_type(image_string)
            return Part(file_data=FileData(file_uri=image_string, mime_type=mime_type))

        if route == Route.BASE64:
            bytes_ = self._bytes_from_b64(image_string)

        if route == Route.URL:
            bytes_ = self._bytes_from_url(image_string)

        if route == Route.LOCAL_FILE:
            msg = (
                "Loading from local files is no longer supported for security reasons. "
                "Please specify media as Google Cloud Storage URI, "
                "base64 encoded data URI (e.g., data:image/..., "
                "data:application/pdf;base64,...), or valid HTTP/HTTPS URL."
            )
            raise ValueError(msg)

        mime_type, _ = mimetypes.guess_type(image_string)
        if not mime_type:
            kind = filetype.guess(bytes_)
            if kind:
                mime_type = kind.mime

        blob = Blob(data=bytes_, mime_type=mime_type)

        return Part(inline_data=blob)

    def _route(self, image_string: str) -> Route:
        # Accept any data URI format (images, PDFs, audio, video, etc.)
        # Examples: data:image/jpeg;base64,..., data:application/pdf;base64,...
        if image_string.startswith("data:"):
            return Route.BASE64

        if image_string.startswith("gs://"):
            return Route.GCS_URI

        if self._is_url(image_string):
            return Route.URL

        if os.path.exists(image_string):
            return Route.LOCAL_FILE

        msg = (
            "Media string must be one of: "
            "valid HTTP/HTTPS URL, "
            "base64 encoded data URI (e.g., data:image/..., "
            "data:application/pdf;base64,...), or "
            "Google Cloud Storage URI (gs://...). "
            f"Instead got '{image_string}'."
        )
        raise ValueError(msg)

    def _bytes_from_b64(self, base64_image: str) -> bytes:
        """Gets media bytes from a base64 encoded data URI.

        Supports any mime type including images, PDFs, audio, video, etc.

        Args:
            base64_image: Base64 encoded data URI (e.g., `data:image/jpeg;base64,...`
                or `data:application/pdf;base64,...`).

        Returns:
            Decoded media bytes.

        Raises:
            ValueError: If the data URI format is invalid.
        """
        # Pattern captures any mime type: image/jpeg, application/pdf, audio/mp3, etc.
        # Format: data:<mime_type>;base64,<encoded_data>
        pattern = r"data:([^;]+);base64,(.*)"
        match = re.search(pattern, base64_image)

        if match is not None:
            # Group 1: mime type (e.g., "image/jpeg", "application/pdf")
            # Group 2: base64 encoded data
            encoded_string = match.group(2)
            return base64.b64decode(encoded_string)

        msg = (
            f"Invalid base64 data URI format. Expected pattern: {pattern}\n"
            f"Examples: data:image/jpeg;base64,... or data:application/pdf;base64,...\n"
            f"Got: {base64_image[:100]}..."
        )
        raise ValueError(msg)

    def _bytes_from_url(self, url: str) -> bytes:
        """Gets media bytes from a public HTTP/HTTPS URL.

        Args:
            url: Valid HTTP or HTTPS URL pointing to media content.

        Raises:
            HTTPError: If the request fails.

        Returns:
            Media bytes (images, PDFs, audio, video, etc.).
        """
        response = requests.get(url)

        if not response.ok:
            response.raise_for_status()

        return response.content

    def _is_url(self, url_string: str) -> bool:
        """Checks if a url is valid.

        Args:
            url_string: Url to check.

        Returns:
            Whether the url is valid.
        """
        try:
            result = urlparse(url_string)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


def image_bytes_to_b64_string(
    image_bytes: bytes, encoding: str = "ascii", image_format: str = "png"
) -> str:
    """Encodes image bytes into a b64 encoded string.

    Args:
        image_bytes: Bytes of the image.
        encoding: Type of encoding in the string. `'ascii'` by default.
        image_format: Format of the image. `'png'` by default.

    Returns:
        B64 image encoded string.
    """
    encoded_bytes = base64.b64encode(image_bytes).decode(encoding)
    return f"data:image/{image_format};base64,{encoded_bytes}"
