import asyncio
import os
import json
import random

import hikari

import image_manager
import config_reader as config
import bot_utils as utils

async def new_member(event, bot):
    """
    Handles a new server member.
    Sends the welcome card.

    Processing:
        Downloads the avatar of the new user
        Converts to png if it is a gif
        Resizes the image to a set size
        Generates the card
        Sends the welcome card and message
    """
    pfp_link = event.member.avatar_url

    pfp_path = await image_manager.download_image(image_url=pfp_link, id=event.member.id)

    if pfp_path == None:
        return None
    
    if str(pfp_path).endswith("gif"):
        pfp_path = await image_manager.gif_to_png(pfp_path)
    
    await image_manager.resize_image(pfp_path)

    await image_manager.make_card(pfp_path)

    file = hikari.File(pfp_path)

    await bot.application.app.rest.create_message(config.Join.channel, f"<@{event.member.id}>, welcome to **Darkyl's Discord**.", attachment=file, user_mentions=True)

    if not await image_manager.delete(pfp_path):
        return

async def skibidy_toilet_enysmo(bot):
    """
    Makes sure Enysmo is being put in his place
    """
    await asyncio.sleep(10)

    enysmo = await bot.application.app.rest.fetch_member(config.Bot.server, user=175892694952837120)
    enysmo.add_role(config.ReactionRoles.skibidy_toilet_role)

async def update_user_stats(user_id: int, msg: bool, cmd: bool, rep: bool, created_at: str):
    """
    Updates the user stats database

    Args:
        user_id (int): The User ID of the account that should be added
        msg (bool): If the event was triggered by a message
        cmd (bool): If the event was triggered by a command
        rep (bool): If the event was triggered by a report
        created_at (str): The string of when the account was created at
    """
    try:
        file_path = os.path.join(config.Bot.data_folder, "User Data", "user_stats.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        if not str(user_id) in data:
            await utils.create_user_entry(user_id, msg, cmd, rep, created_at)
            return
        
        if msg:
            data[str(user_id)]["message count"] += 1
        if cmd:
            data[str(user_id)]["commands used"] += 1
        if rep:
            data[str(user_id)]["reported"] += 1
        
        with open(file_path, 'w') as f:
            json.dump(data, f)

        if rep:
            await update_xp(user_id, report=True)
        else:
            await update_xp(user_id, report=False)
    except Exception as e:
        from bot import logger
        logger.error(f"Error while updating user stats (update_user_stats()): {e}")

async def get_level_from_xp(xp):
    try:
        # calculate level from xp
        xp = int(xp)
        level = 0
        for required_xp in config.Level.leve_from_xp_mapping.values():
            if xp >= required_xp:
                level += 1

            else:
                break
        return level
    except Exception as e:
        from bot import logger
        logger.error(f"Following error occurred during get_level_from_xp(): {e}")
        return None

async def level_increase(level, user_id, bot):
    try:
        embed = hikari.Embed(title="Level increase", description=f"<@{user_id}> is now level {level}!")
        embed.set_thumbnail(os.path.join(config.Bot.assets_folder, "pfp.png"))
        from bot import bot
        await bot.application.app.rest.create_message(channel=config.Bot.level_update_channel, embed=embed)
    except Exception as e:
        from bot import logger
        logger.error(f"Error during level increase message (level_increase()): {e}")

async def update_xp(user_id: int, report: bool) -> bool:
    try:
        file_path = os.path.join(config.Bot.data_folder, "User Data", "user_stats.json")

        with open(file_path, 'r') as f:
            data = json.load(f)

        last_level = data.get(str(user_id), {}).get("level", 0)

        if report:
            xp = random.randint(10, 25)
        else:
            xp = random.randint(3, 15)

        level = await get_level_from_xp(xp)
        if level == None:
            return
        
        data[str(user_id)]["xp"] += xp
        data[str(user_id)]["level"] = level

        if config.Bot.level_updates_enabled:
            if level > last_level:
                level_increase(level, user_id)

        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred while updating xp (update_xp()): {e}")
        return
