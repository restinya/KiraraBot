import discord
from discord.ext import commands
from utawaku import download_audio
import os

class DownloadCog(commands.Cog, name='download'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def download(self, ctx, url):
            file_name = download_audio(url)
            channel = ctx.channel
            try:
                await channel.send(file=discord.File(file_name))
            except:
                await channel.send("There was an error in uploading the file.")
            os.remove(file_name)

def setup(bot):
    bot.add_cog(DownloadCog(bot))
    print('download cog loaded')