from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv('.env'))


class Config:
    ENV = os.getenv('ENV')
    DEV = ENV == 'development'
    DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
    AUTH = os.getenv('AUTH')
    PORT = int(os.getenv('PORT'))
    DOMAIN = 'sharpbit.tk' if not DEV else f'127.0.0.1:{PORT}'
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    BRAWLSTATS_OFFICIAL_TOKEN = os.getenv('BRAWLSTATS_OFFICIAL_TOKEN')