import os
import requests
from typing import Optional


class GrokClient:
    """Minimal Grok API wrapper.

    Authentication: set the GROK_API_KEY environment variable (or pass api_key).
    Configure endpoint with GROK_API_URL if your provider uses a custom URL.
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        self.api_url = api_url or os.getenv("GROK_API_URL") or "https://api.grok.example/v1/complete"
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable not set. Set it or pass api_key to GrokClient.")

    def ask(self, prompt: str, model: str = "grok-1") -> str:
        payload = {"model": model, "prompt": prompt}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # Support a couple common response shapes
            if isinstance(data, dict) and "text" in data:
                return data["text"]
            if isinstance(data, dict) and "choices" in data and data["choices"]:
                return data["choices"][0].get("text") or str(data)
            return str(data)
        except requests.RequestException as e:
            raise RuntimeError(f"Grok API request failed: {e}") from e
