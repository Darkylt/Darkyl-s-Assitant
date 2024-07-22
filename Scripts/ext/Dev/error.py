import error_handler
import lightbulb

plugin = lightbulb.Plugin("error", "Supporting error handling")


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):
    await error_handler.on_error(event=event)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
