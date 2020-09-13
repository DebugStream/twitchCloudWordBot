import json
import os
from twitchio.ext import commands
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from twitter import TwitterService

load_dotenv()

bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)

twitter_service = TwitterService(
    tw_consumer_key=os.environ['TW_CONSUMER_KEY'],
    tw_consumer_secret=os.environ['TW_CONSUMER_SECRET'],
    tw_access_key=os.environ['TW_ACCESS_KEY'],
    tw_access_secret=os.environ['TW_ACCESS_SECRET']
)


@bot.event
async def event_ready():
    """Called once when the bot goes online."""
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me estoy listo")


@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    await bot.handle_commands(ctx)

    # await ctx.channel.send(ctx.content)

    if 'hello' in ctx.content.lower():
        await ctx.channel.send(f"Hi, @{ctx.author.name}!")


@bot.command(name='test')
async def test(ctx):
    await ctx.send('test passed!')


@bot.command(name='cw')
async def cloud_word(ctx):
    term = str(ctx.content)\
        .replace('!cw', '')

    client = mqtt.Client()
    client.connect("localhost")

    response = twitter_service.search_term(term, ctx.author.name)
    if response.has_error is False:
        client.publish("cloudwords", json.dumps(response.to_dict()))
    await ctx.send(response.message)


if __name__ == "__main__":
    bot.run()
