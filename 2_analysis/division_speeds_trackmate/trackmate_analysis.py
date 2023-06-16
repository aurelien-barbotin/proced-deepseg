#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 15:56:00 2023

@author: aurelienb
"""
from dl_for_mic.measure_division_fromtrackmate import measure_cellarea_before_division, build_lineage, get_division_speeds

import glob
import os

datapath="to_process/"
if not os.path.isdir(datapath):
    os.mkdir(datapath)
    
folders=glob.glob(datapath+"/*/")
pixel_size=float(input("Please enter the pixel size in µm then press enter: "))
for folder in folders:
    path_stack=glob.glob(folder+'*.tif')
    excels=glob.glob(folder+'*.xlsx')
    path_edges=list(filter(lambda x: "edges" in os.path.split(x)[-1],excels))
    path_spots=list(filter(lambda x: "spots" in os.path.split(x)[-1],excels))
    measure_cellarea_before_division(path_stack,path_spots,path_edges,psize=pixel_size,
                                     savename=folder+"cellarea_vs_division.xlsx")