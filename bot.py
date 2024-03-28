import discord
import json
import requests
import re
import os
import shutil
import random
import db
from uuid import uuid4
from pathlib import Path
from discord import app_commands
from multi_dice import roll

with open("config.json") as settings:
    config = json.loads(settings.read())

TOKEN = config["TOKEN"]
SERVERID = config["ServerID"]

level0Roles = config["level0Roles"]
level0Accounts = config["level0Accounts"]

allowed_image_urls = config["allowed_image_urls"]

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def file_send(interaction: discord.Interaction, endpoint: str, index: str, url: bool = False):
    """Sends a Discord message with data from a D&D 5E API endpoint.

    Parameters:.Interaction
    - interaction (discord.Interaction): The Discord interaction object.
    - endpoint (str): The API endpoint to request data from.
    - index (str): The index of a specific item in the endpoint.
    - url (bool, optional): Whether to include URLs in the response. Defaults to False.

    The function makes a request to the D&D 5E API, processes the JSON data, and sends it 
    as a message embed or file attachment if too large. Handles paginated list endpoints.
    """
    await interaction.response.defer()

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
        await interaction.followup.send(embed=discord.Embed(title=endpoint, description='Data Too Large, Sending File'))
        await client.get_channel(interaction.channel.id).send(file=discord.File(f'5e/{endpoint}/{index}.json'))

    else:
        await interaction.followup.send(embed=discord.Embed(title=f'{endpoint} {index}', description=f"```json\n{data}```"))

endpoints = json.loads(requests.get('https://www.dnd5eapi.co/api/').text)
if not os.path.isfile("api_endpoints.txt"):
    api_endpoint_list = ''
    for endpoint_ in endpoints:
        api_endpoint_list += f'{endpoint_}:{json.loads(requests.get(
            f'https://www.dnd5eapi.co/api/{endpoint_}').text)['count']} Entries\n'
    with open("api_endpoints.txt","w+") as file:
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


def user_allowed_db(user, accounts_only=False):
    """Checks if a user is allowed to access a database.

    Args:
    user: The Discord user to check.
    accounts_only: If True, only allow users in the accounts list.

    Returns:
    True if the user is allowed, False otherwise.
    """
    allowed = True
    if user.id not in level0Accounts:
        if accounts_only:
            return False

        allowed = False
        for role in level0Roles:
            if role in user.roles:
                allowed = True
                break
    return allowed


@tree.command(name="upload_image", description="Upload an image to be voted on", guild=discord.Object(id=SERVERID))
async def image_upload(interaction: discord.Interaction, creature: str, image_url: str):
    """Uploads an image to be voted on.

    This command allows a user to upload an image of a creature, which can then be voted on. It checks that the user has permission to upload images, validates the URL, downloads the image, gives it a unique ID, stores it in the database, and saves it to the images folder before responding.

    Parameters:
    - interaction: The Discord interaction object.
    - creature: The name of the creature in the image. 
    - image_url: The URL of the image to upload.
    """
    if not user_allowed_db(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="Not allowed to upload images", description="If this is an error contact a member of staff"))

    url_allowed = False
    for url in allowed_image_urls:
        if url in image_url:
            url_allowed = True
            break

    if not url_allowed:
        return await interaction.response.send_message(embed=discord.Embed(title="Invalid URL", description=f"({image_url}) is an invalid url. URL not in allowed urls of {allowed_image_urls}"))

    image_request = requests.get(image_url, stream=True)
    if image_request.status_code != 200:
        return await interaction.response.send_message(embed=discord.Embed(title="Invalid URL", description=f"Status code:{image_request.status_code}"))

    creature = creature.strip()
    for character in (" ", "/", "\\", "."):
        creature = creature.replace(character, "_")
    filepath = os.path.join("images", creature)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    ID = str(uuid4())

    await interaction.response.send_message(embed=discord.Embed(title="Creature Added", description=f"Creature ID: {ID}"))

    db.add_image(creature, ID, interaction.user.id)

    with open(os.path.join(filepath, f"{ID}.jpg"), 'wb+') as f:
        image_request.raw.decode_content = True
        shutil.copyfileobj(image_request.raw, f)


class VoteYesButton(discord.ui.Button):
  def __init__(self, view:discord.ui.View, imageID:str):
    super().__init__(style=discord.ButtonStyle.green, label="Yes")
    self.button_view = view
    self.ID = imageID

  async def callback(self, interaction: discord.Interaction):
    self.button_view.stop()
    await interaction.response.send_message("Vote Submitted")
    db.increment_ranking(self.ID)
    db.increment_votes(self.ID)

class VoteNoButton(discord.ui.Button):
  def __init__(self, view: discord.ui.View, imageID: str):
    super().__init__(style=discord.ButtonStyle.red, label="No")
    self.button_view = view
    self.ID = imageID

  async def callback(self, interaction: discord.Interaction):
    self.button_view.stop()
    await interaction.response.send_message("Vote Submitted")
    db.increment_votes(self.ID)

@tree.command(name="vote_image", description="Find a creature with the least votes for a simple yes/no vote", guild=discord.Object(id=SERVERID))
async def pick_least_voted(interaction: discord.Interaction):
    """Gets the creature with the least votes and prompts users to vote yes/no on the image.

    This command finds a random creature image that has the least votes out of the images in the database, 
    and prompts the user to vote yes or no on that image. 

    It displays the image, creature name, and vote ranking. 
    It also shows who originally submitted the image.

    The yes/no vote buttons update the vote count for that image in the database.
    """
    await interaction.response.defer()
    creature, imageID, total_votes, ranking, userID = random.choice(db.get_bottom_voted())

    creature_path = os.path.join("images", creature, f"{imageID}.jpg")

    view = discord.ui.View()
    view.add_item(VoteNoButton(view, imageID))
    view.add_item(VoteYesButton(view, imageID))

    await interaction.followup.send(f"Cast your vote for this image of `{creature}` submitted by `{client.get_user(userID)}` that has {ranking}/{total_votes} votes:", view=view, file=discord.File(creature_path))


@tree.command(name="generate_api_key", description="Generate a personal API key", guild=discord.Object(id=SERVERID))
async def generate_api_key(interaction: discord.Interaction, key_name: str = ""):
    """
    Generates a new API key for the user and saves it to the database.

    Parameters:
    interaction (discord.Interaction): The interaction object.
    key_name (str): Optional name for the key.

    Returns:
    None. Sends a response to the user with the generated key.

    Saves the key to the database associated with the user's ID.
    """
    if not user_allowed_db(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="Not allowed to obtain key", description="If this is an error contact a member of staff"))

    key = str(uuid4())
    await interaction.response.send_message(embed=discord.Embed(title="API Key (DO NOT SHARE)", description=f"{key}\n\nSet as 'Authorization' header"), ephemeral=True)

    db.add_apikey(key, interaction.user.id, key_name)


@tree.command(name="revoke_apikeys", description="Revoke all api keys for a user", guild=discord.Object(id=SERVERID))
async def revoke_apikeys(interaction: discord.Interaction, user: discord.Member):
    """Revokes all API keys associated with the given user ID in the database.

    Parameters:
    interaction (discord.Interaction): The interaction object.
    user (discord.Member): The Discord user whose keys should be revoked.

    Returns:
    None. Sends a response to the user confirming revocation.
    """
    if not user_allowed_db(interaction.user, True):
        return await interaction.response.send_message("You do not have permission to revoke API keys")

    db.revoke_apikeys(user.id)

    await interaction.response.send_message(f"Revoked all API keys for {user.mention}")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SERVERID))
    print('READY')

client.run(TOKEN)