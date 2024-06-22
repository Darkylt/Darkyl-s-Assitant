import os
import random

import hikari
import lightbulb
import miru

import bot_utils as utils
import config_reader as config
import Verification.verify_db as db

async def handle_captcha(ctx: miru.ViewContext = None, button: miru.Button = None, event: hikari.events.DMMessageCreateEvent = None, regenerate: bool = False):
    from bot import logger

    if ctx and button:
        user_id = ctx.author.id
        button = True
        
    elif event:
        user_id = event.author_id
        button = False

    else:
        logger.error("Error during handle_captcha: Invalid use of arguments. Use either ctx and button or event.")
        return

    id = await utils.generate_id(os.path.join(config.Paths.data_folder, "Generated Captchas"))

    # Choosing one of multiple verification methods at random
    choice = random.randint(1, 1)

    if choice == 1:
        if config.Verification.force_captcha:
            text="We require some extra verification to prove that you're a real user."
        else:
            text="We are experiencing high amounts of traffic at the moment. Due to this we need to perform some extra verification steps."
        embed = hikari.Embed(title="Extra Verification (Image Captcha)", description=f"{text}\n\nBelow is an image of letters. **Write the letters into the channel.**\n\nWrite 'Regenerate' to get a new captcha.")

        from Verification.captcha_gen_image import generate_image
        image, text = await generate_image(id)

        embed.set_image(hikari.File(image))

        embed.set_footer(text=id)

        if await db.get_id_from_user(user_id):
            msg = await db.get_message_id_from_user(user_id)

            if button:
                await ctx.client.app.rest.delete_message(await ctx.author.fetch_dm_channel(), msg)
            else:
                await event.app.rest.delete_message(await event.author.fetch_dm_channel(), msg)

        await db.delete_entries_from_user_id(user_id)

        if button:
            msg = await ctx.author.send(embed=embed)
        else:
            msg = await event.author.send(embed=embed)

        await db.register_captcha(id, user_id, choice, text, msg.id)

        os.remove(image)

async def handle_verify_message(event: hikari.events.DMMessageCreateEvent):
    captcha_id = await db.get_id_from_user(event.author_id)

    if captcha_id == None:
        return
    
    message = event.message.content

    if not message:
        return

    if message == "Regenerate":
        await handle_captcha(event=event, regenerate=True)
        return
    
    data = await db.read_db(captcha_id)

    if data is not None and len(data) > 2:
        string = data[2]
    else:
        from bot import logger
        logger.error("An error occurred during handel_verify_message: The read data was empty")#
        await event.message.respond("An error occurred on my end.")
        return
    
    if string == message:
        member = await event.app.rest.fetch_member(config.Bot.server, event.author)
        await member.add_role(config.Bot.verified_role)
        await event.message.respond("You are now verified!\nHave fun :)")
        await db.delete_entries_from_user_id(event.author_id)
        return
    else:
        await event.message.respond("Failed to verify.")
        msg = await db.get_message_id_from_user(event.author_id)
        await event.app.rest.delete_message(await event.author.fetch_dm_channel(), msg)
        await db.delete_entries_from_user_id(event.author_id)
