import discord
from discord.ui import Button, View
from discord.ext import commands
import time
import json
import os
import requests
import asyncio

# Load the Discord token and embed color from the config.json file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    token = config.get('token')
    proof_Channel = config.get('proof_Channel_id')
    bot_status = config.get('bot_status')
    embed_color = config.get('embed_color', discord.Color.blue().value)

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")

# Dictionary to store ratings
ratings = {}

image_folder = 'feedback_images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Global variable to store Feedback_Embed
Feedback_Embed = None

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=bot_status))
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def feedback(ctx):
    global Feedback_Embed  # Make it a global variable
    servername = ctx.guild.name
    embed = discord.Embed(
        title=f"FEEDBACK BOT | {servername}",
        description="",
        color=embed_color  # Set the embed color
    )

    embed.add_field(name="Please rate your purchase:", value="", inline=False)
    embed.add_field(name="--------------------", value="", inline=False)
    embed.add_field(name="", value="How would you rate the effectiveness of the support?", inline=False)
    embed.add_field(name="", value="Were there any issues that were not resolved?", inline=False)
    embed.add_field(name="", value="Were you satisfied with the support service?", inline=False)
    embed.add_field(name="", value="Were you able to count on prompt assistance?", inline=False)
    embed.add_field(name="--------------------", value="", inline=False)

    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    embed.set_footer(text="Click on the buttons to submit your rating. | made by dasofabe")

    Button1 = Button(style=discord.ButtonStyle.gray, label="⭐", custom_id="⭐")
    Button2 = Button(style=discord.ButtonStyle.gray, label="⭐⭐", custom_id="⭐ ⭐")
    Button3 = Button(style=discord.ButtonStyle.gray, label="⭐⭐⭐", custom_id="⭐ ⭐ ⭐")
    Button4 = Button(style=discord.ButtonStyle.gray, label="⭐⭐⭐⭐", custom_id="⭐ ⭐ ⭐ ⭐")
    Button5 = Button(style=discord.ButtonStyle.gray, label="⭐⭐⭐⭐⭐", custom_id="⭐ ⭐ ⭐ ⭐ ⭐")

    async def button_callback(interaction):
        global Feedback_Embed  # Access the global variable
        # Extract the label of the selected button from the message
        selected_label = interaction.data['custom_id']

        # Save the selected label in the ratings list
        ratings[interaction.user.id] = selected_label

        updated_embed = discord.Embed(
            title=f"FEEDBACK BOT | {servername}",
            description="Please Upload a screenshot or image of the chat history in this channel as Proof.",
            color=embed_color  # Set the embed color
        )
        # Add the selected label to the embed
        updated_embed.add_field(name="Your Rating:", value=ratings[interaction.user.id], inline=False)

        await interaction.message.edit(embed=updated_embed)

    Button1.callback = button_callback
    Button2.callback = button_callback
    Button3.callback = button_callback
    Button4.callback = button_callback
    Button5.callback = button_callback

    view = View()
    view.add_item(Button1)
    view.add_item(Button2)
    view.add_item(Button3)
    view.add_item(Button4)
    view.add_item(Button5)

    Feedback_Embed = await ctx.send(embed=embed, view=view)

@bot.event
async def on_message(message):
    global Feedback_Embed  # Access the global variable
    # Check if the message contains an image and if the user has given a rating
    if message.attachments and message.attachments[0].content_type.startswith('image') and message.author.id in ratings:
        servername = message.guild.name

        image_url = message.attachments[0].url
        image_path = os.path.join(image_folder, f'{message.id}.png')
        response = requests.get(image_url)
        with open(image_path, 'wb') as image_file:
            image_file.write(response.content)

        # Create an embed
        embed = discord.Embed(
            title=f"FEEDBACK BOT | {servername}",
            color=embed_color  # Set the embed color
        )
        embed.set_image(url=message.attachments[0].url)

        if message.guild.icon:
            embed.set_thumbnail(url=message.guild.icon.url)

        # Add the rating to the embed
        embed.add_field(name="Rating", value=ratings[message.author.id])

        # Extract the username, profile picture, and time from the message instance
        username = message.author.name
        avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        # Set the footer with username, profile picture, and time
        embed.set_footer(text=f"{username} | {current_time}", icon_url=avatar_url)

        # Send the image to the desired channel (replace CHANNEL_ID with the actual channel ID)
        channel = bot.get_channel(proof_Channel)
        await channel.send(embed=embed)

        # Send the success message
        success_embed = discord.Embed(
            title=f"FEEDBACK BOT | {servername}",
            description="✅ Successfully submitted feedback!",
            color=embed_color  # Set the embed color
        )
        success_embed.set_thumbnail(url=message.guild.icon.url) if message.guild.icon else None
        await message.channel.send(embed=success_embed)

        # Delete the user's rating message and the image
        await message.delete()

        # Remove the user's rating from the list to prevent repetition
        del ratings[message.author.id]

        # Lösche das Feedback_Embed
        await Feedback_Embed.delete()

    await bot.process_commands(message)

@bot.command()
async def embed(ctx):
    # Create an embed with the specified color
    embed = discord.Embed(
        title="Server Information",
        description=f"Information about {ctx.guild.name}",
        color=embed_color  # Set the embed color
    )

    # Add fields to the embed
    embed.add_field(name="Server Name", value=ctx.guild.name, inline=False)
    embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)

    # Add server logo to the embed
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    # Send the embed
    await ctx.send(embed=embed)

bot.run(token)
