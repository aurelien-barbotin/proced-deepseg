#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 09:43:44 2022

@author: aurelien
"""

import cv2

import numpy as np

# Generates a rectangle
im = np.zeros((20,20)).astype(np.uint8)
im[5:-5,2:-2]=255

im = im.astype(np.uint8)
cnt,hierarchy = cv2.findContours(im, 1, 2)
cnt = np.vstack(cnt).squeeze()

# returns the min area rectangle: ( (x_centre, y_centre), (x_size, y_size), rotation_angle )
rect = cv2.minAreaRect(cnt)
box = cv2.boxPoints(rect) 
box = np.int0(box)

# converts image to BGR (=3 color channels) for display purpose
im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
cv2.drawContours(im,[box],0,(0,0,255),1)
cv2.imshow("example rectangle with overlay",im)

