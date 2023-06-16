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

plt.close('all')
path = "/home/aurelienb/edges_comM surexprime bip+ stab-crop_cp_masks.csv"
def find_next_division(root,G):
    level = 0
    current = [root]
    while len(current)!=0:
        level+=1
        successors = list(G.successors(current[0]))
        if len(successors)>1:
            return successors
        # print("level",level)
        current = successors
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

def get_division_speeds(path, minsize=3):
    """reads a csv file from trackmate (edges), calculates the corresponding 
    graph and measures division time"""
    df = pd.read_csv(path)
    
    nrem = 3
    # Loading data
    track_id =  df['TRACK_ID'].values[nrem:].astype(int)
    
    track_vals = np.unique(track_id)
    
    # building the graph
    out_divtimes = {}
    for trn in track_vals:
        
        graph = build_track_graph(df, trn,minsize=minsize)
        # in node: nombre qui pointent
        root_node = [node for node, in_degree  in graph.in_degree if in_degree==0]
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
                divs_tmp = find_next_division(div,graph)
                
                if len(divs_tmp)>0:
                    last_before_split = get_predecessor(divs_tmp,graph)
                    # -G.nodes[div]['frame']
                    t_root = graph.nodes[div]['frame']
                    t_last = graph.nodes[last_before_split]['frame']
                    ts = (t_root,t_last-t_root)
                    all_times.append(ts)
                    divs_tmp_list.extend(divs_tmp)
        
            divs = divs_tmp_list
            all_divs.append(divs)
            
            sublevel+=1
        out_divtimes[trn] = all_times[1:]
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

process_division_times = True
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