import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound, MissingPermissions
import os
import json
import random

# if not discord.opus.is_loaded():
# 	# The 'opus' library needs to be loaded in order to do voice stuffs on Discord.
# 	# If this part of the program doesn't run properly, make sure you have 'opus.dll' in Windows or 'libopus' installed if on Linux.
# 	# If still you get issues here, replace 'opus' with the directory location of 'opus' in the line below.
# 	discord.opus.load_opus('opus')

coggers = ['download', 'archive', 'kmb'] #modules
def launch_kirara():
    def loadtoken():
        # load globals defined in the config file

        global bot_token

        try:
            with open('configs/token.json') as f:
                print('loading token file for main bot')
                data = json.load(f)
                bot_token = data['token']
                return True
        except:
            bot_token = os.environ.get('bot_token')
            return True

    if not loadtoken():
        exit()

    kirara = commands.Bot(command_prefix='k.') #bot command

    #load our coggers
    def kirara_online():
        for load in coggers:
            try:
                kirara.load_extension('coggers.'+(load))
            except Exception as e:
                print('{} cannot be loaded. [{}]'.format(load, e))

        @kirara.event
        async def on_command_error(ctx, error):
            if isinstance(error, MissingPermissions):
                await ctx.message.add_reaction(emoji='😔')
                return

            raise error

    if __name__ == "__main__":
        kirara_online()

    @kirara.event
    async def on_ready():
        activity = discord.Activity(name='☄️🥐💫🎪', type=discord.ActivityType.watching)
        await kirara.change_presence(activity=activity)
        print('time to slurp')

    kirara.run(bot_token)


launch_kirara()