import os
import logging
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
import openai
import openai.error

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set up Together.ai client with OpenAI-compatible SDK
client = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/"
)


@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    logging.info("FridayGPT (JARVIS-mode) is online as %s!", bot.user)

@bot.command(name="ask")
@commands.cooldown(1, 5, commands.BucketType)