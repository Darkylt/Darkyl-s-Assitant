import typing as t
from typing import cast

import hikari
import lavalink_rs
import lightbulb
from lavalink_voice import LavalinkVoice

plugin = lightbulb.Plugin("Music", "Play Music in a voice channel")
plugin.add_checks(lightbulb.guild_only)


async def _join(ctx: lightbulb.Context):
    if not ctx.guild_id:
        return None

    channel_id = None

    for i in ctx.options.items():
        if i[0] == "channel" and i[1]:
            channel_id = i[1].id
            break

    if not channel_id:
        voice_state = ctx.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)

        if not voice_state or not voice_state.channel_id:
            return None

        channel_id = voice_state.channel_id

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    from bot import bot

    if not voice:
        await LavalinkVoice.connect(
            ctx.guild_id,
            channel_id,
            ctx.bot,
            bot.lavalink,
            (ctx.channel_id, ctx.bot.rest),
            voice,
        )
    else:
        assert isinstance(voice, LavalinkVoice)
        await LavalinkVoice.connect(
            guild_id=ctx.guild_id,
            channel_id=channel_id,
            bot=ctx.bot,
            lavalink=bot.lavalink,
            ctx_info=(ctx.channel_id, ctx.bot.rest),
            old_voice=voice,
        )

    return channel_id


@plugin.command()
@lightbulb.option(
    "channel",
    "The channel you want me to join",
    hikari.GuildVoiceChannel,
    required=False,
    channel_types=[hikari.ChannelType.GUILD_VOICE],
)
@lightbulb.command(
    "join", "Enters the voice channel you are connected to, or the one specified"
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: lightbulb.Context) -> None:
    """Joins the voice channel you are in"""
    channel_id = await _join(ctx)

    if channel_id:
        await ctx.respond(f"Joined <#{channel_id}>")
    else:
        await ctx.respond(
            "Please, join a voice channel, or specify a specific channel to join in"
        )


def load(bot):
    return
    # bot.add_plugin(plugin)


def unload(bot):
    return
    # bot.remove(plugin)
