import random

import lightbulb
import hikari

import bot_utils as utils


plugin = lightbulb.Plugin("F", "Pay your respects!")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("text", "What do you want to pay respect to?", required=False, type=str)
@lightbulb.command("f", "Press F to pay respect.", pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def f_command(ctx: lightbulb.SlashContext, text: str):
    if not await utils.validate_command(ctx):
        return

    reason = f"for **'{text}'** " if text else ""

    hearts = ['❤', '💛', '💚', '💙', '💜', '♥']

    await ctx.respond(f"**{ctx.author.mention}** has paid their respect {reason}{random.choice(hearts)}")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
