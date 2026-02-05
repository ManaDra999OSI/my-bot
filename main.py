import discord
import google.generativeai as genai
import edge_tts
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# -------- GEMINI --------
async def perguntar_gemini(texto):
    resposta = model.generate_content(texto)
    return resposta.text

# -------- TTS --------
async def falar(texto, voice_client):

    arquivo = "voz.mp3"

    tts = edge_tts.Communicate(texto[:200], "pt-BR-AntonioNeural")
    await tts.save(arquivo)

    voice_client.play(discord.FFmpegPCMAudio(arquivo))

    while voice_client.is_playing():
        await asyncio.sleep(1)

# -------- DISCORD --------
@client.event
async def on_ready():
    print("Bot online!")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    if message.content == "!entrar":

        if message.author.voice:
            canal = message.author.voice.channel
            await canal.connect()

    if message.content.startswith("!ai"):

        pergunta = message.content.replace("!ai ", "")

        await message.channel.send("Pensando...")

        resposta = await perguntar_gemini(pergunta)

        voice_client = discord.utils.get(client.voice_clients)

        if voice_client:
            await falar(resposta, voice_client)

        await message.channel.send(resposta)

client.run(TOKEN)
