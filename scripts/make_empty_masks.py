#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 16:24:56 2024

@author: aurelienb
"""

import numpy as np
import glob
import tifffile

todo="masks"
if todo=="masks":
    path = "/home/aurelienb/Data/subtilis_segmentation_dataset/2024_10_16_Zeiss/"
    files = glob.glob(path+"*.tif")
    files.extend(glob.glob(path+"*.TIF"))
    files = list(filter(lambda x: "_mask" not in x,files))
    print(files)
    
    for file in files:
        img = tifffile.imread(file)
        mask = np.zeros_like(img).astype(int)
        tifffile.imwrite(file.rstrip('.tif')+'_mask.tif',mask)
else:
    aa=tifffile.imread("/home/aurelienb/Data/subtilis_segmentation_dataset/2024_08_01_Nikon/cropped/tl0_morpho_w1TIRF 488 SINGLE_s4_t8-1_mask.tif")
    print(aa.min(),aa.max())