import lightbulb
import hikari

import config_reader as config


plugin = lightbulb.Plugin("Verify", "Helping with verification")

@plugin.listener(hikari.events.DMMessageCreateEvent)
async def on_message(event: hikari.events.DMMessageCreateEvent) -> None:
    if event.author.is_bot or event.author.is_system:
        return
    
    from Verification.handle_captcha import handle_verify_message

    await handle_verify_message(event)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
