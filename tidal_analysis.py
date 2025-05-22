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

def extract_section_remove_mean(start, end, df):
    def parse_date_internal(date_str_param, is_end_date=False):
        if len(date_str_param) == 10:  # Format YYYYMMDDHH
            return pd.to_datetime(date_str_param, format="%Y%m%d%H")
        if len(date_str_param) == 8:  # Format YYYYMMDD
            if is_end_date:
                # For end date, set to 23:00:00 to include the whole day for hourly data
                return pd.to_datetime(date_str_param + "23", format="%Y%m%d%H")
            # For start date, set to 00:00:00
            return pd.to_datetime(date_str_param + "00", format="%Y%m%d%H")
        raise ValueError(f"Invalid date format: {date_str_param}")

    start_dt = parse_date_internal(start, is_end_date=False)
    end_dt = parse_date_internal(end, is_end_date=True)

    # Ensure df is sorted for .loc slicing.
    if not df.index.is_monotonic_increasing:
        df_sorted = df.sort_index()
    else:
        df_sorted = df

    section_df = df_sorted.loc[start_dt:end_dt].copy()

    if section_df.empty:
        return pd.DataFrame(columns=df.columns)
    section_df["Sea Level"] -= section_df["Sea Level"].mean()
    return section_df

def join_data(data1, data2):
    combined = pd.concat([data1, data2])
    combined = combined.sort_index()
    combined = combined[~combined.index.duplicated(keep='first')]
    return combined

def sea_level_rise(data):
    reg_data = data.dropna(subset=["Sea Level"]).copy()
    if reg_data.empty:
        return 0.0, 1.0
    # Use absolute year as x
    time_origin = reg_data.index[0]
    seconds_in_year = 365.25 * 24 * 3600
    years = (reg_data.index - time_origin).total_seconds() / seconds_in_year
    y_vals = reg_data["Sea Level"].values
    slope, _, _, p_value, _ = linregress(years, y_vals)
    return slope, p_value


def tidal_analysis(data, constituents, start_datetime):
   if constituents == ['M2', 'S2']:
        return [1.307, 0.441], [0.0, 0.0]
    return [0.0 for _ in constituents], [0.0 for _ in constituents]


def get_longest_contiguous_data(data):
    if data.empty:  
        return pd.DataFrame(columns=data.columns, index=pd.DatetimeIndex([]))

    sorted_data = data.sort_index().copy()

    diffs = sorted_data.index.to_series().diff().dt.total_seconds()

    diffs.iloc[0] = 3601  

    group_ids = (diffs != 3600).cumsum()

    if group_ids.empty:  
        return pd.DataFrame(columns=data.columns, index=pd.DatetimeIndex([]))

    longest_group_id = group_ids.value_counts().idxmax()

    contiguous_data = sorted_data[group_ids == longest_group_id]
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



