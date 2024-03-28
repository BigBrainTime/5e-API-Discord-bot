import discord
import json
import requests
import re
import os
from pathlib import Path
from discord import app_commands
from multi_dice import roll

TOKEN = 0 #Your token
SERVERID = 0 #Your server id

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def file_send(interaction: discord.Interaction, endpoint: str, index: str, url: bool = False):
    """Sends a Discord message with data from a D&D 5E API endpoint.

    Parameters:
    - interaction (discord.Interaction): The Discord interaction object.
    - endpoint (str): The API endpoint to request data from.
    - index (str): The index of a specific item in the endpoint.
    - url (bool, optional): Whether to include URLs in the response. Defaults to False.

    The function makes a request to the D&D 5E API, processes the JSON data, and sends it 
    as a message embed or file attachment if too large. Handles paginated list endpoints.
    """
    await interaction.response.send_message(embed=discord.Embed(title=endpoint, description='Please Wait'))

    data = json.loads(requests.get(
        f'https://www.dnd5eapi.co/api/{endpoint if index == '' else f"{endpoint}/{index}"}').text)
    data = json.dumps(data['results'] if endpoint ==
                      'list' or index == '' else data, indent=2)

    if not url:
        data = re.sub(',\n.*"url":.*\n', '', data)

    if len(data) > 4096:
        if index == '':
            index = 'None'

        Path(f'5e/{endpoint}/').mkdir(parents=True, exist_ok=True)
        with open(f'5e/{endpoint}/{index}.json', 'w') as file_save:
            file_save.write(data)
        await interaction.edit_original_response(embed=discord.Embed(title=endpoint, description='Data Too Large, Sending File'))
        await client.get_channel(interaction.channel.id).send(file=discord.File(f'5e/{endpoint}/{index}.json'))

    else:
        await interaction.edit_original_response(embed=discord.Embed(title=f'{endpoint} {index}', description=f"```json\n{data}```"))


endpoints = json.loads(requests.get('https://www.dnd5eapi.co/api/').text)
if not os.path.isfile("api_endpoints.txt"):
    api_endpoint_list = ''
    for endpoint_ in endpoints:
        api_endpoint_list += f'{endpoint_}:{json.loads(requests.get(
            f'https://www.dnd5eapi.co/api/{endpoint_}').text)['count']} Entries\n'
    with open("api_endpoints.txt", "w+") as file:
        file.write(api_endpoint_list)
else:
    with open("api_endpoints.txt") as file:
        api_endpoint_list = file.read()


@tree.command(name="dnd5e", description='Use endpoint to specify endpoint. Index to specify which index.', guild=discord.Object(id=SERVERID))
async def dnd5e(interaction: discord.Interaction, endpoint: str = 'list', index: str = '', url: bool = False):
    """Handles interactions with the D&D 5E API.

    Parameters:
    - interaction (discord.Interaction): The Discord interaction object.
    - endpoint (str): The API endpoint to request data from.
    - index (str): The index of a specific item in the endpoint. 
    - url (bool): Whether to include URLs in the response.

    Sends API data as a message embed or file attachment. Validates endpoint and index.
    """
    if endpoint != 'list' and endpoint not in endpoints:  # Bad Endpoint
        await interaction.response.send_message(embed=discord.Embed(title='5e', description='Invalid Endpoint'))

    elif endpoint == "list":  # Blank Endpoint
        await interaction.response.send_message(embed=discord.Embed(title=endpoint, description=f'```json\n{api_endpoint_list}```'))

    else:
        await file_send(interaction, endpoint, index, url=url)

@tree.command(name="roll", description="Roll a die", guild=discord.Object(id=SERVERID))
async def die_roll(interaction: discord.Interaction, dice: str = "1d6"):
    """Rolls a die.

    Rolls a die with the specified number of sides. The default is a standard 6-sided die.

    Parameters:
    - interaction: The Discord interaction object. 
    - dice: The dice roll to make, in NdN format.
    """
    await interaction.response.send_message(
        embed=discord.Embed(title=dice, description=str(roll(dice)))
    )


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SERVERID))
    print('READY')

client.run(TOKEN)
