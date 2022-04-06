from pyshowdown import client
import asyncio
if __name__ == "__main__":
    c = client.Client("sim3.psim.us", 443, "/showdown/websocket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(c.keep_connected())