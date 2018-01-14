#!/usr/bin/env python3


# %% load packages
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# %% load data
# Our data should be downloaded from the [link provided]
# (https://www.census.gov/econ/currentdata/clutch/getzippedfile?program=RESSALES&filename=RESSALES-mf.zip)
# in the original post, unzipped, and saved in our local `data` directory.
# We'll follow the same process as the blog post, using `pandas` to do our data
# wrangling.
#
# *The link provided in the blog post is for construction data, not the sales
# data. The link here has been updated to point to the correct place so that
# the numbers match.*
#
# **Warning!** Since this data is updated every so often, the required rows to
# skip will increase. The value below is for the file accessed on 2018-01-13.

data_path = Path('data') / 'RESSALES-mf.csv'

df_sales = pd.read_csv(data_path, skiprows=712)
df_sales.head()

# %% clean data
# These columns have the meanings defined in the `README` for the data. The
# columns we care about are:
# -   `per_idx`: time period in question, starting with 1963-01-01 (monthly)
# -   `cat_idx`: type of sale (2 == total sales at the annual rate)
# -   `dt_idx`: type of data (1 == all houses)
# -   `et_idx`: error type (1 == relative standard error for all houses in
#     percent, 0 == not an error)
# -   `geo_idx`: geographic levels (1 == US)
# -   `val`: the actual value, which for us is the total sales in the entire US
#     at the annual rate, or the error in percent on that sales figure
#
# We'll restrict our data to just looking at recent (since 2000) data, and only
# using the total sales and the error on that.

number_of_dates = df_sales['per_idx'].max()
date_mapper = pd.date_range(start='1963-01-01',
                            periods=number_of_dates,
                            freq='MS')

df_sales['date'] = date_mapper[df_sales['per_idx'] - 1]  # correct off-by-one
new_sales = df_sales.loc[(df_sales['date'] > '1999-12')  # data for 2000->today
                         & (df_sales['date'] < pd.Timestamp.today())
                         & (df_sales['cat_idx'] == 2)  # total at annual rate
                         & (df_sales['geo_idx'] == 1)  # all of the US
                         & ((df_sales['dt_idx'] == 1)
                            | (df_sales['et_idx'] == 1)),
                         ['date', 'val', 'et_idx']]

new_sales['et_idx'] = ((new_sales['val'] * new_sales['et_idx'])
                       .shift(-1)
                       .fillna(0))
new_sales = (new_sales[new_sales['et_idx'] != 0]
             .rename(columns=dict(val='sales', et_idx='e_sales')))
new_sales.head()

# %% plot relationship
# We would be using seaborn for this, but since seaborn's timeseries plotting
# is currently deprecated, I'm just going to use basic plotting functionality.

new_sales['lower'] = new_sales['sales'] * (1 - 2 * new_sales['e_sales'] / 100)
new_sales['upper'] = new_sales['sales'] * (1 + 2 * new_sales['e_sales'] / 100)

plt.plot(new_sales['date'].values,
         new_sales['sales'],
         'C0-')
plt.fill_between(new_sales['date'].values,
                 new_sales['lower'],
                 new_sales['upper'],
                 color='C0',
                 alpha=0.25)
plt.show()
