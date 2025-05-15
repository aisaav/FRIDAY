import asyncio
import os
import logging
import threading
import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import OpenAI, APIError
from discord import app_commands

# Load .env variables
load_dotenv()

# Retrieve API keys from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not TOGETHER_API_KEY or not DISCORD_TOKEN:
    raise EnvironmentError("Missing TOGETHER_API_KEY or DISCORD_TOKEN in environment variables.")

# Once here (line 21-ish)
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Important for full presence recognition

# Initialize bot
bot = commands.Bot(command_prefix="!!", intents=intents)
# And then again here (line 34-ish)
client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1"
)
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the OpenAI-compatible client for Together.ai
client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1"
)


@bot.event
async def on_ready():
    logging.info("FridayGPT is live as %s", bot.user)
    for guild in bot.guilds:
        logging.info(f"🛰️ Connected to: {guild.name} (ID: {guild.id})")

@bot.command(name="ask")
@commands.cooldown(1, 5, commands.BucketType.user)  # 1 request per user every 5 seconds
async def ask(ctx, *, prompt: str):
    logging.info(f"Received !ask from {ctx.author}: {prompt}")
    async with ctx.typing():
        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FRIDAYGPT—a powerful AI assistant designed by a Latina Tony Stark with adhd and a passion for ai ethics"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.85
            )
            answer = response.choices[0].message.content.strip()
            if not answer:
                logging.warning(
                    "🕳️ Empty response received from Together API.")
                await ctx.send("⚠️ Sorry, I didn’t get anything back from the AI. Try again.")
                return
            # ✂️ Discord has a 2000 character limit per message
            max_chunk_size = 1999
            chunks = [answer[i:i + max_chunk_size]
                      for i in range(0, len(answer), max_chunk_size)]
            for chunk in chunks:
                await ctx.send(chunk)
                logging.info("✅ Sent a response chunk.")
                await asyncio.sleep(1.5)  # Ensure you're under 1 request/sec
            logging.info(f"✅ Responded to {ctx.author.display_name}")
        except RateLimitError:
            await ctx.send("🚫 Whoa there! I'm getting rate-limited. Try again in a few seconds.")
            return
        except Exception as e:
            logging.exception("Unexpected error:")
            await ctx.send("⚠️ An unexpected error occurred.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ You're using that too fast! Try again in {error.retry_after:.1f}s.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You missed an argument. Try `!ask your question here`.")
    elif isinstance(error, commands.CommandNotFound):
        return  # Optional: ignore unknown commands silently
    else:
        logging.exception("Unhandled command error:")
        await ctx.send(f"❌ An unexpected error occurred: `{type(error).__name__}`")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong! FRIDAY is alive.")

# Run the bot
if __name__ == "__main__":
    print("Starting bot...")

    def heartbeat():
        while True:
            logging.info("🩺 Bot still alive...")
            time.sleep(60)

    threading.Thread(target=heartbeat, daemon=True).start()
    bot.run(DISCORD_TOKEN)
