"""Entrypoint into `langchain-community`."""

import warnings
from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

warnings.warn(
    "`langchain-community` is being sunset and is no longer actively maintained. "
    "See https://github.com/langchain-ai/langchain-community/issues/674 for "
    "details and migration guidance toward standalone integration packages.",
    DeprecationWarning,
    stacklevel=2,
)
