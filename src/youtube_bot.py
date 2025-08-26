import asyncio
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
import feedparser
import yt_dlp


class YouTubeBot(commands.Bot):
    def __init__(self, data_handler, feed_checker, logger, event_queue):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.data_handler = data_handler
        self.feed_checker = feed_checker
        self.logger = logger
        self.event_queue = event_queue

    async def setup_hook(self) -> None:
        self.tree.add_command(app_commands.Command(
            name="ping",
            description="Check if I'm alive.",
            callback=self.ping
        ))
        self.tree.add_command(app_commands.Command(
            name="target-for-updates",
            description="Target this text channel for updates on subscribed YouTube channels. Limited to one text channel.",
            callback=self.target_for_updates
            )
        )
        self.tree.add_command(app_commands.Command(
            name="subscribe",
            description="Subscribe to a YouTube channel.",
            callback=self.subscribe
            )
        )
        self.tree.add_command(app_commands.Command(
            name="unsubscribe",
            description="Unsubscribe from a YouTube channel.",
            callback=self.unsubscribe
            )
        )
        self.tree.add_command(app_commands.Command(
            name="list-subscriptions", 
            description="List all YouTube channels to which you are currently subscribed.",
            callback=self.list_subscriptions
            )
        )
        self.tree.add_command(app_commands.Command(
            name="clear-subscriptions",
            description="Unsubscribe from all YouTube channels to which you are currently subscribed.",
            callback=self.clear_subscriptions
            )
        )
        self.tree.add_command(app_commands.Command(
            name="clear-target-channel",
            description="Untarget the text channel that is currently targeted for updates on subscribed YouTube channels.",
            callback=self.clear_target_dc_channel
            )
        )
        await self.tree.sync()
        self.loop.create_task(self.feed_checker.produce_events())
        self.loop.create_task(self.consume_events())

    async def on_ready(self) -> None:
        self.logger.log("STARTUP", "on_ready()", f"{self.user} successfully started.")
    
    async def on_guild_join(self, guild: discord.Guild):
        log_message = f"{guild.name} invited bot."
        self.logger.log("ALERT", "on_guild_join()", log_message)
    
    async def on_guild_remove(self, guild: discord.Guild):
        log_message = f"{guild.name} kicked bot."
        self.logger.log("ALERT", "on_guild_remove()", log_message)
        dc_server_id = str(guild.id)
        if self.data_handler.remove_dc_server(dc_server_id):
            log_message = f"{guild.name} successfully removed."
        else:
            log_message = f"{guild.name} has no data to remove."
        self.logger.log("ALERT", "on_guild_remove()", log_message)

    async def consume_events(self) -> None:
        while True:
            event = await self.event_queue.get()
            dc_server_id = event["dc_server_id"]

            dc_server = await self.safe_fetch_guild(dc_server_id)
            if not dc_server:
                continue

            target_dc_channel_id = self.data_handler.data["target_dc_channels"][dc_server_id]
            if not target_dc_channel_id:
                continue
            
            target_dc_channel = await self.safe_fetch_channel(target_dc_channel_id)
            if not target_dc_channel:
                continue

            message = f"{event["yt_channel_name"]} published a new video:\n{event["latest_video_link"]}"
            log_message = f"\"{message}\" -> {dc_server}/{target_dc_channel}"
            self.logger.log("MESSAGE", "consume_events()", log_message)
            await self.safe_send(target_dc_channel, message)
            self.event_queue.task_done()

    async def ping(self, interaction: discord.Interaction) -> None:
        message = "I'm alive."
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        self.logger.log("MESSAGE", "ping()", log_message)
        await interaction.response.send_message(message)

    async def target_for_updates(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        dc_server_id = str(interaction.guild.id)
        dc_channel_id = interaction.channel.id
        self.data_handler.add_target_dc_channel(dc_server_id, dc_channel_id)
        self.data_handler.save_data("target_dc_channels")
        message = "Targeting this text channel for updates."
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        self.logger.log("MESSAGE", "target_for_updates()", log_message)
        await interaction.followup.send(message)

    async def subscribe(self, interaction: discord.Interaction, yt_channel_name: str) -> None:
        await self.change_subscription(interaction, yt_channel_name, add=True)

    async def unsubscribe(self, interaction: discord.Interaction, yt_channel_name: str) -> None:
        await self.change_subscription(interaction, yt_channel_name, add=False)

    async def change_subscription(self, interaction: discord.Interaction, yt_channel_name: str, add: bool) -> None:
        await interaction.response.defer(thinking=True)

        yt_channel_id = self.get_yt_channel_id(yt_channel_name)
        if not yt_channel_id:
            message = f"Couldn't find {yt_channel_name}."
            log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
            self.logger.log("MESSAGE", "change_subscription()", log_message)
            await interaction.followup.send(message)
            return

        dc_server_id = str(interaction.guild.id)
        if dc_server_id not in self.data_handler.data["subscriptions"]:
            self.data_handler.add_dc_server(dc_server_id)

        if add:
            if self.is_subscribed(yt_channel_id, dc_server_id):
                message = f"Already subscribed to {yt_channel_name}."
            else:
                self.data_handler.add_subscription(yt_channel_id, dc_server_id)
                message = f"Successfully subscribed to {yt_channel_name}."
        else:
            if not self.is_subscribed(yt_channel_id, dc_server_id):
                message = f"Not subscribed to {yt_channel_name}."
            else:
                self.data_handler.remove_subscription(yt_channel_id, dc_server_id)
                message = f"Successfully unsubscribed from {yt_channel_name}."

        self.data_handler.save_data("subscriptions")
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        self.logger.log("MESSAGE", "change_subscription()", log_message)
        await interaction.followup.send(message)

    async def list_subscriptions(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if not self.dc_server_has_subscriptions(dc_server_id):
            message = "No subscriptions yet."
            log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
            self.logger.log("MESSAGE", "list_subscriptions()", log_message)
            await interaction.followup.send(message)
            return

        yt_channel_names = []
        for yt_channel_id in self.data_handler.data["subscriptions"][dc_server_id]:
            yt_channel_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_channel_id}"
            yt_channel_feed = feedparser.parse(yt_channel_url)
            if yt_channel_feed.feed and hasattr(yt_channel_feed.feed, "title"):
                yt_channel_name = yt_channel_feed.feed.title
            else:
                yt_channel_name = yt_channel_id

            yt_channel_names.append(f"- {yt_channel_name}")

        yt_channel_names.sort()
        message = "Subscribed channels:\n" + "\n".join(yt_channel_names)
        self.logger.log("MESSAGE", "list_subscriptions()", f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}")
        await interaction.followup.send(message)

    async def clear_subscriptions(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if self.data_handler.clear_subscriptions(dc_server_id):
            message = "Successfully cleared subscriptions."
        else:
            message = "No subscriptions yet."

        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        self.logger.log("MESSAGE", "clear_subscriptions()", log_message)
        await interaction.followup.send(message)

    async def clear_target_dc_channel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if self.data_handler.clear_target_dc_channel(dc_server_id):
            message = "Successfully cleared target channel."
        else:
            message = "No target channel yet."
        
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        self.logger.log("MESSAGE", "clear_target_dc_channel()", log_message)
        await interaction.followup.send(message)

    async def safe_send(self, target_dc_channel: discord.channel.TextChannel, message: str):
        try:
            await target_dc_channel.send(message)
        except Exception as e:
            log_message = str(e)
            self.logger.log("ERROR", "safe_send()", log_message)

    async def safe_fetch_guild(self, dc_server_id: str) -> discord.guild.Guild | None:
        try:
            dc_server = await self.fetch_guild(dc_server_id)
        except Exception as e:
            log_message = str(e)
            self.logger.log("ERROR", "safe_fetch_guild()", log_message)
            dc_server = None

        return dc_server

    async def safe_fetch_channel(self, target_dc_channel_id: str) -> discord.channel.TextChannel | None:
        try:
            target_dc_channel = await self.fetch_channel(target_dc_channel_id)
        except Exception as e:
            log_message = str(e)
            self.logger.log("ERROR", "safe_fetch_channel()", log_message)
            target_dc_channel = None

        return target_dc_channel

    def get_yt_channel_id(self, yt_channel_name: str) -> str | None:
        ydl_opts = {"quiet": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{yt_channel_name}", download=False)["entries"][0]
                return info["channel_id"]
            except:
                return None

    def is_subscribed(self, yt_channel_id: str, dc_server_id: str) -> bool:
        if yt_channel_id in self.data_handler.data["subscriptions"][dc_server_id]:
            return True
        else:
            return False

    def dc_server_has_subscriptions(self, dc_server_id: str) -> bool:
        if not self.data_handler.data["subscriptions"]:
            return False
        elif not self.data_handler.data["subscriptions"][dc_server_id]:
            return False
        else:
            return True
