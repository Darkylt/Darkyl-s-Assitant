import time
import psutil

import lightbulb
import hikari
import hikari.errors

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("ping", "Ping me")

def get_bandwidth_usage():
    """Returns the current bandwidth usage in bytes sent and received."""
    net_io_start = psutil.net_io_counters()
    time.sleep(1)  # Wait a second to measure the difference
    net_io_end = psutil.net_io_counters()
    bytes_sent = net_io_end.bytes_sent - net_io_start.bytes_sent
    bytes_recv = net_io_end.bytes_recv - net_io_start.bytes_recv

    return bytes_sent, bytes_recv

@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("extra", "Do you want extra info?", bool, default=False)
@lightbulb.command("ping", "Ping me.", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping_command(ctx: lightbulb.SlashContext) -> None:
    if not await utils.validate_command(ctx):
        return

    extra = getattr(ctx.options, "extra", None)

    if extra:
        latency = f"{ctx.bot.heartbeat_latency * 1000:.0f}ms"
        bytes_sent, bytes_recv = get_bandwidth_usage()

        start = time.perf_counter()
        msg = await ctx.respond(f"Pong!\n\n**Latency:** {latency},\n**Bytes sent:* {bytes_sent},\n**Bytes received:** {bytes_recv}")
        end = time.perf_counter()

        await msg.edit(f"Pong!\n\n**Latency:** {latency},\n**Bytes sent:* {bytes_sent},\n**Bytes received:** {bytes_recv},\n**REST:** {(end-start)*1000:,.0f}ms")
    else:
        await ctx.respond("Pong!")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
