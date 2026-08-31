from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.display import Markdown, display
from .api import GrokClient
import os


@magics_class
class GrokMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        api_key = os.getenv("GROK_API_KEY")
        self.client = None
        if api_key:
            try:
                self.client = GrokClient(api_key=api_key)
            except Exception:
                self.client = None

    @line_cell_magic
    def grok(self, line, cell=None):
        """%grok <prompt>  or  %%grok <multi-line prompt>

        Outputs Grok's response as rendered Markdown.
        """
        prompt = cell if cell is not None else line
        if not prompt:
            print("Usage: %grok <prompt>  or  %%grok <multi-line prompt>")
            return
        if not self.client:
            try:
                self.client = GrokClient()
            except Exception as e:
                print(f"Grok client initialization error: {e}")
                return
        try:
            resp = self.client.ask(prompt)
            display(Markdown("**Grok**\n\n" + resp))
        except Exception as e:
            print(f"Grok request failed: {e}")


def load_ipython_extension(ipython):
    ipython.register_magics(GrokMagics)


def unload_ipython_extension(ipython):
    # IPython does not provide a stable unregister API for magics; keep this as a noop.
    pass
