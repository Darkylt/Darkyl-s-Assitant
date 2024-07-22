import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin(
    "Show Banner", "Display someones Banner for your viewing pleasure."
)

# FOR SOME REASON TARGET.BANNER_URL IS NONE EVEN IF THE USER HAS A BANNER WTF

# @plugin.command
# @lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
# @lightbulb.option("target", "The person with the avatar you wanna view", type=hikari.User)
# @lightbulb.command("show_banner", "Display someones Banner for your viewing pleasure.", pass_options=True, auto_defer=True, ephemeral=True)
# @lightbulb.implements(lightbulb.SlashCommand)
# async def show_banner_command(ctx: lightbulb.SlashContext, target: hikari.User):
#    if not await utils.validate_command(ctx):
#        return

#    banner = target.banner_url

#    print(banner)

#    if banner:
#        await ctx.respond(f"Here is {target.mention}'s Banner:", attachment=banner)
#    else:
#        await ctx.respond(f"{target.mention} doesn't have a Banner set.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
