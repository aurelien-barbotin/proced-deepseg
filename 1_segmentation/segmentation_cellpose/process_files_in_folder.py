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

# QC_model_path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485"
path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/"
path="/home/aurelienb/Documents/Projects/2022_02_Louise/models/"
models_path = {1:
  "Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485",
          2:
  "Cellpose_MIX_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_25_07_47_36.630602",
  3: None}

folder_in = "to_process/"
folder_out = "results/"

model_nr = -1
kk=models_path.keys()
while model_nr not in kk:
    model_nr = int(input("""Please enter a model number between {} and {}. 
         1: cellpose general, 2: cellpose with antibio, 3: Default (cyto3)\n""".format(min(kk),max(kk))))

model_name = models_path[model_nr]
QC_model_path = path + str(model_name)

if not os.path.isdir(folder_in):
    os.mkdir(folder_in)
    
if not os.path.isdir(folder_out):
    os.mkdir(folder_out)
# path_images = "//data.micalis.com/proced/proced/6- Former Lab Members/LOUISE DESTOUCHES/STAGE FEV JUIN 2022/SEGMENTATION CHA IM DATABASE/TIMELAPSE PRE-PROCESSING FOR SEG/BACI1_200515_S1_selseq_resized/"

subfolder=input("Please enter output folder name:\n")

if os.path.isdir(subfolder):
    print("The filename already exists, please specify another one")
    sys.exit(0)
os.mkdir(folder_out+subfolder+"/")
files = glob.glob(folder_in+"*.tif")
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

# masks, flows, styles, diams


for j in range(len(files2d)):
    if model_name is not None:
        model = models.CellposeModel(gpu=False, pretrained_model=QC_model_path,
                                     diam_mean=30.0, net_avg=True, device=None, 
                                     residual_on=True, style_on=True, concatenation=False)
        out = model.eval(images_2d, diameter=None, channels=channels)
        masks, flows, styles = out
    else:
        model = models.Cellpose(gpu=True, model_type="cyto3")
        if len(images_2d)>0:
            masks, flows, styles, diams = model.eval(images_2d, diameter=0, channels=channels,
                                                  niter=2000) # using more iterations for bacteria
    name = files2d[j].split(os.sep)[-1].split('.')[0]
    out_name = folder_out+subfolder+"/"+name+'_mask.tif'
    mask = masks[j]
    imwrite(out_name,mask)

for j,images in enumerate(images_3d):
    print('Processing images 3D',images.shape)
    if model_name is not None:
        out = model.eval([w for w in images], diameter=None, channels=channels)
        masks, flows, styles = out
    else:
        masks, flows, styles, diams = model.eval([w for w in images], diameter=0, channels=channels,
                                                  niter=2000) # using more iterations for bacteria
    
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
        
    