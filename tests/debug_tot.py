#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:30:58 2024

@author: aurelienb
"""
import numpy as np
import matplotlib.pyplot as plt
from tifffile import imread
from proced_deepseg.morphology_advanced import cell_dimensions_skel
from scipy.ndimage import label as label_function

file = "/home/aurelienb/Desktop/thomas_debug_44_01_P561_mask.tif"
label = imread(file)
indices = np.unique(label)
indices = np.array([w for w in indices if w!=0])

indice = indices[-1]

name='miaou'
fig,ax = plt.subplots(1,1)
fig.suptitle(name)
lab = label.copy().astype(float)
lab[lab==0]=np.nan
ax.imshow(lab,cmap="tab20")
all_ws=[]
all_ls = []
for indice in indices:
    mask = label==indice
    lab_check, _ = label_function(mask)
        
    ws, ls = cell_dimensions_skel(mask,plot_in_context = True)
    all_ws.append(ws)
    all_ls.append(ls)
all_ws = np.array(all_ws)*0.11
print('mean {} +/- {}'.format(all_ws.mean(),all_ws.std()))