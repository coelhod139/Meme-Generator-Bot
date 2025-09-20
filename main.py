import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import openai  # ✅ Add OpenAI import

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

secret_role = "Gamer"
last_media = {}  # ✅ Store last emoji or image per channel


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ✅ Store last image/gif or emoji in the channel
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.png', '.gif', '.webp']):
                last_media[message.channel.id] = attachment.url
    elif any(char in message.content for char in ['😀', '😂', '🔥', '💀', '😭']):
        last_media[message.channel.id] = message.content

    # ✅ Trigger description using LLM
    if message.content.lower().strip() in ["describe that", "what does that mean?", "explain that"]:
        media = last_media.get(message.channel.id)
        if not media:
            await message.channel.send("I don't see anything to describe.")
        else:
            response = await describe_media(media)
            await message.channel.send(response)

    # ✅ Bad word filter
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")

    await bot.process_commands(message)


async def describe_media(media):
    if media.startswith("http"):
        try:
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image or gif in detail, including meme or cultural references if any."},
                        {"type": "image_url", "image_url": {"url": media}}
                    ]}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error (image): {e}")
            return "There was an error analyzing the image or gif."
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"What does this emoji or message mean? '{media}'. Explain humorously or culturally."}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error (emoji): {e}")
            return "Couldn't interpret the emoji."


# ✅ Basic Commands (unchanged)
@bot.command()
async def hello(ctx):
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


@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")


# ✅ Fix: token variable
bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
