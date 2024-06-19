import hikari
import lightbulb

import member_managment


plugin = lightbulb.Plugin("welcome", "Handles joining")

@plugin.listener(hikari.MemberCreateEvent)
async def handle_join(event: hikari.MemberCreateEvent):
    """
    Get's called when a new member joins.
    It runs a helper function used for handling new joins.
    """
    try:
        if event.member.is_bot or event.member.is_system:
            return
        
        await member_managment.new_member(event, plugin.bot)
    except Exception as e:
        from bot import logger
        logger.error(f"Error during member join event: {e}")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
