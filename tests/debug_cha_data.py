#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 10:21:57 2023

@author: aurelienb
"""

import numpy as np
import tifffile
import matplotlib.pyplot as plt
from dl_for_mic.morphology_advanced import cell_dimensions_skel
from skimage.morphology import binary_erosion

plt.close('all')

path = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Cha_Aurelien/Papier ponA/A analyser/3-segmentation/to_process/PonA/Label Image 9-1_corrected.tif"

label = 152
"""
path="/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Cha_Aurelien/Papier ponA/A analyser/3-segmentation/to_process/MreB/Label Image 10-1_corrected.tif"

label = 236"""
path='/home/aurelienb/Desktop/tmp/cha/PonA/Label Image 10-1_corrected.tif'
label=156
upsampling_factor=5
stack = tifffile.imread(path)

theory_length=9

mask = stack[-1]==label
plt.figure()
plt.imshow(mask)

width,length = cell_dimensions_skel(mask,plot_in_context=True,upsampling_factor=upsampling_factor)

print("width, length:",width,length)

import matplotlib.pyplot as plt

from skimage.morphology import medial_axis
from skimage.measure import find_contours

from scipy.ndimage import gaussian_filter, zoom, median_filter

from skimage.draw import polygon

from skimage.graph import route_through_array
from skimage.morphology import binary_erosion, disk
import tifffile
from dl_for_mic.morphology_advanced import extract_roi, prolongate_skel, get_skel_extrema, unzoom_skel

width_percentile = 75
plot_single = True
plot_in_context = False

margin = 2*upsampling_factor
submask_coords, submask = extract_roi(mask, margin = margin)

submask_eroded = binary_erosion(submask)
new_img = zoom(gaussian_filter(submask_eroded.astype(float),sigma=0.8),
               upsampling_factor)

poly = find_contours(new_img/new_img.max(),level=0.5)[0]

rr, cc = polygon(poly[:, 0], poly[:, 1], new_img.shape)
out = np.zeros_like(new_img)
out[rr, cc] = 1

# extracts the skeleton on the processed image
skel, _ = medial_axis(out, return_distance = True)
_, dist = medial_axis(zoom(submask.astype(int),upsampling_factor).astype(int), return_distance = True)
# factor 2 because measures distance to an edge
cell_widths = 2*dist[skel>0]/upsampling_factor
cell_width = np.percentile(cell_widths, width_percentile)
print('new cell width',cell_width)

plt.figure()
plt.subplot(321)
plt.title('Distance transform')
plt.imshow(dist)
plt.subplot(322)
plt.title('skeleton')
plt.imshow(skel)
plt.subplot(323)
plt.title('zoomed')
plt.imshow(new_img)
plt.subplot(324)
plt.title('original')
plt.imshow(submask)
plt.subplot(325)
plt.imshow(out)

x_refs, y_refs = get_skel_extrema(skel)

skel = prolongate_skel(skel, [x_refs[0],y_refs[0]], 
                       neighbour_dist=6*upsampling_factor)
skel = prolongate_skel(skel, [x_refs[1],y_refs[1]],
                       neighbour_dist=6*upsampling_factor)

submask_zoomed = zoom(submask.astype(int),upsampling_factor)


skel = np.logical_and(submask_zoomed==1,skel).astype(int)

if plot_single:
    plt.figure()
    plt.imshow(submask_zoomed)
    xskel, yskel = np.where(skel>0)
    plt.plot(yskel,xskel,"o",color="k")
skel_unzoomed = unzoom_skel(skel, upsampling_factor)
skelf =  medial_axis(skel_unzoomed, return_distance = False)

    
if plot_in_context:
    xskel, yskel = np.where(skelf>0)
    plt.plot(yskel-margin+submask_coords[1],xskel-margin+submask_coords[0],
             "o",markersize=0.5,color="k")

x_0, y_0 = get_skel_extrema(skelf)
try:
    start = x_0[0], y_0[0]
except:
    plt.figure()
    plt.imshow(mask)
    print(np.count_nonzero(mask))
    print(np.where(mask))
    raise ValueError()
end = x_0[1], y_0[1]
skelf[skelf==0] = 100
path, cell_length = route_through_array(skelf.astype(float), start, end ,
                                 geometric=True)
from scipy.ndimage import convolve
from scipy.ndimage import label as labelf
def remove_forks(skel):
    connectivity = convolve(skel.astype(int),np.ones((3,3)))*skel.astype(int)
    
    connectivity[connectivity>3]=0
    labs,nlabs=labelf(connectivity,structure=np.ones((3,3)))
    counts=[np.count_nonzero(labs==w+1) for w in range(nlabs)]
    final_index = counts.index(max(counts))+1
    skel_final = (labs==final_index).astype(int)
    plt.figure()
    plt.subplot(121)
    plt.imshow(connectivity)
    plt.subplot(122)
    plt.imshow(skel_final)
remove_forks(skel)