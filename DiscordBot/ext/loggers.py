import discord
from discord.ext import commands
import os
import asyncio
import json

with open('config.json') as f:
    file = json.load(f)
    config = file['Configuration']['Loggers']

#? All optimised!
class Announcers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_channel = config['Announcers']['JoinChannel']
        self.leave_channel = config['Announcers']['LeaveChannel']
        self.logging_channel = config['Announcers']['LogChannel']

    @commands.Cog.listener()
    async def on_member_join(self, member):
        joinchannel = self.bot.get_channel(self.join_channel)
        logchannel = self.bot.get_channel(self.logging_channel)

        embed=discord.Embed(title=f'**Bem-vindo {member.mention}!**')
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name=f':beginner: Registre-se!', value='<#1107131329222553641>', inline=True)
        embed.add_field(name=f':twitch: Twitch', value=f'https://twitch.tv/gaby_ballejo', inline=True)
        embed.set_footer(text=f'ID do usuário: {member.id}')
        await joinchannel.send(embed=embed)

        await joinchannel.send(f'Bem vindo {member.mention}!')
        logchannel.send(f'{member.id} | {member.name}#{member.discriminator} entrou no servidor!')
        
    @commands.Cog.listener()
    async def on_member_remove(self, member): #turn this into member remove raw
        leavechannel = self.bot.get_channel(self.leave_channel)
        logchannel = self.bot.get_channel(self.logging_channel)
        await leavechannel.send(f'Adeus {member.name}#{member.discriminator}.')
        logchannel.send(f'{member.id} | {member.name}#{member.discriminator} saiu do servidor!')

#? All optimised!
class Loggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_channel = config['Loggers']['LogChannel']
        self.cmdlogging_channel = config['Loggers']['CmdLogChannel']
         
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            channel = self.bot.get_channel(self.logging_channel)
            await channel.send(f'Alteração de nickname! {before.display_name} -> {after.display_name} ({before.name}#{before.discriminator} - {before.id})')
        if before.name != after.name:
            channel = self.bot.get_channel(self.logging_channel)
            await channel.send(f'Alteração de nome! {before.name} -> {after.name} ({before.id})')
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('!'):
            channel = self.bot.get_channel(self.cmdlogging_channel)
            await channel.send(f'({str(message.author.id)}) | {message.author.display_name}: {message.content}')
          
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            channel = self.bot.get_channel(self.logging_channel)
            await channel.send(f'Mensagem de {after.author.mention} editada em {before.channel.mention}!\n{before.content}\n{after.content}')
        if before.pinned != after.pinned:
            channel = self.bot.get_channel(self.logging_channel)
            await channel.send(f'Mensagem de {after.author.mention} (desa)fixada em {after.channel.mention}!\n{after.content}')
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return
        
        channel = self.bot.get_channel(self.logging_channel)
        await channel.send(f'Mensagem apagada em {message.channel}\n({message.author.id}) | {message.author.mention}: {message.content}')
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        with open('bulkdelete.txt', 'w') as f:
            for message in messages:
                f.write(f'({str(message.author.id)}) | {message.author.display_name}: {message.content}\n')
        discord_file = discord.File('bulkdelete.txt')
        channel = self.bot.get_channel(self.logging_channel)
        await channel.send(f'Bulk delete (!clear) detectado!', file=discord_file)
        await asyncio.sleep(0.5)
        os.remove('bulkdelete.txt')
            
async def setup(bot):
    await bot.add_cog(Announcers(bot))
    await bot.add_cog(Loggers(bot))