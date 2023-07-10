#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 14:44:40 2022

@author: aurelienb
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob

path = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Cha_Aurelien/Papier ponA/A analyser/3-segmentation/to_process/"

folders_labels=[]
reprocess = True

xlsxs = glob.glob(path+"/*.xlsx")

all_dfs = [pd.read_excel(w) for w in xlsxs]

# ------ plotting -----------
plt.close("all")
keywords = ["MreB cyclo", "MreB", "PonA cyclo","PonA"]
fig,axes = plt.subplots(1,4, sharex = True, sharey = True)
axes = axes.ravel()
fig2,axes2 = plt.subplots(1,4, sharex = True, sharey = True)
axes2 = axes2.ravel()

PSIZE = 1 # already converted in um
DT = 12 #TOcheck
nfiles=0 # sanity check
secondary_axes = list()
maxn = 0
for j, kw in enumerate(keywords):
    df_condition = all_dfs[j]
    nframes = df_condition['frame_nr'].values.max()
    frames = np.arange(nframes)

    all_condition = df_condition
    
    # finds nr of cells
    files = np.unique(df_condition['File'])
    ncells=[]
    for file in files:
        df_tmp=df_condition[df_condition['File']==file]
        # N the number of cells is identical for each label in a same frame
        # so we need only one of the values in the arry
        ncells_file = [df_tmp[df_tmp["frame_nr"]==fr]["N"].values[0] for fr in range(nframes)]
        ncells.append(np.array(ncells_file))

    # ncells = [np.array([n[0] if len(n)>0 else 0 for n in subn]) for subn in ncells]
    ncells = [subn/subn[0] for subn in ncells]
    maxn = max(maxn, max([max(w) for w in ncells]))
    widths = [df_condition[df_condition["frame_nr"]==fr]["Width [µm]"].values*PSIZE for fr in range(nframes)]
    lengths = [all_condition[all_condition["frame_nr"]==fr]["Length [µm]"].values*PSIZE for fr in range(nframes)]


    
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
assert(nfiles==len(folders_labels))