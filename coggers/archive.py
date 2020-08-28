import discord
from discord.ext import commands
from utawaku import archive_audio, archive_video
import os

class ArchiveCog(commands.Cog, name='archive'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def archive(self, ctx, url, archive_type):
            if archive_type == 'video':
                archive_video(url)
            if archive_type == 'audio':
                archive_audio(url)
            channel = ctx.channel
            try:
                await channel.send('Uploaded file to {url}'.format(url='https://drive.google.com/open?id=' + file_id.get('id')))
            except:
                await channel.send("There was an error in uploading the file.")
            os.remove(file_name)

def setup(bot):
    bot.add_cog(ArchiveCog(bot))
    print('archive cog loaded')