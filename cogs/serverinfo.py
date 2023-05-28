
import discord

from utils.constants import *

from discord import app_commands
from discord.ext import commands

class Serverinfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description=f"Veja as informações do servidor")
    async def serverinfo(self, interaction: discord.Interaction):

        guild = interaction.guild
        total_members = guild.member_count
        online_members = sum(member.status != discord.Status.offline for member in guild.members)
        bot_members = sum(member.bot for member in guild.members)
        human_members = abs(total_members - bot_members)
        categories = len(guild.categories)

        server_invite_link = await interaction.channel.create_invite()

        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        server_created = guild.created_at.timestamp()

        embed = discord.Embed(description=f'**Informações de [{guild.name}]({server_invite_link})**', color=EMBED_COLOR)

        view = discord.ui.View()

        try:
            embed.set_thumbnail(url=guild.icon.url)
            view.add_item(discord.ui.Button(label="Avatar do servidor", url=guild.icon.url))

        except AttributeError:
            pass

        if guild.banner:
            view.add_item(discord.ui.Button(label="Banner do servidor", url=guild.banner.url))

        fields = [
            ("\📘 Nome do Servidor:", f"```{guild}``` ```({guild.id})```", False),
            ("\👑 Dono do Servidor:", f"```{guild.owner}``` ```({guild.owner.id})```", False),
            (f"\📖 Canais do Servidor ({total_channels}):", f"```Canais de Texto: {text_channels}``` ```Canais de Voz: {voice_channels}``` ```Categorias: {categories}```", True),
            (f"\👀 Membros do Servidor ({total_members}):", f"```Humanos: {human_members}``` ```Online: {online_members}``` ```Bots: {bot_members}```", True),
            ("\📅 Servidor criado em:", f"<t:{int(server_created)}:f> (<t:{int(server_created)}:R>)", False),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Serverinfo(bot))