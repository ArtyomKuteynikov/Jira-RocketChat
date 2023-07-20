import asyncio
import discord
from discord.ext import commands
from rocketchat_API.rocketchat import RocketChat
from settings import *
from jira_operations import jira_create_task
import json

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
bot = commands.Bot(command_prefix='/', intents=intents)
rocket = RocketChat(rocket_username, rocket_password, server_url=rocket_url)
cache = open("cache.json", "r")
cache = cache.read()
sent_messages = json.loads(cache)
users = open("users.json", "r")
users = users.read()
users = json.loads(users)


def send_message_to_rocket(message):
    if message.author.bot:
        return
    rocket.chat_post_message(f'{message.author.name}: {message.content}', channel=rocket_channel_id)


@bot.event
async def on_message(message):
    if message.channel.id == ds_channel_id:
        if message.content.startswith(r'\task') or message.content.startswith(r'/task'):
            if len(message.content.split('\n')) >= 4:
                if message.content.split('\n')[3] in users:
                    id = jira_create_task(message.content.split('\n')[1], message.content.split('\n')[2],
                                          assignee=users[message.content.split('\n')[3]])
                    channel = bot.get_channel(ds_channel_id)
                    await channel.send(f'Задача {id} создана')
                else:
                    channel = bot.get_channel(ds_channel_id)
                    await channel.send(f'Пользователь не найден')
            elif len(message.content.split('\n')) >= 3:
                id = jira_create_task(message.content.split('\n')[1], message.content.split('\n')[2])
                channel = bot.get_channel(ds_channel_id)
                await channel.send(f'Задача {id} создана')
            elif len(message.content.split('\n')) == 2:
                channel = bot.get_channel(ds_channel_id)
                await channel.send(f'Не задано поле "Description"')
            else:
                channel = bot.get_channel(ds_channel_id)
                await channel.send(f'Не задано поле "Summary"')
        else:
            if message.author != bot.user:
                send_message_to_rocket(message)


@bot.event
async def on_ready():
    while True:
        try:
            messages = rocket.channels_history(rocket_channel_id, count=1).json()['messages']
        except Exception:
            room_id = rocket.groups_info(rocket_channel_id).json()["channel"]["_id"]
            messages = rocket.groups_history(room_id, count=1).json()['messages']
        for message in messages:
            if message['u']['username'] == rocket_username:
                continue
            if message['u']['username'] != 'rocket.cat' and message['_id'] not in sent_messages:
                sent_messages.append(message['_id'])
                cache = open("cache.json", "w")
                cache.write(json.dumps(sent_messages))
                cache.close()
                if message["msg"].startswith(r'\task') or message["msg"].startswith(r'/task'):
                    if len(message["msg"].split('\n')) >= 4:
                        if message["msg"].split('\n')[3] in users:
                            id = jira_create_task(message["msg"].split('\n')[1], message["msg"].split('\n')[2],
                                                  assignee=users[message["msg"].split('\n')[3]])
                            rocket.chat_post_message(f'Задача {id} создана', channel=rocket_channel_id)
                        else:
                            rocket.chat_post_message(f'Пользователь не найден', channel=rocket_channel_id)
                    elif len(message["msg"].split('\n')) == 3:
                        id = jira_create_task(message["msg"].split('\n')[1], message["msg"].split('\n')[2])
                        rocket.chat_post_message(f'Задача {id} создана', channel=rocket_channel_id)
                    elif len(message["msg"].split('\n')) == 2:
                        rocket.chat_post_message(f'Не задано поле "Description"', channel=rocket_channel_id)
                    else:
                        rocket.chat_post_message(f'Не задано поле "Summary"', channel=rocket_channel_id)
                else:
                    channel = bot.get_channel(ds_channel_id)
                    await channel.send(f'{message["u"]["username"]}: {message["msg"]}')
        await asyncio.sleep(1)


if __name__ == '__main__':
    bot.run(ds_token)
