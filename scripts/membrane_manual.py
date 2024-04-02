#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:52:45 2024

@author: aurelienb
"""

import czifile
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu

plt.close('all')
path="/home/aurelienb/Data/2024_03_13_morpho/FM4-64_expo/Image 1.czi"

img = czifile.imread(path).squeeze()
msk=img>threshold_otsu(img)
plt.figure()
plt.subplot(121)
plt.imshow(msk)
plt.subplot(122)
plt.imshow(img)