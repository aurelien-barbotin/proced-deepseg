# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 09:30:21 2023

@author: proced_user
"""

from proced_deepseg.morphology_advanced import extract_morphology_from_movie
import os
import glob
import numpy as np
import tifffile


def filterim(im):
    u,v = im.shape
    l1 = np.unique(im[0,:])
    l2 = np.unique(im[:,0])
    l3 = np.unique(im[u-1,:])
    l4 = np.unique(im[:,v-1])
    all_labels = list(l1)+list(l2)+list(l3)+list(l4)
    for lab in all_labels:
        if lab !=0:
            im[im==lab]=0
    return im
        
datapath="to_process/"
if not os.path.isdir(datapath):
    os.mkdir(datapath)


files = glob.glob(datapath+"/*.tif")
 
for nfile, file in enumerate(files):
     print('Processing file {}'.format(file.split(os.sep)[-1]))
     stack = tifffile.imread(file)
     if stack.shape==2:
         stack=stack.reshape(1,*stack.shape)
     stack = np.array([filterim(w) for w in stack])
     tifffile.imwrite(file[:-4]+"_edgesrem.tif", stack)
