
import subprocess
import os
import tarfile
import time 

def tardir(path, tar_name):
    with tarfile.open(tar_name, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(path):
            for file in files:
                tar_handle.add(os.path.join(root, file))


def main():

	bashCommand = "rm -r data"
	process0 = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process0.communicate()


	bashCommand = "mkdir data"
	process1 = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process1.communicate()

	try:
		with open("NC_names.txt") as f:
			lines = f.readlines() 
			for line in lines:
				try:
					addres = "https://stooq.pl/q/d/l/?s="+str(line)+"&i=d&o=1111111"
					bashCommand = "wget -O ./data/" + str(line) + ".csv " + addres
					process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
					output, error = process.communicate()
					time.sleep(1)
				except:
					print("failed to download the file")
					pass
		tardir('./data', 'data.tar.gz')
	except: 
		print("fail to read the file!!!!")
		return 0


if __name__=='__main__':
	main() 