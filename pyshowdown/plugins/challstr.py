import json

import aiohttp

from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message


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
            async with session.post(base_url, data=data) as resp:
                result = await resp.text()
                self.client.cookies = resp.cookies
                print("----------")
                print(self.client.cookies)
                print("----------")

                # strip the leading [
                result = result[1:]
                result = json.loads(result)

                await self.client.send(
                    "", "/trn {},0,{}".format(self.client.username, result["assertion"])
                )


def setup(client) -> list:
    """Creates an instance of the ChallstrHandler plugin and returns it.

    Args:
        client (Client): A reference to the client.

    Returns:
        list: A list containing the ChallstrHandler plugin.
    """
    return [ChallstrHandler(client)]
