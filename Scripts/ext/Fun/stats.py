import os

import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("Stats", "Get fun stats on the bot")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("stats", "Get statistics on me!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def stats_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    # Unpack the tuple returned by count_lines_in_files
    lines, file_count = await utils.count_lines_in_files(directory=config.Paths.root_folder)

    code_line_count = lines + 27000000 + 50000000 + 350000 + 500 + 46000#+Linux kernel +Ubuntu +CPython +Python interpreter +Discord

    command_count  = int(len(str(config.HelpMessage.message_all).split("\n"))) + int(len(str(config.HelpMessage.message_all_admin).split("\n")))

    thumbnail = os.path.join(config.Paths.assets_folder, "pfp.png")

    embed = hikari.Embed(title="Bot statistics", description="Here are some fun stats about me!")
    embed.set_thumbnail(thumbnail)
    embed.add_field("File Count:", f"I have over **{file_count}** files!", inline=False)
    embed.add_field("Code Lines:", f"I run on over **{code_line_count}** lines of code!", inline=False)
    embed.add_field("Commands Count:", f"I have **{command_count}** commands!", inline=False)

    await ctx.respond(embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
