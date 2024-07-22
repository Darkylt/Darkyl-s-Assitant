import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Verify", "Helping with verification")


@plugin.listener(hikari.events.DMMessageCreateEvent)
async def on_message(event: hikari.events.DMMessageCreateEvent) -> None:
    if event.author.is_bot or event.author.is_system:
        return

    from Verification import captcha, captcha_db

    if await captcha_db.get_id_from_user(event.author_id):
        if event.message.content.lower() == "regenerate":
            await captcha.regenerate(plugin.bot, event.author_id)
            return

        await captcha.verify_solution(event.message)
    else:
        return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
