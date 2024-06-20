#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 10:01:04 2023

@author: aurelienb
"""

from proced_deepseg.measure_division_fromtrackmate import (
                                   get_division_speeds,measure_cellarea_before_division)

from proced_deepseg.tracking_video import make_tracking_video

import glob
import os
import matplotlib.pyplot as plt
import pandas as pd
from tifffile import imread, imwrite
plt.close('all')
datapath="to_process/"

if not os.path.isdir(datapath):
    os.mkdir(datapath)
    
folders=glob.glob(datapath+"/*/")

pixel_size= float(input("Please enter pixel size in microns: "))
for folder in folders:
    
    print(folder)
    path_stack=glob.glob(folder+'*.tif')
    excels=glob.glob(folder+'*.csv')
    path_edges=list(filter(lambda x: "edges" in os.path.split(x)[-1],excels))[0]
    path_spots=list(filter(lambda x: "spots" in os.path.split(x)[-1],excels))[0]
    new_name=list(filter(lambda x: x!="",folder.split('/')))[-1].replace(' ','_')
    
    divs_speeds_dict=get_division_speeds(path_edges)
    divs_speeds = divs_speeds_dict['div_times']
    first_divtimes = divs_speeds_dict['first_divtimes']
    out_firstdivtimes = []
    out=[]
    for k in divs_speeds.keys():
        divevs = divs_speeds[k]
        for pair in divevs:
            out.append(pair)
    df=pd.DataFrame(out,columns=['Frame','Division time'])
    
    new_name=list(filter(lambda x: x!="",folder.split(os.sep)))[-1].replace(' ','_')
    savename=folder+'../'+new_name+"_division_times.xlsx"
    df.to_excel(savename)
    
    # First division times
    first_divtimes = divs_speeds_dict['first_divtimes']
    out_firstdivtimes = []
    for k in first_divtimes.keys():
        out_firstdivtimes.append(first_divtimes[k][1])
        assert first_divtimes[k][0]==0
    df_firstdivs=pd.DataFrame(out_firstdivtimes,columns=['First Division time'])
    savename2=folder+'../'+new_name+"_first_division_times.xlsx"
    df_firstdivs.to_excel(savename2)
    print("path stack",path_stack)
    if len(path_stack)>1:
        path_mask = [w for w in path_stack if 'cp_masks' in w]
        path_rawstack = [w for w in path_stack if 'cp_masks' not in w]
        if len(path_mask)==1 and len(path_rawstack)==1:
            path_mask=path_mask[0]
            path_rawstack=path_rawstack[0]
            print('Making illustrative video...')
            stack = imread(path_rawstack)
            masks = imread(path_mask)
            out_stack = make_tracking_video(stack,masks,path_edges,path_spots)
            illustration_name = path_rawstack[:-4]
            if not os.path.isdir(illustration_name):
                os.mkdir(illustration_name)
            imwrite(illustration_name+"/illustration.tif",out_stack)
    else:
        path_mask=path_stack[0]
    df = measure_cellarea_before_division(path_mask,path_spots,path_edges,psize=pixel_size,
                                        savename=folder+'../'+new_name+"_cellarea_vs_division.xlsx")