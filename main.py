import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import openai
import aiohttp

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

secret_role = "Gamer"

# Store last bot message per user for !delete
user_last_message = {}

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.command()
async def hello(ctx):
    print('hello command triggered')
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

# AI Meme/GIF/Emoji Commands

async def ask_llm(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You help map descriptions into memes, gifs, or emojis. "
            "You aren't providing the meme, gif, or emoji, but I'd like you to provide a one line "
            "statement that captures my description and then allows it to be passed as a description "
            "to Tenor to find the exact meme/emoji/gif that I'm looking for or if the user specifys to "
            "make the meme with Dali then make it with Dalle "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    print(f'prompt: {prompt}')
    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()


async def get_tenor_gif(query: str) -> str:
    """Fetch a GIF URL from Tenor API based on query."""
    tenor_key = os.getenv("TENOR_API_KEY")  # make sure to set in .env
    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={tenor_key}&limit=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["media_formats"]["gif"]["url"]
    return None

async def generate_dalle_image(prompt: str) -> str:
    print('generating dalle image')
    try:
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="auto"
        )
        print("got response:", response)
        return response.data[0].url
    except Exception as e:
        print("error generating image:", e)
        return None


@bot.command()
async def meme(ctx, *, description):
    print('!meme command triggered')
    query = await ask_llm(f"Find a meme for: {description}")
    print('ran func ask_llm')
    print(f"query: {query}")
    if 'Dalle' in description:
        print('Dali in query - running dalle image')
        image_url = await generate_dalle_image(query)
    else:
        print('Dali NOT IN query')
        gif_url = await get_tenor_gif(query)
        print('ran get_tenor_gif')
            
    if gif_url:
        print('inside gif_url')
        sent = await ctx.send(gif_url)
    else:
        print('inside else gif_url')
        await ctx.send("Couldn't find an existing meme — generating one for you 🎨")
        image_url = await generate_dalle_image(f"Meme style image of {description}")
        sent = await ctx.send(image_url)

    user_last_message[ctx.author.id] = sent

@bot.command()
async def gif(ctx, *, description):
    query = await ask_llm(f"Find a gif for: {description}")
    gif_url = await get_tenor_gif(query)

    if gif_url:
        sent = await ctx.send(gif_url)
    else:
        await ctx.send("Couldn't find a GIF — generating a meme-style image instead 🎨")
        image_url = await generate_dalle_image(f"Meme style image of {description}")
        sent = await ctx.send(image_url)

    user_last_message[ctx.author.id] = sent


@bot.command()
async def emoji(ctx, *, description):
    emoji_text = await ask_llm(f"Suggest a single emoji for: {description}")
    sent = await ctx.send(emoji_text)
    user_last_message[ctx.author.id] = sent

@bot.command()
async def delete(ctx):
    if ctx.author.id in user_last_message:
        try:
            await user_last_message[ctx.author.id].delete()
            await ctx.send(f"{ctx.author.mention}, your last bot reply was deleted.")
        except:
            await ctx.send("Couldn't delete the message (maybe already gone).")
    else:
        await ctx.send("I don't remember sending you anything to delete.")


bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
