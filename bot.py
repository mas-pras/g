import discord
from discord.ext import commands
import datetime
import asyncio

# Error anzeigen
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

TOKEN = 'MTEwNTE1NjM4MDA4MTUyODg4Mw.GuiySJ._nIiXHgEvwCowPzgZk74w2AGPla0UCijz6-IDw'

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

bot.remove_command("help")


@bot.event
async def on_ready():
    print(f'{bot.user.name} ist bereit.')


@bot.command()
async def ticket(ctx):
    if ctx.author.id == 977993035717681252:
        embed = discord.Embed(title='**Ticket**',
                              description=f'Wenn du ein Ticket erstellen möchtest, drücke einfach die Reaktion: 💼',
                              timestamp=datetime.datetime.utcnow(),
                              color=0x808080)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('💼')
    else:
        return


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member == bot.user:
        return

    if payload.emoji.name == '💼':  # Stellt sicher, dass die Reaktion die richtige ist
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Überprüft, ob der Kanal bereits existiert
        for c in guild.channels:
            if c.name == f'{payload.member.name}s-ticket':
                await message.remove_reaction(payload.emoji, payload.member)
                return await payload.member.send('Du hast bereits ein Ticket offen.')

        # Erstelle das Support-Ticket
        SUPPORT_ROLE_ID = 1105158038396080178

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        category = discord.utils.get(guild.categories, name='Tickets')
        if category is None:
            category = await guild.create_category(name='Tickets')
        channel = await guild.create_text_channel(name=f'{payload.member.name}s-ticket', overwrites=overwrites, category=category)

        # Sende eine Nachricht mit dem Link zum neuen Ticket
        embed1 = discord.Embed(title='**Ticket**',
                               description=f'Dein Ticket wurde erstellt: {channel.mention}',
                               timestamp=datetime.datetime.utcnow(),
                               color=0x808080)

        await payload.member.send(embed=embed1)

        # Sende eine Nachricht im Ticket
        embed = discord.Embed(title=f'**{payload.member.name}`s Ticket**',
                              description=f'<@&{SUPPORT_ROLE_ID}>\nBitte um Bearbeitung.',
                              timestamp=datetime.datetime.utcnow(),
                              color=0x808080)

        embed.add_field(name='Ticket schließen:',
                        value='💀')

        reaction_message = await channel.send(f'<@&{SUPPORT_ROLE_ID}>', embed=embed)
        await reaction_message.add_reaction('💀')

        # Überprüfung der Reaktion
        def check(reaction, user):
            return str(reaction.emoji) == '💀' and user.guild_permissions.administrator and reaction.message == reaction_message

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=None, check=check)
        except:
            pass
        else:
            cooldown_message = await channel.send('Ticket wird gelöscht in **5**')
            for i in range(4, 0, -1):
                await asyncio.sleep(1)
                await cooldown_message.edit(content=f'Ticket wird gelöscht in **{i}**')
            await asyncio.sleep(1)
            await cooldown_message.edit(content='Ticket wird gelöscht in **Bye!**')
            await asyncio.sleep(1)
            await channel.send('Ticket wurde geschlossen.')
            await channel.delete()

bot.run(TOKEN)
