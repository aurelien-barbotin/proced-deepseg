#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:19:18 2023

@author: aurelienb

This script runs the analysis pipeline that extracts width and length of cellular
masks in segmented images.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

import glob
from tifffile import imread
from morphology_advanced import cell_dimensions_skel
from scipy.ndimage import label as label_function

plt.close('all')

folder_in = "to_process/"

if not os.path.isdir(folder_in):
    os.mkdir(folder_in)

path_labels = folder_in

folders_labels = glob.glob(path_labels+"/*/")

PSIZE= float(input("Please specify the pixel size of your images in µm: "))

plot = True
all_dfs = []
for folder in folders_labels:
    print("Processing folder {}".format(folder))
    files = glob.glob(folder+"/*.tif")
    files.sort()
    
    out_dict = {"Folder": [],"File":[], "Label":[], "Width [µm]":[],
                "Length [µm]":[],"N":[]}
    for j in range(len(files)):
        file = files[j]
        print("Processing file",file.split("/")[-1])
        
        label = imread(file)
        indices = np.unique(label)
        indices = np.array([w for w in indices if w!=0])
        
        improper_labels = []
        
        name = file.strip(path_labels)
        if plot:
            fig,ax = plt.subplots(1,1)
            fig.suptitle(name)
            lab = label.copy().astype(float)
            lab[lab==0]=np.nan
            ax.imshow(lab,cmap="tab20")
        
        for indice in indices:
            mask = label==indice
            lab_check, _ = label_function(mask)
            if len(np.unique(lab_check))>2:
                improper_labels.append(indice)
                
            ws, ls = cell_dimensions_skel(mask,plot_in_context = True)
            out_dict["File"].append(name.split(os.sep)[-1])
            out_dict["Folder"].append(name.split(os.sep)[0])
            out_dict["Label"].append(indice)
            out_dict["Width [µm]"].append(ws*PSIZE)
            out_dict["Length [µm]"].append(ls*PSIZE)
            out_dict["N"].append(len(indices))
        if len(improper_labels)>0:
            
            ff = file.split(os.sep)
            outname = "/".join(ff[:-1])+'_'+ff[-1][:-4]+"WARNING.txt"
            with open(outname,'w') as f:
                for il in improper_labels:
                    f.write('Label {} is not continuous, please check\n'.format(il))

    df = pd.DataFrame(out_dict)
    
    tmp = folder.split(os.sep)
    fname = tmp[-2]+"_processed.csv"
    new_folder = (os.sep).join(tmp[:-2])
    df.to_csv(new_folder+os.sep+fname)
    all_dfs.append(df)
dfc = pd.concat(all_dfs)
dfc.to_csv(new_folder+os.sep+"results_merged.csv")

