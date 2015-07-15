# -*- coding: utf-8 -*-
"""

"""
import requests
from sqlalchemy import create_engine

import pandas as pd

def get_match_ids(engine):
    query = """
    select match from tournaments
    order by match
    """
    matches = pd.read_sql_query(query, engine)
    return matches.match

def get_match(match_id):
    # We're serving this with eve
    base_url = 'http://127.0.0.1:5000/matches/'

def parse_match(details):
    pass

def main():
    engine = create_engine("sqlite:///data/dota.db")
    matches = get_match_ids(engine)
    for match_id in matches:
        details = get_match(match_id)
