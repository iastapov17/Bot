import psycopg2
import json

with open('config.json') as f:
    config = json.load(f)

conn = psycopg2.connect(database=config['database'], user=config['user'], host=config['host'],
                        port=config['port'], password=config['password'])
BOT_TOKEN = config['token']
cursor = conn.cursor()
