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

proba = flows[n0][2]

mask[mask==0]=np.nan

plt.figure()
plt.subplot(131)
plt.imshow(images[n0])
plt.subplot(132)
plt.imshow(mask%20,cmap="tab20")
plt.subplot(133)
plt.imshow(proba, cmap = "RdYlGn")
plt.title('probability map')
plt.colorbar()
plt.suptitle('Cellpose')

# ------- Stardist ---------

path_model_stardist = "/home/aurelienb/Documents/Projects/2022_02_Louise/models/"
model_sd = StarDist2D(None,name="StarDist_GM100_selval",basedir = path_model_stardist)

out_sd = model_sd.predict_instances(normalize(images[n0],pmin=0,pmax=99.8), return_predict = True)
labels, polygons = out_sd[0]
proba_sd = out_sd[1][0]

labels = labels.astype(float)

labels[labels==0]=np.nan
plt.figure()
plt.subplot(131)
plt.imshow(images[n0])
plt.subplot(132)
plt.imshow(labels%20,cmap="tab20")
plt.subplot(133)
plt.imshow(proba_sd, cmap = "RdYlGn")
plt.title('probability map')
plt.suptitle("Stardist")
plt.colorbar()