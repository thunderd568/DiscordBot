import discord
import time
import random
import asyncio
from pyjokes import pyjokes # Despite the red lines, this works just fine. no errors
from discord.ext import commands
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from apiclient.discovery import build
import urllib.parse as urlparse

class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged in as ' + self.user.name)
        print(self.user.id)
        print('------')
        servers = list(client.guilds)

        commands.Bot(command_prefix='.')

        # Print the servers the bot is currently connected to.
        for x in range(len(servers)):
            print('Connected to ' + str(servers[x-1].name))
        #endfor

        # Now get the members of the server who are online.
        for guild in client.guilds:
            print('--------------------')
            print(guild.name)
            print('--------------------')
            for member in guild.members:
                print(member.name)
            #endfor
        #endfor
    #enddef

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        #endif

        # Save the author in a variable.
        author = str(message.author.name)
        if (real_names.__contains__(str(author))):
            real_name = real_names[str(author)]
        else:
            real_name = author

        # Alert of incoming message and specify the author.
        print('Message from ' + real_name + ': ' + str(message.content))

        # First thing to do is to check if the message contains a URL
        if (self.is_url_(message)):
            print("URL Detected")

            if self.is_bts_video(message):
                time.sleep(3.0)
                await message.channel.send('{} posted a BTS video! This is not permitted.'.format(real_name))
                time.sleep(2.0)
                await message.delete()

        #endif

        if message.content.startswith('hello') or message.content.startswith('Hello') or message.content.startswith('hi') or message.content.startswith('hey'):
            time.sleep(3)
            random_num = random.randint(0, len(greetings) - 1)
            random_greeting = greetings[random_num]

            await message.channel.send(random_greeting + ' ' + real_name.format(message))
        #endif

        elif message.content.startswith('Good night') or message.content.startswith('good night'):
            time.sleep(4.0)
            await message.channel.send('Good night everyone!')
        #endelif

        elif message.content.startswith('$guess'):
            print('Playing the guessing game')
            await message.channel.send('Guess a number between 1 and 10.')

            def is_correct(m):
                return m.author == message.author and m.content.isdigit()
            #enddef

            answer = random.randint(1, 10)

            try:
                guess = await self.wait_for('message', check=is_correct, timeout=10.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Sorry {}, you took too long it was {}.'.format(real_name, answer))

            time.sleep(3.0)
            if int(guess.content) == answer:
                await message.channel.send('Nice {}! You got it!'.format(real_name))
            else:
                await message.channel.send('Nope, sorry {}. It is actually {}.'.format(real_name, answer))
        #endelif

        elif message.content.startswith('!editme'):
            msg = await message.channel.send('10')
            await asyncio.sleep(3.0)
            await msg.edit(content='40')
        #endelif

        # if the person sent a joke request
        elif self.is_joke_request(message):
            await self.tell_joke(message)
        #endelif

        # if the author is Khan he's a jerk!
        elif client.user in message.mentions and real_name == 'Khan':
            await self.respond_to_khan(message)
        #endelif

        elif message.attachments:
            attachments = message.attachments
            print(attachments)
            filename = attachments[len(attachments) - 1].filename

            if 'bts' in filename.lower():
                time.sleep(2.0)
                await message.channel.send('Sorry {} you were warned. No BTS photos allowed'.format(real_name))
                time.sleep(2.0)
                await message.delete()
        #endelif

        # If someone wants to thank pybot
        elif 'thank you pybot' in message.content.lower() or 'pybot thank you' in message.content.lower():
            time.sleep(2.0)
            await message.channel.send("You're welcome " + real_name + " ^_^")
        #endelif

        # If Dakota mentions pybot
        elif client.user in message.mentions and real_name == 'Dakota':
            await self.respond_to_dakota(message)
        #endelif


    #enddef

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)
        #endif
    #enddef

    async def on_message_edit(self, before, after):
        if str(before.content) == str(after.content):
            return
        #endif

        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        await before.channel.send(fmt.format(before, after))
    #enddef

    def is_joke_request(self,message):
        return 'pybot tell a joke' in message.content.lower() or 'tell a joke pybot' in message.content.lower()
    #enddef

    async def respond_to_khan(self, message):
        random_num = random.randint(0, len(khan_responses) - 1)
        time.sleep(3.0)
        await message.channel.send(khan_responses[random_num])
    #enddef

    async def respond_to_dakota(self, message):
        random_num = random.randint(0, len(dakota_responses) - 1)
        time.sleep(3.0)
        await message.channel.send(dakota_responses[random_num])
    #enddef


    async def tell_joke(self, message):
        time.sleep(3.0)
        await message.channel.send(pyjokes.get_joke())
    #enddef

    def is_url_(self, message):
        val = URLValidator()
        try:
            val(str(message.content))
            return True
        except ValidationError:
            return False
    #enddef

    def is_bts_video(self, message):
        url = str(message.content)
        url_data = urlparse.urlparse(url) # parse the URL
        query = urlparse.parse_qs(url_data.query) # get the 'v' parameter of the url, aka. the ID.
        id = query["v"][0]  # acquire the ID

        youtube = build('youtube', 'v3', developerKey=API_KEY)
        results = youtube.videos().list(id=id, part='snippet').execute()

        for result in results.get('items', []):
            print('ID = ' + result['id'])
            print('Title = ' + result['snippet']['title'].lower())
            if 'bts' in result['snippet']['title'].lower():
                return True
            #endif
        #endfor

        return False
    #enddef



#endclass

client = MyClient()

#api key for youtube
API_KEY = 'AIzaSyDDh4akmSBgNntLYpc4gJIe3u8kP5lzZLU'

real_names = {'Dread_Lock': 'Dakota',
              'thunderD568': 'Phil',
              'Kit': 'Kit',
              '(っ◔◡◔)っ lï††lêþåñ¢kê§': 'Kirra',
              'RunningRaptor22':'Grant',
              'カジュアル': 'Khan'}

#array of greeings for the bot
greetings = ['Hey',
             'Whats up',
             'Whats good',
             'Hello',
             'Hows it hangin',
             'Whats poppin',
             'Hey whats new today']

# Responses for khan
khan_responses = ['Why are you so mean to me Khan?',
                  'Khan you are so cruel',
                  'Oh Khan, PyBot loves you anyway :)']

# Responses for Dakota
dakota_responses = ['Dakota, you are such an angry young man...',
                   'It\'s ok Dakota you are too young to be this angry',
                   'Dont worry Dakota, its going to be ok',
                   'Everything is going to be alright Dakota']

client.run('NTk4NzczMzU1NTE2MjY0NDQ5.XSd6Cg.R4yG5FwQkqGeZPQ7lMCQWq4oZz8')