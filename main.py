import discord
import os
from keep_alive import keep_alive

# Intents setzen
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Secrets laden
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
HF_TOKEN = os.getenv('HF_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID')) if os.getenv('CHANNEL_ID') else None

@client.event
async def on_ready():
    print(f'Bot ist online als {client.user}')
    if CHANNEL_ID:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send('Bot ist gestartet!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    
    if message.content.startswith('!hf'):
        await message.channel.send(f'HF Token geladen: {"Ja" if HF_TOKEN else "Nein"}')

# Webserver für UptimeRobot starten
keep_alive()

# Bot starten
client.run(DISCORD_TOKEN)
