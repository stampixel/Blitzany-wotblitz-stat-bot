import json
import requests
from discord import Embed, Member
from discord.ext import commands
import discord
import datetime
import asyncio

client = commands.Bot(command_prefix=">")
client.remove_command("help")


async def status_task():
    while True:
        await client.change_presence(activity=discord.Game(name="🍕 Eating pizza..."))
        await asyncio.sleep(15)
        await client.change_presence(activity=discord.Game(name="🍹 Drinking smoothies..."))
        await asyncio.sleep(15)
        await client.change_presence(activity=discord.Game(name="🧀 Try >stats..."))
        await asyncio.sleep(15)


'''
------------------------------------------------------------------------------------------------------------------------
'''


def get_account_id(player, server):
    data = requests.get(
        f"https://api.wotblitz.{server}/wotb/account/list/?application_id=95523cc25e231e510f678729e21a9e10&search={player}")
    json_data = json.loads(data.text)
    info = json_data['data']
    account_id = info[0]['account_id']
    return account_id


def get_clan_id(account_id, server):
    data = requests.get(
        f"https://api.wotblitz.{server}/wotb/clans/accountinfo/?application_id=95523cc25e231e510f678729e21a9e10&account_id={account_id}")
    json_data = json.loads(data.text)
    total_data = json_data['data']
    player_id_category = total_data[f'{account_id}']
    if player_id_category is None:
        clan_id = None
    else:
        clan_id = player_id_category['clan_id']

    return clan_id


'''
------------------------------------------------------------------------------------------------------------------------
'''


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(status_task())


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in all required arguments.")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("This command does not exist / Invalid command used")


'''
------------------------------------------------------------------------------------------------------------------------
'''


@client.command()
async def stats(ctx, player=None, *, server=None):
    if server is None:
        server = "com"
    elif server == "na" or "Na" or "NA":
        server = "com"
    if player is None:
        await ctx.send("Please input a player. (`!stats [PLAYER]`)")
    else:

        try:
            account_id = get_account_id(player=player, server=server)

            data = requests.get(
                f"https://api.wotblitz.{server}/wotb/account/info/?application_id=95523cc25e231e510f678729e21a9e10&account_id={account_id}")
            json_data = json.loads(data.text)

            # json subcatagory scraping
            total_data = json_data['data']
            player_id_category = total_data[f'{account_id}']
            player_nickname = player_id_category['nickname']
            statistic = player_id_category['statistics']
            player_stats = statistic['all']

            total_wins = player_stats['wins']
            total_losses = player_stats['losses']
            total_random_battles = player_stats['battles']
            total_frags = player_stats['frags']

            damage_dealt = player_stats['damage_dealt']
            damage_received = player_stats['damage_received']

            player_last_battle = datetime.datetime.fromtimestamp(player_id_category['last_battle_time'])
            account_creation_date = datetime.datetime.fromtimestamp(player_id_category['created_at'])

            embed = Embed(title=f"`{player_nickname}`'s Career Stats",
                          description="Here are the stats of the player's life time career on WoTBlitz:",
                          colour=discord.Colour.blurple())

            winrate = float("{0:.2f}".format(total_wins / total_random_battles * 100))
            damage_ratio = float("{0:.2f}".format(damage_dealt / damage_received))

            embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar_url)
            embed.add_field(name=':triangular_flag_on_post: **Battles**', value=f'┕`{total_random_battles}`',
                            inline=True)
            embed.add_field(name=':100: **Wins**', value=f'┕`{total_wins}`', inline=True)
            embed.add_field(name=':flag_white: **Losses**', value=f'┕`{total_losses}`', inline=True)
            embed.add_field(name=':dart: **Winrate**', value=f'┕`{winrate}%`', inline=True)
            embed.add_field(name=':no_entry_sign: **Kills/Frags**', value=f'┕`{total_frags}`', inline=True)
            embed.add_field(name=':hourglass_flowing_sand: **Damage Ratio**', value=f'┕`{damage_ratio}`', inline=True)
            embed.add_field(name=f":clock1: Created At: `{account_creation_date.strftime('%Y-%m-%d %H:%M:%S')}`",
                            value='==================================', inline=False)

            clan_id = get_clan_id(account_id=account_id, server=server)
            if clan_id is None:
                embed.add_field(name=':x: **ERROR**', value=f'┕`{player_nickname}` is either not in a clan or an '
                                                            f'error has occured. Please contact __**[stampixel]('
                                                            f'https://dsc.bio/stampy)**__ if you have any questions '
                                                            f'or concerns.', inline=False)
                embed.set_footer(
                    text=f"Server: {server} | ID Blitz Account: {account_id} | Last Battle: {player_last_battle.strftime('%Y-%m-%d %H:%M:%S')}")

            else:
                data = requests.get(
                    f"https://api.wotblitz.{server}/wotb/clans/info/?application_id=95523cc25e231e510f678729e21a9e10&clan_id={clan_id}")
                json_data = json.loads(data.text)

                total_data = json_data['data']
                clan_id_category = total_data[f'{clan_id}']
                clan_name = clan_id_category['name']
                member_count = clan_id_category['members_count']

                embed.add_field(name=':trident: **Clan Name**', value=f'┕`{clan_name}`', inline=True)
                embed.add_field(name=':pencil: **Member Count**', value=f'┕`{member_count}`', inline=True)

                embed.set_footer(
                    text=f"Server: {server} | ID Blitz Account: {account_id} | Last Battle: {player_last_battle.strftime('%Y-%m-%d %H:%M:%S')}")

            await ctx.send(embed=embed)
        except IndexError:
            await ctx.send(f"Player (`{player}`) not found.")


client.run('TOKEN')