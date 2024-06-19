import lightbulb
import hikari

import config_reader as config

plugin = lightbulb.Plugin("suggest", "Suggest a feature anonymously")

@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("suggestion", "The suggestion", type=str)
@lightbulb.command("suggest", "Suggest something to the admins anonymously.", auto_defer = True, ephemeral = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def suggest_command(ctx: lightbulb.SlashContext, suggestion: str) -> None:
    # Don't use validate command function for anonymity

    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond("This command can not be executed by other bots.")
        return
    
    embed = hikari.Embed(title="Suggestion", description=f"An anonymous suggestion by a server member:\n\n{suggestion}", color=hikari.Color.from_rgb(255, 214, 33))

    await plugin.app.rest.create_message(949315761791438939, embed=embed)

    await ctx.respond("Suggestion sent! :)")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
