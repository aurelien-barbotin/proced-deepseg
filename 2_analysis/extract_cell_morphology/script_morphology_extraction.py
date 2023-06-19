# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 09:30:21 2023

@author: proced_user
"""

from dl_for_mic.morphology_advanced import extract_morphology_from_movie
import os

datapath="to_process/"
if not os.path.isdir(datapath):
    os.mkdir(datapath)

pixel_size=float(input("Please enter the pixel size in µm then press enter: "))
"""repetition_keyword= input('''(optional) If this data has several replicates, please specify \
the keyword for replicate nr (exemple in test_rep1.tif, enter 'rep'). Otherwise just press enter ''')"""
extract_morphology_from_movie(datapath,pixel_size=pixel_size, rep_keyword = None)