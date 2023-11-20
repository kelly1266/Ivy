import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from gtts import gTTS
import asyncio

load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!ivy ', intents=intents)

@client.command()
async def intro(ctx):
    if (len(ctx.message.attachments) == 0):
        await ctx.send("Error: Message did not contain an attachment")
        return

    if (len(ctx.message.attachments) > 1):
        await ctx.send("Error: Message contained more than 1 attachment")
        return

    att = ctx.message.attachments[0]

    if (not att.filename.endswith(".mp3")):
        await ctx.send("Error: File must be an mp3")
        return

    intro_path = f"./intros/{ctx.author.id}.mp3"
    await att.save(intro_path)
    await ctx.send("File upload complete")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    if(not os.path.exists("./intros/default.mp3")):
        msg = "Looks like some dumb ass without an intro just joined the channel"
        phrase_mp3 = gTTS(text=msg, lang="en", slow=False)
        phrase_mp3.save("./intros/default.mp3")

@client.event
async def on_voice_state_update(member, before, after):
    joined = (before.channel is None) and (after.channel is not None)
    left_channel = (before.channel is not None) and (after.channel is None)
    valid_join_condition = (not member.bot) and (len(client.voice_clients) == 0)

    if (not valid_join_condition):
        return

    if (joined):
        ffmpeg_executable_path = os.environ.get("FFMPEG_PATH")
        mp3_file_path = f"./intros/{member.id}.mp3"
        if (not os.path.exists(mp3_file_path)):
            mp3_file_path = "./intros/default.mp3"

        # Join channel and play the intro
        vc = await after.channel.connect()
        src = discord.FFmpegPCMAudio(executable=ffmpeg_executable_path, source=mp3_file_path)
        vc.play(src)
        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
    elif (left_channel and len(before.channel.members) > 0):
        # Create leaving message
        name = member.nick if member.nick is not None else member.name
        msg = f"{name} has left the channel"
        phrase_mp3 = gTTS(text=msg, lang="en", slow=False)
        phrase_mp3.save(f"./outros/{member.id}.mp3")
        
        # Join channel and play the message
        vc = await before.channel.connect()
        ffmpeg_executable_path = os.environ.get("FFMPEG_PATH")
        mp3_file_path = f"./outros/{member.id}.mp3"
        src = discord.FFmpegPCMAudio(executable=ffmpeg_executable_path, source=mp3_file_path)
        vc.play(src)
        while vc.is_playing():
            await asyncio.sleep()
        await vc.disconnect()


token = os.environ.get("DISCORD_TOKEN")
client.run(token)