# -*- coding: utf-8 -*-
"""
From directory of zips to ?
"""
import os
import re
import glob
import json
import logging
import zipfile
from functools import lru_cache

import click
import pandas as pd

logger = logging.getLogger(__name__)
STOREPATH = 'data/store.h5'

# TODO: assert consistent / engarde
def dd_fp_to_span(fp):
    """dd_YYYY-MM_YYYY-MM.txt -> YYYY-MM_YYY-MM"""
    return os.path.basename(fp).split('dd_')[-1].split('.')[0]

def span_to_dd_key(span):
    "2008-01_2008-12 -> /dds/2008_01_2008_12"
    return '/dds/dd{}'.format(span.replace('-', '_'))

def dd_key_to_span(key):
    "/dds/2008_01_2008_12 -> 2008-01_2008-12"
    parts = key.lstrip('/').lstrip('dds/dd').split('_')
    return '-'.join(parts[:2]) + '_' + '-'.join(parts[2:])

def parse_dd(fp):
    expr = re.compile(r'[\x0c]{0,1}(\w+)\*?[\s\t]*(\d{1,2})[\s\t]*(.*?)'
                      r'[\s\t]*\(*(\d+)\s*[\-–]\s*(\d+)\)*\s*$')
    with open(fp) as f:
        lines = (expr.match(x) for x in f)
        matches = filter(None, lines)
        groups = (x.groups() for x in matches)

        df = (pd.DataFrame(list(groups),
                           columns=['field', 'width', 'desc', 'start', 'end'])
                .convert_objects(convert_numeric=True))
    return df

def store_dd(dd, span):
    dd.to_hdf('data/store.h5', span_to_dd_key(span))

@lru_cache(1)
def _make_dd_map():
    with pd.HDFStore('data/store.h5') as store:
        keys = filter(lambda x: x.startswith('/dds'), store.keys())
        dds = map(dd_key_to_span, keys)
        d = {}
        for dd in dds:
            start, end = dd.split('_')
            for month in pd.period_range(start=start, end=end, freq='M'):
                d[month.strftime('%Y-%m')] = dd
    return d

def month_to_dd(month):
    key = month_to_dd_key(month)
    with pd.HDFStore('data/store.h5') as store:
        return store.select(key)

def month_to_dd_key(month):
    d = _make_dd_map()
    key = span_to_dd_key(d[month])
    return key

# -------
# Monthly
# -------

# Naming

def zip_fp_to_month(fp):
    return os.path.basename(fp).split(".")[0]

def month_to_hdf_key(month):
    "2015-01 -> monthly/2015_01"
    try:
        month = month.strftime('%Y-%m')
    except AttributeError:
        pass
    return "/monthly/m{}".format(month.replace('-', '_'))

def hdf_key_to_month(key):
    "[/]monthly/2015_01 -> 2015-01"
    return key.lstrip('/').lstrip('monthly/m').replace('_', '-')

# extracting

def extract(fp):
    logger.info("Unzipping %s", fp)
    z = zipfile.ZipFile(fp)
    assert len(z.namelist()) == 1
    name = z.namelist()[0]
    data_fp = z.extract(name, path='data')
    return data_fp

def parse_monthly(fp, cache=True, nrows=None):
    with open('interesting.json') as f:
        col_map = json.load(f)
        month = zip_fp_to_month(fp)
        hdf_key = month_to_hdf_key(month)
        dd_key = month_to_dd_key(month)
        span = dd_key_to_span(dd_key)
        cm = col_map[span]

    if cache:
        with pd.HDFStore('data/store.h5') as store:
            if hdf_key in store:
                return None

    data_fp = extract(fp)
    try:
        dd = month_to_dd(month)
        subset = dd.loc[dd.field.isin(cm.keys())]
        names = list(subset.field)
        colspecs = (subset[['start', 'end']]
                    .assign(start=lambda df: df.start - 1)
                    .values.tolist())
        # TALK: run through with subset first (nrows=100)

        df = (pd.read_fwf(data_fp, colspecs=colspecs, names=names,
                          usecols=names, nrows=nrows)
                .rename(columns=cm)
                .sort(['mis']))
        key = month_to_hdf_key(month)
        with pd.HDFStore(STOREPATH) as store:
            store.append(key, df, format='table', data_columns=True)
    except:
        os.remove(data_fp)
        raise
    os.remove(data_fp)

def filter_working_years(df):
    """
    Only those aged 18 - 65
    """
    return df.query('18 <= age <= 65')

def run_dd():
    dds = iter(glob.glob('dds/*.txt'))
    for fp in dds:
        span = dd_fp_to_span(fp)
        dd = parse_dd(fp)
        store_dd(dd, span)
        print(span, end='\r')

def run_monthly(cache=True, nrows=None):
    zips = iter(glob.glob('data/*.zip'))
    for fp in zips:
        parse_monthly(fp, cache=cache, nrows=nrows)
        print(fp, end='\r')


@click.command()
@click.option('--job-type', type=click.Choice(['all', 'dd', 'monthly']))
@click.option('--cache/--no-cache', default=True)
@click.option('--nrows', default=None, type=int)
def run(job_type, cache, nrows=None):

    if job_type == 'dd':
        run_dd()
    elif job_type == 'monthly':
        run_monthly(nrows=nrows)
    elif job_type == 'all':
        print("Running dd")
        run_dd()
        print("Running monthly")
        run_monthly(nrows=nrows)

if __name__ == '__main__':
    run()

