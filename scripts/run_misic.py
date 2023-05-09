#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 10:06:26 2023

@author: aurelienb

Example script for misic. To run in 'misic' environment.
"""

from misic.misic import *
from misic.extras import *
from skimage.io import imsave,imread
from skimage.transform import resize,rescale

import matplotlib.pyplot as plt
path = '/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/proced/5- User Exchange folders/Aurelien_MerveNur/Microscopy acq_Growth curve/230406/'
filename = path+'subframe.tif'

gamma=0.2
# read image using your favorite package
im = imread(filename)
imsave(filename[:-4]+"_gamma_correcttion.tif",im**gamma)

sr,sc = im.shape

# Parameters that need to be changed
## Ideally, use a single image to fine tune two parameters : mean_width and noise_variance (optional)

#input the approximate mean width of microbe under consideration
mean_width = 12

# compute scaling factor
scale = (10/mean_width)

# Initialize MiSiC
mseg = MiSiC()

# preprocess using inbuit function or if you are feeling lucky use your own preprocessing
im = rescale(im,scale,preserve_range = True)

plt.figure()
plt.subplot(121)
plt.imshow(im/im.max())

im=im**gamma

plt.subplot(122)
plt.imshow(im/im.max())
# add local noise
img = add_noise(im,sensitivity = 0.013,invert = True)

# segment
yp = mseg.segment(img,invert = True)
yp = resize(yp,(sr,sc))

# body = resize(yp[:,:,0],[sr,sc])
# contours = resize(yp[:,:,1],[sr,sc])

# watershed based post processing (optional)
# yp = postprocess_ws(img,yp)

# save 8-bit segmented image and use it as you like
plt.figure()
plt.subplot(121)
plt.imshow(img)
plt.subplot(122)
plt.imshow(yp)

# imsave('segmented.tif', yp.astype(np.uint8))
