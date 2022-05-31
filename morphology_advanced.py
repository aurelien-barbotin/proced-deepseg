#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:57:33 2022

@author: aurelienb
"""

import numpy as np
import matplotlib.pyplot as plt

from skimage.morphology import medial_axis
from skimage.graph import shortest_path
from skimage.measure import find_contours

from scipy.ndimage import median_filter, gaussian_filter, zoom
from tifffile import imread

def extract_roi(mask, margin=3):
    xx,yy=np.where(mask==1)
    xmin = max(0,xx.min()-margin)
    xmax = min(xx.max() + margin, mask.shape[0])
    ymin = max(yy.min()-margin, 0)
    ymax = min(yy.max() + margin, mask.shape[1])
    
    return (xmin,ymin,xmax,ymax), mask[xmin:xmax,ymin:ymax]

plt.close('all')
path = "/home/aurelienb/Documents/Projects/2022_02_Louise/CCBS616_1_561.tif-labels.tif"

img = imread(path)
nce = 59

mask = img==nce
skel, dist = medial_axis(mask, return_distance = True)

contours = find_contours(mask,level=0.5)
assert len(contours)==1
contours = contours[0]
img_show = img.copy().astype(float)
img_show[img_show==43]=np.nan

plt.figure()
plt.subplot(121)
plt.imshow(img_show, cmap="Set1")
plt.subplot(122)
plt.imshow(skel.astype(float))
# plt.contour(mask,[0.5],cmap="magma_r")
plt.plot(contours[:,1],contours[:,0])
"""
contours[:,0] = median_filter(contours[:,0],size=5)
contours[:,1] = median_filter(contours[:,1],size=5)"""
contours = find_contours(gaussian_filter(mask.astype(float),sigma=2),level=0.5)[0]
plt.plot(contours[:,1],contours[:,0], color = "red")

from skimage.draw import polygon
upsampling_factor = 3

# fill polygon
submask_coords, submask = extract_roi(mask)
new_img = zoom(gaussian_filter(submask.astype(float),sigma=2),upsampling_factor)
poly = find_contours(new_img,level=0.5)[0]
rr, cc = polygon(poly[:, 0], poly[:, 1], img.shape)
out = np.zeros_like(new_img)
out[rr, cc] = 1

skel, dist = medial_axis(out, return_distance = True)

plt.figure()
plt.imshow(skel)
plt.contour(out,[0.5],cmap='magma_r')
