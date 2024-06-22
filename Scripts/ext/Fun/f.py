import random

import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("F", "Pay your respects!")

hearts = ['❤', '💛', '💚', '💙', '💜', '♥', 'o7']

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("text", "What do you want to pay respect to?", required=False, type=str)
@lightbulb.command("f", "Press F to pay respect.", pass_options = True, aliases=["respect"])
@lightbulb.implements(lightbulb.SlashCommand)
async def f_command(ctx: lightbulb.SlashContext, text: str):
    if not await utils.validate_command(ctx):
        return

    reason = f"for **'{text}'** " if text else ""

    await ctx.respond(f"**{ctx.author.mention}** has paid their respect {reason}{random.choice(hearts)}")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("respect", "Press F to pay respect.")
@lightbulb.implements(lightbulb.MessageCommand)
async def f_message_command(ctx: lightbulb.Context):
    if ctx.author.is_bot or ctx.author.is_system:
        return

    from bot import logger
    logger.info(f"{ctx.author.username} used respect message command.")#

    message = ctx.options.target
    author = message.author#

    msg = await plugin.app.rest.fetch_message(ctx.channel_id, message)

    await msg.respond(f"**{ctx.author.mention}** has paid their respect for {author.mention}{random.choice(hearts)}", reply=msg)

    await ctx.respond("Respects paid o7", flags=hikari.MessageFlag.EPHEMERAL)


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
