# About
Joe's YouTube Bot is a Discord bot for interfacing with YouTube. It allows a Discord server to function like a Google Account by subscribing to YouTube channels and receiving updates about them.
<br><br>

# Setup
### Invite the bot to a Discord server.
1. Click this [invite link.](https://discord.com/oauth2/authorize?client_id=1407095826551013558&permissions=2048&integration_type=0&scope=bot+applications.commands)
2. Select the Discord server to which you want to invite the bot.
3. Click `Continue`.
4. Ensure the `Send Messages` permission is selected.
5. Click `Authorize`.

### Set up YouTube channel updates.
By default, the bot doesn't send updates on subscribed YouTube channels.\
Run `/target-for-updates` in a text channel to target it for updates. Only one text channel can be targeted at a time.\
Updates include notifications when subscribed YouTube channels publish new videos, complete with links and embedded videos.

### Set up permissions and integrations (optional).
#### Permissions
You may want to configure a text channel so that only the bot can send messages in it. To do this:
1. Right-click on the text channel.
2. Click `Edit Channel`.
3. Click `Permissions` in the left pane.
4. Under `Advanced Permissions`, click the `@everyone` role.
5. Under `Text Channel Permissions`, click the red X next to `Send Messages`.
6. Click the `Joe's YouTube Bot` role.
7. Under `Text Channel Permissions`, click the green check mark next to `Send Messages`.

#### Integrations
To configure integrations:
1. Right-click the server icon or name.
2. Hover over `Server Settings`.
3. Click `Integrations`.
4. Under `Bots and Apps`, click `Joe's YouTube Bot`.
5. From this menu, you can configure the bot so that its commands can only be run by certain members or in certain text channels.
<br><br>

# Usage
### `/ping`
Check if the bot is running.

### `/target-for-updates`
Run in a text channel to target it for updates. The bot will send updates on subscribed YouTube channels to that text channel.

### `/subscribe` `<yt_channel_name>`
Subscribe to a YouTube channel.

**Note**:\
On rare occasions, this command subscribes to unexpected YouTube channels. If this happens, provide the channel's handle (without the @ symbol) instead of its name. A channel's handle can be found on its channel page underneath the name. For example, running `/subscribe` `saba` might subscribe to Saba Pivot the rapper instead of saba the VTuber. In this case, running `/subscribe` `SamekoSaba` is a workaround. This problem sometimes occurs because of the way `yt_dlp` resolves channel names to channel IDs.

### `/unsubscribe` `<yt_channel_name>`
Unsubscribe from a YouTube channel.

### `/list-subscriptions`
List all YouTube channels to which you are currently subscribed.

### `/clear-subscriptions`
Unsubscribe from all YouTube channels to which you are currently subscribed.

### `/clear-target-channel`
Untarget the text channel that is currently targeted for updates on subscribed YouTube channels. You won't receive updates until a text channel is targeted using `/target-for-updates`.
<br><br>

# Built Using
### discord.py
- [repository](https://github.com/Rapptz/discord.py?tab=readme-ov-file)
- [documentation](https://discordpy.readthedocs.io/en/stable/)
### feedparser
- [repository](https://github.com/kurtmckee/feedparser)
- [documentation](https://feedparser.readthedocs.io/en/stable/)
### yt-dlp
- [repository](https://github.com/yt-dlp/yt-dlp)
- [documentation](https://pypi.org/project/yt-dlp/)