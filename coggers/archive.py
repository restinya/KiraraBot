import discord
from discord.ext import commands
from utawaku import archive_audio, archive_video
import os

class ArchiveCog(commands.Cog, name='archive'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def archive(self, ctx, url, archive_type):
        try:
            if archive_type == 'video':
                file_name, file_id = archive_video(url)
            if archive_type == 'audio':
                file_name, file_id = archive_audio(url)
            channel = ctx.channel
            await channel.send('Uploaded file to {url}'.format(url='https://drive.google.com/open?id=' + file_id))
            os.remove(file_name)
        except:
            await channel.send('Error in archiving file. Please retry in a few moments.')


def setup(bot):
    bot.add_cog(ArchiveCog(bot))
    print('archive cog loaded')