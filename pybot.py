import aiohttp
import discord
import time
import random
import asyncio

import requests
from pyjokes import pyjokes # Despite the red lines, this works just fine. no errors
from discord.ext import commands
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from apiclient.discovery import build
from io import BytesIO
import urllib.parse as urlparse
import face_recognition
import os


# Constants
BTS_IMAGES_PATH = './BTS Members/'
MESSAGE_IMGS_PATH ='./Message Imgs/'

"""
Determines if the image passed in contains faces of any bts members

img= the picture as a bytes object to pass into the face recognition functions.

Return boolean True or False if a match is found. img is compared to the pictures in the path
specified by BTS_IMAGES_PATH
"""
def image_is_bts_content(img):
    tolerance = 0.5 # Threshold of match for the image.

    # Encode the picture and prepare it for facial recognition.
    picture = face_recognition.load_image_file(img)
    picture_encoding = face_recognition.face_encodings(picture)[0]  # I just want the first item

    for file in os.listdir(BTS_IMAGES_PATH):
        # For every file in BTS members, check if it is in fact one of the members.
        # The bts picture to compare it to.
        bts_picutre = face_recognition.load_image_file(BTS_IMAGES_PATH + '/' + file)
        bts_picture_encoding = face_recognition.face_encodings(bts_picutre)[0]

        # Compare faces
        results = face_recognition.compare_faces([picture_encoding], bts_picture_encoding, tolerance=tolerance)
        print(f'Results after comparing to {file}: {results}')

        if results[0]:
            print("Match Found with file " + file)
            return True
    #endfor

    print("No match found")
    return False

#enddef


