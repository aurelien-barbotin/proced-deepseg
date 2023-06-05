#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 17:21:39 2023

@author: aurelienb
"""
import delta
import matplotlib.pyplot as plt
file_path = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/ZEISS_ELYRA7/Joseph/2023_06_02/substack/Substack (1-360-10).tif"

# reload, analysis
reader = delta.utilities.xpreader(file_path,use_bioformats=True)
processor = delta.pipeline.Pipeline(reader, reload=True)

lin = processor.positions[0].rois[0].lineage
first_cells = lin.cellnumbers[0]

plt.figure()
for cell in lin.cells:
    if cell['id'] not in first_cells:
        plt.plot(cell['frames'],cell['length'],color=[.5,.5,.5])

for cnb in first_cells:
    cell = lin.cells[cnb]
    plt.plot(cell['frames'],cell['length'])

plt.xlabel('frame #')
plt.ylabel('length (pixels)')

import numpy as np

# Last labels frame:
labels = processor.positions[0].rois[0].label_stack[-1]

# Initialize color image (all light gray)


def which_first(lineage, cell_nb, first_cells):

    # Get cell dict:
    cell = lineage.cells[cell_nb]

    # If orphan or reached one of the first two cells:
    if cell['mother'] is None or cell['mother'] in first_cells:
        return cell['mother']

    # Otherwise go up the lineage tree:
    else:
        return which_first(lineage, cell['mother'], first_cells)

color_image = np.zeros_like(labels,dtype=float)

# Go over cells in last frame:
for cnb in lin.cellnumbers[-1]:

    # Which initial cell is ancestor?
    ancestor = which_first(lin, cnb, first_cells)

    if ancestor is not None:
        color_image[labels==cnb+1]=ancestor
        
color_image
color_image[labels==0]=np.nan
plt.figure()
plt.subplot(121)
plt.imshow(labels>0)
plt.subplot(122)
plt.imshow(color_image,cmap="tab20")
plt.show()