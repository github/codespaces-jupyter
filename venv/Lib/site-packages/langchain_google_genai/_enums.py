from google.genai.types import (
    BlockedReason,
    ComputerUse,
    Environment,
    HarmBlockThreshold,
    HarmCategory,
    MediaModality,
    MediaResolution,
    Modality,
    SafetySetting,
)

__all__ = [
    "BlockedReason",
    "ComputerUse",
    "Environment",
    "HarmBlockThreshold",
    "HarmCategory",
    "MediaModality",
    "MediaResolution",
    "Modality",
    "SafetySetting",
]

# Migration notes:
# - Added:
#   - `BlockedReason`
#   - `SafetySetting`
#
# Parity between generativelanguage_v1beta and genai.types
# - `HarmBlockThreshold`: equivalent
# - `HarmCategory`: there are a few Vertex-only and categories not supported by Gemini
# - `MediaResolution`: equivalent
#
# `MediaModality` has additional modalities not present in `Modality`:
# - `VIDEO`
# - `DOCUMENT`
#
# TODO: investigate why both? Or not just use `MediaModality` everywhere?
