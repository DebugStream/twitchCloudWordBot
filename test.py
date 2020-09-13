import json
import os
from dotenv import load_dotenv
from twitter import TwitterService
import paho.mqtt.client as mqtt


load_dotenv()

client = mqtt.Client()
client.connect("localhost")


twitter_service = TwitterService(
    tw_consumer_key=os.environ['TW_CONSUMER_KEY'],
    tw_consumer_secret=os.environ['TW_CONSUMER_SECRET'],
    tw_access_key=os.environ['TW_ACCESS_KEY'],
    tw_access_secret=os.environ['TW_ACCESS_SECRET']
)

terms = [
    'xbox',
    'brazil',
    'nintendo',
    'netflix',
    'camila',
    'microsoft',
    'auronplay',
    'disney plus',
    'ministerio de cultura',
    'peru',
    'swing',
    'luisito comunica',
    'lofi rap',
    'techno 90',
    'pokemons',
    'covid19',
    'coronavirus',
    'ceviche'
]
# terms = ['lofi', 'madona pop', 'america', 'panama', 'peru', 'guatemala']
for x in terms:
    term = str(f'!cw {x}') \
        .replace('!cw', '')

    print(term)
    r = twitter_service.search_term(term, 'edux87')
    print(json.dumps(r.to_dict()))
    client.publish("cloudwords", json.dumps(r.to_dict()))
