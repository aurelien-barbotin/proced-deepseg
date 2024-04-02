#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 15:37:27 2023

@author: aurelienb
To segment movies

"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import numpy as np
from cellpose_omni import models, core, io
import matplotlib.pyplot as plt
import glob
import tifffile
from tifffile import imwrite
use_GPU = core.use_gpu()

datapath="to_process/"
if not os.path.isdir(datapath):
    os.mkdir(datapath)
    
savepath=datapath+'masks/'

if not os.path.isdir(savepath):
    os.mkdir(datapath+"masks/")
files = glob.glob(datapath+"*.tif")

print(files)

from omnipose.utils import normalize99
imgs = [io.imread(f) for f in files]

# print some info about the images.
for i in imgs:
    print('Original image shape:',i.shape)
    print('data type:',i.dtype)
    print('data range:', i.min(),i.max())
nimg = len(imgs)
print('number of images:',nimg)

# Normalization. Not sure it is super useful
for k in range(len(imgs)):
    imgs[k] = normalize99(imgs[k])
    
model_custom='C:/Users/proced_user/Documents/Segmentation/models_round_pseudomonas/2023_11_04/cellpose_residual_on_style_on_concatenation_off_omni_nclasses_4_MerveNur_withcrops_2023_11_03_17_10_45.709962'


chans = None #this means segment based on first channel, no second channel 

# define parameters
mask_threshold = -1
verbose = 0 # turn on if you want to see more output 
use_gpu = use_GPU #defined above
transparency = True # transparency in flow output
rescale=None # give this a number if you need to upscale or downscale your images
omni = True # we can turn off Omnipose mask reconstruction, not advised 
flow_threshold = 0 # default is .4, but only needed if there are spurious masks to clean up; slows down output
niter = None # None lets Omnipose calculate # of Euler iterations (usually <20) but you can tune it for over/under segmentation 
resample = True #whether or not to run dynamics on rescaled grid or original grid 
cluster = True # use DBSCAN clustering
augment = False # average the outputs from flipped (augmented) images; slower, usually not needed 
tile = False # break up image into smaller parts then stitch together
affinity_seg = 1 #new feature, stay tuned...

all_masks = []
all_flows = []
all_styles=[]
model = models.CellposeModel(gpu=use_GPU, model_type=None,pretrained_model=model_custom, nchan=2)

all_masks = []
all_flows = []
all_styles=[]
for j,img in enumerate(imgs):
    print('Segmenting stack {}'.format(j))
    masks, flows, styles = model.eval([img[i] for i in range(img.shape[0])],
                                      channels=chans,
                                      rescale=rescale,
                                      mask_threshold=mask_threshold,
                                      transparency=transparency,
                                      flow_threshold=flow_threshold,
                                      niter=niter,
                                      omni=omni,
                                      cluster=cluster, 
                                      resample=resample,
                                      verbose=verbose, 
                                      affinity_seg=affinity_seg,
                                      tile=tile,
                                      augment=augment)


    all_masks.append(masks)
    old_name=files[j].split(os.sep)[-1][:-4]
    fn=savepath+"/"+old_name+"_cp_masks.tif"
    tifffile.imwrite(fn,np.array(masks))
