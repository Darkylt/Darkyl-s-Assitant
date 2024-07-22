import os
import subprocess
import sys

import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Restart", "A restart command for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


async def restart():
    """
    A helper function used for restarting the bot
    """
    try:
        from bot import logger

        logger.info("Bot restarts by command.")

        await plugin.bot.close()  # Stops the bot loop
        executable = sys.executable

        script_path = os.path.join(config.Paths.scripts_folder, "run.py")

        subprocess.Popen([executable, script_path])

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during restart: {e}")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("admin_restart", "Restart the Bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def restart_command(ctx: lightbulb.SlashContext) -> None:
    """
    A command that restarts the bot.
    It checks if the command is executed by darkyl and then calls the restart function.
    """
    from bot import Logging

    try:
        if ctx.author.id == config.Bot.darkyl_id:
            await ctx.respond("Bot is restarting.", flags=hikari.MessageFlag.EPHEMERAL)
            from bot import logger

            logger.info(f"{ctx.author.id} executed /{ctx.command.name}")

            # await Logging.log_message("Restarting...")

            await plugin.bot.update_presence(status=hikari.Status.OFFLINE)

            await restart()
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during /admin_restart command: {e}")
        await ctx.respond("An error occurred.", flags=hikari.MessageFlag.EPHEMERAL)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
