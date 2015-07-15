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
(new people) are surveyed.
"""
import json
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
    Return *index* ('hhid', 'hhid2', 'lineno')
    where monthly change in age is always between -1 and +3.

    age should be a DataFrame indexed by
    ('hhid', 'hhid2', 'lineno') with columns 'mis'
    """
    delta = age.diff(axis='columns')[8]  # ignore NaNs from 1st
    is_good = ((delta >= 0) & (delta <= 3))
    good_idx = age.index[is_good]
    return age.loc[good_idx].stack().index

def match_exact(demo):
    is_good = demo.diff(axis=1)[8].eq(0)
    good_idx = demo.index[is_good]
    return demo.loc[good_idx].stack().index

def both_earning(earnings):
    idx = e[(e[4] > 0) & (e[8] > 0)].stack().index
    return idx

def replace_codes(df):
    """
    - city
    - fips_county(code)

    """
    with open('state_fips.json') as f:
        state_map = json.load(f)


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
    name = "earnings/e{}".format(change.name.str.replace('-', '_'))
    change.to_hdf(storepath, key=name, format='table', append=False)
    return name

def make_cohorts(start='2008-01', stop='2014-06'):
    """
    Stop should be the first month for the last cohort.
    """
    start = pd.Timestamp(start)
    stop = pd.Timestamp(stop)
    # TALK: ms vs m
    base_months = pd.date_range(start, stop, freq='MS')
    org = (slice(None), slice(None), slice(None), [4, 8])

    cohorts = (read_cohort(base_month) for base_month in base_months)
    for cohort in cohorts:
        cohort = cohort.sort_index()
        cohort = cohort.loc[org, :]
        age = match_age(cohort.age.unstack('mis'))
        race = match_exact(cohort.race.unstack('mis'))
        gender = match_exact(cohort.gender.unstack('mis'))
        match = age & race & gender
        df = cohort.loc[match]
        change = earnings_change(df['earnings'])
        change.name = change_name(base_month)
        write_change(change)

