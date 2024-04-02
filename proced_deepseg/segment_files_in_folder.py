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

# QC_model_path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485"
path = "C:/Users/proced_user/Documents/Segmentation/FINAL_models/"
models_path = {1:
  "Cellpose_GM_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_18_13_33_18.490485",
          2:
  "Cellpose_MIX_FINAL/cellpose_residual_on_style_on_concatenation_off_train_folder_2022_05_25_07_47_36.630602"}



folder_in = "to_process/"
folder_out = "results/"

model_nr = -1
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



subfolder=input("Please enter output folder name:\n")

if os.path.isdir(subfolder):
    print("The filename already exists, please specify another one")
    sys.exit(0)
os.mkdir(folder_out+subfolder+"/")
files = glob.glob(folder_in+"*.tif*")
images = [imread(w) for w in files]
channels=[[0,0]]

model = models.CellposeModel(gpu=False, pretrained_model=QC_model_path,
                             diam_mean=30.0, net_avg=True, device=None, 
                             residual_on=True, style_on=True, concatenation=False)

out = model.eval(images, diameter=None, channels=channels)

names = [w.split(os.sep)[-1] for w in files]
# masks, flows, styles, diams

masks, flows, styles = out

for j in range(len(files)):
    name = files[j].split(os.sep)[-1].split('.')[0]
    out_name = folder_out+subfolder+"/"+name+'_mask.tif'
    """image = tifffile.imread(files[j])
    masks, flows_orig, _ = CP.eval(image, 
                                    channels=channels, 
                                    # channel_axis=channel_axis,
                                    diameter=diameter,
                                    net_avg=True,
                                    resample=False,
                                    cellprob_threshold=cellprob_threshold,
                                    flow_threshold=flow_threshold,
                                    do_3D=False,
                                    #stitch_threshold=stitch_threshold
                                    )"""
    mask = masks[j]
    imwrite(out_name,mask)
    