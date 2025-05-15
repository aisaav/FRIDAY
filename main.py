import asyncio
import os
import logging
import threading
import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import OpenAI, APIError, RateLimitError
from discord import app_commands

# Load .env variables
load_dotenv()

# Retrieve API keys from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not TOGETHER_API_KEY or not DISCORD_TOKEN:
    raise EnvironmentError(
        "Missing TOGETHER_API_KEY or DISCORD_TOKEN in environment variables.")

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
@commands.cooldown(1, 5, commands.BucketType.user)
async def ask(ctx, *, prompt: str = None):
    if not prompt:
        await ctx.send("⚠️ You need to provide a prompt! Try `!!ask your question here`.")
        return

    logging.info(f"Received !ask from {ctx.author}: {prompt}")

    async with ctx.typing():
        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FRIDAYGPT, a Latina Tony Stark-inspired AI assistant with ADHD and a passion for AI ethics."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.85
            )

            answer = response.choices[0].message.content.strip()

            if not answer:
                await ctx.send("⚠️ I didn't get a useful response back from Together.ai.")
                return

            logging.info("📤 Sending prompt to Together.ai...")
            response = client.chat.completions.create(...)
            logging.info("✅ Received response")

            answer = response.choices[0].message.content.strip()
            logging.info(f"🧠 Answer processed: {answer[:60]}...")

            # Chunking & sending response
            for i in range(0, len(answer), 1999):
                logging.info(f"📤 Sending chunk: {i}")
                await ctx.send(answer[i:i+1999])
                await asyncio.sleep(1)

        except RateLimitError:
            await ctx.send("🚫 I'm being rate-limited. Please try again in a moment.")
        except NameError as e:
            logging.error(f"⚠️ NameError: {e}")
            await ctx.send("❌ A variable I tried to use wasn't defined. Bug noted!")
        except Exception as e:
            logging.exception("🚨 Unhandled exception:")
            await ctx.send("❌ An unexpected error occurred inside the command.")


@bot.event
async def on_command_error(ctx, error):
    logging.error(
        f"❌ Command error: {error.__class__.__name__} - {str(error)}")

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ You're using that too fast! Try again in {error.retry_after:.1f}s.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You missed an argument. Try `!!ask your question here`.")
    elif isinstance(error, commands.CommandNotFound):
        return  # Silently ignore unknown commands
    elif isinstance(error, commands.CommandInvokeError):
        # NEW: log inner error for visibility
        inner_error = error.original
        logging.exception("🚨 Inner error:")
        await ctx.send(f"❌ An unexpected error occurred inside the command: `{type(inner_error).__name__}`")
    else:
        logging.exception("⚠️ Unhandled command error:")
        await ctx.send(f"❌ Unexpected error: `{type(error).__name__}`")


@bot.command(name="ping")
async def ping(ctx):
    if ctx.guild is None:
        return  # skip DMs if needed
    await ctx.send("🏓 Pong! FRIDAY is alive.")


@bot.event
async def on_message(message):
    logging.info(f"📥 Received: {message.author}: {message.content}")
    await bot.process_commands(message)  # Don’t forget this or commands break


# Run the bot
if __name__ == "__main__":
    logging.info("🔥 main.py loaded")
    print("Starting bot...")

    def heartbeat():
        while True:
            logging.info("🩺 Bot still alive...")
            time.sleep(60)

    threading.Thread(target=heartbeat, daemon=True).start()
    bot.run(DISCORD_TOKEN)
