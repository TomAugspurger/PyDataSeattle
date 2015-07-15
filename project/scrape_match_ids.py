# -*- coding: utf-8 -*-
"""
Scrape match ids from datdota for pro matches

# Tournaments

- TI4

"""
import os
import json
import time

from lxml import html
import requests
import pandas as pd
from sqlalchemy import create_engine


with open(os.path.expanduser('/Users/tom.augspurger/Dropbox/bin/api-keys.txt')) as f:
    KEY = json.load(f)['steam']

def get_tournaments():
    url = "http://www.datdota.com/events.php"
    tree = html.parse(url)
    root = tree.getroot()
    tournaments = filter(lambda x: 'tournament' in x[2], root.iterlinks())
    pairs = ((x[0].text, x[2].split('&')[0]) for x in tournaments)

    base = "http://www.datdota.com/"
    seen = set()
    for name, q in pairs:
        if q not in seen:
            df = scrape_tournament(base + q)
            if df is None:
                continue
            df['tournament_name'] = name
            seen.update(q)
            yield df

def scrape_tournament(url):
    """
    url -> Maybe DataFrame
    """
    tables = pd.read_html(url, attrs={'class': 'dataTable'})
    assert len(tables) == 1
    df = tables[0]
    if len(df) == 0:
        return None
    score = df.Score.str.split(' - ', expand=True).rename(
        columns={0: 'score_radiant', 1: 'score_dire'}
    )
    df[['score_radiant', 'score_dire']] = score
    df['Date'] = pd.to_datetime(df.Date)
    df = df.drop('Score', axis=1).rename(columns=lambda x: x.lower())
    return df

def get_match_details(match_id):
    base = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/"
    payload = {'match_id': match_id, 'key': KEY}
    r = requests.get(base, params=payload)
    return r.json()['result']

def parse_result(r):
    pass

def main():
    engine = create_engine('sqlite:///data/dota.db')
    tournaments = get_tournaments()
    for tournament, url in tournaments:
        df = scrape_tournament(url)
        df['tournament'] = tournament
        df.to_sql('tournaments', engine, if_exists='append', index=False)
        print("Finished", tournament, end='\r')
        time.sleep(.5)

