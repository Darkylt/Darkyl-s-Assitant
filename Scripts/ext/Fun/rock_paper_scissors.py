import lightbulb
import hikari

import bot_utils as utils
import buttons
import config_reader as config

plugin = lightbulb.Plugin("Rock Paper Scissors", "Play Rock Paper Scissors")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("rock_paper_scissors", "Play Rock Paper Scissors.")
@lightbulb.implements(lightbulb.SlashCommand)
async def rps_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    view=buttons.RockPaperScissors()

    await ctx.respond("Choose your option!", components=view)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
