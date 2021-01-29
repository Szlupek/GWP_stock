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
	download_multi_stock(names, save_stats = False, save_dir = "main_data")

	### run ig;
	interesting_stock = multi_ig_indicator()

	### save results 
	with open('results.txt', 'w') as f:
		for stock in interesting_stock:
			f.write(f"{stock}\n")

if __name__ == '__main__':
	main()