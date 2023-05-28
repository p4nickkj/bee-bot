
import os
import re
import aiohttp
import discord
import requests

from utils.constants import *

from discord import app_commands
from discord.ext import commands

# Verifica se é um link
def verificar_link(url):
    padrao_link = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    if padrao_link.match(url):
        if verificar_tipo_imagem(url):
            return True
    return False

# Verifica se é um URL compatível
def verificar_tipo_imagem(url):
    response = requests.head(url)
    content_type = response.headers.get('content-type')
    extension = os.path.splitext(url)[1][1:]
    return extension, content_type in ['image/gif', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp']

# Adiciona o Emoji no servidor
async def adicionar_emoji(interaction, guild, emoji_name, emoji_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(emoji_url) as response:
            image_bytes = await response.read()

    padrao = r'\.(gif|jpeg|png|webp|jpg)'
    correspondencia = re.search(padrao, emoji_url, re.IGNORECASE)

    if correspondencia:
        extensao = correspondencia.group(1)
        file_path = f"temp.{extensao}"

        with open(file_path, "wb") as file:
            file.write(image_bytes)

        with open(file_path, "rb") as file:
            await guild.create_custom_emoji(name=emoji_name, image=file.read())

        os.remove(file_path)
    else:
        return await interaction.response.send_message("Aparentemente, alguma coisa correu errado...")

# Cria a Embed para mostrar as informações do emoji
def criar_embed(emoji_name, emoji_type, emoji_url):
    embed = discord.Embed(title="Adicionar Emoji", color=EMBED_COLOR)
    embed.add_field(name="\👨‍🔬 Nome:", value=f"```{emoji_name}```")
    embed.add_field(name="\🧬 Tipo:", value=f"```{emoji_type}```")
    embed.set_thumbnail(url=emoji_url)
    return embed

class Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(timeout=None, title="Informações do Banimento")

    nome = discord.ui.TextInput(label="Novo nome do Emoji", style=discord.TextStyle.short, required=True)
    link = discord.ui.TextInput(label="Novo link do Emoji", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):

        if len(str(self.nome)) > 32 or len(str(self.nome)) < 2:
            return await interaction.followup.send(f"🙇‍♂️ | {interaction.user.mention} Infelizmente, o Discord não permite que eu adicione emojis com o nome abaixo de 2 caracteres e acima de 32. Tente trocar o nome, quem sabe resulte.", ephemeral=True)

        try: extension, validade = verificar_tipo_imagem(str(self.link))
        except: await interaction.response.send_message("Você tem a certeza que especificou um link? Confira bem antes de me culpar por isso...", ephemeral=True)

        else:
            if validade:
                padrao = r'\.(gif|jpeg|png|webp|jpg)'
                correspondencia = re.search(padrao, str(self.link), re.IGNORECASE)
                if correspondencia:
                    extensao = correspondencia.group(1)
                    emoji_type = 'Animado' if extensao == 'gif' else 'Estático'
                    view = ButtonHandler(str(self.nome), str(self.link))
                    view.add_item(discord.ui.Button(label="Abrir imagem no Navegador", url=str(self.link), row=2))
                    await interaction.response.edit_message(embed=criar_embed(str(self.nome), emoji_type, str(self.link)), view=view)
            else:
                return await interaction.response.send_message(f":man_gesturing_no: | {interaction.user.mention} O link que você especificou não é um link válido para este tipo de ação.", ephemeral=True)

class ButtonHandler(discord.ui.View):

    def __init__(self, emoji_name, emoji_url):
        super().__init__(timeout=None)
        self.emoji_name = emoji_name
        self.emoji_url = emoji_url

    @discord.ui.button(label="Adicionar Emoji", style=discord.ButtonStyle.blurple, row=1)
    async def add_emoji(self, interaction: discord.Interaction, child: discord.ui.Button):

        try:
            await adicionar_emoji(interaction, interaction.guild, self.emoji_name, self.emoji_url)

        except discord.errors.HTTPException:
            await interaction.followup.send(f":man_gesturing_no: | {interaction.user.mention} Infelizmente, eu não consegui adicionar este emoji...\nIsto pode acontecer por três motivos:\n**1.** O arquivo é muito grande para ser um emoji\n**2.** Eu não tenho permissão para Gerenciar Emojis\n**3.** O nome que você colocou contém símbolos especiais", ephemeral=True)

        else:
            for child in self.children:
                if not child.url:
                    child.disabled = True

            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f":sparkles: {interaction.user.mention} Emoji adicionado com sucesso!", ephemeral=True)

    @discord.ui.button(label="Alterar Configurações", style=discord.ButtonStyle.gray, row=1)
    async def configs(self, interaction: discord.Interaction, child: discord.ui.Button):
        await interaction.response.send_modal(Modal())

class Emoji(commands.GroupCog, name="adicionar"):

    def __init__(self, bot):
        self.bot = bot

    def substituir_simbolos(self, string, substituicoes):
        for simbolo, substituto in substituicoes.items():
            string = string.replace(simbolo, substituto)
        return string

    def verificar_emoji(self, message):
        emoji_pattern = re.compile(r"<a?:\w+:\d+>")
        if re.search(emoji_pattern, message):
            return True
        return False

    @app_commands.command(name="emoji", description=f"Adicione um emoji no seu servidor")
    @app_commands.describe(nome='Nome do emoji a ser adicionado', emoji="Emoji que você quer adicionar (Pode usar um link ou mencionando o emoji)")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def add_emoji(self, interaction: discord.Interaction, nome: str, emoji: str):

        await interaction.response.defer(ephemeral=True)

        if len(nome) > 32 or len(nome) < 2:
            return await interaction.followup.send(f"🙇‍♂️ | {interaction.user.mention} Infelizmente, o Discord não permite que eu adicione emojis com o nome abaixo de 2 caracteres e acima de 32. Tente trocar o nome, quem sabe resulte.", ephemeral=True)

        if len(nome.split()) > 1:
            return await interaction.followup.send(f"🙇‍♂️ | {interaction.user.mention} Infelizmente, o Discord não permite colocar nomes num emoji ao mesmo tempo. Então escolha apenas um nome para o emoji que quer adicionar...", ephemeral=True)

        if len(emoji.split()) > 1:
            return await interaction.followup.send(f"🙇‍♂️ | {interaction.user.mention} Infelizmente, o Discord não permite colocar vários emojis ao mesmo tempo. Então escolha apenas um para adicionar...", ephemeral=True)

        if verificar_link(emoji):

            b, validade = verificar_tipo_imagem(emoji)

            if validade:
                padrao = r'\.(gif|jpeg|png|webp|jpg)'
                correspondencia = re.search(padrao, emoji, re.IGNORECASE)
                if correspondencia:
                    extensao = correspondencia.group(1)
                    extension = 'Animado' if extensao == 'gif' else 'Estático'
                    view = ButtonHandler(nome, emoji)
                    view.add_item(discord.ui.Button(label="Abrir Imagem no Navegador", url=emoji, row=2))
                    await interaction.followup.send(embed=criar_embed(nome, extension, emoji), view=view)
            else:
                return await interaction.followup.send(f":man_gesturing_no: | {interaction.user.mention} O link que você especificou não é um link válido para este tipo de ação.", ephemeral=True)

        elif self.verificar_emoji(emoji):

            substituicoes = {"<": "", "\\": ""}
            emoji = emoji.split(":")
            emoji_id = emoji[-1].replace(">", "")
            emoji_extension = "gif" if self.substituir_simbolos(emoji[0], substituicoes) == "a" else "png"
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{emoji_extension}"
            emoji_type = f'{"Animado" if emoji_extension == "gif" else "Estático"}'

            embed = criar_embed(nome, emoji_type, emoji_url)

            view = ButtonHandler(nome, emoji_url)
            view.add_item(discord.ui.Button(label="Abrir Imagem no Navegador", url=emoji_url, row=2))

            await interaction.followup.send(embed=embed, view=view)

        else:
            return await interaction.followup.send(f":man_shrugging: | {interaction.user.mention} Infelizmente, o emoji que você está tentando colocar não existe.\nCertifique-se de que colocou um link válido ou um emoji, antes de me culpar por isso.", ephemeral=True)

    @add_emoji.error
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message("Você não tem permissão para executar este comando. Falta-lhe a permissão `Gerenciar Emojis e Figurinhas`.", ephemeral=True)
        else: return await interaction.response.send_message(f"Ocorreu um erro ao executar o comando:\n```\n{error}\n```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Emoji(bot))