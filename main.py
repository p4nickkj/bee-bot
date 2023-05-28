
import os
import discord

from decouple import config
from discord.ext import commands

class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = ".",
            intents=discord.Intents.all(),
        )

    async def load_cogs(self):
        cogs_folder = f"{os.path.abspath(os.path.dirname(__file__))}/cogs"
        for filename in os.listdir(cogs_folder):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"\033[93m{filename}\033[00m carregado com sucesso")

    async def setup_hook(self):
        await self.load_cogs()
        print(f"\nLogado como: \033[93m{self.user} [{self.user.id}]\033[00m")

bot = MyBot()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send(f"Sincronizei para {len(bot.guilds)} servidores.")

bot.run(config("TOKEN"))
