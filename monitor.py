import discord
import pyautogui
import time
from PIL import ImageChops
import asyncio
import signal
import sys
from io import BytesIO

channel_name = ""
link = ""

# Discord bot token
with open("token.txt") as file:
    TOKEN = file.read()

# Channel ID where you want the bot to send messages
CHANNEL_ID = 1234567890  

# Define your monitor region
monitor_region = (1464, 171, 311, 43)

# Initialize intents
intents = discord.Intents.default()
intents.messages = True

# Initialize the Discord client with intents
client = discord.Client(intents=intents)

# Take initial screenshot
previous_screenshot = pyautogui.screenshot(region=monitor_region)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    asyncio.create_task(detect_change())
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("**Monitor for @" + channel_name + "'s giveaways has started**", silent=True)
    await send_message(link, silent=True)

async def send_message(message, silent=False):
    channel = client.get_channel(CHANNEL_ID)
    if silent:
        await channel.send(message, silent=True)
    else:
        await channel.send(message)

async def send_image(image):
    channel = client.get_channel(CHANNEL_ID)
    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(image_binary, filename='image.png')
        await channel.send(file=file, silent=True)

async def detect_change():
    global previous_screenshot
    started = False
    while True:
        # Capture current screenshot
        current_screenshot = pyautogui.screenshot(region=monitor_region)
        
        # Compare screenshots
        diff = ImageChops.difference(previous_screenshot, current_screenshot)
        if diff.getbbox():  # If there is a difference
            if started == False:
                await send_message("@" + channel_name + " is running a giveaway!")
                await send_image(current_screenshot)  # Send the image of the change
                started = True
            else:
                started = False
                await send_message("Giveaway has ended.", silent=True)
            # Perform your action here
            
        # Update previous screenshot
        previous_screenshot = current_screenshot
        
        # Add a small delay to prevent high CPU usage
        await asyncio.sleep(5)

def signal_handler(sig, frame):
    asyncio.create_task(stop_bot())

async def stop_bot():
    await send_message("**Giveaways for @" + channel_name + " are no longer being monitored**", silent=True)
    await client.close()

# Set up the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Start the bot
client.run(TOKEN)
