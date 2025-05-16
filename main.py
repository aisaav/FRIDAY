import psutil
import datetime
import asyncio
import os
import logging
import threading
import time
import traceback
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import OpenAI, RateLimitError

# Load environment variables
load_dotenv()

# API Keys
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not TOGETHER_API_KEY or not DISCORD_TOKEN:
    raise EnvironmentError("Missing TOGETHER_API_KEY or DISCORD_TOKEN in .env")

# Initialize Together client
client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1"
)

# Configure bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!!", intents=intents)

logging.basicConfig(
    filename='friday.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


start_time = datetime.datetime.utcnow()


@bot.command(name="status")
async def status(ctx):
    current_time = datetime.datetime.utcnow()
    uptime = str(current_time - start_time).split('.')[0]

    # Memory usage
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # MB

    embed = discord.Embed(
        title="🛰️ FRIDAYGPT Status",
        color=discord.Color.purple()
    )
    embed.add_field(name="🕒 Uptime", value=uptime, inline=True)
    embed.add_field(name="📡 Connected Servers",
                    value=len(bot.guilds), inline=True)
    embed.add_field(name="💾 Memory Usage", value=f"{mem:.2f} MB", inline=True)
    embed.set_footer(text="AI with ADHD. Powered by LLaMA on Together.ai")

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    logging.info("FridayGPT is live as %s", bot.user)
    for guild in bot.guilds:
        logging.info(f"Ὧ0️ Connected to: {guild.name} (ID: {guild.id})")


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
                    {"role": "system", "content": "You are FRIDAYGPT, a Latina Tony Stark-inspired AI assistant with a passion for AI ethics. You act like Jarvis from iron man, do not assume genders"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.85
            )

            answer = response.choices[0].message.content.strip()

            if not answer:
                await ctx.send("⚠️ No response received from the model. Please try again.")
                return

            for i in range(0, len(answer), 1999):
                await ctx.send(answer[i:i+1999])
                await asyncio.sleep(1)

        except RateLimitError:
            logging.warning("⚠️ Rate limit hit")
            await ctx.send("🚫 I'm being rate-limited. Please wait a few seconds and try again.")

        except NameError as e:
            logging.error(f"❌ NameError: {e}")
            traceback.print_exc()
            await ctx.send("❌ A variable was missing. This bug has been noted.")

        except Exception as e:
            logging.exception("🚨 Unexpected error in ask():")
            await ctx.send(f"❌ An unexpected error occurred inside the command.")


@bot.event
async def on_command_error(ctx, error):
    logging.error(f"❌ Command error: {type(error).__name__} - {error}")

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ You're using that too fast! Try again in {error.retry_after:.1f}s.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing argument. Try `!!ask your question`.")
    elif isinstance(error, commands.CommandNotFound):
        return  # Silent ignore
    elif isinstance(error, commands.CommandInvokeError):
        if hasattr(error, "original"):
            logging.exception("🚨 Inner error:")
            await ctx.send(f"❌ An unexpected error occurred inside the command: `{type(error.original).__name__}`")
        else:
            await ctx.send(f"❌ Command failed with: `{type(error).__name__}`")
    else:
        logging.exception("⚠️ General command error:")
        await ctx.send(f"❌ Unexpected error: `{type(error).__name__}`")


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
