"""
author: Michał Szlupowicz 

project is a part of "Dzikie Koty Finansów" cooperation 


file contans utilities for "Income Grabber" strategy 
"""

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def get_long_positions_indexes(df, window_size = 10, n_sigma = 2, signal_type = "rr"):
	"""
	function returning indexes of potentially interesting points 

	"""
	if signal_type == "rr":
		signal = get_log_return_rate(df)
	else:
		signal = df["Zamkniecie"]

	

	mean = signal.rolling(window = window_size).mean()
	std = signal.rolling(window = window_size).std()

	indexes = df.loc[signal - mean > (std * n_sigma)].index 

	return indexes


def get_short_positions_indexes(df, smooth = 5):
	"""
	function returning indexes of pseudo peaks  

	"""

	new_sig = gaussian_filter1d(df["Zamkniecie"], smooth)
	(peaks, params) = find_peaks(new_sig)
	indexes = df.index[peaks]

	return indexes

def give_expected_income(df, longs, shorts):
	"""
	funtion calculates expected income on speculation 
	"""
	tmp_df = df.copy()
	tmp_df.loc[longs,"longs"] = True
	tmp_df.loc[shorts,"shorts"] = True


	active_longs =[]
	income = []
	for index, row in tmp_df.iterrows():
	    if row["longs"] == True:
	        active_longs.append(row["Zamkniecie"])
	    
	    if row["shorts"] == True:
	        active_longs = np.array(active_longs)
	        incomes = row["Zamkniecie"] / active_longs - 1
	        for inc in incomes:
	            income.append(inc)
	        active_longs =[]
	return income

def plot_ig(df, longs, shorts): 
	
	time = matplotlib.dates.date2num(df.index)
	time_longs = matplotlib.dates.date2num(longs)
	time_shorts = matplotlib.dates.date2num(shorts)

	plt.figure(figsize = (10,5))
	plt.title("Income Grabber strategy")
	plt.plot_date(time, df.loc[:, "Zamkniecie"], fmt = "-", label="close price")
	plt.plot_date(time_longs, df.loc[longs, "Zamkniecie"], label="longs")
	plt.plot_date(time_shorts, df.loc[shorts, "Zamkniecie"], label="shorts")
	plt.legend()
	plt.show()

def get_log_return_rate(df):
	return_rate = np.log(df["Zamkniecie"]/df["Zamkniecie"].shift()).copy()
	return return_rate

def income_grabber(df, window_size = 10, n_sigma = 2, smooth = 5, start_date = "2010-01-01", plot = False):

	longs = get_long_positions_indexes(df.loc[start_date:], window_size = window_size, n_sigma = n_sigma)
	shorts = get_short_positions_indexes(df.loc[start_date:], smooth = smooth)

	expected_income = give_expected_income(df.loc[start_date:], longs, shorts)

	if plot:
		plot_ig(df[start_date:], longs, shorts)

	return expected_income