class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged in as ' + self.user.name)
        print(self.user.id)
        print('------')
        servers = list(client.guilds)

        self.messages_deleted = 0
        self.messages_edited = 0

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


    """Method to display status of Pybot"""
    async def status(self, message):
        await message.channel.send('Online. 0 user suspended\n{} messages deleted. {} edited.'.format(self.messages_deleted, self.messages_edited))
    #enddef

    """
    Handles the message passed in if it is not from the bot itself.
    """
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
        #endif


        # Alert of incoming message and specify the author.
        print('Message from ' + real_name + ': ' + str(message.content))

        # If the status command is entered by me and me only.
        if message.content.startswith('.status') and real_name == ME:
            time.sleep(2.0)
            await self.status(message)
        # endif

        # First thing to do is to check if the message contains a URL
        if (self.is_url_(message)):
            print("URL Detected")
            if 'youtube' in str(message.content) or 'youtu.be' in str(message.content):
                print("Youtube URL Detected")

                if self.is_bts_video(message):
                    await self.delete_video(message, real_name)
                #endif
                else:
                    print("OK, not a BTS video")
                #endelse
            #endif
            else:
                # Check to see if the URL is an image of a BTS photo
                url = str(message.content)
                r = requests.get(url)
                img = BytesIO(r.content)

                if image_is_bts_content(img):
                    await self.delete_picture(message, real_name)
                # endif
        #endif

        if message.content.startswith('hello') or message.content.startswith('Hello') or message.content.startswith(' hi ') or message.content.startswith(' hey '):
            time.sleep(3)
            random_num = random.randint(0, len(greetings) - 1)
            random_greeting = greetings[random_num]

            await message.channel.send(random_greeting + ' ' + real_name.format(message))
        #endif

        elif 'say good night pybot' in message.content.lower():
            time.sleep(3.0)
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

        # If the message has files and attachments check if its bts content.
        elif message.attachments:
            attachments = message.attachments   # Get the list of attachments in the message.
            print(attachments)  # See the contents of the list.

            url = attachments[len(attachments) - 1].proxy_url   # Store the filename of the last one sent.
            print(f'URL of image: {url} loaded')

            r = requests.get(url)
            img = BytesIO(r.content)

            # If the image has BTS content, delete the message with the picture.
            if image_is_bts_content(img):
                await self.delete_picture(message, real_name)
            #endif
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

        # If the shutdown command is given. End the script.
        elif client.user in message.mentions and '.shutdown' in str(message.content) and real_name == ME:
            time.sleep(2.0)
            await message.channel.send('Pybot logging off...')
            exit()
        #endelif
    #enddef


    """
    Deletes a message with a BTS picture.
    """
    async def delete_picture(self, message, real_name):
        time.sleep(2.0)
        await message.channel.send('BTS detected! No BTS memes or pictures are allowed {}!'.format(real_name))
        time.sleep(2.0)
        await message.delete()
    #enddef

    async def delete_video(self, message, real_name):
        time.sleep(3.0)
        await message.channel.send('Attention {}, BTS videos are prohibited.'.format(real_name))
        time.sleep(2.0)
        await message.delete()
        await message.channel.send('Pop!')
        self.messages_deleted = self.messages_deleted + 1
    #enddef

    """
    Checks if any bts member is mentioned in the filename of the image
    
    filename= a string with the name of the file.
    
    Returns True or False if any member is found in the name of the file.
    """
    def bts_members_in_filename(self, filename):
        for member in bts_members:

            if member in filename:
                print('Found {} in filename'.format(member) )
                return True
            #endif
        #endfor
        return False
    #endef

    """
    When a member joins pybot will greet them
    member= the member object that joined the guild/server
    """
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)
        #endif
    #enddef

    """
    If a message is edited, Pybot will handle it by showing the before and after versions of the message.
    """
    async def on_message_edit(self, before, after):
        if str(before.content) == str(after.content):
            return
        #endif

        self.messages_edited = self.messages_edited + 1

        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        await before.channel.send(fmt.format(before, after))
    #enddef

    """
    Determines if the message contains a request for a joke.
    Returns True or False if the message contains a joke request.
    """
    def is_joke_request(self,message):
        return 'pybot tell a joke' in message.content.lower() or 'tell a joke pybot' in message.content.lower()
    #enddef

    """
    Pybot responds to khan if message is authored by Khan
    message= the message sent by Khan
    """
    async def respond_to_khan(self, message):
        random_num = random.randint(0, len(khan_responses) - 1)
        time.sleep(3.0)
        await message.channel.send(khan_responses[random_num])
    #enddef

    """
    Pybot responds to Dakota if message is authored by Dakota and Pybot is mentioned.
    message= the messsage sent my Dakota
    """
    async def respond_to_dakota(self, message):
        random_num = random.randint(0, len(dakota_responses) - 1)
        time.sleep(3.0)
        await message.channel.send(dakota_responses[random_num])
    #enddef

    """
    Pybot will tell a random joke
    message= used to acquire the channel to send the joke.
    """
    async def tell_joke(self, message):
        time.sleep(3.0)
        await message.channel.send(pyjokes.get_joke())
    #enddef

    """
    Determines if the message is a url.
    message= the message sent that could contain a URL.
    Returns true or false if the URL can be validated.
    """
    def is_url_(self, message):
        val = URLValidator()
        try:
            val(str(message.content))
            return True
        except ValidationError:
            return False
    #enddef

    """
    Method to determine if the video is a BTS video
    message= the message sent.
    """
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

            # Check if any of the members are mentioned now
            for member in bts_members:
                print("Checking for {}".format(member))
                if member in result['snippet']['title'].lower():
                    print('Found BTS member {} in title of video'.format(member))
                    return True
                #endif
            #endfor
        #endfor

        return False
    #enddef



#endclass

client = MyClient()

#api key for youtube
API_KEY = 'AIzaSyDDh4akmSBgNntLYpc4gJIe3u8kP5lzZLU'
ME = 'Phil'

real_names = {'Dread_Lock': 'Dakota',
              'thunderD568': 'Phil',
              'Kit': 'Kit',
              '(っ◔◡◔)っ lï††lêþåñ¢kê§': 'Kirra',
              'RunningRaptor22':'Grant',
              'カジュアル': 'Khan'}

#List of BTS members
bts_members = ['j-hope',
               'suga',
               'jungkook',
               'rm', ' v ',
               'jimin',
               'kim seokjin',
               'kim taehyung' ]

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