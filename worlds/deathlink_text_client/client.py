import asyncio
import urllib.parse

from CommonClient import CommonContext, get_base_parser, gui_enabled, logger
from typing import Set, Dict, Any


class DeathLinkTextContext(CommonContext):
    tags: Set[str] = {"AP", "TextOnly", "DeathLink"}
    game = ""
    items_handling = 0b111
    want_slot_data = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(DeathLinkTextContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.game = self.slot_info[self.slot].game

    async def disconnect(self, allow_autoreconnect: bool = False):
        self.game = ""
        await super().disconnect(allow_autoreconnect)

    def on_deathlink(self, data: Dict[str, Any]) -> None:
        """Gets dispatched when a new DeathLink is triggered by another linked player."""
        self.last_death_link = max(data["time"], self.last_death_link)
        killer = data.get("source", "")
        cause = data.get("cause", "")
        if killer and cause:
            logger.info(f"DeathLink: Killed by {killer}, \"{cause}\"")
        else:
            if cause:
                logger.info(f"DeathLink: Killed, \"{cause}\"")
            else:
                if killer:
                    logger.info(f"DeathLink: Killed by {killer}")
                else:
                    logger.info("DeathLink: Killed")


async def main(args):
    ctx = DeathLinkTextContext(args.connect, args.password)
    ctx.auth = args.name

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    await ctx.exit_event.wait()
    await ctx.shutdown()


def launch():
    import colorama

    parser = get_base_parser(description="Gameless Archipelago Client, for text interfacing.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    args = parser.parse_args()

    if args.url:
        url = urllib.parse.urlparse(args.url)
        args.connect = url.netloc
        if url.username:
            args.name = urllib.parse.unquote(url.username)
        if url.password:
            args.password = urllib.parse.unquote(url.password)

    # use colorama to display colored text highlighting on windows
    colorama.init()

    asyncio.run(main(args))
    colorama.deinit()


if __name__ == "__main__":
    launch()
