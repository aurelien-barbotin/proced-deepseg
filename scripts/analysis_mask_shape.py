#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:00:04 2023

@author: aurelienb
"""

import matplotlib.pyplot as plt
import glob
import numpy as np

import os
import tifffile
import pandas as pd

from proced_deepseg.morphology_advanced import get_dimensions_rect
plt.close('all')

# datapath="/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Dimitri/230504 bip induction 30min timelapse/pour_segmentationmasks/"
def extract_morphology_from_movie(datapath):
    """Given apath containing segmented movies, extracts cell morphology (width, length, area)
    using the rectangle method and saves results in an excel file"""
    files = glob.glob(datapath+"/*.tif")
    
    # each stack
    for nfile, file in enumerate(files):
        print('Processing file {}'.format(file.split(os.sep)[-1]))
        mask = tifffile.imread(file)
        nt, nx, ny = mask.shape
        
        all_dfs = []
        
        # time
        for j in range(nt):
            frame = mask[j]
            vals = np.unique(frame)
            if vals[0]!=0:
                raise ValueError('No background in this dataset?')
            vals = vals[1:]
            out_dict = {"widths":[],
                        "lengths":[],
                        "frame nr":[],
                        "index":[],
                        "areas":[],
                        "area_all":[],
                        'nr_cells':[]}
            # individual cell within a frame
            a1 = np.count_nonzero(frame>0)
            a2=len(np.unique(frame))-1
            for val in vals:
                msk = frame==val
                wt, lt = get_dimensions_rect(msk)
                out_dict["widths"].append(wt)
                out_dict["lengths"].append(lt)
                out_dict["frame nr"].append(j)
                out_dict["index"].append(val)
                out_dict["areas"].append(np.count_nonzero(msk))
                
                out_dict["area_all"].append(a1)
                out_dict["nr_cells"].append(a2)
            all_dfs.append(pd.DataFrame(out_dict))
        
        df_final = pd.concat(all_dfs)
        
        excel_name = file[:-4]+".xlsx"
        df_final.to_excel(excel_name)
        
        grp = df_final.groupby(['frame nr'])
        means = grp.mean()
        stds = grp.std()
        maxs = grp.max()
        fr = grp.groups.keys() #to test
        # export summaries
        out={}
        out["frame nr"] = fr
        out["width mean"] = means['widths']
        out["width std"] = stds['widths']
        
        out["length mean"] = means['lengths']
        out["length std"] = stds['lengths']
        
        out["cell area mean"] = means['areas']
        out["cell area std"] = stds['areas']
        
        # no need to take the means as they all have the same value
        out["All cells area"] = means['area_all']
        out["nr cells"] = means['nr_cells']
        
        df = pd.DataFrame(out)
        df.to_excel(file[:-4]+"_summaries.xlsx")

