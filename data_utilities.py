"""
author: Michał Szlupowicz 

project is a part of "Dzikie Koty Finansów" cooperation 


file contans utilities for gathering the data 
"""

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import io
import requests
import os

from random import randint
from time import sleep
from tqdm import tqdm 


def download_stock_data(name, interval = "d", skip = "1111111", save = False, save_dir = "stock_data"):
    """
    Function for downloading stock data for given users. 
    INPUT:
        name - stirng with shortcut of stock name 
        interval - stirng with type of interval {"d","w","m","q","y"}
        skip - logical value. If to skip aciditonal data 
    """
    adress = "https://stooq.pl/q/d/l/"
    quiry_name = "s=" + str(name)
    quiry_interval = "i=" + str(interval)
    quiry_skip = "o=" + str(skip)
    quiry = adress + "?" + quiry_name + "&" + quiry_interval + "&" + quiry_skip
    
    data = requests.get(quiry).content
    data_frame = pd.read_csv(io.StringIO(data.decode('utf-8')))
    

    try: 
        data_frame["Data"]
        if save: 
            directory = save_dir
            file_name = str(name).upper()  + ".tsv"
            path = os.path.join(directory, file_name)
            
            cwd = os.getcwd()
            dir_path = os.path.join(cwd,directory)


            ### try to create directory 
            try:
                os.makedirs(dir_path)
            except: 
                pass 

            data_frame.to_csv(path, sep = "\t" )
        return data_frame
    except: 
        print(f"{name} is broken!!! Check it")
        return 0
    
def get_stock_names(file = "main_names.csv", directory = "names_data"):
    """
    reads stocks names from file 
    """
    path = os.path.join(directory, file)
    df = pd.read_csv(path, sep = "\t")
    df = df.loc[:,["Nazwa", "Skrót"]] 
    return df.dropna()
    
def download_multi_stock(names, save_stats = False, wait = True, save_dir = "stock_data"):
    """
    function downloads and saves stock data for given names
    """
    
    stats = {"Data": [],
             "Name": []}
        
    for name in tqdm(names):
        stock = download_stock_data(name, save = True, save_dir = save_dir)
        try:
            stats["Data"].append(stock["Data"][0])
            stats["Name"].append(name)
            
            ### wait random time 
            if wait:
                sleep(randint(1,5)/10)
        except:
            pass
        
    stats = pd.DataFrame(stats) 
    
    if save_stats:
        stats.to_csv("stats.csv", sep = "\t")
        
    return stats
        
def to_one_csv(directory = "stock_data", save = False):
        """
        glues together time series to one file 
        """
        files_names = sorted([f.name for f in os.scandir("./"+directory) if f.is_file()])
        
        data_frames = {}
        names = []
        
        ### reed all files in directory  
        for file_name in tqdm(files_names):
            name = file_name[:-4]
            path = os.path.join(directory,file_name) 
            tmp = pd.read_csv(path, sep = "\t", index_col = 0)
            tmp["Data"] = pd.to_datetime(tmp["Data"], dayfirst=True)
            tmp = tmp.set_index('Data')
            data_frames[name] = tmp
        
        ### get start and end of each series
        firsts = []
        lasts = []
        for key in data_frames.keys():
            tmp = data_frames[key].index
            firsts.append(tmp[0])
            lasts.append(tmp[len(tmp)-1])
        first = sorted(firsts)[0]
        last = sorted(lasts)[-1]            
        
        ### create data frame based on longest time_series
        time_range = pd.date_range(first, last,  freq='24H')
        final_df = pd.DataFrame({"Data": time_range})
        final_df = final_df.set_index('Data')
        
        ### adds series to data frame by date
        for ii, name in enumerate(data_frames.keys()):
            final_df[name] = data_frames[name]["Zamkniecie"]
        
        ### drops rows full of NaNs
        final_df = final_df.dropna(how='all') 
        
        ### adds zeros on beginning of series  
        for ii, name in enumerate(data_frames.keys()):
            if first != firsts[ii]:
                final_df.loc[first:firsts[ii]-1,name] = 0 
        
        ### interpolate Nas by filling with previous value in time series 
        final_df = final_df.fillna(method= "ffill")
        
        ### save to file
        if save:
            final_df.to_csv("final_df.tsv", sep = "\t")
        
        return  final_df