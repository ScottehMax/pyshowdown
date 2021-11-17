from pyshowdown import client
import asyncio
import ssl
import certifi

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_verify_locations(certifi.where())


async def main():
    c = client.Client("sim3.psim.us", 443, "/showdown/websocket", ssl_context=context)
    await c.keep_connected()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())