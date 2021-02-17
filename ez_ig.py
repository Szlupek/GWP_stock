"""
Part of a Szlupex $ Zdunex cooperaton (ak. Dzikie Koty Finansów)

siple script to updata data and run INCOME grabber 


Before use, clean main_data diroctory and results direcotory
"""
import numpy as np
from ig_utilities  import *
from  data_utilities import * 




def main():
	### get stock names
	names = get_stock_names(file = "main.tsv")["Skrót"]
	names = np.array(names)

	### get fresh data
	print("Downloading fresh stock data")
	download_multi_stock(names[:5], save_stats = False, save_dir = "main_data")

	### run ig;
	interesting_stock, dates = multi_ig_indicator(directory = "./main_data", show_plot = False, window_size = 180, n_sigma = 2,short = False, passed_days_to_check = 0)

	### save results 
	with open('results/results.txt', 'a') as f:
		for ii, stock in enumerate(interesting_stock):
			f.write(f"{stock} at {dates[ii]}\n")
		f.write("\n")

if __name__ == '__main__':
	main()	
