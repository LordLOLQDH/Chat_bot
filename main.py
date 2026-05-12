import discord
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot ist online als {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')

# Webserver für UptimeRobot starten
keep_alive()

# Bot starten
TOKEN = os.getenv('TOKEN')
client.run(TOKEN)
