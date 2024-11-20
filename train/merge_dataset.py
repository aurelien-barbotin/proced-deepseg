#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:54:32 2024

@author: aurelienb
"""

import glob
import os
import shutil
import cv2
import tifffile
import numpy as np

path = "/home/aurelienb/Data/subtilis_segmentation_dataset/processed/"
outpath="/home/aurelienb/Data/subtilis_segmentation_dataset/merged_dataset/"
dirs = os.listdir(path)

def read_pixelsize_readme(readme_path):
    with open(readme_path,'r') as f:
        psize = f.readline()
    psize = psize.split(":")[-1].split(' nm')[0].strip(' ')
    try:
        return int(psize)
    except:
        return float(psize)
    
def resize_imagefile(file,factor,is_mask=False):
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

resize =True
target_psize=100

count=0
for dd in dirs:
    files = glob.glob(path+dd+'/*.tif')
    if resize:
        psize = read_pixelsize_readme(path+dd+"/readme.txt")
        print(psize)
    print(len(files))
    for file in files:
        fname = file[len(path):].replace('/','_')
        if fname[-9:]!='_mask.tif':
            fname = fname.rstrip('.tif')+'_img.tif'
            
        if resize and np.abs(psize-target_psize)/target_psize>0.2:
            resized = resize_imagefile(file,psize/target_psize,is_mask=fname[-9:]=='_mask.tif')
            tifffile.imwrite(outpath+fname,resized)
        else:
            shutil.copyfile(file, outpath+fname)
        count+=1

1/0
 # --------- Louise preprocessed dataset ---------------       
path1="/run/user/1001/gvfs/smb-share:server=data.micalis.com,share=proced/proced/6- Former Lab Members/LOUISE DESTOUCHES/STAGE FEV JUIN 2022/TRAINING DATA/"
dir1="TRAININGDATA_GM_100/"
dset_name = 'louise_data'
folders1= os.listdir(path1+dir1)
for folder in folders1:
    files = glob.glob(path1+dir1+folder+'/*.tif')    
    for file in files:
            fname = dset_name+'_'+file.split('/')[-1]
            if "im" in folder.lower():
                fname = fname.rstrip('.tif')+'_img.tif'
            elif "mask" in folder.lower():
                fname = fname.rstrip('.tif')+'_mask.tif'
            shutil.copyfile(file, outpath+fname)
            count+=1
    

print('{} files copied'.format(count))