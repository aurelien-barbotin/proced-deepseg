#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 10:01:04 2023

@author: aurelienb

Scripts used to annotate tracking videos. The main method is make_tracking_video
"""

from dl_for_mic.measure_division_fromtrackmate import (measure_cellarea_before_division,
                                   build_lineage, get_division_speeds,get_division_speeds)

import glob
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tifffile import imread, imwrite
import cv2
from skimage import measure

def update_stack(stacknew,stack,lablist):
    out_stack = stacknew
    for ll in lablist:
        fr, lab = ll
        out_stack[fr,stack[fr]==lab] = 2
    return out_stack

def get_boundingbox(track,spots,shape, expansion_factor=1.2):
    """From track list"""
    out=[]
    bboxes = []
    for tr in track:
        subdf = spots[spots['ID']==tr]
        assert len(subdf)==1
        lab=int(float(subdf['MEDIAN_INTENSITY_CH1'].values[0]))
        frame=int(subdf['FRAME'].values[0])
        
        xpos = float(subdf['POSITION_X'].values[0])
        ypos = float(subdf['POSITION_Y'].values[0])
        radius = float(subdf['RADIUS'].values[0])*expansion_factor
        bbox = [
            (int(max(0,ypos-radius)), int(max(0,xpos-radius))),
            (int(min(shape[0],ypos+radius)),int(min(shape[1],xpos+radius)))
                ]
        bboxes.append((frame,bbox))
        out.append((frame,lab))
    return out, bboxes

def collapse_bboxlist(boxlist):
    """On a list of boxes, calculates the englobing box"""
    frames=[w[0] for w in boxlist]
    boxes = np.array([w[1] for w in boxlist])
    mins=boxes[:,0].min(axis=0).astype(int)
    maxs=boxes[:,1].max(axis=0).astype(int)
    new_box=[[frames[j],[mins,maxs]]for j in range(len(frames))]
    return new_box

def make_tracking_video(stack_original,stack_labels,path_edges,path_spots):
    """Makes an annotated tracking video.
    Parameters:
        stack_original (ndarray): 3d (time, x, y). Typically phase-contrast image
        stack_labels (ndarray): 3d (time, x, y). Segmented version of stack_original.
            dtype is integer
        path_edges (str): path to csv file of edges generated with Trackmate on 
            stack_labels
        path_spots (str): path to csv file of spots generated with Trackmate on 
            stack_labels
    Returns:
        ndarray: a 4D (t, x, y, 3) array annotated with cell outlines and cell 
        divisions used for doubling times measurements.
        """
    divs_speeds, tracks=get_division_speeds(path_edges,return_track=True)
    out=[]
    for k in divs_speeds.keys():
        divevs = divs_speeds[k]
        for pair in divevs:
            out.append(pair)
            
    df_spots = pd.read_csv(path_spots)
    
    all_bboxes=[]
    for j,track in enumerate(tracks):
        print('track {}'.format(j))
        lablist,bboxes = get_boundingbox(track, df_spots,stack_labels.shape[1:])
        all_bboxes.append(bboxes)
    stack_fordisplay = np.repeat(stack_original[:,:,:,np.newaxis],3,axis=3).astype(float)
    stack_fordisplay -= stack_fordisplay.min()
    stack_fordisplay/=stack_fordisplay.max()
    stack_fordisplay = (255*stack_fordisplay).astype(np.uint8)

    for bboxes_tracks in all_bboxes:
        bbox_collapsed=collapse_bboxlist(bboxes_tracks)
        # bbox_collapsed=bboxes_tracks
        for bboxes in bbox_collapsed:
            frame,bbox = bboxes
            cv2.rectangle(stack_fordisplay[frame],tuple(bbox[0][::-1]),tuple(bbox[1][::-1]),
                          (255,0,255),1)

    all_contours=[]
    for j in range(stack_labels.shape[0]):
        img =stack_labels[j]
        label_values = np.unique(img)[1:]
        frame_contours=[]
        for lab in label_values:
            r=(img==lab).astype(np.uint8)
            contours = measure.find_contours(r, 0.8)
            # assert len(contours)==1
            contours=contours[0]
            frame_contours.append(np.array(contours))
        cont_frame=np.round(np.concatenate(frame_contours,axis=0), 
                            decimals=0).astype(int)
        all_contours.append(cont_frame)
        stack_fordisplay[j,cont_frame[:,0],cont_frame[:,1],1]=255
    return stack_fordisplay

if __name__=="__main__":
    path = "/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/microscopy/NIKON/Dimitri/230717 mura rep 4/compil/"
    path_original = path+"1 wt csp- iptg+ treated.tif"
    files_original = glob.glob(path+"*.tif")
    nrs = [int(w.split('/')[-1][0]) for w in files_original]
    subfolder="fichiers analyse/"
    
    folders = glob.glob(path+subfolder+"*/")
    foldnrs=[int(w.split(subfolder)[-1][0]) for w in folders]
    
    for j in range(len(files_original)):
        print('Processing file {}'.format(j))
        nr = nrs[j]
        file_original = files_original[j]
        folder = folders[j]
        path_stack=glob.glob(folder+'*.tif')[0]
        excels=glob.glob(folder+'*.csv')
        path_edges=list(filter(lambda x: "edges" in os.path.split(x)[-1],excels))[0]
        path_spots=list(filter(lambda x: "spots" in os.path.split(x)[-1],excels))[0]
        
        stack_original = imread(file_original)
        stack_labels = imread(path_stack)
        out_stack = make_tracking_video(stack_original,stack_labels,path_edges,path_spots)
        imwrite(path+'../illustration_'+str(nr)+".tif",out_stack)
