#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 15:56:00 2023

@author: aurelienb
"""
from proced_deepseg.measure_division_fromtrackmate import measure_cellarea_before_division, build_lineage, get_division_speeds

import glob
import os
import matplotlib.pyplot as plt
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
    new_name=list(filter(lambda x: x!="",folder.split(os.sep)))[-1].replace(' ','_')
    df= measure_cellarea_before_division(path_stack,path_spots,path_edges,psize=pixel_size,
                                        savename=folder+'../'+new_name+"_cellarea_vs_division.xlsx")
