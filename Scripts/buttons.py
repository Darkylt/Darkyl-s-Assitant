import os
import json
import datetime
import random

import hikari.errors
import miru
import hikari
import miru.text_input
import miru.view
import lightbulb

import config_reader as config
import member_managment
import bot_utils as utils
import database_interaction

class ManageViews:
    async def start_views(client, views):
        for view in views:
            client.start_view(view(), bind_to=None)

class VerifyView(miru.View):

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @miru.button(label="Click me to verify!", style=hikari.ButtonStyle.SUCCESS, custom_id="verify")
    async def basic_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            return
        
        if any(num == config.Bot.verified_role for num in ctx.member.role_ids):
            await ctx.respond("You are already verified :)", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.member.add_role(config.Bot.verified_role)
        await ctx.respond("You are now verified!\nHave fun :)", flags=hikari.MessageFlag.EPHEMERAL)

class ReactionRoles():
    class Descriptor(miru.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)
        
        @miru.button(label="Gamer", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_gamer")
        async def gamer_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.gamer_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Musician", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_musician")
        async def musician_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.musician_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="DJ", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_dj")
        async def dj_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.dj_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Photographer", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_photographer")
        async def photographer_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.photographer_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Content Creator", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_content_creator")
        async def content_creator_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.content_creator_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Visual Artist", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_visual_artist")
        async def visual_artist_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.visual_artist_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
    
    class Pronouns(miru.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)
        @miru.button(label="He/Him", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_he_him")
        async def he_him_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.he_him_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="She/Her", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_she_her")
        async def she_her_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.she_her_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="They/Them", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_they_them")
        async def they_them_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.they_them_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Other (ask)", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_other_ask")
        async def other_ask_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.other_ask_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Skibidy/Toilet", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_skibidy_toilet")
        async def skibidy_toilet_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.skibidy_toilet_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            

            if ctx.author.id == 175892694952837120:
                return

            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
    
    class Region(miru.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)
        @miru.button(label="North America", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_north_america")
        async def north_america_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.north_america_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="South America", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_south_america")
        async def south_america_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.south_america_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Europe", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_europe")
        async def europe_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.europe_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Asia", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_asia")
        async def asia_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.asia_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Africa", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_africa")
        async def africa_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.africa_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
        
        @miru.button(label="Oceania/Australia", style=hikari.ButtonStyle.PRIMARY, custom_id="reaction_roles_oceania_australia")
        async def australia_button(self, ctx: miru.ViewContext, button: miru.Button, role=config.ReactionRoles.oceania_australia_role) -> None:
            if ctx.author.is_bot or ctx.author.is_system:
                return
            
            if any(num == role for num in ctx.member.role_ids):
                await ctx.member.remove_role(role)
                await ctx.respond(f"Removed the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)
                return
            
            await ctx.member.add_role(role)
            await ctx.respond(f"Added the <@&{role}> role :)", flags=hikari.MessageFlag.EPHEMERAL)

async def find_key_by_report_message(report_message: int, return_reporter=False):
        with open(Report.reports_path, "r") as file:
            json_data = json.load(file)
        for main_key, values in json_data.items():
            for reason_key, reason_value in values["reasons"].items():
                if reason_value["report_message"] == report_message:
                    if return_reporter:
                        reporter = reason_value["reporter"]
                        return main_key, reason_key, reporter
                    return main_key, reason_key
        return None

class Report(miru.View):
    reports_path = os.path.join(config.Bot.data_folder, "User Data", "reports.json")
    
    def __init__(self) -> None:
            super().__init__(timeout=None)

    @miru.button(label="Warn", style=hikari.ButtonStyle.DANGER, custom_id="report_warn")
    async def warn_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not ctx.author.is_bot or not ctx.author.is_system:
            key = await find_key_by_report_message(ctx.message.id, True)

            if key == None:
                await ctx.respond("Couldn't find the report in the database.")
                return
            else:
                user_id, reason, reporter = key

            database_path = os.path.join(config.Bot.data_folder, "User Data", "warnings.json")
            if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
                with open(database_path, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}

            # Check if user already exists in the data dictionary
            if user_id in data:
                # Append new reason to existing list of reasons
                data[user_id].append(reason)
            else:
                # Create a new entry with the user ID and a list containing the new reason
                data[user_id] = [reason]
            
            if len(data.get(user_id, [])) > 2 and len(data.get(user_id, [])) < 4:
                await ctx.client.app.rest.kick_user(ctx.guild_id, user_id, reason="Too many warnings.")
                from bot import Logging
                await Logging.log_message(f"User <@{user_id}> has been kicked.")
                await ctx.respond(f"Warned <@{user_id}> for '{reason}'.\n\n(User was kicked for too many warnings)")
            elif len(data.get(user_id, [])) > 4:
                await ctx.client.app.rest.ban_user(ctx.guild_id, user_id, reason="Too many warnings.")
                from bot import Logging
                await ctx.respond(f"Warned <@{user_id}> for '{reason}'.\n\n(User was banned for too many warnings)")
            else:
                await ctx.respond(f"Warned <@{user_id}> for '{reason}'.")
            
            reporter = await ctx.client.app.rest.fetch_user(reporter)
            embed = hikari.Embed(title="Update on your report", description=f"Your report of <@{user_id}> for '{reason}' has been processed by our mods.", color=hikari.Color.from_hex_code("#fc0000"))
            embed.add_field(name="Update:", value=f"<@{user_id}> received a warning.")
            reporter.send()
    
    @miru.button(label="Kick", style=hikari.ButtonStyle.DANGER, custom_id="report_kick")
    async def kick_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            return
        
        key = await find_key_by_report_message(ctx.message.id, True)

        if key == None:
                await ctx.respond("Couldn't find the report in the database.")
                return
        else:
            user_id, reason, reporter = key
        
        try:
            await ctx.client.app.rest.kick_user(config.Bot.server, user_id, reason=reason)
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have permission to kick that user.")
            return

        await ctx.respond(f"Kicked <@{user_id}> for '{reason}'.")

        from bot import Logging
        await Logging.log_message(f"User <@{user_id}> has been kicked.")

        reporter = await ctx.client.app.rest.fetch_user(reporter)
        embed = hikari.Embed(title="Update on your report", description=f"Your report of <@{user_id}> for '{reason}' has been processed by our mods.", color=hikari.Color.from_hex_code("#fc0000"))
        embed.add_field(name="Update:", value=f"<@{user_id}> has been kicked.")
        reporter.send()

    @miru.button(label="Ban", style=hikari.ButtonStyle.DANGER, custom_id="report_ban")
    async def ban_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            return

        key = await find_key_by_report_message(ctx.message.id, True)

        if key == None:
                await ctx.respond("Couldn't find the report in the database.")
                return
        else:
            user_id, reason, reporter = key
        
        try:
            await ctx.client.app.rest.ban_user(config.Bot.server, user_id, reason=reason)
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have permission to ban that user.")
            return

        await ctx.respond(f"Banned <@{user_id}> for '{reason}'.")

        from bot import Logging
        await Logging.log_message(f"User <@{user_id}> has been banned.")

        reporter = await ctx.client.app.rest.fetch_user(reporter)
        embed = hikari.Embed(title="Update on your report", description=f"Your report of <@{user_id}> for '{reason}' has been processed by our mods.", color=hikari.Color.from_hex_code("#fc0000"))
        embed.add_field(name="Update:", value=f"<@{user_id}> has been banned.")
        reporter.send()

    @miru.button(label="Ignore", style=hikari.ButtonStyle.SECONDARY, custom_id="report_ignore")
    async def ignore_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            return
        
        message_id = ctx.message.id
        
        database_path = os.path.join(config.Bot.data_folder, "User Data", "reports.json")
        
        # Load the data from warnings.json
        with open(database_path, 'r') as file:
            warnings_data = json.load(file)
        
        # Iterate over each user entry in the data
        for user_id, user_data in warnings_data.items():
            # Iterate over each reason in the user's data
            for reason, reason_data in user_data["reasons"].items():
                # Check if the report_message matches the message id
                if reason_data["report_message"] == message_id:
                    # Remove the reason
                    del warnings_data[user_id]["reasons"][reason]
                    break  # Exit the inner loop once the reason is found
        
        # Write the updated data back to warnings.json
        with open(database_path, 'w') as file:
            json.dump(warnings_data, file, indent=4)
        
        await ctx.respond("Report has been ignored.")

class Worm(miru.View):

    def __init__(self) -> None:
            super().__init__(timeout=None)
    
    @miru.button(label="Stop worm", style=hikari.ButtonStyle.DANGER, custom_id="stop_worm")
    async def worm_stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            return

        if not config.Bot.worm_is_running:
            await ctx.respond("There is no worm running...")
            return
        
        from Worm.worm_simulator import stop_the_worm

        await stop_the_worm()

        await ctx.message.edit(content="Worm stopped.", embeds=[], attachments=[], components=[])

        config.Bot.worm_is_running = False

class Rules(miru.View):
    tos = miru.LinkButton(url="https://discord.com/terms", label="📰Terms of Service")
    guidelines = miru.LinkButton(url="https://discord.com/guidelines", label="📚Guidelines")

class Scam(miru.View):
    scam = miru.LinkButton(url="https://discord.com/terms", label="General Tips to Protect Against Spam and Hacking")

class ModMenu(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(label="Warn", style=hikari.ButtonStyle.DANGER, custom_id="mod_menu_warn", row=0)
    async def warn_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This can only be run by humans.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        mentions = ctx.message.content
        
        # Remove first two and last characters
        mentions = mentions[2:-1]
        
        # Convert to integer
        try:
            mentions_int = int(mentions)
        except ValueError:
            await ctx.respond("Invalid format for mentions.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        id = await utils.generate_id()

        if not await member_managment.warn_member(user_id=mentions_int, reason=f"Warned from ModMenu {id}"):
            await ctx.respond("Failed to warn member. Most likely missing permissions.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.respond("Warned member.", flags=hikari.MessageFlag.EPHEMERAL)
    
    @miru.button(label="Kick", style=hikari.ButtonStyle.DANGER, custom_id="mod_menu_kick", row=0)
    async def kick_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This can only be run by humans.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        mentions = ctx.message.content
        
        # Remove first two and last characters
        mentions = mentions[2:-1]
        
        # Convert to integer
        try:
            mentions_int = int(mentions)
        except ValueError:
            await ctx.respond("Invalid format for mentions.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        try:
            await ctx.client.app.rest.kick_member(ctx.guild_id, mentions_int, reason="Kicked manually by a Moderator.")
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have the permissions to kick that member.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.respond("Banned member.", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(label="Ban", style=hikari.ButtonStyle.DANGER, custom_id="mod_menu_ban", row=0)
    async def ban_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:

        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This can only be run by humans.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        mentions = ctx.message.content
        
        # Remove first two and last characters
        mentions = mentions[2:-1]
        
        # Convert to integer
        try:
            mentions_int = int(mentions)
        except ValueError:
            await ctx.respond("Invalid format for mentions.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        try:
            await ctx.client.app.rest.ban_member(ctx.guild_id, mentions_int, reason="Banned manually by a Moderator.")
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have the permissions to ban that member.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        await ctx.respond("Banned member.", flags=hikari.MessageFlag.EPHEMERAL)
    
    timeout_options = {
        "Timeout for: 1 Hour": 3600,
        "Timeout for: 2 Hours": 7200,
        "Timeout for: 5 Hours": 18000,
        "Timeout for: 1 Day": 86400,
        "Timeout for: 2 Days": 172800,
        "Timeout for: 3 Days": 259200,
        "Timeout for: 1 Week": 604800,
        "Timeout for: 2 Weeks": 1209600,
        "Timeout for: 3 Weeks": 1814400,
        "Timeout for: 28 Days": 16934399
    }

    @miru.text_select(placeholder="Timeout a User", options=[
        miru.SelectOption(label=label) for label in timeout_options.keys()
    ], custom_id="mod_menu_timeout", row=1)
    async def timeout_select(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This can only be run by humans.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        selected = str(select.values)[2:-2]
        timeout_seconds = ModMenu.timeout_options[selected]

        now = datetime.datetime.now()
        then = now + datetime.timedelta(seconds=timeout_seconds)

        if (then - now).days > 28:
            await ctx.respond("You can't time someone out for more than 28 days", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        mentions = str(ctx.message.content)[2:-1]

        try:
            mentions_int = int(mentions)
        except ValueError:
            await ctx.respond("Invalid format for mentions.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        try:
            await ctx.client.app.rest.edit_member(user=mentions_int, guild=ctx.get_guild(), communication_disabled_until=then, reason="Timed out manually by a Moderator.")
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have the permissions to timeout that member.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.respond("Timed out member.", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(label="Clear Warnings", style=hikari.ButtonStyle.PRIMARY, custom_id="mod_menu_clear_warnings", row=2)
    async def clear_warnings_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This can only be run by humans.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        user_id = str(ctx.message.content)[2:-1]

        database_path = os.path.join(config.Bot.data_folder, "User Data", "warnings.json")
        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        if user_id in data:
            del data[user_id]
        
        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)
        
        await ctx.respond(f"Successfully removed all warnings.", flags=hikari.MessageFlag.EPHEMERAL)

class NSFWOptOut(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @miru.button(label="Opt Out of NSFW", style=hikari.ButtonStyle.DANGER, custom_id="nsfw_opt_out")
    async def nsfw_opt_out_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        user_id = ctx.author.id

        if database_interaction.update_nsfw_status(user_id, True):
            await ctx.respond("Successfully opted out!", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await ctx.respond(f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL)

class NSFWOptIn(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @miru.button(label="Opt into NSFW", style=hikari.ButtonStyle.DANGER, custom_id="nsfw_opt_in")
    async def nsfw_opt_out_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        user_id = ctx.author.id

        if database_interaction.update_nsfw_status(user_id, False):
            await ctx.respond("Successfully opted in!", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await ctx.respond(f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL)

ROCK = 1
PAPER = 2
SCISSORS = 3

class RockPaperScissors(miru.View):
    def __init__(self) -> None:
            super().__init__(timeout=None)

    win_msg = [
        "You got lucky this time!",
        "Enjoy the win, it won't happen again!",
        "Even a broken clock is right twice a day.",
        "Don't get used to it, I'll win next time!",
        "You win this round, but I'll be back!",
        "Well played... for now.",
        "Savor this victory, it's a rare one!",
        "Congrats, but don't get too cocky!",
        "You got me this time, but I'm coming for you!",
        "A fluke, I'm sure. Let's go again!",
        "You win... this time. Don't get comfortable.",
        "Beginner's luck! I'll get you next round.",
        "Enjoy it while it lasts!",
        "You may have won this battle, but not the war!",
        "I'll admit defeat, but it won't happen again!",
        "Nice one! Don't expect it to happen often.",
        "Well done! Let's see if you can do it twice.",
        "A lucky break, nothing more!",
        "Don't get used to it. I'll win the next one!",
        "Fine, you got me. Rematch?",
        "This isn't over! I'm coming for you next time!",
        "You got the best of me this round, but I'm not done yet!",
        "A temporary setback. I'll bounce back!",
        "Okay, you win. But I'll be back stronger!",
        "Alright, you got me. But just wait for the next round!",
        "You may have won this round, but I'm not giving up!",
        "Good job! Let's see if you can keep it up!",
        "I'll let you have this one. Enjoy it while it lasts!",
        "Fine, you win. Let's see how long that lasts!"
                
    ]

    tie_msg = [
        "A tie? Really? How boring!",
        "Wow, a tie! Guess we think alike. Scary!",
        "A tie? Well, that was anticlimactic.",
        "Looks like we're evenly matched... for now.",
        "A tie? Meh, I was hoping for a win.",
        "We both chose the same? Lame!",
        "Tie game! You got lucky... this time.",
        "A tie? That's no fun!",
        "Well, well, well... it's a tie. How original.",
        "A tie? Guess we're both pretty smart. Or not.",
        "Tie? I expected more of a challenge.",
        "Seriously? A tie? How predictable.",
        "Great minds think alike, I guess. Boring!",
        "A tie? We need to break this stalemate!",
        "Tie game! Let's see you try to beat me next time.",
        "A tie? How disappointing.",
        "We tied? I demand a rematch!",
        "Looks like we're on the same wavelength... unfortunately.",
        "A tie? That's just delaying my inevitable win.",
        "Well, it's a tie. What a letdown."
    ]

    lose_msg = [
        "Haha! I win! Better luck next time! *(You're gonna need it!)*",
        "I gotcha! I'm so lucky!",
        "YES! I WON!!!",
        "Too easy! Let's play again!",
        "Another win in the bag! Want to try again?",
        "Haha, I knew you'd pick that! Better luck next round!",
        "Gotcha! I must be a mind reader!",
        "Nice try, but I came out on top!",
        "You put up a good fight, but I still won!",
        "Yes! Another win for me!",
        "Too bad! I've got the magic touch.",
        "Too easy! Maybe next time, champ.",
        "Oh snap! Did you really think you had a chance?",
        "Better luck next time, rookie!",
        "Is that all you've got? Pathetic!",
        "You call that a challenge? Try again.",
        "Nice try! But not nice enough.",
        "Did you really think you could beat me? Think again!",
        "Come on, you can do better than that! Or can you?",
        "Gotcha! You never stood a chance!",
        "Ha! Predictable! Better luck next time!",
        "Crushed it! Feeling lucky yet?",
        "Smoked ya! Maybe practice a bit more?",
        "Boom! Victory is mine!",
        "Too easy! Maybe try harder next time?",
        "Another one bites the dust! Keep trying!",
        "Told you I'm unbeatable! Want to go again?"
    ]

    CHOICES = {
        ROCK: "🪨 Rock",
        PAPER: "📄 Paper",
        SCISSORS: "✂️ Scissors"
        }

    async def choose(user_choice: int) -> int:
        """
        Chooses either rock paper or scissors

        1: Rock
        2: Paper
        3: Scissors
        """

        cheat = False
        always_loose = False
        always_tie = False

        if cheat:
            return {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}[user_choice]
        if always_loose:
            return {ROCK: SCISSORS, PAPER: ROCK, SCISSORS: PAPER}[user_choice]
        if always_tie:
            return user_choice
        
        return random.randint(1, 3)

    async def handle_choice(self, ctx: miru.ViewContext, user_choice: int) -> None:
        bot_choice = await RockPaperScissors.choose(user_choice)

        # Define constants for colors
        WIN_COLOR = 0x00FF00  # Green
        LOSE_COLOR = 0xFF0000  # Red
        TIE_COLOR = 0xFFFF00  # Yellow

        result_message = {
            (ROCK, ROCK): ("We tie", random.choice(self.tie_msg), TIE_COLOR),
            (ROCK, PAPER): ("You lose", random.choice(self.lose_msg), LOSE_COLOR),
            (ROCK, SCISSORS): ("You win", random.choice(self.win_msg), WIN_COLOR),
            (PAPER, ROCK): ("You win", random.choice(self.win_msg), WIN_COLOR),
            (PAPER, PAPER): ("We tie", random.choice(self.tie_msg), TIE_COLOR),
            (PAPER, SCISSORS): ("You lose", random.choice(self.lose_msg), LOSE_COLOR),
            (SCISSORS, ROCK): ("You lose", random.choice(self.lose_msg), LOSE_COLOR),
            (SCISSORS, PAPER): ("You win", random.choice(self.win_msg), WIN_COLOR),
            (SCISSORS, SCISSORS): ("We tie", random.choice(self.tie_msg), TIE_COLOR),
        }

        result, message, color = result_message[(user_choice, bot_choice)]

        embed = hikari.Embed(
            title="Rock Paper Scissors!",
            description=f"'**{self.CHOICES[user_choice]}**' vs '**{self.CHOICES[bot_choice]}**'\n{result}!\n{message}",
            color=color
        )

        view=RockPaperScissorsReplay()

        await ctx.message.edit(content="", embed=embed, components=view)

    @miru.button(label="Rock", style=hikari.ButtonStyle.SECONDARY, custom_id="rps_rock")
    async def rock_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await self.handle_choice(ctx, ROCK)

    @miru.button(label="Paper", style=hikari.ButtonStyle.SECONDARY, custom_id="rps_paper")
    async def paper_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await self.handle_choice(ctx, PAPER)

    @miru.button(label="Scissors", style=hikari.ButtonStyle.SECONDARY, custom_id="rps_scissors")
    async def scissors_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await self.handle_choice(ctx, SCISSORS)

class RockPaperScissorsReplay(miru.View):
    def __init__(self) -> None:
            super().__init__(timeout=None)

    @miru.button(label="Replay", style=hikari.ButtonStyle.SUCCESS, custom_id="rps_replay")
    async def replay_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:

        view=RockPaperScissors()

        await ctx.message.edit(content="Choose your option!", embeds=[], components=view)
