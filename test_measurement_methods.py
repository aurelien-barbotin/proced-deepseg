#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:43:39 2022

@author: aurelienb
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import glob

from tifffile import imread
from morphology_advanced import extract_roi, cell_dimensions_skel, get_dimensions_rect

plt.close("all")
path = "/home/aurelienb/Data/STAGE FEV JUIN 2022/MANUAL VS CODE WIDTH MEASURES/ANTIBIOTIC BACTERIA/manual measures/"
path2  ="/home/aurelienb/Data/STAGE FEV JUIN 2022/MANUAL VS CODE WIDTH MEASURES/NORMAL BACTERIA/manual measures csv/"
files = glob.glob(path+"/*.csv")
files = list(filter(lambda x:"_updated" not in x, files))
# files.extend(glob.glob(path2+"/*.csv"))
files.sort()

path_masks = "/home/aurelienb/Data/STAGE FEV JUIN 2022/MANUAL VS CODE WIDTH MEASURES/ANTIBIOTIC BACTERIA/labels used/"
path_masks2 = "/home/aurelienb/Data/STAGE FEV JUIN 2022/MANUAL VS CODE WIDTH MEASURES/NORMAL BACTERIA/images used"
files_masks = glob.glob(path_masks+"/*.tif")
# files_masks.extend(glob.glob(path_masks2+"/*.tif"))
files_masks.sort()

lw_manual = []
lw_rect = []
lw_skel = []

for jj in range(len(files)):
    file = files[jj]
    mask = imread(files_masks[jj])
    df = pd.read_csv(file)
    
    indices= np.unique(df["Median"])
    
    plt.figure()
    mm = mask%19+1
    mm[mask==0]=0
    plt.imshow(mm, cmap = "tab20")
    plt.imshow(mask,alpha=0)
    plt.title(file.split("/")[-1])
    tmp_measured_rect = []
    tmp_measured_skel = []
    for index in indices:
        length, width = df[df["Median"]==index]["Length"].values
        if length<width:
            print("Warning! width is larger than length")
        
        coords, roi = extract_roi(mask==int(index))
        
        wr, lr = get_dimensions_rect(roi)
        ws, ls = cell_dimensions_skel(mask==int(index), plot_in_context=True)
        lw_manual.append([length,width])
        lw_rect.append([lr,wr])
        lw_skel.append([ls,ws])
        tmp_measured_rect.extend([lr,wr])
        tmp_measured_skel.extend([ls,ws])
    df["Meas rect"] = tmp_measured_rect
    df["Meas skel"] = tmp_measured_skel
    tmp_measured_rect = np.asarray(tmp_measured_rect)
    tmp_measured_skel = np.asarray(tmp_measured_skel)
    # df["error rect"] = (tmp_measured_rect-df["len"])
    df.to_csv(file[:-4]+"_updated.csv")
    
lw_manual = np.asarray(lw_manual)
lw_rect = np.asarray(lw_rect)
lw_skel = np.asarray(lw_skel)

plt.figure()
plt.subplot(121)
plt.title("Length")
plt.scatter(lw_manual[:,0], lw_rect[:,0],label="Rectangle")
plt.scatter(lw_manual[:,0], lw_skel[:,0],label="Skeleton")
xx = np.linspace(0,max(lw_manual[:,0]),10)
plt.plot(xx,xx, "k--")
plt.xlabel("Manually input value")
plt.ylabel("Measured value")
plt.legend()

plt.subplot(122)
plt.title("Width")
plt.scatter(lw_manual[:,1], lw_rect[:,1],label="Rectangle")
plt.scatter(lw_manual[:,1], lw_skel[:,1],label="Skeleton")
xx = np.linspace(0,max(lw_manual[:,1]),10)
plt.plot(xx,xx, "k--")
plt.xlabel("Manually input value")
plt.ylabel("Measured value")
plt.legend()

for j in range(2):
    error_skel = np.abs((lw_manual[:,j] - lw_skel[:,j])/lw_manual[:,j])*100
    error_rect = np.abs((lw_manual[:,j] - lw_rect[:,j])/lw_manual[:,j])*100
    print("Mean error: rect {:.1f}%, skel {:.1f}%".format(np.mean(error_rect),np.mean(error_skel)))
