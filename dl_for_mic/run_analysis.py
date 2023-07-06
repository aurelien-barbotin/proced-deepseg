#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:19:18 2023

@author: aurelienb

This script runs the analysis pipeline that extracts width and length of cellular
masks in segmented images using the skeleton method
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

import glob
from tifffile import imread
from dl_for_mic.morphology_advanced import cell_dimensions_skel
from scipy.ndimage import label as label_function

plt.close('all')

folder_in = "to_process/"

if not os.path.isdir(folder_in):
    os.mkdir(folder_in)

path_labels = folder_in

folders_labels = glob.glob(path_labels+"/*/")[-2:]

# PSIZE= float(input("Please specify the pixel size of your images in µm: "))
PSIZE=0.1
plot = True
all_dfs = []

min_nr_pixels_per_label = 6 # arbitrary-ish. If there are less pixels than that 
# in the cell, excludes the mask
for folder in folders_labels:
    print("Processing folder {}".format(folder))
    files = glob.glob(folder+"/*.tif")
    files.sort()
    
    out_dict = {"Folder": [],"File":[], "Label":[], "Width [µm]":[],
                "Length [µm]":[],"N":[],"frame_nr":[]}
    for j in range(len(files)):
        file = files[j]
        print("Processing file",file.split("/")[-1])
        # treats everyone as a 3D stack
        lab_tmp = imread(file)
        if lab_tmp.ndim ==2:
            lab_tmp=lab_tmp.reshape(1,*lab_tmp.shape)
            
        improper_labels = []
        residual_labels = []
        last_to_show=lab_tmp[-1].astype(float)
        last_to_show[last_to_show==0]=np.nan
        plt.figure()
        plt.imshow(last_to_show%20,cmap="tab20")
        
        for framenr,label in enumerate(lab_tmp):
            indices = np.unique(label)
            indices = np.array([w for w in indices if w!=0])
            
            name = file[len(path_labels):]
            if plot:
                fig,ax = plt.subplots(1,1)
                fig.suptitle(name)
                lab = label.copy().astype(float)
                lab[lab==0]=np.nan
                ax.imshow(lab,cmap="tab20")
            
            for indice in indices:
                mask = label==indice
                
                if np.count_nonzero(mask)<min_nr_pixels_per_label:
                    residual_labels.append([framenr,indice])
                    continue
                
                lab_check, _ = label_function(mask)
                if len(np.unique(lab_check))>2:
                    improper_labels.append([framenr, indice])
                # plots only last frame
                ws, ls = cell_dimensions_skel(mask,
                                  plot_in_context = framenr==lab_tmp.shape[0]-1)
                
                name0 = name.split(os.sep)
                name0 = [w for w in name0 if len(w)>0]
                out_dict["File"].append(name0[1])
                out_dict["Folder"].append(name0[0])
                out_dict["Label"].append(indice)
                out_dict["Width [µm]"].append(ws*PSIZE)
                out_dict["Length [µm]"].append(ls*PSIZE)
                out_dict["N"].append(len(indices))
                out_dict["frame_nr"].append(framenr)

    if len(improper_labels)>0:
        
        ff = file.split(os.sep)
        outname = "/".join(ff[:-1])+'_'+ff[-1][:-4]+"WARNING.txt"
        with open(outname,'w') as f:
            for imp_list in improper_labels:
                fr, il = imp_list
                f.write('Label {} in frame {} is not continuous, please check\n'.format(il, fr))
            for imp_list in residual_labels:
                fr, il = imp_list
                f.write('Label {} in frame {} has less than {} pixels, please check\n'.format(
                    il, fr,min_nr_pixels_per_label))

    df = pd.DataFrame(out_dict)
    
    tmp = folder.split(os.sep)
    fname = tmp[-2]+"_processed.xlsx"
    new_folder = (os.sep).join(tmp[:-2])
    df.to_excel(new_folder+os.sep+fname)
    all_dfs.append(df)
dfc = pd.concat(all_dfs)
dfc.to_excel(new_folder+os.sep+"results_merged.xlsx")


