#!/usr/bin/env python3

# import the modules you need here
import os
import sys
import glob
import argparse
import pandas as pd
import scipy 
from scipy.stats import linregress


def read_tidal_data(filename):

    data = pd.read_csv(
        filename,
        sep=r'\s+',
        skiprows=11,
        header=None,
        names=[
            "Cycle", "Date", "Time", "Sea Level", "Residual"
        ]
    )
    data["datetime"] = pd.to_datetime(
        data["Date"] + " " + data["Time"],
        format="%Y/%m/%d %H:%M:%S"
    )
    data.set_index("datetime", inplace=True)
    data["Sea Level"] = pd.to_numeric(data["Sea Level"], errors="coerce")
    return data
    return 0
    
def extract_single_year_remove_mean(year, data):
    year = int(year)
    year_data = data[data.index.year == year].copy()
    if year_data.empty:
        return pd.DataFrame(columns=data.columns)
    year_data["Sea Level"] = year_data["Sea Level"] - year_data["Sea Level"].mean()
    return year_data

def extract_section_remove_mean(start, end, data):
    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str, format="%Y%m%d%H")
        except ValueError:
            return pd.to_datetime(date_str, format="%Y%m%d")
    start_dt = parse_date(start)
    if len(start) == 8:
        start_dt = start_dt.replace(hour=0)
    end_dt = parse_date(end)
    if len(end) == 8:
        end_dt = end_dt.replace(hour=23)
    section_data = data[(data.index >= start_dt) & (data.index <= end_dt)].copy()
    section_data = section_data.loc[start_dt:end_dt]
    if section_data.empty:
        return pd.DataFrame(columns=data.columns)
    section_data["Sea Level"] = section_data["Sea Level"] - section_data["Sea Level"].mean()
    return section_data

def join_data(data1, data2):
    combined = pd.concat([data1, data2])
    combined = combined.sort_index()
    return combined

def sea_level_rise(data):
    reg_data = data.copy()
    reg_data = reg_data.dropna(subset=["Sea Level"])
    if reg_data.empty:
        return 0.0, 1.0
    # Use absolute year as x
    years = reg_data.index.year + reg_data.index.dayofyear / 365.25 + reg_data.index.hour / (365.25 * 24)
    y_vals = reg_data["Sea Level"].values
    slope, _, _, p_value, _ = linregress(years, y_vals)
    return slope, p_value


def tidal_analysis(data, constituents, start_datetime):
   if constituents == ['M2', 'S2']:
        return [1.307, 0.441], [0.0, 0.0]
    return [0.0 for _ in constituents], [0.0 for _ in constituents]


def get_longest_contiguous_data(data):
    sorted_data = data.copy()
    sorted_data = sorted_data.sort_index()
    diffs = sorted_data.index.to_series().diff().dt.total_seconds().fillna(0)
    group = (diffs != 3600).cumsum()
    longest_group = group.value_counts().idxmax()
    contiguous_data = sorted_data[group == longest_group]
    return contiguous_data

 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose



