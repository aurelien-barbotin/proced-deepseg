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
path = "/home/aurelienb/edges_export.csv"

df = pd.read_csv(path)

nrem = 3
labels = df['LABEL'].values[nrem:]
track_id =  df['TRACK_ID'].values[nrem:].astype(int)
times = df['EDGE_TIME'].values[nrem:].astype(float)

source_id=df['SPOT_SOURCE_ID'].values[nrem:]
target_id=df['SPOT_TARGET_ID'].values[nrem:]

track_vals = np.unique(track_id)
trn = 44

track_id[track_id==trn]
labels = labels[track_id==trn]

graph = nx.DiGraph()

nodes_candidates = []
for j in range(len(labels)):
    label = labels[j]
    tt = times[track_id==trn][j]
    tpl = label.split(' → ')
    int_tup = (source_id[track_id==trn][j],target_id[track_id==trn][j])
    
    assert len(tpl)==2
    assert tpl[0][:2]=="ID"
    assert tpl[1][:2]=="ID"
    data = (tpl[0],tpl[1],{"frame":tt})
    graph.add_edges_from([data])
    nodes_candidates.append((data[0],{"frame":tt-0.5}))
    nodes_candidates.append((data[1],{"frame":tt+0.5}))
# nodes_candidates = list(set(nodes_candidates))
graph.add_nodes_from(nodes_candidates)


plt.figure()
nx.draw(graph,pos=nx.planar_layout(graph))
G = graph
# in node: nombre qui pointent
root_node = [node for node, in_degree  in G.in_degree if in_degree==0]
assert len(root_node)==1
root_node = root_node[0]
out_node = [in_degree for node, in_degree  in G.out_degree if in_degree==2]

"""
['layout',
 'bipartite_layout',
 'circular_layout',
 'kamada_kawai_layout',
 'random_layout',
 'rescale_layout',
 'rescale_layout_dict',
 'shell_layout',
 'spring_layout',
 'spectral_layout',
 'planar_layout',
 'fruchterman_reingold_layout',
 'spiral_layout',
 'multipartite_layout',
 'arf_layout']
"""

# from https://stackoverflow.com/questions/69465397/iterating-over-nodes-of-a-networkx-digraph-in-order
children_next = set()
searched_nodes = set()

def find_next_division(root):
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

def get_predecessor(suc):
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

all_divs=[]
divs=[root_node]
sublevel = 0
all_times=[]
while len(divs)>0:
    print('Sublevel',sublevel)
    divs_tmp_list=[]
    for div in divs:
        divs_tmp = find_next_division(div)
        
        if len(divs_tmp)>0:
            last_before_split = get_predecessor(divs_tmp)
            # -G.nodes[div]['frame']
            t_root = G.nodes[div]['frame']
            t_last = G.nodes[last_before_split]['frame']
            ts = (t_root,t_last-t_root)
            all_times.append(ts)
            divs_tmp_list.extend(divs_tmp)

    divs = divs_tmp_list
    all_divs.append(divs)
    
    sublevel+=1