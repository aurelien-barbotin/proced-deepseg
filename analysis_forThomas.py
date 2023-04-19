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
from scipy.ndimage import label as label_function
plt.close('all')

path_labels = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Thomas_Aurélien/Mask/"

folders_labels = glob.glob(path_labels+"/*_mask/")

PSIZE=0.064 #µm
reprocess = True
plot = True
if reprocess:
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
else:
    csvs = glob.glob(path_labels+"/*.csv")
    all_dfs = [pd.read_csv(w) for w in csvs]
