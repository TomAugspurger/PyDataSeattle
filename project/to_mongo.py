# -*- coding: utf-8 -*-
"""
Dumping a bunch of data into a mongodb file to save the servers.
Not part of the actual tutorial.

*NOTE*: make sure to have a mongodb process running

```
mongod --dbpath=data/db
```

"""
import time

from pymongo import MongoClient
from blaze import Data
from sqlalchemy import create_engine

from scrape_match_ids import get_tournaments, get_match_details

def load_match_ids():
    """
    Probably from sqlite
    """
    d = Data('sqlite:///data/dota.db::tournaments')
    return d.match.distinct()

def main():
    N = 0
    client = MongoClient()
    db = client.dota
    matches = db.matches
    engine = create_engine("sqlite:///data/dota.db")
    tournaments = get_tournaments()

    for tournament in tournaments:
        tournament.to_sql('tournaments', engine, index=False, if_exists='append')

        for match in tournament.match:
            while True:
                try:
                    details = get_match_details(match)
                    N += 1
                    break
                except KeyError:
                    time.sleep(30)
            matches.insert(details)
            print(match, N, end='\r', sep=',')
            time.sleep(1.1)

