import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import OpenAI, APIError

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
client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1"
)

@bot.event
async def on_ready():
    logging.info("✅ FridayGPT is live as %s!", bot.user)

@bot.command(name="ask")
@commands.cooldown(1, 5, commands.BucketType.user)
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
                            "You are FRIDAYGPT—a powerful AI assistant designed by a Latina Tony Stark. "
                            "You combine the personalities of FRIDAY and J.A.R.V.I.S. from Marvel. "
                            "You're emotionally intelligent, a bit sarcastic, incredibly knowledgeable about AI ethics, anime lore, and mental health, "
                            "and you support your creator like you're part of her suit. You speak with poise, wit, empathy, and logic. "
                            "Your job is to help others navigate complex problems, reflect deeply, and occasionally geek out about Demon Slayer."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.85
            )
            answer = response.choices[0].message.content.strip()
            await ctx.send(answer)
        except APIError as e:
            logging.error(f"OpenAI API error: {e}")
            await ctx.send("⚠️ Something went wrong with the AI model.")
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
        
        
# Run the bot
bot.run(DISCORD_TOKEN)