
import discord

from utils.constants import *

from discord import app_commands
from discord.ext import commands

def key(interaction: discord.Interaction):
    return interaction.user

def verificar_badges(user):
    userFlags = user.public_flags.all()
    return [badges.get(flag.name) for flag in userFlags if badges.get(flag.name)]

class ButtonNotInServer(discord.ui.View):
    def __init__(self, user, target):
        super().__init__()
        self.user = user
        self.target = target
        self.cd = commands.CooldownMapping.from_cooldown(1.0, 3.0, key)

    @discord.ui.button(label="Curiosidades do usuário", style=discord.ButtonStyle.gray, row=1, emoji="✨")
    async def curiosities(self, interaction: discord.Interaction, child: discord.ui.Button):
        retry_after = self.cd.update_rate_limit(interaction)
        if retry_after:
            await interaction.response.send_message(f"Você está em cooldown... Aguarde `{int(retry_after)}` segundos.", ephemeral=True)
            return False

        embed = discord.Embed(title="Curiosidades", color=EMBED_COLOR)
        badge_count = len(verificar_badges(self.user))

        if badge_count >= 1:
            badges_text = " ".join(verificar_badges(self.user))
            if badge_count == 1:
                embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} tem apenas **{badge_count} badge** no seu perfil. Ela é: {badges_text}')
            else:
                embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} tem **{badge_count} badges** no seu perfil. Elas são: {badges_text}')
        else:
            embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} aparentemente não tem nenhuma badge no seu perfil...')

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.target.id: return True
        else: return await interaction.response.send_message(f"🙅‍♂️ Você não é {self.target.mention}, então você não tem permissão para usar este botão!", ephemeral=True)

class ButtonHandler(discord.ui.View):

    def __init__(self, user, target):
        super().__init__()
        self.user = user
        self.target = target
        self.cd = commands.CooldownMapping.from_cooldown(1.0, 11.0, key)
        self.cd2 = commands.CooldownMapping.from_cooldown(1.0, 3.0, key)

    async def verificar_permissoes(self, member):
        pt_permissions = [PERMISSIONS_PT.get(name, name) for name, value in member.guild_permissions if value]
        pt_permissions = [f'`{p}`' for p in pt_permissions]
        sorted_permissions = sorted(pt_permissions)
        return ', '.join(sorted_permissions), len(pt_permissions)

    async def verificar_cargos(self, member):
        roles = sorted(member.roles[1:], key=lambda x: len(x.name))
        role_mentions = [r.mention for r in roles]
        roles_text = ", ".join(role_mentions)
        return roles_text, len(role_mentions)

    @discord.ui.button(label="Permissões do Usuário", style=discord.ButtonStyle.gray, row=1)
    async def permissions(self, interaction: discord.Interaction, child: discord.ui.Button):
        retry_after = self.cd2.update_rate_limit(interaction)
        if retry_after:
            return await interaction.response.send_message(f"Você está em cooldown... Aguarde `{int(retry_after)}` segundos.", ephemeral=True)

        if interaction.user != self.target:
            return await interaction.response.send_message("Você não tem permissão para usar este botão! O pedido de casamento não é para você.", ephemeral=True)

        perms, num_perms = await self.verificar_permissoes(self.user)
        roles, num_roles = await self.verificar_cargos(self.user)

        message = f'\n\n**Estas permissões vêm dos seguintes cargos: **{roles}' if num_roles > 1 else f'\n\n**Estas permissões vêm do seguinte cargo:** **{roles}**'

        embed = discord.Embed(color=EMBED_COLOR, description=f'**Atualmente, {self.user.name} tem {num_perms} permissões**:\n\n{perms}{message}')

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Curiosidades do usuário", style=discord.ButtonStyle.gray, row=1, emoji="✨")
    async def curiosities(self, interaction: discord.Interaction, child: discord.ui.Button):

        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            return await interaction.response.send_message(f"Você está em cooldown... Aguarde `{int(retry_after)}` segundos.", ephemeral=True)

        await interaction.response.send_message("Aguarde um pouco... As curiosidades podem demorar de 10 a 20 segundos a aparecer...", ephemeral=True)

        message_member = ""

        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)
        for index, member in enumerate(members, start=1):
            if member.mention == self.user.mention:
                message_member = f'{self.user.mention} foi o {index}º usuário a entrar no servidor, superando {len(interaction.guild.members)-index} membros.'

        oldest_message = None

        for channel in interaction.guild.text_channels:
            async for message in channel.history(limit=None, oldest_first=True):
                if message.author.id == self.user.id:
                    if oldest_message is None or message.created_at < oldest_message.created_at:
                        oldest_message = message
                    break

        if oldest_message is not None:
            old_message = f"A primeira mensagem de {self.user.mention} no servidor foi <t:{int(oldest_message.created_at.timestamp())}:R>. Você pode encontrá-la [clicando aqui]({oldest_message.jump_url})."
        else:
            old_message = "Aparentemente, o usuário não enviou nenhuma mensagem no servidor."

        embed = discord.Embed(title="Curiosidades", color=EMBED_COLOR)

        if interaction.guild.get_member(self.user.id) is not None:
            embed.add_field(name="**Primeira mensagem...**", value=old_message)
            embed.add_field(name="**Ordem de chegada...**", value=message_member)

        badge_count = len(verificar_badges(self.user))

        if badge_count >= 1:
            badges_text = " ".join(verificar_badges(self.user))
            if badge_count == 1:
                embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} tem **{badge_count} badge** no seu perfil. Ela é: {badges_text}')
            else:
                embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} tem **{badge_count} badges** no seu perfil. Elas são: {badges_text}')
        else:
            embed.add_field(name="**Quantidade de badges...**", value=f'{self.user.mention} aparentemente não tem nenhuma badge no seu perfil...')

        await interaction.edit_original_response(content=None, embed=embed)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.target.id: return True
        else: return await interaction.response.send_message(f"🙅‍♂️ Você não é {self.target.mention}, então você não tem permissão para usar estes botões!", ephemeral=True)

class Userinfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description=f"Veja as informações de um usuário")
    async def info(self, interaction: discord.Interaction, usuario: discord.User = None):

        await interaction.response.defer()

        user = usuario or interaction.user
        view = ButtonNotInServer(user, interaction.user)

        fields = [("\📘 Nome:", f"```{user}```", False), ("\📙 ID do Usuário:", f"```{user.id}```", False)]

        if interaction.guild.get_member(user.id) is not None:
            if user.nick: fields.append(("\✍️ Apelido do Usuário", f'```{user.nick}```', False))

        fields.append(("\📅 Conta criada em:", f"<t:{int(user.created_at.timestamp())}:f> (<t:{int(user.created_at.timestamp())}:R>)", False))

        if interaction.guild.get_member(user.id) is not None:
            view = ButtonHandler(user, interaction.user)
            fields.append(("\📅 Entrou no servidor em:", f'<t:{int(user.joined_at.timestamp())}:f> (<t:{int(user.joined_at.timestamp())}:R>)', False))

        embed = discord.Embed(description=f"**Informações de [{user.name}](https://discord.com/users/{user.id})**", color=EMBED_COLOR)

        try:
            avatar_url = user.avatar.url
        except AttributeError:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/1.png?size=2048"

        embed.set_thumbnail(url=avatar_url)

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Userinfo(bot))