import os
from typing import List
import discord
from discord.ext import commands
from discord import app_commands
import random

intents = discord.Intents.all()
intents.typing = False
bot = commands.Bot(command_prefix="_", intents=intents, help_command=None, owner_ids=[])

def random_embed_color():
    return discord.Color(random.randint(0, 0xFFFFFF))

@bot.event
async def on_ready():
    print("起動完了")
    await bot.load_extension("playlist")
    await bot.tree.sync()

# @bot.tree.command(name="test", description="test")
# async def test_command(interaction: discord.Interaction):
#     await interaction.response.send_message('test')

bot.run("TOKEN")
