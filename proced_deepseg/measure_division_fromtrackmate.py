#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 13:31:51 2023

@author: aurelienb

Reads from edges export in trackmate
"""

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from proced_deepseg.morphology_advanced import get_dimensions_rect
from tifffile import imread

def find_next_division(root,G, return_path=False):
    """Given a graph G and a node root, finds the nodes corresponding to the next 
    division"""
    level = 0
    current = [root]
    if return_path:
        path=[root]
    while len(current)!=0:
        level+=1
        successors = list(G.successors(current[0]))
        if len(successors)>1:
            if return_path:
                return successors,path
            else:
                return successors
        # print("level",level)
        current = successors
        path.extend(current)
    if return_path:
        return [],[]
    else:
        return []

    
def get_predecessor(suc,G):
    """From a list of successors, checks they all ahve same predecessor
    and returns its unique ID"""
    preds = [list(G.predecessors(d)) for d in suc]
    if len(preds)==0:
        return preds
    out = []
    for p in preds:
        assert len(p)==1
        out.append(p[0])
    out = np.asarray(out)
    assert((out==out[0]).all())
    return out[0]

def find_graph_level(root_node,G):
    """Finds the depth of a graph G starting from a particular node root_node.
    Returns the depth as well as all nodes involved"""
    children_next = set()
    searched_nodes = set()
    children_current = [root_node]
    
    level = 0
    while len(children_current) != 0:
    
    
        for n in children_current:
            searched_nodes.add(n)
    
            for s in G.successors(n): #exchange with predecessors to get parents
                children_next.add(s)
    
            children_next = children_next.difference(searched_nodes)
    
        children_current = list(children_next)
    
        level += 1
    return level, searched_nodes

def graph_cleanup(G, minsize=5):
    """Removes branches in a graph G if they contain less than minsize elements"""
    nodes_split = [node for node, in_degree  in G.out_degree if in_degree>1]
    
    to_remove=  []
    for node in nodes_split:
        successors = G.successors(node)
        for successor in successors:
            depth, children = find_graph_level(successor,G)
            if depth<minsize:
                to_remove.extend(list(children))

    to_remove = list(set(to_remove))
    for node_to_remove in to_remove:
        G.remove_node(node_to_remove)

def build_track_graph(df,trn,minsize=3):
    """Given a tracking (edges) Dataframe and an edge number, builds the track graph
    """
    
    nrem = 3
    track_id =  df['TRACK_ID'].values[nrem:].astype(int)
    times = df['EDGE_TIME'].values[nrem:].astype(float)
    
    source_id=df['SPOT_SOURCE_ID'].values[nrem:]
    target_id=df['SPOT_TARGET_ID'].values[nrem:]
    all_labels = df['LABEL'].values[nrem:]
    labels = all_labels[track_id==trn]
    
    graph = nx.DiGraph()
    
    nodes_candidates = []
    for j in range(len(labels)):
        tt = times[track_id==trn][j]
        tpl = (source_id[track_id==trn][j],target_id[track_id==trn][j])
        
        data = (tpl[0],tpl[1],{"frame":tt})
        graph.add_edges_from([data])
        nodes_candidates.append((data[0],{"frame":tt-0.5}))
        nodes_candidates.append((data[1],{"frame":tt+0.5}))
    # nodes_candidates = list(set(nodes_candidates))
    graph.add_nodes_from(nodes_candidates)
    
    graph_cleanup(graph,minsize=minsize)
    return graph

def get_division_speeds(path, minsize=3, return_track=False):
    """reads a csv file from trackmate (edges), calculates the corresponding 
    graph and measures division time. Returns frames pairs (frame for div 1, time until division)"""
    df = pd.read_csv(path)
    
    nrem = 3
    # Loading data
    track_id =  df['TRACK_ID'].values[nrem:].astype(int)
    
    track_vals = np.unique(track_id)
    
    # building the graph
    out_divtimes = {}
    all_tracks=[]
    for trn in track_vals:
        
        graph = build_track_graph(df, trn,minsize=minsize)
        # in node: nombre qui pointent
        root_node = [node for node, in_degree in graph.in_degree if in_degree==0]
        if len(root_node)>1:
            plt.figure()
            nx.draw(graph,pos=nx.planar_layout(graph))
            print(trn)
            
        assert len(root_node)==1
        root_node = root_node[0]
        
        # from https://stackoverflow.com/questions/69465397/iterating-over-nodes-of-a-networkx-digraph-in-order

        all_divs=[]
        divs=[root_node]
        sublevel = 0
        all_times=[]
        while len(divs)>0:
            print('Sublevel',sublevel)
            divs_tmp_list=[]
            for div in divs:
                divs_tmp = find_next_division(div,graph, return_path=return_track)
                if return_track:
                    divs_tmp, track = divs_tmp
                if len(divs_tmp)>0:
                    last_before_split = get_predecessor(divs_tmp,graph)
                    t_root = graph.nodes[div]['frame']
                    t_last = graph.nodes[last_before_split]['frame']
                    if return_track and t_root>0:
                        all_tracks.append(track)
                    ts = (t_root,t_last-t_root)
                    all_times.append(ts)
                    divs_tmp_list.extend(divs_tmp)
        
            divs = divs_tmp_list
            all_divs.append(divs)
            
            sublevel+=1
        # eliminate first division
        out_divtimes[trn] = all_times[1:]
    if return_track:
        return out_divtimes, all_tracks
    else:
        return out_divtimes

def merge_times_dict(td):
    outx = []
    outy = []
    for k in td.keys():
        pairs = td[k]
        for pair in pairs:
            outx.append(pair[0])
            outy.append(pair[1])
    return outx, outy
import glob

process_division_times = False
path="""/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/\
microscopy/NIKON/Dimitri/230428 contraste phase/ilastik images/masks/edges/"""
if process_division_times:
    
    files = glob.glob(path+"*.csv")
    
    fig,axes = plt.subplots(2,5,sharex=True,sharey=True)
    axes=axes.ravel()
    
    for j, file in enumerate(files):
        
        ax = axes[j]
        name = file.split('/')[-1].strip('result ')[:-4]
        ax.set_title(name)
    
        times_dict = get_division_speeds(file,minsize=5)
        x,y=merge_times_dict(times_dict)
        ax.scatter(x,y)
        lims = np.arange(20,60)
        ax.plot(lims,60-lims,'k--')
        ax.set_ylabel('Division time (min)')
        ax.set_xlabel('Time (min)')
     
        out = {}
        out["t"] = x
        out[name+"division_time"] = y
        df = pd.DataFrame(out)
        df.to_csv(path+"division_times/"+name+"_division_times.csv")
        df.to_excel(path+"division_times/"+name+"_division_times.xlsx")
    
    fig.suptitle("Cell division times")
    # fig.savefig(path+"summary_doubling_times.png")
    df=pd.DataFrame(out)
    
    """
    for k in times_dict.keys():
        for tup in times_dict[k]:
            if tup[0]>44:
                print(k)"""

from skimage.morphology import closing
def isnr(st):
    try:
        u = float(st)
        return True
    except:
        return False
    
def measure_cellarea_before_division(path_stack,path_spots,path_edges, psize=1,
                                     savename=None, tol=10):
    # tol: tolerance in pixels. Eliminates everything too close to edge
    stack = imread(path_stack)
    stack_detection=np.array([closing(w,footprint=np.ones((3,3))) for w in stack])
    
    
    # spots
    df_spots = pd.read_csv(path_spots)
    xspot=df_spots["POSITION_X"].values
    for j in range(10):
        if isnr(xspot[j]):
            nrem=j
            break
    xspot=df_spots["POSITION_X"].values[nrem:].astype(float)
    yspot=df_spots["POSITION_Y"].values[nrem:].astype(float)
    id_fromspot = df_spots["ID"].values[nrem:].astype(int)
    medians=df_spots['MEDIAN_INTENSITY_CH1'].values[nrem:].astype(float).astype(int)
    frames_fromspot = df_spots["FRAME"].values[nrem:].astype(int)
    
    # edges
    df = pd.read_csv(path_edges)
    
    # Loading data
    track_id =  df['TRACK_ID'].values[nrem:].astype(int)
    track_vals = np.unique(track_id)
    
    out_dividing = []
    # Finds dividing cells
    for trn in track_vals:
        graph = build_track_graph(df, trn)
        # in node: nombre qui pointent
        root_node = [node for node, in_degree  in graph.in_degree if in_degree==0]
        if len(root_node)>1:
            plt.figure()
            nx.draw(graph,pos=nx.planar_layout(graph))
            print(trn)
            
        assert len(root_node)==1
        root_node = root_node[0]
        
        divs=[root_node]
        sublevel = 0
        while len(divs)>0:
            # print('Sublevel',sublevel)
            divs_tmp_list=[]
            for div in divs:
                divs_tmp = find_next_division(div,graph)
                if len(divs_tmp)>0:
                    
                    last_before_split = get_predecessor(divs_tmp,graph)
                    msk = id_fromspot==int(last_before_split)
                    # print(np.count_nonzero(msk),last_before_split)
                    assert np.count_nonzero(msk)==1
                    xl,yl = xspot[msk][0], yspot[msk][0]
                    frame = frames_fromspot[msk][0]
                    index_instack = medians[msk][0]
                    
                    if not (xl<tol or yl<tol or xl>stack.shape[2]-tol or yl>stack.shape[1]-tol):
                        out_dividing.append({"frame":frame,
                                             "index_instack": index_instack,
                                             "xl":xl,
                                             "yl":yl})
                        divs_tmp_list.extend(divs_tmp)
                        
                        if stack_detection[frame,int(yl),int(xl)]!=medians[msk][0]:
                            print('warning, mismatch',index_instack,medians[msk][0])
                        if index_instack==0 or stack_detection[frame,int(yl),int(xl)]!=medians[msk][0]:
                            print("bb",divs_tmp,frame,last_before_split)
                            print(xl,yl,index_instack)
                            print('cc')
                            plt.figure()
                            plt.imshow(stack[frame])
                            
            divs = divs_tmp_list
            sublevel+=1
            
    # calculate morphology
    for j in range(len(out_dividing)):
        frame,index_instack = out_dividing[j]["frame"],out_dividing[j]["index_instack"]
        img = stack[frame]
        msk=img==index_instack
        width,length = get_dimensions_rect(msk)
        
        out_dividing[j]["width"]=width
        out_dividing[j]["length"]=length
        out_dividing[j]["area"]=np.count_nonzero(msk)
        if out_dividing[j]["area"]>1000:
            print(index_instack,frame)
    
    sizepairs={'frame':[],
               'area [µm2]':[]}
    for j in range(len(out_dividing)):
        div = out_dividing[j]
        sizepairs['frame'].append(div['frame'])
        sizepairs['area [µm2]'].append(div['area'])
    df = pd.DataFrame(sizepairs)
    if savename is not None:
        df.to_excel(savename)
    return df



def build_lineage(path_stack,path_spots,path_edges):
    
    stack = imread(path_stack)
    
    nrem = 3
    # spots
    df_spots = pd.read_csv(path_spots)
    xspot=df_spots["POSITION_X"].values[nrem:].astype(float)
    yspot=df_spots["POSITION_Y"].values[nrem:].astype(float)
    id_fromspot = df_spots["ID"].values[nrem:].astype(int)
    frames_fromspot = df_spots["FRAME"].values[nrem:].astype(int)
    
    # edges
    df = pd.read_csv(path_edges)
    
    # Loading data
    track_id =  df['TRACK_ID'].values[nrem:].astype(int)
    track_vals = np.unique(track_id)
    
    # only first and lastframes. list of lists, each item is:
    # [label_in_first_frame,[labels corresponding in last frame]]
    
    lineages=[]
    out_ims = []
    final_image = np.zeros_like(stack[-1]).astype(int)
    growth_image=np.zeros_like(stack[-1]).astype(float)
    
    growth_pairs=[]
    
    for j,trn in enumerate(track_vals):
        # finds the root node of this portion of graph
        graph = build_track_graph(df, trn)
        # in node: nombre qui pointent
        root_node = [node for node, in_degree  in graph.in_degree if in_degree==0]
        if len(root_node)>1:
            plt.figure()
            nx.draw(graph,pos=nx.planar_layout(graph))
            print(trn)
            
        assert len(root_node)==1
        root_node = root_node[0]
        
        
        msk = id_fromspot==int(root_node)
        assert np.count_nonzero(msk)==1
        ref_frame=frames_fromspot[msk][0]
        # ici c'est des cellules qui apparaissent sur les bords
        if ref_frame!=0:
            continue

        xl,yl = xspot[msk][0], yspot[msk][0]
        index_instack = stack[ref_frame,int(yl),int(xl)]
        index_firstframe = index_instack
        
        lineages.append([index_instack,[]])
        out_ims.append([stack[0]==index_instack,np.zeros_like(stack[-1])])
        descendants = nx.descendants(graph, root_node)

        for node_desc in descendants:
            msk = id_fromspot==int(node_desc)
            assert np.count_nonzero(msk)==1
            frame=frames_fromspot[msk][0]
            if frame==frames_fromspot.max():
                xl,yl = xspot[msk][0], yspot[msk][0]
                index_instack = stack[frame,int(yl),int(xl)]
                lineages[j][1].append(index_instack)
                out_ims[-1][1]+=(stack[-1]==index_instack).astype(np.uint8)
    
        final_image+=(j+1)*out_ims[-1][1]
        growth_rate = np.count_nonzero(out_ims[-1][1])/np.count_nonzero(stack[0]==index_firstframe)
        growth_image[out_ims[-1][1]>0]= growth_rate
        
        growth_pairs.append([np.count_nonzero(stack[0]==index_firstframe),growth_rate])
        
    ff=(final_image%20).astype(float)
    growth_image[final_image==0]=np.nan
    ff[final_image==0]=np.nan
    plt.figure()
    plt.subplot(121)
    plt.imshow(ff,cmap="tab20")
    plt.title('individual colonies')
    plt.subplot(122)
    plt.imshow(growth_image)
    plt.colorbar()
    plt.title('Relative growth')
    
    growth_pairs =np.asarray(growth_pairs)
    plt.figure()
    plt.scatter(growth_pairs[:,0],growth_pairs[:,1])
    
if __name__=='__main__':
    
    plt.close('all')
    
    # csp -
    path_stack1="""/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/\
