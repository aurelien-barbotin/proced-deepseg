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

path_labels = "/home/aurelienb/Data/STAGE FEV JUIN 2022/SEGMENTATION CHA IM DATABASE/LABELS WITH THE BAC ON THE EDGE REMOVED/"

folders_labels = glob.glob(path_labels+"/*/")

files = glob.glob(folders_labels[0]+"/*.tif")
path = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Thomas_Aurélien/Mask/44_0moe_mask/"
folders_labels=[]
reprocess = True
if reprocess:
    all_dfs = []
    for folder in folders_labels:
        print("Processing folder {}".format(folder))
        files = glob.glob(folder+"/*.tif")
        files.sort()
        
        out_dict = {"File":[], "Frame":[], "Label":[], "Width":[],"Length":[],"N":[]}
        for j in range(len(files)):
            file = files[j]
            print("Processing file",file.split("/")[-1])
            label = imread(file)
            indices = np.unique(label)
            assert 0 in indices
            indices = indices[1:]
            
            for indice in indices:
                ws, ls = cell_dimensions_skel(label==indice,plot_in_context = False)
                out_dict["File"].append(file)
                out_dict["Label"].append(indice)
                out_dict["Width"].append(ws)
                out_dict["Length"].append(ls)
                out_dict["Frame"].append(j)
                out_dict["N"].append(len(indices))
        df = pd.DataFrame(out_dict)
        
        tmp = folder.split(os.sep)
        fname = tmp[-2]+"_processed.csv"
        new_folder = (os.sep).join(tmp[:-2])
        df.to_csv(new_folder+os.sep+fname)
        all_dfs.append(df)
else:
    csvs = glob.glob(path_labels+"/*.csv")
    
    all_dfs = [pd.read_csv(w) for w in csvs]
# ------ plotting -----------
plt.close("all")
keywords = ["BAC", "CHLORA", "FOSFO","CTRL","CYCLO","VANCO","LYS","PEN"]
fig,axes = plt.subplots(2,4, sharex = True, sharey = True)
axes = axes.ravel()
fig2,axes2 = plt.subplots(2,4, sharex = True, sharey = True)
axes2 = axes2.ravel()

PSIZE = 0.1 # um
DT = 30 #TOcheck
nframes = len(files)
nfiles=0 # sanity check
secondary_axes = list()
maxn = 0
for j, kw in enumerate(keywords):
    frames = np.arange(nframes)
    if reprocess:
        fds = list(filter(lambda x: "/"+kw in x or "LABEL_"+kw in x, folders_labels))
        indices = [folders_labels.index(fd) for fd in fds]
    else:
        fds = list(filter(lambda x: "/"+kw in x or "LABEL_"+kw in x, csvs))
        indices = [csvs.index(fd) for fd in fds]
    nfiles += len(fds)
    df_condition = [all_dfs[ind] for ind in indices]
    all_condition = pd.concat(df_condition)
    ncells = [[dfc[dfc["Frame"]==fr]["N"].values for fr in range(nframes)] for dfc in df_condition]
    ncells = [np.array([n[0] if len(n)>0 else 0 for n in subn]) for subn in ncells]
    ncells = [subn/subn[0] for subn in ncells]
    maxn = max(maxn, max([max(w) for w in ncells]))
    widths = [all_condition[all_condition["Frame"]==fr]["Width"].values*PSIZE for fr in range(nframes)]
    lengths = [all_condition[all_condition["Frame"]==fr]["Length"].values*PSIZE for fr in range(nframes)]


    
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