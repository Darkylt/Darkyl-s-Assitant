import asyncio

import lightbulb
import hikari
import miru
import miru.client

import bot_utils as utils
import config_reader as config
import buttons

plugin = lightbulb.Plugin("Test", "Some test stuff for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


ENABLED = False


async def test(ctx: lightbulb.SlashContext):

    await ctx.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, attachment=hikari.File("E:/YouTube/Music Libary/Evening Spies Epidemic Sound.mp3"), flags=hikari.MessageFlag.IS_VOICE_MESSAGE)



@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("admin_test", "A command used for testing the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def test_command(ctx: lightbulb.SlashContext):
    """
    A command used to test the bot.
    It performs some basic checks and then executes the test() function
    """
    if not await utils.validate_command(ctx):
        return
    
    try:
        if not ctx.author.id == config.Bot.darkyl_id:
            await ctx.respond("This command can only be used by Darkyl.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        if not ENABLED:
            await ctx.respond("Command disabled.", flags=hikari.MessageFlag.EPHEMERAL)
            return
    except Exception as e:
        print(f"An error occurred while processing the /admin_tst command {e}")
    
    try:
        await test(ctx)
    except Exception as e:
        print(f"An error occurred during the test: {e}")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
