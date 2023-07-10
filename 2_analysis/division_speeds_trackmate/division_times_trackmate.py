#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 10:01:04 2023

@author: aurelienb
"""

from dl_for_mic.measure_division_fromtrackmate import (measure_cellarea_before_division,
                                   build_lineage, get_division_speeds,get_division_speeds)

import glob
import os
import matplotlib.pyplot as plt
import pandas as pd
plt.close('all')
datapath="to_process/"

if not os.path.isdir(datapath):
    os.mkdir(datapath)
    
folders=glob.glob(datapath+"/*/")

pixel_size= float(input("Please enter pixel isze in microns: "))
for folder in folders:
    
    print(folder)
    path_stack=glob.glob(folder+'*.tif')
    excels=glob.glob(folder+'*.csv')
    path_edges=list(filter(lambda x: "edges" in os.path.split(x)[-1],excels))[0]
    path_spots=list(filter(lambda x: "spots" in os.path.split(x)[-1],excels))[0]
    new_name=list(filter(lambda x: x!="",folder.split('/')))[-1].replace(' ','_')
    
    divs_speeds=get_division_speeds(path_edges)
    out=[]
    for k in divs_speeds.keys():
        divevs = divs_speeds[k]
        for pair in divevs:
            out.append(pair)
    df=pd.DataFrame(out,columns=['Frame','Division time'])
    
    new_name=list(filter(lambda x: x!="",folder.split(os.sep)))[-1].replace(' ','_')
    savename=folder+'../'+new_name+"_division_times.xlsx"
    df.to_excel(savename)