import discord
from discord.ext import voice_recv
import google.generativeai as genai
import edge_tts
import speech_recognition as sr
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = voice_recv.VoiceRecvClient(intents=intents)

recognizer = sr.Recognizer()

# -------- GEMINI --------
async def perguntar_gemini(texto):
    resposta = model.generate_content(texto)
    return resposta.text

# -------- TTS --------
async def falar(texto, vc):

    arquivo = "resposta.mp3"

    tts = edge_tts.Communicate(texto[:200], "pt-BR-AntonioNeural")
    await tts.save(arquivo)

    vc.play(discord.FFmpegPCMAudio(arquivo))

    while vc.is_playing():
        await asyncio.sleep(1)

# -------- RECEBER AUDIO --------
class Listener(voice_recv.AudioSink):

    def __init__(self, vc):
        self.vc = vc

    def write(self, user, data):

        with open("input.wav", "ab") as f:
            f.write(data.pcm)

    def cleanup(self):

        try:
            with sr.AudioFile("input.wav") as source:
                audio = recognizer.record(source)

            texto = recognizer.recognize_google(audio, language="pt-BR")

            print("Usuário disse:", texto)

            resposta = asyncio.run(perguntar_gemini(texto))
            asyncio.run(falar(resposta, self.vc))

        except:
            pass

# -------- DISCORD --------
@client.event
async def on_ready():
    print("Bot ouvindo!")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    if message.content == "!entrar":

        if message.author.voice:
            canal = message.author.voice.channel
            vc = await canal.connect(cls=voice_recv.VoiceRecvClient)

            vc.listen(Listener(vc))

client.run(TOKEN)
