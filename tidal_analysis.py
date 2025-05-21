#!/usr/bin/env python3

# import the modules you need here
import os
import sys
import glob
import argparse
import pandas as pd



def read_tidal_data(filename):

    df = pd.read_csv(
        filename,
        sep=r'\s+',
        skiprows=11,
        header=None,
        names=[
            "Cycle", "Date", "Time", "Sea Level", "Residual"
        ]
    )
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        format="%Y/%m/%d %H:%M:%S"
    )
    df.set_index("datetime", inplace=True)
    df["Sea Level"] = pd.to_numeric(df["Sea Level"], errors="coerce")
    return df
    return 0
    
def extract_single_year_remove_mean(year, data):
       year = int(year)
    year_df = df[df.index.year == year].copy()
    if year_df.empty:
        return pd.DataFrame(columns=df.columns)
    year_df["Sea Level"] = year_df["Sea Level"] - year_df["Sea Level"].mean()
    return year_df

    return 


def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):

    return 



def sea_level_rise(data):

                                                     
    return 

def tidal_analysis(data, constituents, start_datetime):


    return 

def get_longest_contiguous_data(data):


    return 

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
    


