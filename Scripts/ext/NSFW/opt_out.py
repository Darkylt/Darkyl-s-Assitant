import json
import os

import bot_utils as utils
import buttons
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Opt Out", "Choose not to be included in NSFW contexts")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command(
    "nsfw_opt_out",
    "Choose not to be included in NSFW contexts",
    nsfw=False,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def opt_out_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx, nsfw=False):
        return

    user_id = ctx.author.id

    if await utils.nsfw_blacklisted(user_id):
        view = buttons.NSFWOptIn()
        await ctx.respond(
            "Hey. You are opting in to nsfw.\nThis means users are able to include you in nsfw or other love related commands. If you wish to proceed hit the button below.",
            components=view,
        )
    else:
        view = buttons.NSFWOptOut()
        await ctx.respond(
            "Hey. You are opting out of nsfw.\nThis means that users are not able to include you in nsfw or other love related commands. If you wish to proceed hit the button below.",
            components=view,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
