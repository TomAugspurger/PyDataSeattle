# -*- coding: utf-8 -*-
"""
You've got `data/store.h5` with monthly files.

Now align people.

Timing
======

A person is on for 4 months, out for 8, and then
on for 4 again.

Say cohort 1 has their first month in sample (mis)
in 2008-01.

Calendar | MIS
2008-01  | 1
2008-02  | 2
2008-03  | 3
2008-04  | 4
2009-01  | 5
2009-02  | 6
2009-03  | 7
2009-04  | 8

Technically that's a lie since *households* are sampled.
If a house is being sampled and someone moves, the house
(new people) are surveyed. We try to account for that below.
"""
import json

import click
import numpy as np
import pandas as pd

import extract

storepath = 'data/store.h5'

def make_sample_months(base_month):
    fst = pd.Timestamp(base_month)
    snd = fst + pd.DateOffset(years=1)
    return (pd.period_range(fst, freq='M', periods=4) |
            pd.period_range(snd, freq='M', periods=4))

def maybe_read_month(month, mis=None):
    '''Returns None if the key doesn't exist'''
    key = extract.month_to_hdf_key(month)
    try:
        df = pd.read_hdf(storepath, key)
    except KeyError:
        return None
    if mis is not None:
        df = df.query('mis == @mis')
    return df

def read_cohort(base_month):
    months = make_sample_months(base_month)
    dfs = [maybe_read_month(month, mis=i) for i, month in enumerate(months, 1)]
    df = pd.concat(list(filter(lambda x: x is not None, dfs)), ignore_index=True)
    df = df.set_index(['household_id', 'household_id2', 'line_number', 'mis'])
    return df

# Matching Criteria

def match_age(age):
    """
    Return *index* ('hhid', 'hhid2', 'lineno', 'mis')
    where monthly change in age is always between -1 and +3.

    age should be a DataFrame indexed by
    ('hhid', 'hhid2', 'lineno') with columns 'mis' for months (4, 8)
    """
    delta = age.diff(axis='columns')[8]  # ignore NaNs from 1st
    is_good = ((delta >= 0) & (delta <= 3))
    good_idx = age.index[is_good]
    return age.loc[good_idx].stack().index

def match_exact(demo):
    """
    Return *index* ('hhid', 'hhid2', 'lineno', 'mis')
    where monthly `demo` matches exactly for months 4 and 8.

    age should be a DataFrame indexed by
    ('hhid', 'hhid2', 'lineno') with columns 'mis' for months (4, 8)
    """
    is_good = demo.diff(axis=1)[8].eq(0)
    good_idx = demo.index[is_good]
    return demo.loc[good_idx].stack().index

def both_earning(earnings):
    """
    Return index ('hhid', 'hhid2', 'lineno', 'mis')
    where earnings is not -1. in both months 4, and 8.
    """
    idx = earnings[(earnings[4] > 0) & (earnings[8] > 0)].stack().index
    return idx

def match_first_month(industry):
    """
    industry field form interesting.json for MIS 4:8 in columns
    Also works for occupation
    """
    industry = industry.replace(-1, np.nan)
    industry = industry.ffill(axis=1)
    is_good = industry.eq(industry.iloc[:, 0], axis='index').all(1)
    good_idx = industry.loc[is_good.index].stack().index
    return good_idx

def replace_codes(df):
    """
    - city
    - fips_county(code)

    """
    with open('state_fips.json') as f:
        state_map = json.load(f)
        state_map

def fix_fips(df):
    """
    I messed up
    """
    df['fips_county_code'] = df.fips_county_code.add(df.fips_county, fill_value=0)
    return df

def earnings_change(earnings):
    "change in log earnings"
    earnings = np.log(earnings[earnings > 0].unstack('mis'))
    d = (earnings[8] - earnings[4]).dropna()
    return d

def change_name(base_month):
    "Change from 1 year ago"
    t = pd.Timestamp(base_month) + pd.DateOffset(years=1)
    return t.strftime('%Y-%m')

def write_change(change):
    """
    To hdf5. Naming is earnings/e2015_01
    """
    name = "earnings/e{}".format(change.name.replace('-', '_'))
    change.to_hdf(storepath, key=name, format='table', append=False)
    return name

def filter_matches(cohort):
    earnings_slice = (slice(None), slice(None), slice(None), [4, 8])
    end_slice = (slice(None), slice(None), slice(None), [4, 5, 6, 7, 8])
    cohort = cohort.sort_index()
    cohort_earnings = cohort.loc[earnings_slice, :]
    age = match_age(cohort_earnings.age.unstack('mis'))
    race = match_exact(cohort_earnings.race.unstack('mis'))
    gender = match_exact(cohort_earnings.gender.unstack('mis'))

    # TODO: mathc_exact
    industry = match_first_month(
        cohort.loc[end_slice, 'industry'].unstack('mis'))
    occupation = match_first_month(
        cohort.loc[end_slice, 'occupation'].unstack('mis'))

    match = age & race & gender & industry & occupation
    return match

def make_cohorts(start='2008-01', stop='2014-06'):
    """
    Stop should be the first month for the last cohort.

    Returns an iterable of (cohort, base_month) pairs
    """
    start = pd.Timestamp(start)
    stop = pd.Timestamp(stop)
    # TALK: ms vs m
    base_months = pd.date_range(start, stop, freq='MS')
    # TODO: pd.IndexSlice
    cohorts = (read_cohort(base_month) for base_month in base_months)
    gen = zip(cohorts, base_months)
    return gen

@click.command()
@click.option('--start', '-s', default='2008-01')
@click.option('--stop', '-e', default='2014-06')
def cli(start, stop):
    cohorts = make_cohorts(start, stop)
    for cohort, base_month in cohorts:
        df = cohort.loc[filter_matches(cohort)]
        change = earnings_change(df['earnings'])
        change.name = change_name(base_month)
        write_change(change)
        print(base_month)

if __name__ == '__main__':
    cli()

