"""
app.config.settings.py

"""
import os

from dotenv import load_dotenv


class Settings:

    def __init__(self):
        load_dotenv()
        self.HOST = os.getenv('HOST')
        self.API = os.getenv("URL")
        self.PORT = os.getenv('PORT')
        self.DISTRICT_URL = os.getenv("STATE_DISTRICT_API_URL")
        self.DATA_URL = os.getenv("DATA_URL")
        self.CASE_URL = os.getenv("CASE_URL")
        self.GEO_JSON = os.getenv("GEO_JSON_PATH")
