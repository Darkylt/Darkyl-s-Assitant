import lightbulb
import hikari

import bot_utils as utils

plugin = lightbulb.Plugin("Converter Binary", "Convert to or from binary")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("target", "The person with the pfp you wanna view", type=hikari.User)
@lightbulb.command("show_avatar", "Display someones avatar for your viewing pleasure.", pass_options=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def show_avatar_command(ctx: lightbulb.SlashContext, target: hikari.User):
    if not await utils.validate_command(ctx):
        return
    
    await ctx.respond(f"Here is {target.mention}'s Avatar:", attachment=target.display_avatar_url)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
