
"""
This script simply runs the DeLTA pipeline on a movie.

Please download the latest models and evaluation movies first with
delta.assets.download_assets().

In order to use on bioformats-compatible files such .nd2, .czi, .oib, ome-tiff
 etc files please install python-bioformats first.

@author: jeanbaptiste
"""

import delta
import glob
from tifffile import imread,imwrite
import numpy as np
import os

# Load config ('2D' or 'mothermachine'):
delta.config.load_config(presets="2D")

# Use eval movie as example (or replace by None for interactive selection):
file_path = "to_process/"
files = glob.glob(file_path+"*.tif")

for file in files:
    
    # reformat to avoid bioformats
    stack = imread(file).astype(float)
    stack-=stack.min()
    stack=255*stack/stack.max()
    stack=stack.astype(np.uint8)
    new_path = file[:-4]
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    to_clear = []
    for j,im in enumerate(stack):
        name = new_path+"/frame_{:04d}.tif".format(j)
        to_clear.append(name)
        imwrite(name,im)
    # new_path="to_process\del-gacS_rep1/"
    # Init reader (use bioformats=True if working with nd2, czi, ome-tiff etc):
    xpreader = delta.utils.xpreader(new_path,use_bioformats=False,
                                    prototype='frame_%04d.tif',
                                    fileorder='t',)
    
    # Init pipeline:
    xp = delta.pipeline.Pipeline(xpreader)
    
    # Run it (you can specify which positions, which frames to run etc):
    xp.process()
    
    for tc in to_clear:
        os.remove(tc)
"""
from scipy.io import loadmat
matpath="/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/ZEISS_ELYRA7/Joseph/2023_06_02/substack/Substack (1-360-10)_delta_results/Position000000.mat"
mat = loadmat(matpath)
segmented=mat['res'][0,0][0,0][0]
from tifffile import imsave
imsave(matpath[:-4]+".tif",segmented)
"""

