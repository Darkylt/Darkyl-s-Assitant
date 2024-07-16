import lightbulb
import hikari

import database_interaction as db

plugin = lightbulb.Plugin("Leave", "Removes a user from the databse if they leave")

@plugin.listener(hikari.events.MemberDeleteEvent)
async def leave(event: hikari.MemberDeleteEvent) -> None:

    db.delete_user_entry(user_id=event.user_id)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
