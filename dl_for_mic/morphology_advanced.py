#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:57:33 2022

@author: aurelienb

https://www.microbej.com/doc/
main interface/Bacteria/Morphologies/contour
"""

import numpy as np
import matplotlib.pyplot as plt

import cv2
from skimage.morphology import medial_axis
from skimage.measure import find_contours

from scipy.ndimage import gaussian_filter, zoom, convolve
from tifffile import imread
from scipy.stats import linregress

from skimage.draw import polygon, line

from skimage.graph import route_through_array
import glob
import os
import tifffile
import pandas as pd

def extract_roi(mask, margin=8):
    xx,yy=np.where(mask==1)
    xmin = xx.min()
    xmax = xx.max()
    ymin = yy.min()
    ymax = yy.max()
    
    out = np.zeros((xmax-xmin+2*margin, ymax-ymin+2*margin))
    out[margin:-margin,margin:-margin ] = mask[xmin:xmax,ymin:ymax]
    return (xmin,ymin,xmax,ymax), out

def get_skel_extrema(skel):
    """Given a skeletonized image, finds the position of its extremities
    (hopefully only 2)
    Parameters:
        skel (ndarray): skeletonized image
    Returns:
        ndarray: coordinates of extremities of the skeleton"""
    if skel.dtype==bool:
        skel = skel.astype(int)
    connectivity = convolve(skel.astype(int),np.ones((3,3)))*skel.astype(int)
    return np.array(np.where(connectivity==2))

def sort_list_fromref(to_sort, ref):
    return [x for _, x in sorted(zip(ref,to_sort))]

def get_neighbouring_points(xs, ys, xy_ref, dist = 30):
    """Finds all the points within a list of coordinates that are in the vicinity
    of another point
    Parameters:
        xs (list): x coordinates
        ys (list): y coordinates
        xy_ref (list): (x,y) coordinates of the centre 
        dist (float): distance within which points are considered to be in the 
            vicinity of the ref
    Returns:
        list: xs,ys: list of coordinates of points in the neighbourhood of the ref"""
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    dists = np.sqrt((xs-xy_ref[0])**2 + (ys - xy_ref[1])**2)
    
    msk1 = dists<dist
    xs = xs[msk1]
    ys = ys[msk1]
    dists = dists[msk1]
    
    xs = np.array(sort_list_fromref(xs,dists))
    ys = np.array(sort_list_fromref(ys,dists))
    return xs,ys



def prolongate_skel(skel, xy_ref, t_ext = -2, neighbour_dist = 30):
    """Prolongates a skeleton at one of its extremities using linear interpolation.
    Parameters:
        skel (ndarray): the skeletton in int format
        xy_ref (list): x, y values of the extremum from which we want to prolongate
        t_ext (int): has to be negative, how far we want to prolongate
        beighbour_dist (float): distance to the ref point within which we look
            for neighbours
    Returns:
        ndarray: the prolongated skeleton"""
    xs, ys = (skel>0).nonzero()
    xn, yn = get_neighbouring_points(xs,ys,xy_ref, dist = neighbour_dist)
    txn = np.linspace(0,1,xn.size)
    outlinx = linregress(txn,xn)
    outliny = linregress(txn,yn)
    
    r1 = outlinx.slope*t_ext + outlinx.intercept
    c1 = outliny.slope*t_ext + outliny.intercept
    
    rr,cc = line(xy_ref[1], xy_ref[0], int(c1), int(r1))
    msk1 = np.logical_and(rr>=0,rr<skel.shape[1])
    msk2 = np.logical_and(cc>=0,cc<skel.shape[0])
    msk = np.logical_and(msk1, msk2)
    skel=skel.astype(int)
    skel[cc[msk],rr[msk]] = 2
    return skel

def unzoom_skel(skel_zoomed,factor):
    skel_unzoomed = skel_zoomed.reshape(-1,factor,
                         skel_zoomed.shape[1]//factor,factor).sum(axis=(-1,-3))
    return (skel_unzoomed>0)

def cell_dimensions_skel(mask, upsampling_factor = 5,
                         plot_in_context = True, plot_single=False, width_percentile = 90):
    """Measures dimensions of a rod-shaped mask using skeletonization.
    Parameters:
        mask (ndarray): binary mask, represents a rod-shaped bacteria which dimensions
            we are looking for
        upsampling_factor (int): Masks are upsampled by this factor to increase
            method precision. Higher coefficient yields slower but more accurate
            results.
        plot_in_context (bool): if Ture, plots the resulting skeleton
        plot_single (bool): if True, plots the upsampled image of the mask
            along its skeleton. Useful for debuging purpose
            width_percentile (int or float): defines the with as the n-th 
                percentile of all widths measured along the cell. Higher percentile
                means higher width for a given mask
    Returns:
        list: [cell_width, cell_length]"""

    margin = 2*upsampling_factor
    submask_coords, submask = extract_roi(mask, margin = margin)
    
    new_img = zoom(gaussian_filter(submask.astype(float),
                                   sigma=upsampling_factor*4/5),upsampling_factor)

    poly = find_contours(new_img/new_img.max(),level=0.5)[0]

    rr, cc = polygon(poly[:, 0], poly[:, 1], new_img.shape)
    out = np.zeros_like(new_img)
    out[rr, cc] = 1
    
    skel, dist = medial_axis(out, return_distance = True)
    # factor 2 because measures distance to an edge
    cell_widths = 2*dist[skel]/upsampling_factor
    cell_width = np.percentile(cell_widths, width_percentile)
    
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
    start = x_0[0], y_0[0]
    end = x_0[1], y_0[1]
    skelf[skelf==0] = 100
    path, cell_length = route_through_array(skelf.astype(float), start, end ,
                                     geometric=True)

    return cell_width, cell_length

def get_dimensions_rect(msk, plot=False):
    """Gets the width and length of a mask using minarea rectangle"""
    mask = msk.copy()
    mask = mask.astype(np.uint8)
    if np.count_nonzero(mask)<2:
        return 0
    cnt,hierarchy = cv2.findContours(mask, 1, 2)
    cnt = np.vstack(cnt).squeeze()
    
    # returns the min area rectangle: ( (x_centre, y_centre), (x_size, y_size), rotation_angle )
    rect = cv2.minAreaRect(cnt)
    if plot:
        box = cv2.boxPoints(rect) 
        box = np.int0(box)
        
        # converts image to BGR (=3 color channels) for display purpose
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(mask,[box],0,(0,0,255),1)
        cv2.imshow("mask and approximation",mask)
    return min(rect[1]), max(rect[1])

if __name__=='__main__':
    plt.close('all')
    path = "/home/aurelienb/Documents/Projects/2022_02_Louise/CCBS616_1_561.tif-labels.tif"
    path="/home/aurelienb/Documents/Projects/2022_02_Louise/resized_testim_labels.tif"
    img = imread(path)
    # img[img==43] = 0
    img = img[-1]
    nce = 78
    nce = 89
    widths = []
    lengths = []
    img_dsp = img.copy().astype(float)
    img_dsp[img_dsp==0]=np.nan
    plt.figure()
    plt.imshow(img_dsp, cmap="Set2")
    
    labels = np.unique(img).tolist()
    labels.pop(0)
    for nce in labels:
        mask = img==nce
        width, length = cell_dimensions_skel(mask,upsampling_factor=5)
        widths.append(width)
        lengths.append(length)
    
    lab = np.random.choice(labels)
    # lab=699
    width, length = cell_dimensions_skel(img==lab,upsampling_factor=5,plot_in_context=False,
                                         plot_single = True)
    
    plt.figure()
    plt.subplot(121)
    plt.hist(widths,bins=10)
    plt.xlabel("width [pixels]")
    plt.subplot(122)
    plt.hist(lengths,bins=10)
    plt.xlabel("length [pixels]")
    """plt.figure()
    plt.imshow(mask)"""
    

def extract_morphology_from_movie(datapath):
    """Given apath containing segmented movies, extracts cell morphology (width, length, area)
    using the rectangle method and saves results in an excel file"""
    files = glob.glob(datapath+"/*.tif")
    
    # each stack
    for nfile, file in enumerate(files):
        print('Processing file {}'.format(file.split(os.sep)[-1]))
        mask = tifffile.imread(file)
        nt, nx, ny = mask.shape
        
        all_dfs = []
        
        # time
        for j in range(nt):
            frame = mask[j]
            vals = np.unique(frame)
            if vals[0]!=0:
                raise ValueError('No background in this dataset?')
            vals = vals[1:]
            out_dict = {"widths":[],
                        "lengths":[],
                        "frame nr":[],
                        "index":[],
                        "areas":[],
                        "area_all":[],
                        'nr_cells':[]}
            # individual cell within a frame
            a1 = np.count_nonzero(frame>0)
            a2=len(np.unique(frame))-1
            for val in vals:
                msk = frame==val
                wt, lt = get_dimensions_rect(msk)
                out_dict["widths"].append(wt)
                out_dict["lengths"].append(lt)
                out_dict["frame nr"].append(j)
                out_dict["index"].append(val)
                out_dict["areas"].append(np.count_nonzero(msk))
                
                out_dict["area_all"].append(a1)
                out_dict["nr_cells"].append(a2)
            all_dfs.append(pd.DataFrame(out_dict))
        
        df_final = pd.concat(all_dfs)
        
        excel_name = file[:-4]+".xlsx"
        df_final.to_excel(excel_name)
        
        grp = df_final.groupby(['frame nr'])
        means = grp.mean()
        stds = grp.std()
        maxs = grp.max()
        fr = grp.groups.keys() #to test
        # export summaries
        out={}
        out["frame nr"] = fr
        out["width mean"] = means['widths']
        out["width std"] = stds['widths']
        
        out["length mean"] = means['lengths']
        out["length std"] = stds['lengths']
        
        out["cell area mean"] = means['areas']
        out["cell area std"] = stds['areas']
        
        # no need to take the means as they all have the same value
        out["All cells area"] = means['area_all']
        out["nr cells"] = means['nr_cells']
        
        df = pd.DataFrame(out)
        df.to_excel(file[:-4]+"_summaries.xlsx")

