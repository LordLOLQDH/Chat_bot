import discord
from discord.ext import commands
from huggingface_hub import InferenceClient
import os
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
BOT_CHANNEL_ID = int(os.getenv("BOT_CHANNEL_ID"))
HISTORY_FILE = "chat_history.json"

client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=HF_TOKEN)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Chatverlauf laden
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        chat_history = json.load(f)
else:
    chat_history = {}

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

SYSTEM_PROMPT = """Du bist ein hilfsbereiter Discord Bot.
Du kannst übersetzen, programmieren, erklären und normal chatten.
Antworte kurz, hilfreich und auf Deutsch. Nutze den gesamten Gesprächsverlauf."""

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    print(f"Aktiver Kanal: {BOT_CHANNEL_ID}")
    print(f"Geladene User-Verläufe: {len(chat_history)}")

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return
    if message.channel.id!= BOT_CHANNEL_ID:
        return

    user_id = str(message.author.id)
    user_msg = message.content.strip()

    if user_msg == "/reset!":
        chat_history[user_id] = []
        save_history()
        await message.reply("🧹 Speicher gelöscht!")
        return

    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "user", "content": user_msg})

    async with message.channel.typing():
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[user_id]
            prompt = "<s>"
            for m in messages:
                prompt += f"{m['role'].capitalize()}: {m['content']}\n"
            prompt += "Assistant: "

            # Falls Prompt zu lang wird, alte Nachrichten kürzen
            if len(prompt) > 6000:
                messages = [messages[0]] + messages[-20:]
                prompt = "<s>"
                for m in messages:
                    prompt += f"{m['role'].capitalize()}: {m['content']}\n"
                prompt += "Assistant: "

            response = client.text_generation(
                prompt,
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                stop=["User:", "</s>"]
            )
            answer = response.strip()
            chat_history[user_id].append({"role": "assistant", "content": answer})
            save_history()
            await message.reply(answer)

        except Exception as e:
            await message.reply(f"Fehler: {e}")

bot.run(DISCORD_TOKEN)
