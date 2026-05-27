import json
import logging
from typing import Any, List, Optional

from langchain_core.callbacks import CallbackManagerForToolRun

from langchain_community.tools.slack.base import SlackBaseTool


class SlackGetChannel(SlackBaseTool):
    """Tool that gets Slack channel information."""

    name: str = "get_channelid_name_dict"
    description: str = (
        "Use this tool to get channelid-name dict. There is no input to this tool"
    )

    def _get_all_channels_by_type(self, types: str = "public_channel") -> List[dict]:
        """
        Retrieve all channels of specified types using pagination.

        Args:
            types: Comma-separated list of channel types to retrieve.
                   Options: "public_channel", "private_channel", "mpim", "im"
                   Defaults to "public_channel" if not specified.

        Returns:
            List of all channels for the specified type(s).
        """
        all_channels = []
        cursor = None

        while True:
            if cursor:
                result = self.client.conversations_list(
                    types=types, cursor=cursor, limit=200
                )
            else:
                result = self.client.conversations_list(types=types, limit=200)

            channels = result["channels"]
            all_channels.extend(channels)

            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return all_channels

    def _run(
        self, *args: Any, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            logging.getLogger(__name__)

            public_channels = self._get_all_channels_by_type()
            private_channels = self._get_all_channels_by_type(
                types="private_channel,mpim,im"
            )
            all_channels = public_channels + private_channels

            filtered_result = [
                {key: channel[key] for key in ("id", "name", "created", "num_members")}
                for channel in all_channels
                if "id" in channel
                and "name" in channel
                and "created" in channel
                and "num_members" in channel
            ]
            return json.dumps(filtered_result, ensure_ascii=False)

        except Exception as e:
            return "Error creating conversation: {}".format(e)
