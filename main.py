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
client = OpenAI.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1"
)

@bot.event
async def on_ready():
    logging.info(f"✅ FridayGPT is live as {bot.user} (ID: {bot.user.id})")

@bot.command(name="ask")
@commands.cooldown(1, 5, commands.BucketType.user)
async def ask(ctx, *, prompt: str):
    logging.info(f"Received !ask from {ctx.author}: {prompt}")
    try:
        await ctx.typing()
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

        if hasattr(response, "choices") and len(response.choices) > 0:
            answer = response.choices[0].message.content.strip()
            await ctx.send(answer)
        else:
            await ctx.send("⚠️ FRIDAYGPT didn't return a valid response.")
            logging.error("Response object invalid or empty: %s", response)

    except APIError as e:
        logging.error(f"OpenAI API error: {e}")
        await ctx.send(f"❌ API Error: {str(e)}")
    except Exception as e:
        logging.exception("Unexpected error occurred")
        await ctx.send(f"❌ Unexpected Error: {str(e)}")\
            
            
# Run the bot
bot.run(DISCORD_TOKEN)