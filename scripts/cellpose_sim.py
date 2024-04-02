# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 09:50:49 2023

@author: proced_user
"""
import glob
from tifffile import imread, imwrite
import os
import sys

from cellpose import models
import numpy as np



files = ['/home/aurelienb/Documents/Projects/collaborations/MerveNur/SIM/Co-culture_Active_MCR-1_1green.tif']
images = [imread(w) for w in files]
images_2d = []
images_3d = []
files2d=[]
files3d=[]

for file in files:
    im = imread(file)
    if im.ndim==2:
        images_2d.append(im)
        files2d.append(file)
    elif im.ndim==3:
        
        images_3d.append(im)
        files3d.append(file)

channels=[[0,0]]

model = models.CellposeModel(gpu=False,
                             net_avg=True, device=None, 
                             residual_on=True, style_on=True, concatenation=False)
images_3d = np.array(images_3d).squeeze()
images_3d = [w for w in images_3d]
out = model.eval(images_3d, diameter=None, channels=channels)

masks, flows, styles = out

import matplotlib.pyplot as plt
plt.figure()
plt.imshow(masks)
# masks, flows, styles, diams
"""
masks, flows, styles = out

for j in range(len(files2d)):
    name = files2d[j].split(os.sep)[-1].split('.')[0]
    out_name = folder_out+subfolder+"/"+name+'_mask.tif'
    mask = masks[j]
    imwrite(out_name,mask)

for j,images in enumerate(images_3d):
    print('Processing images 3D',images.shape)
    out = model.eval([w for w in images], diameter=None, channels=channels)
    masks, flows, styles = out
    print(len(masks))
    name = files3d[j].split(os.sep)[-1].split('.')[0]
    subdir = folder_out+subfolder+"/"+name+'_mask'
    try:
        imwrite(subdir+".tif",np.array(masks))
        print('success writing')
    except: # if they don't all hve the same size
        if not os.path.isdir(subdir):
            os.mkdir(subdir)
        for k in range(len(masks)):
            imwrite(subdir+'/{}.tif'.format(k+1),masks[k])
        
    """