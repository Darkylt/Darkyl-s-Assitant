import os
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config_reader as config


# Function to retrieve the latest video uploaded by a channel
async def get_latest_video(api_key, channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            order='date',
            maxResults=1
        )
        response = request.execute()
        if 'items' in response:
            if config.YouTube.check_frequency == 3600:
                config.YouTube.check_frequency == config.YouTube.provided_check_frequency
            return response['items'][0]
        else:
            return None
    except HttpError as e:
        # Check if the error is due to quota exceeded
        if e.resp.status == 403 and 'quotaExceeded' in str(e):
            from bot import logger
            logger.error("YouTube Quota exceeded.")
            config.YouTube.check_frequency = 3600
            return None
        else:
            raise

# Function to read the last video ID from a file
async def read_last_video_id():
    if os.path.exists(config.YouTube.last_uploaded_video_file):
        with open(config.YouTube.last_uploaded_video_file, 'r') as file:
            return file.read().strip()
    else:
        return None

# Function to write the last video ID to a file
async def write_last_video_id(video_id):
    with open(config.YouTube.last_uploaded_video_file, 'w') as file:
        file.write(video_id)

async def announce_last_video(latest_video, bot):
    id = latest_video['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={id}"

    video_title = latest_video['snipped']['title']

    message = f"**Darkyl** uploaded: [**{video_title}**]({video_url})\n\n<@&{config.YouTube.ping_role}>"

    await bot.application.app.rest.create_message(config.YouTube.discord_channel, message, role_mentions=True)

async def run(bot):
    API_KEY = config.YouTube.api_key
    CHANNEL_ID = config.YouTube.channel
    check_frequency = config.YouTube.check_frequency

    # Main loop to periodically check for new videos
    while True:
        last_video_id = await read_last_video_id()
        latest_video = await get_latest_video(API_KEY, CHANNEL_ID)
        if latest_video:
            video_id = latest_video['id']['videoId']
            if video_id != last_video_id:
                await announce_last_video(latest_video, bot)
                #print("New video uploaded:", latest_video['snippet']['title'])
                await write_last_video_id(video_id)
            else:
                pass
                #print("No new videos.")
        else:
            from bot import logger
            logger.error("Error: Could not retrieve latest video.")
        
        # Wait for some time before checking again
        await asyncio.sleep(check_frequency)
