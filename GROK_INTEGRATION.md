Grok bot integration for Codespaces Jupyter

Overview
- Adds a minimal Grok API client and an IPython magic to call it from notebooks.

Authentication
- Set the GROK_API_KEY environment variable to your API key, e.g. in Codespaces /devcontainer.json or your shell:

  export GROK_API_KEY="sk-..."  # Linux/macOS
  # PowerShell
  $env:GROK_API_KEY = "sk-..."

- Optionally set GROK_API_URL to a custom endpoint if your provider requires it.

Usage in notebooks
- Load the extension once per kernel:

  %load_ext grok_bot.magic

- Use line magic:

  %grok What is the summary of this dataset?

- Use cell magic for multi-line prompts:

  %%grok
  Analyze the following:
  - Column A distribution
  - Suggestions for visualization

Notes
- The client uses the GROK_API_KEY env var by default. The API URL is configurable via GROK_API_URL.
- Error handling prints helpful messages in the notebook; exceptions from the HTTP client are surfaced as text.

Developer notes
- The package lives in grok_bot/ and exposes GrokClient and IPython extension loader.
- Requirements updated to include `requests`.

Security
- Do not commit API keys to the repository. Prefer Codespaces secrets or devcontainer environment variables.
