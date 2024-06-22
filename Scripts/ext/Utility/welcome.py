import hikari
import lightbulb
import asyncio
from collections import deque
from datetime import datetime, timedelta

import member_managment
import config_reader as config
from vars import raid
from Verification.captcha_enabling import update_captcha_status

plugin = lightbulb.Plugin("welcome", "Handles joining")

# Raid detection configuration
RAID_THRESHOLD = 10  # Number of members joining within the time frame to be considered a raid
TIME_FRAME = timedelta(seconds=10)  # Time frame in which the number of joins are counted
join_times = deque()  # Stores the join times of members

@plugin.listener(hikari.MemberCreateEvent)
async def handle_join(event: hikari.MemberCreateEvent):
    """
    Gets called when a new member joins.
    It runs a helper function used for handling new joins.
    """
    global raid

    try:
        if event.member.is_bot or event.member.is_system:
            return

        now = datetime.now()

        # Remove join times outside the time frame
        while join_times and now - join_times[0] > TIME_FRAME:
            join_times.popleft()

        # Add the current join time
        join_times.append(now)

        # Check for raid condition
        if len(join_times) >= RAID_THRESHOLD:
            raid = True

            await plugin.app.rest.create_message(config.Bot.logs_channel, f"Raid detected! More than {RAID_THRESHOLD} members joined within {TIME_FRAME} seconds.")

            from bot import logger
            logger.warning(f"Raid detected! More than {RAID_THRESHOLD} members joined within {TIME_FRAME} seconds.")
        else:
            raid = False

        await update_captcha_status()

        if not raid:
            await member_managment.new_member(event, plugin.bot)
        
    except Exception as e:
        from bot import logger
        logger.error(f"Error during member join event: {e}")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
