import discord
from discord.ext import commands
from time import sleep

kirara = commands.Bot(command_prefix='k.')
#kills me baby
class KillMeBaby(commands.Cog, name="kmb"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def killmebaby(self, ctx):
        await ctx.bot.close()
        #TODO : make it restart
        print("Bot logged out...?")

def setup(bot):
    bot.add_cog(KillMeBaby(bot))
    print('self destruct sequence loaded')