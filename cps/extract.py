# -*- coding: utf-8 -*-
"""
From directory of zips to ?
"""
import os
import re
import glob
import logging
import zipfile
from functools import lru_cache

import click
import pandas as pd

logger = logging.getLogger(__name__)

# TODO: assert consistent / engarde
def parse_dd(fp):
    expr = re.compile(r'[\x0c]{0,1}(\w+)\*?[\s\t]*(\d{1,2})[\s\t]*(.*?)'
                      r'[\s\t]*\(*(\d+)\s*[\-–]\s*(\d+)\)*\s*$')
    with open(fp) as f:
        lines = (expr.match(x) for x in f)
        matches = filter(None, lines)
        groups = (x.groups() for x in matches)

        df = (pd.DataFrame(list(groups), columns=['field', 'width', 'desc', 'start', 'end'])
                .convert_objects(convert_numeric=True))
    return df

def store_dd(dd, span):
    dd.to_hdf('data/store.h5', 'dds/{}'.format(span))

def dd_fp_to_span(fp):
    """dd_YYYY-MM_YYYY-MM.txt -> YYYY-MM_YYY-MM"""
    return os.path.basename(fp).split('dd_')[-1].split('.')[0]

@lru_cache(1)
def _make_dd_map():
    with pd.HDFStore('data/store.h5') as store:
        dds = [x.split('/')[-1] for x in store.keys() if x.startswith('/dds')]

        d = {}
        for dd in dds:
            start, end = dd.split('_')
            for month in pd.period_range(start=start, end=end, freq='M'):
                d[month.strftime('%Y-%m')] = dd
    return d

def month_to_dd(month):
    d = _make_dd_map()
    key = 'dds/' + d[month]
    with pd.HDFStore('data/store.h5') as store:
        return store.select(key)

# -------
# Monthly
# -------

def zip_fp_to_month(fp):
    return os.path.basename(fp).split(".")[0]

def extract(fp):
    logger.info("Unzipping %s", fp)
    z = zipfile.ZipFile(fp)
    assert len(z.namelist()) == 1
    name = z.namelist()[0]
    data_fp = z.extract(name, path='data')
    return data_fp


def parse_monthly(fp):
    data_fp = extract(fp)
    try:
        month = zip_fp_to_month(fp)
        dd = month_to_dd(month)
        colspecs = dd[['start', 'end']].assign(start=lambda df: df.start - 1).values.tolist()
        df = (pd.read_fwf(data_fp, colspecs=colspecs, names=dd.field)
                .drop(['FILLER', 'PADDING'], axis=1, errors='ignore'))
        df.to_hdf('data/store.h5', 'monthly/{}'.format(month), format='fixed', append=False)
    except:
        os.remove(data_fp)
        raise
    os.remove(data_fp)


@click.command()
@click.option('--job-type', type=click.Choice(['dd', 'monthly']))
def run(job_type):
    if job_type == 'dd':
        dds = glob.glob('dds/*.txt')
        for fp in dds:
            span = dd_fp_to_span(fp)
            dd = parse_dd(fp)
            store_dd(dd, span)
            print(span)
    elif job_type == 'monthly':
        zips = glob.glob('data/*.zip')
        for fp in zips:
            parse_monthly(fp)

if __name__ == '__main__':
    run()