microscopy/NIKON/Dimitri/230428 contraste phase/ilastik images/masks/wt csp - stab-crop_cp_masks.tif"""
    path_edges1 = "/home/aurelienb/Desktop/tmp/dimdim/wt csp-/edges_wt-_stab_crop.csv"
    path_spots1="/home/aurelienb/Desktop/tmp/dimdim/wt csp-/spots_wt-_stab_crop.csv"

    # csp+
    path_edges2="/home/aurelienb/Desktop/tmp/dimdim/wt csp+/edges_wt csp+_stab_crop.csv"
    path_spots2="/home/aurelienb/Desktop/tmp/dimdim/wt csp+/spots_wt csp+_stab_crop.csv"
    path_stack2="""/run/user/1000/gvfs/smb-share:server=data.micalis.com,share=proced/\
microscopy/NIKON/Dimitri/230428 contraste phase/ilastik images/masks/wt csp + \
stab-crop-1 corrige_cp_masks.tif"""
    
    measure_cellarea_before_division(path_stack2, path_spots2, path_edges2)
    plt.title('csp+')
    
    build_lineage(path_stack2, path_spots2, path_edges2)
    plt.title('csp+')
    build_lineage(path_stack1, path_spots1, path_edges1)
    plt.title('csp-')
    
    """
    measure_cellarea_before_division(path_stack1, path_spots1, path_edges1)
    plt.title('csp -')
    plt.savefig('/home/aurelienb/Desktop/tmp/dimdim/csp-.png')
    measure_cellarea_before_division(path_stack2, path_spots2, path_edges2)
    plt.title("csp+")
    plt.savefig('/home/aurelienb/Desktop/tmp/dimdim/csp+.png')
    # deliberate mistake
    measure_cellarea_before_division(path_stack1, path_spots2, path_edges2)"""
    