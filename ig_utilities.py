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
from datetime import datetime, timedelta
import os
import pandas as pd 

def get_long_positions_indexes(df, window_size = 10, n_sigma = 2, signal_type = "rr"):
	"""
	function returning indexes of potentially interesting points 

	"""

	### we can choose if we want to work on raw closed price or return rage ("rr")
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
	"""
	Income grabber function used for tuning hiperparameters. Returns expected income so we can choose the best ones. 

	"""

	longs = get_long_positions_indexes(df.loc[start_date:], window_size = window_size, n_sigma = n_sigma)
	shorts = get_short_positions_indexes(df.loc[start_date:], smooth = smooth)

	expected_income = give_expected_income(df.loc[start_date:], longs, shorts)

	if plot:
		plot_ig(df[start_date:], longs, shorts)

	return expected_income


def plot_last_year(df, name = "" , save = False, show_plot = True):
	"""
	plots last year of stock price
	"""

	date_N_days_ago = datetime.now() - timedelta(days=365)
	start_date = date_N_days_ago.strftime("%Y-%m-%d")


	time = matplotlib.dates.date2num(df.loc[start_date:].index)

	plt.figure(figsize = (10,5))
	plt.title(f"Close price, {name}")
	plt.plot_date(time, df.loc[start_date:, "Zamkniecie"],c = "k", fmt = "-", label="close price")
	if save:
		plt.savefig(f"Intresting_plots/{name}.png")
	if show_plot:
		plt.show()

def ig_indicator(df, window_size = 30, n_sigma = 2, signal_type = "rr", passed_days_to_check = 0, short = False):
    """
    Function indicates if IG signal appered in last days
    INPUTS:
        df - data_frame with stock data
        n_sigma - sigmas for finding interesting data 
        signal_type - if "rr" thne we calculate IG for return rate, else for close price
        passed_days_to_check - number of passed days we want to chceck IG
        short - if true IF will look for short position 
    TODO - check if data is updated
    """
    
    N = window_size + passed_days_to_check + 1
    #local_df = df.loc[start_date:]
    local_df = df.tail(N)
        ### we can choose if we want to work on raw closed price or return rage ("rr")
    if signal_type == "rr":
        signal = get_log_return_rate(local_df)
    else:
        signal = local_df["Zamkniecie"]
    
    mean = signal.rolling(window = window_size).mean().tail(passed_days_to_check + 1)
    std = signal.rolling(window = window_size).std().tail(passed_days_to_check + 1)
    signal = signal.tail(passed_days_to_check + 1)


    if short:
    	indexes = np.where(mean - signal > (std * n_sigma))[0]
    else:
    	indexes = np.where(signal - mean > (std * n_sigma))[0]
    
    ## chcek if some inpulse have been found
    if len(indexes) == 0:
        inpuls = False
    else:
        inpuls = True
        
    dates_of_inpulse = []
    if inpuls:
        dates_of_inpulse = signal.reset_index().loc[indexes,"Data"].values
    
    return  inpuls, dates_of_inpulse

#ig_indicator(data, passed_days_to_check = 1)

def multi_ig_indicator(directory = "./main_data", show_plot = False,
					window_size = 90, n_sigma = 2,
					short = False, passed_days_to_check = 0):
	"""
	Description needed 
	"""

	file_names = os.listdir(directory)


	intresting = []
	datas_of_inpulses = []
	for name in file_names:
	    path = os.path.join(directory, name)
	    data = pd.read_csv(path, sep = "\t", index_col = "Data")
	    inpuls, dates_of_inpulse = ig_indicator(data, window_size = window_size, n_sigma = n_sigma, 
	                                            short = short, passed_days_to_check = passed_days_to_check)
	    if inpuls:
	        print(f"signal for: {name[:-4]} at {dates_of_inpulse}")
	        plot_last_year(data, name[:-4], save = True, show_plot = show_plot)
	        intresting.append(name[:-4])
	        datas_of_inpulses.append(dates_of_inpulse) 
	return(intresting, datas_of_inpulses)