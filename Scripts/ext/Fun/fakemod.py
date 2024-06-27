import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("Fakemod", "Troll people")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The user you want to fake ban", type=hikari.OptionType.USER, required=True)
@lightbulb.option("channel", "The channel you want to send the message in", type=hikari.TextableGuildChannel, required=False, default=None)
@lightbulb.option("reason", "Why should the user be banned?", type=str, required=False, default=None)
@lightbulb.command("fakeban", "Do some trolling by fake banning someone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def fakeban_command(ctx: lightbulb.SlashContext, user: hikari.User, channel: hikari.TextableGuildChannel, reason: str):
    if not await utils.validate_command(ctx):
        return
    
    await ctx.respond("✅", flags=hikari.MessageFlag.EPHEMERAL)

    if not channel:
        channel = ctx.channel_id

    if not reason:
        reason = "No reason provided"

    await plugin.app.rest.create_message(channel=channel, content=f"{user.mention} was banned for: '{reason}'!")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.KICK_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The user you want to fake kick", type=hikari.OptionType.USER, required=True)
@lightbulb.option("channel", "The channel you want to send the message in", type=hikari.TextableGuildChannel, required=False, default=None)
@lightbulb.option("reason", "Why should the user be kicked?", type=str, required=False, default=None)
@lightbulb.command("fakekick", "Do some trolling by fake kicking someone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def fakeban_command(ctx: lightbulb.SlashContext, user: hikari.User, channel: hikari.TextableGuildChannel, reason: str):
    if not await utils.validate_command(ctx):
        return
    
    await ctx.respond("✅", flags=hikari.MessageFlag.EPHEMERAL)

    if not channel:
        channel = ctx.channel_id

    if not reason:
        reason = "No reason provided"

    await plugin.app.rest.create_message(channel=channel, content=f"{user.mention} was kicked for: '{reason}'!")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
