"""
app.model.py

"""

import requests

from app.config import _config


class Population:

    def get_population(self):
        return requests.get(_config.GEO_API).json()
