<p align="center">
 <img src="https://raw.githubusercontent.com/ScottehMax/pyshowdown/main/assets/logo.png" width=300 alt="pyshowdown logo"/>
</p>

<p align="center">
  This is a client library for the Pokémon Showdown! battle simulator.
</p>

## Installation

```bash
pip install pyshowdown
```

## Usage

```python
from pyshowdown import client
import asyncio

if __name__ == "__main__":
    c = client.Client(
        username="username",
        password="password",
        url="wss://sim3.psim.us/showdown/websocket",
    )

    # System plugins (challstr, init, deinit, title, users) are automatically loaded
    # Load any additional custom plugins here if needed:
    # c.load_plugin("custom_plugin_name")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(c.keep_connected())
```

## Documentation

Full documentation is available at [https://docs.scotteh.me/pyshowdown/](https://docs.scotteh.me/pyshowdown/).