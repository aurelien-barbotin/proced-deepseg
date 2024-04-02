# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 09:50:49 2023

@author: proced_user
"""
import glob
from tifffile import imwrite
from czifile import imread as _imread
import os
import sys

from cellpose import models
import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import gaussian

def imread(file):
    im = np.squeeze(_imread(file))
    im = im.astype(float)
    im-=im.min()
    im/=np.percentile(im,99)
    im = gaussian(im,sigma=3)
    return im
# QC_model_path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485"
path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/"
path="/home/aurelienb/Documents/Projects/2022_02_Louise/models/"
models_path = {1:
  "Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485",
          2:
  "Cellpose_MIX_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_25_07_47_36.630602"}

folder_in = "/home/aurelienb/Data/2024_03_13_morpho/2_stat_RT_FM464/"
folder_out = folder_in

model_nr = 1
kk=models_path.keys()
while model_nr not in kk:
    model_nr = int(input("""Please enter a model number between {} and {}. 
         1: cellpose general, 2: cellpose with antibio,""".format(min(kk),max(kk))))

QC_model_path = path + models_path[model_nr]
if not os.path.isdir(folder_in):
    os.mkdir(folder_in)
    
if not os.path.isdir(folder_out):
    os.mkdir(folder_out)
# path_images = "//data.micalis.com/proced/proced/6- Former Lab Members/LOUISE DESTOUCHES/STAGE FEV JUIN 2022/SEGMENTATION CHA IM DATABASE/TIMELAPSE PRE-PROCESSING FOR SEG/BACI1_200515_S1_selseq_resized/"

subfolder="masks"

if not os.path.isdir(folder_out+subfolder):
    os.mkdir(folder_out+subfolder+"/")
files = glob.glob(folder_in+"*.czi*")
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
diam=70
model = models.CellposeModel(gpu=False, pretrained_model=QC_model_path,
                             diam_mean=diam, net_avg=True, device=None, 
                             residual_on=True, style_on=True, concatenation=False)

out = model.eval(images_2d, diameter=diam, channels=channels)
# masks, flows, styles, diams
masks, flows, styles = out
print(masks[0].max())
plt.figure()
plt.subplot(221)
plt.imshow(images_2d[0])
plt.subplot(222)
plt.imshow(flows[0][0])
plt.subplot(223)
plt.imshow(masks[0])
plt.subplot(224)
plt.imshow(flows[0][2])


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
        
    