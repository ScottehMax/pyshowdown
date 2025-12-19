import asyncio
import json
from http.cookies import SimpleCookie
from typing import List, Optional

import aiofiles
import aiohttp
import yarl
from aiohttp import CookieJar
from aiohttp.abc import AbstractCookieJar

from pyshowdown.client import Client
from pyshowdown.message import ChallstrMessage, Message
from pyshowdown.plugins.plugin import BasePlugin

base_url = "https://play.pokemonshowdown.com/api"


async def save_cookies(
    cookie_jar: AbstractCookieJar, filename: str = "cookies.json"
) -> None:
    """Save cookies from an aiohttp CookieJar to a JSON file.

    Args:
        cookie_jar (AbstractCookieJar): The cookie jar to save.
        filename (str): The name of the file to save cookies to.
    """
    cookies = []

    for cookie in cookie_jar:
        cookie_dict = {
            "name": cookie.key,
            "value": cookie.value,
            "domain": cookie.get("domain"),
            "path": cookie.get("path"),
            "secure": cookie.get("secure", False),
            "max_age": cookie.get("max-age"),
        }
        cookies.append(cookie_dict)

    async with aiofiles.open(filename, "w") as f:
        await f.write(json.dumps(cookies, indent=2))


async def load_cookies(filename: str = "cookies.json") -> Optional[CookieJar]:
    """Load cookies from a JSON file into a new CookieJar.

    Args:
        filename (str): The name of the file to load cookies from.
    """
    try:
        cookie_jar = CookieJar()
        async with aiofiles.open(filename, "r") as f:
            try:
                cookies = json.loads(await f.read())
            except json.JSONDecodeError:
                return None

        for cookie in cookies:
            morsel = SimpleCookie()
            morsel[cookie["name"]] = cookie["value"]
            morsel[cookie["name"]]["domain"] = cookie["domain"]
            morsel[cookie["name"]]["path"] = cookie["path"]
            if cookie.get("secure", False):
                morsel[cookie["name"]]["secure"] = True
            if cookie.get("max_age") is not None:
                morsel[cookie["name"]]["max-age"] = cookie["max_age"]

            cookie_jar.update_cookies(
                morsel, response_url=yarl.URL(f"https://{cookie['domain']}")
            )

        return cookie_jar
    except FileNotFoundError:
        return None


async def password_login(client: Client, challstr: str) -> None:
    """Tries to log in using a password.

    Args:
        client (Client): The client to log in.
        challstr (str): The challstr to use.
    """
    valid_cookies = False
    result = {}

    cookie_jar = await load_cookies()
    if cookie_jar:
        client.print("Found existing cookies. Attempting to use them to login...")

        async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
            try:
                async with session.get(
                    f"{base_url}/upkeep", data={"challstr": challstr}
                ) as resp:
                    if resp.status == 200:
                        result_str = await resp.text()
                        if result_str.startswith("]"):
                            result_str = result_str[1:]
                        result = json.loads(result_str)

                        if result.get("loggedin", False):
                            await save_cookies(session.cookie_jar)
                            client.cookies = cookie_jar
                            client.print("Successfully logged in using cookies.")
                            valid_cookies = True
                        else:
                            client.print("Cookies are invalid.")
                            client.print(result)

            except (aiohttp.ClientError, json.JSONDecodeError) as e:
                client.print(f"Error during cookie login: {e}")

    if not valid_cookies:
        client.print("Cookies are invalid. Logging in again...")
        data = {
            "name": client.username,
            "pass": client.password,
            "challstr": challstr,
        }

        result = None
        async with aiohttp.ClientSession() as session:
            for _ in range(10):
                try:
                    async with session.post(f"{base_url}/login", data=data) as resp:
                        result_str = await resp.text()
                        jar = CookieJar()
                        jar.update_cookies(resp.cookies)
                        client.cookies = jar

                        async with aiofiles.open("cookies.json", "w") as f:
                            await save_cookies(jar)

                        # strip the leading [
                        result_str = result_str[1:]
                        result = json.loads(result_str)

                        client.backoff = 1
                        valid_cookies = True
                        break

                except Exception as e:
                    client.print("Error logging in: {}".format(e))
                    await asyncio.sleep(10)

    if valid_cookies and result and result.get("assertion"):
        client.logging_in = True
        await client.send(
            "", "/trn {},0,{}".format(client.username, result["assertion"])
        )
    else:
        client.print("Failed to log in after multiple attempts.")


class ChallstrHandler(BasePlugin[ChallstrMessage]):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a challstr.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a challstr, False otherwise.
        """
        return isinstance(message, ChallstrMessage)

    async def response(self, message: ChallstrMessage) -> None:
        """Responds to a challstr message and logs in.

        Args:
            message (ChallstrMessage): The message to respond to.
        """
        self.client.print("Got challstr! Trying to log in...")
        if self.client.login_type == "password":
            await password_login(self.client, message.challstr)
        else:
            self.client.print("Login type not supported.")


def setup(client: Client) -> List[BasePlugin]:
    """Creates an instance of the ChallstrHandler plugin and returns it.

    Args:
        client (Client): A reference to the client.

    Returns:
        List[BasePlugin]: A list containing the ChallstrHandler plugin.
    """
    return [ChallstrHandler(client)]
