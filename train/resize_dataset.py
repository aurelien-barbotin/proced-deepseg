#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:48:28 2024

@author: aurelienb
"""

import glob
from skimage.transform import rescale
import tifffile
import matplotlib.pyplot as plt
import cv2

plt.close('all')

path="/home/aurelienb/Data/subtilis_segmentation_dataset/processed/2024_10_31_Zeiss/"
file_mask="/home/aurelienb/Data/subtilis_segmentation_dataset/processed/2024_10_31_Zeiss/Image 97_mask.tif"
file="/home/aurelienb/Data/subtilis_segmentation_dataset/processed/2024_10_31_Zeiss/Image 97.tif"

def resize_file(file,factor,is_mask=False):
    """Resizes a 2D image file.
    Parameters:
        file (str): target path. Has to be tif
        factor (float): resize factor
        is_mask (bool): if True, applies a specific resizing for masks to keep labels intact
    Returns:
          ndarray: resized image"""
    im = tifffile.imread(file).astype(float)
    dsize=[int(w*factor) for w in im.shape]
    if is_mask:
        interp = cv2.INTER_NEAREST
    else:
        interp = cv2.INTER_LINEAR
    im_resized = cv2.resize(im, dsize=dsize, interpolation=interp)
    return im_resized

files = [file, file_mask]
ims = [tifffile.imread(w) for w in files]
im_resizeds = [resize_file(w,1.6) for w in files]

fig,axes = plt.subplots(2,2)
axes=axes.ravel()

axes[0].imshow(ims[0])
axes[1].imshow(im_resizeds[0])

axes[2].imshow(ims[1])
axes[3].imshow(im_resizeds[1])
