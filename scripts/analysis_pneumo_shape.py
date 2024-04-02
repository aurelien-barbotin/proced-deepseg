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

datapath="/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Dimitri/230428 contraste phase/ilastik images/masks/"
# datapath="/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Dimitri/230504 bip induction 30min timelapse/pour_segmentationmasks/"
files = glob.glob(datapath+"/*.tif")

xn1 = 2
xn2 = 4
fig1,axes1 = plt.subplots(xn1,xn2,sharex=True,sharey=True) # widths
fig2,axes2 = plt.subplots(xn1,xn2,sharex=True, sharey = True) # lengths
fig3,axes3 = plt.subplots(xn1,xn2,sharex=True, sharey = True) # areas
fig4,axes4 = plt.subplots(xn1,xn2,sharex=True, sharey = True) # area total
fig5,axes5 = plt.subplots(xn1,xn2,sharex=True, sharey = True) # n cells


fig1.suptitle('Widths')
fig2.suptitle('Lengths')
fig3.suptitle('Avg areas')
fig4.suptitle('Overall area')
fig5.suptitle('# cells')

axes1=axes1.ravel()
axes2=axes2.ravel()
axes3=axes3.ravel()
axes4=axes4.ravel()
axes5=axes5.ravel()

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

    name = file.split(os.sep)[-1].split('_cp_masks')[0]
    ax1 = axes1[nfile]
    ax2 = axes2[nfile]
    ax3 = axes3[nfile]
    ax4 = axes4[nfile]
    ax5 = axes5[nfile]
    
    ax1.errorbar(fr,means['widths'],yerr=stds['widths'])
    ax2.errorbar(fr,means['lengths'],yerr=stds['lengths'])
    ax3.errorbar(fr,means['areas'],yerr=stds['areas'])
    ax4.plot(fr,means['area_all']/means['area_all'][0])
    ax5.plot(fr,means['nr_cells'])
    
    ax1.set_title(name)
    ax2.set_title(name)
    ax3.set_title(name)
    ax4.set_title(name)
    ax5.set_title(name)
    
    ax1.set_xlabel("# Frame")
    ax2.set_xlabel("# Frame")
    ax1.set_ylabel("Width [px]")
    ax2.set_ylabel("Length [px]")
    ax3.set_ylabel("Area [px]")
    
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

