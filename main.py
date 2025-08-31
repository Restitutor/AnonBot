#!/usr/bin/env python3
"""Main entry point for the Discord bot."""

import logging as logger
import random
from datetime import datetime, timedelta

import discord
from config import CHANNEL_ID, GUILD_ID, PREFIX, TOKEN

# Bot setup
bot = discord.Bot(
    allowed_mentions=discord.AllowedMentions.none(),
    intents=discord.Intents.none()
    | discord.Intents.message_content
    | discord.Intents.guilds
    | discord.Intents.dm_messages,
)

# Message tracking
LAST_MSG: dict[int, datetime] = {}
MESSAGE_PAIRS: dict[int, int] = {}  # Maps DM message ID to channel message ID
MINUTE = timedelta(minutes=1)

# User identification
ANIMAL_NAMES = [
    "Panda",
    "Koala",
    "Fox",
    "Otter",
    "Penguin",
    "Hamster",
    "Hedgehog",
    "Ferret",
    "Squirrel",
    "Raccoon",
]
AVAILABLE_ANIMALS = []
USER_ANIMALS: dict[int, str] = {}


def get_user_animal(user_id: int) -> str:
    """Get a cute animal name for a user ID."""
    if user_id not in USER_ANIMALS:
        if not AVAILABLE_ANIMALS:
            # If we somehow run out, just use "User" + number
            return f"User{len(USER_ANIMALS) + 1}"

        animal = AVAILABLE_ANIMALS.pop()
        USER_ANIMALS[user_id] = animal

    return USER_ANIMALS[user_id]


@bot.event
async def on_ready() -> None:
    """Called when the bot is ready."""
    global AVAILABLE_ANIMALS
    AVAILABLE_ANIMALS = ANIMAL_NAMES.copy()
    random.shuffle(AVAILABLE_ANIMALS)

    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        await bot.wait_until_ready()
        logger.info("Bot is fully initialized and ready")
    except Exception as e:
        logger.exception(f"Error during initialization: {e}")


@bot.listen("on_message")
async def on_text_message(message: discord.Message) -> None:
    """Processes incoming messages.

    Args:
        message: Discord message

    """
    # Ignore bot messages and non DMs
    if message.author.bot or isinstance(message.author, discord.member.Member):
        return

    try:
        # Get the target channel
        channel = await bot.fetch_channel(CHANNEL_ID)

        # Prepare message content with user animal
        user_animal = get_user_animal(message.author.id)
        msg = f"**{user_animal}:** {message.clean_content}"
        last_time = LAST_MSG.get(message.channel.id)

        # Add prefix if it's a new conversation (60+ minutes since last message)
        if not last_time or (datetime.now() - last_time) > timedelta(minutes=60):
            msg = f"**New {PREFIX}:**\n{msg}"

        # Send message and update tracking
        if disabled:
            await message.reply("Sorry the bot is disabled. Try again later.")
        else:
            channel_message = await channel.send(msg)
            MESSAGE_PAIRS[message.id] = channel_message.id
            LAST_MSG[message.channel.id] = datetime.now()

    except Exception as e:
        logger.exception(f"Error processing message: {e}")


disabled = False


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
    """Handles message edit events.

    Args:
        before: Original message
        after: Edited message

    """
    # Ignore bot messages and non DMs
    if after.author.bot or isinstance(after.author, discord.member.Member):
        return

    try:
        # Check if we have the message pair tracked
        if after.id in MESSAGE_PAIRS:
            channel = await bot.fetch_channel(CHANNEL_ID)
            channel_message = await channel.fetch_message(MESSAGE_PAIRS[after.id])

            # Prepare edited message content with user animal
            user_animal = get_user_animal(after.author.id)
            msg = f"**{user_animal}:** {after.clean_content}"

            # Preserve prefix if it exists
            if channel_message.content.startswith(f"**New {PREFIX}:**\n"):
                msg = f"**New {PREFIX}:**\n{msg}"

            # Update the channel message
            await channel_message.edit(content=msg)

    except Exception as e:
        logger.exception(f"Error processing message edit: {e}")


@bot.event
async def on_message_delete(message: discord.Message) -> None:
    """Handles message deletion events.

    Args:
        message: Deleted message

    """
    # Ignore bot messages and non DMs
    if message.author.bot or isinstance(message.author, discord.member.Member):
        return

    try:
        # Check if we have the message pair tracked
        if message.id in MESSAGE_PAIRS:
            channel = await bot.fetch_channel(CHANNEL_ID)
            channel_message = await channel.fetch_message(MESSAGE_PAIRS[message.id])

            # Prepare deleted message content with user animal
            user_animal = get_user_animal(message.author.id)
            msg = f"**{user_animal}:** [Deleted]"

            # Preserve prefix if it exists
            if channel_message.content.startswith(f"**New {PREFIX}:**\n"):
                msg = f"**New {PREFIX}:**\n{msg}"

            # Update the channel message
            await channel_message.edit(content=msg)

            # Remove from tracking
            del MESSAGE_PAIRS[message.id]

    except Exception as e:
        logger.exception(f"Error processing message deletion: {e}")


@bot.slash_command(
    name="toggle",
    guild_ids=[GUILD_ID],
    default_member_permissions=discord.Permissions(mute_members=True),
)
async def toggle(
    ctx: discord.ApplicationContext,
    mode: discord.Option(str, choices=["on", "off"]),
) -> None:
    """Toggles the bot on/off.

    Args:
        ctx: Application context
        mode: Toggle mode ("on" or "off")

    """
    global disabled
    disabled = mode == "off"
    await ctx.respond(f"The bot is now {mode}")


if __name__ == "__main__":
    try:
        logger.info("Starting bot")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Fatal error starting bot: {e}")
