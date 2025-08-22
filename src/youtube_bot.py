import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import feedparser
import yt_dlp
from data_handler import DataHandler
from feed_checker import FeedChecker


class YouTubeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.data_handler = DataHandler()
        self.feed_checker = FeedChecker(self, self.data_handler)

    async def setup_hook(self):
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
            description="Unsubscribe from all channels to which you are currently subscribed.",
            callback=self.clear_subscriptions
            )
        )
        self.tree.add_command(app_commands.Command(
            name="clear-target-channel",
            description="Untarget the text channel that is currently targeted for updates on subscribed YouTube channels.",
            callback=self.clear_target_channel
            )
        )
        await self.tree.sync()
        asyncio.create_task(self.feed_checker.check_feeds())

    async def on_ready(self):
        print(f"{self.user} successfully started.")
    
    def get_channel_id(self, channel_name: str) -> str | None:
        ydl_opts = {"quiet": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{channel_name}", download=False)["entries"][0]
                return info["channel_id"]
            except:
                return None
    
    async def target_for_updates(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        self.data_handler.data["target_channels"][guild_id] = interaction.channel.id
        self.data_handler.save_data("target_channels")
        await interaction.followup.send(f"Targeting this text channel for updates.")

    async def subscribe(self, interaction: discord.Interaction, channel_name: str):
        await self.change_subscription(interaction, channel_name, add=True)
    
    async def unsubscribe(self, interaction: discord.Interaction, channel_name: str):
        await self.change_subscription(interaction, channel_name, add=False)
    
    async def change_subscription(self, interaction: discord.Interaction, channel_name: str, add: bool):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        channel_id = self.get_channel_id(channel_name)

        if channel_id is None:
            await interaction.followup.send(f"Couldn't find {channel_name}.")
            return
        
        if guild_id not in self.data_handler.data["subscriptions"]:
            self.data_handler.data["subscriptions"][guild_id] = []
        
        if add:
            if channel_id in self.data_handler.data["subscriptions"][guild_id]:
                message = f"Already subscribed to {channel_name}."
            else:
                self.data_handler.data["subscriptions"][guild_id].append(channel_id)
                message = f"Successfully subscribed to {channel_name}."
        else:
            if channel_id not in self.data_handler.data["subscriptions"][guild_id]:
                message = f"Not subscribed to {channel_name}."
            else:
                self.data_handler.data["subscriptions"][guild_id].remove(channel_id)
                message = f"Successfully unsubscribed from {channel_name}."
        
        self.data_handler.save_data("subscriptions")
        await interaction.followup.send(message)

    async def list_subscriptions(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)

        if guild_id not in self.data_handler.data["subscriptions"] or not self.data_handler.data["subscriptions"][guild_id]:
            await interaction.followup.send("No subscriptions yet.")
            return

        channel_names = []
        for channel_id in self.data_handler.data["subscriptions"][guild_id]:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(url)
            if feed.feed and hasattr(feed.feed, "title"):
                channel_name = feed.feed.title
            else:
                channel_name = channel_id
            
            channel_names.append(f"- {channel_name}")
        
        channel_names.sort()
        await interaction.followup.send("Subscribed channels:\n" + "\n".join(channel_names))
    
    async def clear_subscriptions(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)

        if self.data_handler.clear_guild_subscriptions(guild_id):
            await interaction.followup.send(f"Successfully cleared subscriptions.")
        else:
            await interaction.followup.send(f"No subscriptions to clear.")
    
    async def clear_target_channel(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)

        if self.data_handler.clear_guild_target_channel(guild_id):
            await interaction.followup.send(f"Successfully cleared target channel.")
        else:
            await interaction.followup.send(f"No target channel to clear.")
