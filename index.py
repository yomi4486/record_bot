import discord,audio2txt,os
bot = discord.Bot()
from pydub import AudioSegment
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("BOT_TOKEN")

@bot.command(description="ボイスチャンネルに参加します。")
async def join(ctx):
    if ctx.author.voice is None:
        embed = discord.Embed(title="エラー",description="あなたがボイスチャンネルに参加していません。",color=discord.Colour.red())
        await ctx.respond(embed=embed)
        return
    try:
        await ctx.author.voice.channel.connect()
    except Exception as e:
        embed = discord.Embed(title="エラー",description="ボイスチャンネルに接続できません。\nボイスチャンネルの権限を確認してください。",color=discord.Colour.red())
        await ctx.respond(embed=embed)
        print(e)
        return
    embed = discord.Embed(title="成功",description="ボイスチャンネルに接続しました。",color=discord.Colour.green())
    await ctx.respond(embed=embed)

@bot.command(description="ボイスチャンネルから切断します。")
async def leave(
    ctx,
):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(title="エラー",description="ボイスチャンネルに接続していません。",color=discord.Colour.red())
        await ctx.respond(embed=embed)
        return
    await ctx.guild.voice_client.disconnect()
    embed = discord.Embed(title="成功",description="ボイスチャンネルから切断しました。",color=discord.Colour.green())
    await ctx.respond(embed=embed)

@bot.command(description="録音を開始します。")
async def record(
    ctx:discord,
):
    format_sink = discord.sinks.MP3Sink()
    if ctx.guild.voice_client is None:
        embed = discord.Embed(title="エラー",description="ボイスチャンネルに接続していません。",color=discord.Colour.red())
        await ctx.respond(embed=embed)
        return
    ctx.voice_client.start_recording(format_sink, finished_callback, ctx)
    embed = discord.Embed(title="成功",description="ボイスチャンネルの録音を開始しました。",color=discord.Colour.green())
    await ctx.respond(embed=embed)

@bot.command(description="録音を停止します。")
async def record_stop(
    ctx,
):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(title="エラー",description="ボイスチャンネルに接続していません。",color=discord.Colour.red())
        await ctx.respond(embed=embed)
        return
    ctx.voice_client.stop_recording()
    embed = discord.Embed(title="成功",description="ボイスチャンネルの録音を停止しました。",color=discord.Colour.green())
    await ctx.respond(embed=embed)

async def finished_callback(sink, ctx, *args):
    recorded_users = [f"<@{user_id}>" for user_id, _ in sink.audio_data.items()]
    for user_id,audio in sink.audio_data.items():
        AudioSegment.from_file(audio.file, format="mp3").export(f"{user_id}.mp3",format="mp3")
    descriptions = [audio2txt.file2txt(path=f"{user_id}.mp3") for user_id, _ in sink.audio_data.items()]
    try:
        await ctx.respond(f"録音が完了しました！\n録音されたユーザー: {', '.join(recorded_users)}.\n内容：\n{', '.join(descriptions)}"[:2000])
    except:
        try:
            await ctx.guild.voice_client.channel.send(f"録音が完了しました！\n録音されたユーザー: {', '.join(recorded_users)}.\n内容：\n{', '.join(descriptions)}"[:2000])
        except Exception as e:
            print(e)

@bot.event # ミュート解除されたら録音開始、ミュート時に録音を終了し、会話内容をテキストにして送信。
async def on_voice_state_update(member, prev, cur):
    if cur.self_mute and not prev.self_mute:
        if member.guild.voice_client is None:
            return
        member.guild.voice_client.stop_recording()
        embed = discord.Embed(title="成功",description="ボイスチャンネルの録音を停止しました。",color=discord.Colour.green())
        await member.guild.voice_client.channel.send(embed=embed)
    elif prev.self_mute and not cur.self_mute:
        format_sink = discord.sinks.MP3Sink()
        if member.guild.voice_client is None:
            return
        member.guild.voice_client.start_recording(format_sink, finished_callback, member)
        embed = discord.Embed(title="成功",description="ボイスチャンネルの録音を開始しました。",color=discord.Colour.green())
        await member.guild.voice_client.channel.send(embed=embed)

bot.run(TOKEN)