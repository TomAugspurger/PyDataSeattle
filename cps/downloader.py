# -*- coding: utf-8 -*-
"""
Get the raw monthly CPS files from

http://www.nber.org/data/cps_basic.html
"""
import os
import click
import requests
import pandas as pd


def download_month(url, cache=True):
    """
    url like http://nber.../jan08pub.zip

    Download to `data/YYYY-MM`
    """
    month = pd.to_datetime(url.split('/')[-1][:5], format='%b%y')
    fp = os.path.join('data', month.strftime('%Y-%m') + '.zip')

    if cache and os.path.exists(fp):
        return fp
    r = requests.get(url, stream=True)
    with open(fp, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return fp

def make_months(start, end):
    months = pd.period_range(start=start, end=end, freq='M')
    return months

def download_months(start, end, cache=True):
    base_url = 'http://www.nber.org/'

    months = make_months(start, end)
    links = ["cps-basic/{}pub.zip".format(x.strftime('%b%y').lower())
             for x in months]
    N = len(links)
    for i, link in enumerate(links):
        url = base_url + link
        download_month(url, cache=cache)
        print(url, '{}/{}'.format(i, N), end='\r')

# -----------------
# Data Dictionaries
# -----------------

def make_dd_fp(start, end):
    "dd/dd_<start>_<end>.txt; Valid from start-end"
    return 'dds/dd_{}_{}.txt'.format(start, end)


def download_dds(cache=True):
    # tuples of (url, start, end) for when that dd was valid (closed both sides)
    DDS = [('http://thedataweb.rm.census.gov/pub/cps/basic/200508-/augnov05dd.txt', '2005-08', '2006-12'),
           ('http://thedataweb.rm.census.gov/pub/cps/basic/200701-/jan07dd.txt', '2007-01', '2008-12'),
           ('http://www.nber.org/cps-basic/cpsbjan09.ddf', '2009-01', '2009-12'),
           ('http://www.nber.org/cps-basic/cpsbjan10.ddf', '2010-01', '2012-04'),
           ('http://www.nber.org/cps-basic/cpsbmay12.ddf', '2012-05', '2012-12'),
           ('http://thedataweb.rm.census.gov/pub/cps/basic/201301-/January_2013_Record_Layout.txt', '2013-01', '2013-12'),
           ('http://thedataweb.rm.census.gov/pub/cps/basic/201401-/January_2014_Record_Layout.txt', '2014-01', '2014-12'),
           ('http://www.nber.org/cps-basic/January_2015_Record_Layout.txt', '2015-01', '2015-06')]
    for url, start, end in DDS:
        fp = make_dd_fp(start, end)
        if cache and os.path.exists(fp):
            print('cached {}'.format(fp))
            continue
        r = requests.get(url)
        with open(fp, 'w') as f:
            f.write(r.text)
        print(url, start, end)

@click.command()
@click.option("--job", type=click.Choice(["dd", "monthly"]))
def cli(job):
    if job == "dd":
        print("Data Dictionaries")
        os.makedirs('dds/', exist_ok=True)
        download_dds()

    elif job == "monthly":
        os.makedirs('data/', exist_ok=True)
        download_months('2005-08', '2015-06')

if __name__ == '__main__':
    cli()

