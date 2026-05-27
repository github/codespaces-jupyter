"""LangChain Google Gen AI integration.

!!! note "Vertex AI consolidation & compatibility"

    As of `langchain-google-genai` 4.0.0, this package uses the consolidated
    [`google-genai`](https://googleapis.github.io/python-genai/) SDK
    instead of the legacy [`google-ai-generativelanguage`](https://googleapis.dev/python/generativelanguage/latest/)
    SDK.

    This migration brings support for Gemini models both via the Gemini API and Gemini
    API in Vertex AI, superseding certain classes in `langchain-google-vertexai`, such
    as `ChatVertexAI`. Certain Vertex AI features are not yet supported in the
    consolidated SDK (and subsequently this package) Refer to [the docs](https://docs.langchain.com/oss/python/integrations/providers/google)
    for more information.

This module provides an interface to Google's Generative AI models, specifically the
Gemini series, with the LangChain framework. It provides classes for interacting with
chat models, generating embeddings, and more.

**Chat Models**

The [`ChatGoogleGenerativeAI`][langchain_google_genai.ChatGoogleGenerativeAI] class is
the primary interface for interacting with Google's Gemini chat models. It allows users
to send and receive messages using a specified Gemini model, suitable for various
conversational AI applications.

**Embeddings**

The
[`GoogleGenerativeAIEmbeddings`][langchain_google_genai.GoogleGenerativeAIEmbeddings]
class provides functionalities to generate embeddings using Google's models. These
embeddings can be used for a range of NLP tasks, including semantic analysis, similarity
comparisons, and more.

See [the docs](https://docs.langchain.com/oss/python/integrations/providers/google) for
more information on usage of this package.
"""

from langchain_google_genai._enums import (
    ComputerUse,
    Environment,
    HarmBlockThreshold,
    HarmCategory,
    MediaResolution,
    Modality,
)
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.utils import create_context_cache

__all__ = [
    "ChatGoogleGenerativeAI",
    "ComputerUse",
    "Environment",
    "GoogleGenerativeAI",
    "GoogleGenerativeAIEmbeddings",
    "HarmBlockThreshold",
    "HarmCategory",
    "MediaResolution",
    "Modality",
    "create_context_cache",
]
