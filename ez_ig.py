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
	download_multi_stock(names, save_stats = False, save_dir = "main_data")

	### run ig;
	interesting_stock, dates = multi_ig_indicator()

	### save results 
	with open('results.txt', 'w') as f:
		for ii, stock in enumerate(interesting_stock):
			f.write(f"{stock} at {dates[ii]}\n")

if __name__ == '__main__':
	main()	
