# Discord Meme Bot

A fun Discord bot built with `discord.py` that can:
- Assign and remove roles
- Welcome new members
- Run simple commands (`!hello`, `!poll`, `!reply`, etc.)
- Generate memes, GIFs, and emojis using **OpenAI** and **Tenor API**
- Support secret role–gated commands

---

## Features

- **Basic Commands**
  - `!hello` → Bot greets you.
  - `!dm <message>` → Bot DMs you your message.
  - `!reply` → Replies to your message.
  - `!poll <question>` → Starts a poll with 👍 and 👎 reactions.

- **Role Management**
  - `!assign` → Assigns you the role of `Meme Generation` allowing you to add memes/gifs/emojis.
  - `!remove` → Removes the user role.
    
- **AI Meme/GIF/Emoji Commands**
  - `!meme <description>` → 
    - Uses GPT-4o-mini to interpret your description.
    - Tries to fetch a GIF from **Tenor**.
    - Falls back to generating an image with **DALL·E** (if available).
  - `!gif <description>` → Fetches a GIF or falls back to image generation.
  - `!emoji <description>` → Suggests a single emoji.

- **Message Management**
  - `!delete` → Deletes the bot’s last response to you.

---

## Requirements

- Python **3.9+**
- [discord.py 2.x](https://pypi.org/project/discord.py/)
- [aiohttp](https://pypi.org/project/aiohttp/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [openai Python SDK](https://pypi.org/project/openai/)

Install dependencies:

```bash
pip install discord.py aiohttp python-dotenv openai
```

Meme Generation Bot is hosted on render for use.
