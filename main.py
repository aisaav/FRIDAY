import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import openai
import logging
import time
import asyncio
import openai.error

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO)
logging.info(f"Bot is running as {bot.user}")

# Set up Together.ai client with OpenAI-compatible SDK
client = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/"




@bot.event
async def on_ready():
    print(f"FridayGPT (JARVIS-mode) is online as {bot.user}!")

@bot.command(name="ask")
@commands.cooldown(1, 5, commands.BucketType.user)  # 1 request per user every 5 seconds
async def ask(ctx, *, prompt: str):
    async with ctx.channel.typing():
        max_attempts = 3
        delay = 2  # base delay between retries
        for attempt in range(max_attempts):
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
                break  # exit the retry loop if successful

            except openai.RateLimitError:
                if attempt < max_attempts - 1:
                    await ctx.send(f"⚠️ I'm thinking too fast. Cooling down... retrying in {delay} seconds.")
                    await asyncio.sleep(delay)
                    delay *= 2  # exponential backoff
                else:
                    await ctx.send("⚠️ I hit my limit and need a breather. Please try again soon.")
                    break

            except Exception as e:
                await ctx.send(f"⚠️ Unexpected error: {str(e)}")
                break
                
                

bot.run(DISCORD_TOKEN)
