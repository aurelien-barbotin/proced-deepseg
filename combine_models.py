#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 16:48:38 2022

@author: aurelienb
"""

import cellpose
import stardist

from stardist.models import StarDist2D
from cellpose import models
from tifffile import imread
import glob
import matplotlib.pyplot as plt
import numpy as np
from csbdeep.utils import Path, normalize

plt.close('all')
QC_model_path = """/home/aurelienb/Documents/Projects/2022_02_Louise/models/\
Cellpose_CycloFosfo_selval2im_3000e/cellpose_residual_on_style_on_concatenation\
_off_train_folder_2022_05_10_07_32_50.203772"""

# -------- cellpose ---------------

path_images = "/home/aurelienb/Documents/Projects/2022_02_Louise/sample_images/"
images = glob.glob(path_images+'*.tif')
images = [imread(w) for w in images]
channels=[[0,0]]

model = models.CellposeModel(gpu=False, pretrained_model=QC_model_path,
                             diam_mean=30.0, net_avg=True, device=None, 
                             residual_on=True, style_on=True, concatenation=False)

out = model.eval(images, diameter=None, channels=channels)

# masks, flows, styles, diams

masks, flows, styles = out

n0 = 0

mask = masks[n0].astype(float)

mask[mask==0]=np.nan

plt.figure()
plt.subplot(121)
plt.imshow(images[n0])
plt.subplot(122)
plt.imshow(mask%20,cmap="tab20")

# ------- Stardist ---------

path_model_stardist = "/home/aurelienb/Documents/Projects/2022_02_Louise/models/"
model = StarDist2D(None,name="StarDist_GM100_selval",basedir = path_model_stardist)

labels, polygons = model.predict_instances(normalize(images[n0],pmin=0,pmax=99.8))
labels = labels.astype(float)

labels[labels==0]=np.nan
plt.figure()
plt.subplot(121)
plt.imshow(images[n0])
plt.subplot(122)
plt.imshow(labels%20,cmap="tab20")
plt.suptitle("Stardist")