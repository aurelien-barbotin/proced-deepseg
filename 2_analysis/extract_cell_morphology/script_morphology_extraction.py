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

extract_morphology_from_movie(datapath)