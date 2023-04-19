#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 14:44:40 2022

@author: aurelienb
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

import glob
from tifffile import imread
from morphology_advanced import cell_dimensions_skel

path_labels = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Thomas/Timelapse overnight/26.01.2023 RCL44 WT Timelapse overnight/Position1_P561_resuzed_labels.tif"

pl = ['/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Thomas/Timelapse overnight/26.01.2023 RCL44 WT Timelapse overnight/processing/slice1_cellpose.tif',
      '/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Thomas/Timelapse overnight/26.01.2023 RCL44 WT Timelapse overnight/processing/slice15_cellpose.tif']
labels = np.array([imread(w) for w in pl])
# labels = imread(path_labels)
reprocess = True
if reprocess:
    all_dfs = []
    for j in range(labels.shape[0]):
        out_dict = {"Frame":[], "Label":[], "Width":[],"Length":[],"N":[]}

           
        label = labels[j]
        indices = np.unique(label)
        assert 0 in indices
        indices = indices[1:]
        
        for indice in indices:
            try:
                ws, ls = cell_dimensions_skel(label==indice,
                                              plot_in_context = False,
                                              plot_single=False)
                out_dict["Label"].append(indice)
                out_dict["Width"].append(ws)
                out_dict["Length"].append(ls)
                out_dict["Frame"].append(j)
                out_dict["N"].append(len(indices))
            except:
                print("bouh ca marche pas")
            
        df = pd.DataFrame(out_dict)
        
        tmp = path_labels.split(os.sep)
        fname = tmp[-2]+"_processed.csv"
        new_folder = (os.sep).join(tmp[:-1])
        df.to_csv(new_folder+os.sep+fname)
        all_dfs.append(df)
        
        tmp = path_labels.split(os.sep)
        new_folder = (os.sep).join(tmp[:-1])
        df_all = pd.concat(all_dfs)
        df_all.to_csv(new_folder+"/results.csv")
else:
    csvs = glob.glob(path_labels+"/*.csv")
    
    all_dfs = [pd.read_csv(w) for w in csvs]

    
tmp = path_labels.split(os.sep)
new_folder = (os.sep).join(tmp[:-1])
# ------ plotting -----------
plt.close("all")
fig,axes = plt.subplots(2,1, sharex = True, sharey = True)
axes = axes.ravel()

PSIZE = 0.1 # um
DT = 30 #TOcheck
nframes = labels.shape[0]
nfiles=0 # sanity check
secondary_axes = list()
maxn = 0
tmp = path_labels.split(os.sep)
fname = new_folder+"/results.csv"
frames = np.arange(nframes)
df = pd.read_csv(fname)

widths = [df[df["Frame"]==fr]["Width"].values*PSIZE for fr in range(nframes)]
lengths = [df[df["Frame"]==fr]["Length"].values*PSIZE for fr in range(nframes)]
ncells = [df[df["Frame"]==fr]["N"].values*PSIZE for fr in range(nframes)]

maxn = max(maxn, max([max(w) for w in ncells]))


axes[0].violinplot(widths,positions = frames)
axes[0].set_xlabel('Frame')
axes[0].set_ylabel('Width [µm]')
axes[1].violinplot(lengths,positions = frames)
axes[1].set_xlabel('Frame')
axes[1].set_ylabel('lengths [µm]')
    
"""
    ax2 = axes[j].twinx()
    ax2.set_ylabel(r"$\rm N/N_{0}$")
    secondary_axes.append(ax2)
    for k in range(len(ncells)):
        ax2.plot(frames,ncells[k],"-o",color="gray")
    # WIDTHS    
    # remove points with no detections for plotting
    prefilter = [len(w)>0 for w in widths]
    frames = np.array([frames[j] for j in range(len(prefilter)) if prefilter[j]])
    widths = [widths[j] for j in range(len(prefilter)) if prefilter[j]]
    
    axes[j].violinplot(widths,positions = frames)
    axes[j].boxplot(widths,positions = frames)
    axes[j].set_title(kw)
    axes[j].set_xlabel("Frame (min)")
    axes[j].set_ylabel("Width [µm]")
    
    # LENGTHS
    # remove points with no detections for plotting
    prefilter = [len(w)>0 for w in lengths]
    frames = np.array([frames[j] for j in range(len(prefilter)) if prefilter[j]])
    lengths = [lengths[j] for j in range(len(prefilter)) if prefilter[j]]
    
    axes2[j].violinplot(lengths,positions = frames)
    axes2[j].boxplot(lengths,positions = frames)
    axes2[j].set_title(kw)
    axes2[j].set_xlabel("Frame (min)")
    axes2[j].set_ylabel("Length [µm]")
    
    frames = np.arange(nframes) # redefines bc we want in the legend even if removed
    axes2[j].set_xticks(frames,labels=frames*DT)
    axes[j].set_xticks(frames,labels=frames*DT)
    
[w.set_ylim(bottom=0, top=maxn) for w in secondary_axes]
assert(nfiles==len(folders_labels))"""