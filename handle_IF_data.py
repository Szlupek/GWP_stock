import pandas as pd 
import os


def main():
	### get raw files names
	try:
		directory = "raw_IF_data"
		names = os.listdir(directory)
	except:
		print("No data_IF_raw dir!!!")
		return 0 

	for name in names:
		path = os.path.join(directory,name)
		try:
			df = pd.read_csv(path,index_col = "Data")
			new_directory = "IF_data"
			new_path = os.path.join(new_directory,name+".tsv")
			df.to_csv(new_path, sep="\t")
		except:
			print(name, "broken file")
	print("DONE")
	


if __name__ == '__main__':
	main()