import discord
from discord.ext import commands
from tinydb import TinyDB, Query
import re
import asyncio

db = TinyDB('data.json', sort_keys=True, indent=2, separators=(',', ': '))
commands_table = db.table('custom_commands')

class CustomCommand:
    def __init__(self, command, answer, description, creator_id):
        self.command = command
        self.answer = answer
        self.description = description
        self.creator = creator_id

CommandQuery = Query()

def placeholders(ctx, command):
    _placeholders = {'%author_name%':ctx.author.display_name,
                     '%author_id%':ctx.author.id,
                     '%author_mention%':ctx.author.mention,
                     '%channel%':ctx.channel.mention}
    
    for k, v in _placeholders.items():
        command = command.replace(k, v)

class CreateCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_names = [command.name for command in self.bot.commands] + [alias for command in self.bot.commands for alias in command.aliases]

    @commands.command(aliases=['cc', 'cccreate'])
    @commands.has_role('Manager')
    async def customcommand(self, ctx):
        async def name_check(ctx, m):
            if m.author == ctx.author and m.channel == ctx.channel and re.match(r'[a-z]*', m.content):
                if m.content in [item['command'] for item in commands_table] or m.content in self.blocked_names:
                    await ctx.send('Este comando já existe!')
                    return False
                if len(m.content) <= 2:
                    await ctx.send('Comando muito curto, deve ter pelo menos 3 caracteres!')
                    return False
                return True
            return False         

        async def answer_check(ctx, m):
            if m.author == ctx.author and m.channel == ctx.channel:
                if len(m.content) < 5:
                    await ctx.send('A resposta deve ter no mínimo 5 caracteres!')
                    return False
                return True
            return False    

        async def description_check(ctx, m):
            if m.author == ctx.author and m.channel == ctx.channel:
                if len(m.content) < 10:
                    await ctx.send('A descrição deve ter no mínimo 10 caracteres!')
                    return False
                return True
            return False

        await ctx.send('Como você quer que o comando seja chamado? (SEM a exclamação, apenas caracteres em minúsculo!)')
        try:
            command_name = self.wait_for('message', timeout=60, check = lambda m: name_check(ctx, m))
        except asyncio.TimeoutError:
            await ctx.send('Você não enviou um nome válido a tempo!')

        try:
            command_answer = self.wait_for('message', timeout=120, check = lambda m: answer_check(ctx, m))
        except asyncio.TimeoutError:
            await ctx.send('Você não uma resposta válida a tempo!')

        try:
            command_description = self.wait_for('message', timeout=120, check = lambda m: description_check(ctx, m))
        except asyncio.TimeoutError:
            await ctx.send('Você não inseriu uma descrição válida a tempo!')

        command = CustomCommand(command_name.content, command_answer.content, command_description.content, ctx.author.id)
        commands_table.insert({'command':command.command, 'answer':command.answer, 'description':command.description, 'creator':command.creator})

        async def custom_command_function(ctx):
            command = commands_table.get(CommandQuery.command == ctx.invoked_with)
            if command:
                answer = placeholders(ctx, command['answer'])
                await ctx.send(answer)
        
        self.bot.add_command(commands.Command(custom_command_function, command.command))
        await ctx.send(f'Criou o comando {command.command}!')

    @commands.Cog.listener()
    async def on_ready(self):
        for item in commands_table:
            async def custom_command_function(ctx):
                if item:
                    answer = placeholders(ctx, item['answer'])
                    await ctx.send(answer)
                self.bot.add_command(commands.Command(custom_command_function, item['command']))

class ManageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['customcommandsdelete'])
    @commands.has_role('Manager')
    async def ccdelete(self, ctx, command_name = None):
        if command_name is None:
            await ctx.send('Você não inseriu um comando para ser deletado')
            return
        
        command = commands_table.get(CommandQuery.command == command_name)
        if command is None:
            await ctx.send('O comando que você inseriu não existe')
            return
        
        self.bot.remove_command(command_name)
        commands_table.remove(CommandQuery.command == command_name)
        await ctx.send(f'Apagou o comando {command_name}')

    @commands.command(aliases=['customcommandslist'])
    async def cclist(self, ctx):
        commands = [f'!{item.command} - {item.description}\n' for item in commands_table]
        await ctx.send(f'Comandos customizados:\n\n {commands}')

async def setup(bot):
    await bot.add_cog(CreateCommands(bot))
    await bot.add_cog(ManageCommands(bot))