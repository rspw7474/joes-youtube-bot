import discord
from discord import app_commands
from discord.ext import commands
from logger import logger


class YTBot(commands.Bot):
    def __init__(self, data_handler, event_queue, yt_channel_fetcher, yt_feed_checker):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.yt_channel_fetcher = yt_channel_fetcher
        self.yt_feed_checker = yt_feed_checker
        self.repo_link = "https://github.com/rspw7474/joes-youtube-bot"

    async def setup_hook(self) -> None:
        self.tree.add_command(app_commands.Command(
            name="ping",
            description="Check if I'm alive.",
            callback=self.ping
        ))
        self.tree.add_command(app_commands.Command(
            name="view-source-code",
            description="Receive a link to my GitHub repository.",
            callback=self.view_source_code
        ))
        self.tree.add_command(app_commands.Command(
            name="get-notifications",
            description="Get notifications about subscribed YouTube channels in this text channel (limited to one).",
            callback=self.target_for_notifications
        ))
        self.tree.add_command(app_commands.Command(
            name="stop-notifications",
            description="Stop getting notifications about subscribed YouTube channels.",
            callback=self.untarget_for_notifications
        ))
        self.tree.add_command(app_commands.Command(
            name="subscribe",
            description="Subscribe to a YouTube channel.",
            callback=self.subscribe
        ))
        self.tree.add_command(app_commands.Command(
            name="unsubscribe",
            description="Unsubscribe from a YouTube channel.",
            callback=self.unsubscribe
        ))
        self.tree.add_command(app_commands.Command(
            name="list-subscriptions", 
            description="List all YouTube channels to which you are currently subscribed.",
            callback=self.list_subscriptions
        ))
        self.tree.add_command(app_commands.Command(
            name="clear-subscriptions",
            description="Unsubscribe from all YouTube channels.",
            callback=self.clear_subscriptions
        ))
        await self.tree.sync()

    async def on_ready(self) -> None:
        self.loop.create_task(self.yt_feed_checker.produce_events())
        self.loop.create_task(self.consume_events())
        log_message = f"{self.user} successfully started."
        logger.info(log_message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        log_message = f"{guild.name} invited bot."
        logger.info(log_message)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        log_message = f"{guild.name} kicked bot."
        logger.info(log_message)

        dc_server_id = str(guild.id)
        if self.data_handler.remove_dc_server(dc_server_id):
            log_message = f"{guild.name} successfully removed."
        else:
            log_message = f"{guild.name} has no data to remove."

        logger.info(log_message)

    async def consume_events(self) -> None:
        while True:
            event = await self.event_queue.get()
            try:
                dc_server_id = event["dc_server_id"]
                dc_server = await self.get_dc_server(dc_server_id)
                if not dc_server:
                    continue

                target_dc_channel_id = self.data_handler.get_target_dc_channel(dc_server_id)
                if not target_dc_channel_id:
                    continue

                target_dc_channel = await self.get_dc_channel(target_dc_channel_id)
                if not target_dc_channel:
                    continue

                message = f"{event["yt_channel_name"]} published a new video:\n{event["latest_video_link"]}"
                log_message = f"\"{message}\" -> {dc_server}/{target_dc_channel}".replace("\n", " ")
                logger.info(log_message)
                await self.send_message(target_dc_channel, message)

            except Exception as e:
                log_message = str(e)
                logger.error(log_message)

            finally:
                self.event_queue.task_done()

    async def ping(self, interaction: discord.Interaction) -> None:
        message = "I'm alive."
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.response.send_message(message)

    async def view_source_code(self, interaction: discord.Interaction) -> None:
        message = self.repo_link
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.response.send_message(message)

    async def target_for_notifications(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        dc_channel_id = interaction.channel.id
        self.data_handler.add_target_dc_channel(dc_server_id, dc_channel_id)

        message = "You will get notifications in this text channel."
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.followup.send(message)

    async def untarget_for_notifications(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if self.data_handler.clear_target_dc_channel(dc_server_id):
            message = "You will no longer get notifications."
        else:
            message = "Not receiving notifications."

        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.followup.send(message)

    async def subscribe(self, interaction: discord.Interaction, yt_channel_name: str) -> None:
        await self.change_subscription(interaction, yt_channel_name, add=True)

    async def unsubscribe(self, interaction: discord.Interaction, yt_channel_name: str) -> None:
        await self.change_subscription(interaction, yt_channel_name, add=False)

    async def change_subscription(self, interaction: discord.Interaction, yt_channel_name: str, add: bool) -> None:
        await interaction.response.defer(thinking=True)

        yt_channel_id = self.yt_channel_fetcher.get_yt_channel_id(yt_channel_name)
        if not yt_channel_id:
            message = f"Couldn't find {yt_channel_name}."
            log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
            logger.info(log_message)
            await interaction.followup.send(message)
            return

        dc_server_id = str(interaction.guild.id)
        if add:
            if self.data_handler.add_subscription(yt_channel_id, dc_server_id):
                message = f"Successfully subscribed to {yt_channel_name}."
            else:
                message = f"Already subscribed to {yt_channel_name}."
        else:
            if self.data_handler.remove_subscription(yt_channel_id, dc_server_id):
                message = f"Successfully unsubscribed from {yt_channel_name}."
            else:
                message = f"Not subscribed to {yt_channel_name}."

        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.followup.send(message)

    async def list_subscriptions(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if not self.data_handler.list_subscriptions(dc_server_id):
            message = "No subscriptions yet."
            log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
            logger.info(log_message)
            await interaction.followup.send(message)
            return

        yt_channel_names = []
        for yt_channel_id in self.data_handler.list_subscriptions(dc_server_id):
            yt_channel_feed = self.yt_feed_checker.yt_feed_fetcher.get_yt_channel_feed(yt_channel_id)
            if yt_channel_feed.feed and hasattr(yt_channel_feed.feed, "title"):
                yt_channel_name = yt_channel_feed.feed.title
            else:
                yt_channel_name = yt_channel_id

            yt_channel_names.append(f"- {yt_channel_name}")

        yt_channel_names.sort()
        message = "Subscribed channels:\n" + "\n".join(yt_channel_names)
        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}".replace("\n", " ")
        logger.info(log_message)
        await interaction.followup.send(message)

    async def clear_subscriptions(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        dc_server_id = str(interaction.guild.id)
        if self.data_handler.clear_subscriptions(dc_server_id):
            message = "Successfully cleared subscriptions."
        else:
            message = "No subscriptions yet."

        log_message = f"\"{message}\" -> {interaction.guild.name}/{interaction.channel.name}"
        logger.info(log_message)
        await interaction.followup.send(message)

    async def send_message(self, target_dc_channel: discord.channel.TextChannel, message: str) -> None:
        await target_dc_channel.send(message)

    async def get_dc_server(self, dc_server_id: str) -> discord.guild.Guild | None:
        try:
            dc_server = await self.fetch_guild(dc_server_id)
            return dc_server
        except Exception as e:
            logger.error(e)
            return None

    async def get_dc_channel(self, target_dc_channel_id: str) -> discord.channel.TextChannel | None:
        try:
            target_dc_channel = await self.fetch_channel(target_dc_channel_id)
            return target_dc_channel
        except Exception as e:
            logger.error(e)
            return None
