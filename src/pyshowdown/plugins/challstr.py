import asyncio
import json
from typing import List

import aiohttp
from pyshowdown.client import Client
from pyshowdown.message import Message
from pyshowdown.plugins.plugin import BasePlugin


class ChallstrHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a challstr.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a challstr, False otherwise.
        """
        return message.type == "challstr"

    async def response(self, message: Message) -> None:
        """Responds to a challstr message and logs in.

        Args:
            message (Message): The message to respond to.
        """
        print("Got challstr! Trying to log in...")
        base_url = "https://play.pokemonshowdown.com/action.php"
        data = {
            "act": "login",
            "name": self.client.username,
            "pass": self.client.password,
            "challstr": message.challstr,
        }

        async with aiohttp.ClientSession() as session:
            for _ in range(10):
                try:
                    async with session.post(base_url, data=data) as resp:
                        result_str = await resp.text()
                        self.client.cookies = resp.cookies

                        # strip the leading [
                        result_str = result_str[1:]
                        result = json.loads(result_str)

                        self.client.logging_in = True

                        self.client.backoff = 1

                        await self.client.send(
                            "", "/trn {},0,{}".format(self.client.username, result["assertion"])
                        )
                        break

                except Exception as e:
                    print("Error logging in: {}".format(e))
                    await asyncio.sleep(10)


def setup(client: Client) -> List[BasePlugin]:
    """Creates an instance of the ChallstrHandler plugin and returns it.

    Args:
        client (Client): A reference to the client.

    Returns:
        List[BasePlugin]: A list containing the ChallstrHandler plugin.
    """
    return [ChallstrHandler(client)]
