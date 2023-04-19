DL for microscopy
=================

A collection of scripts to perform deep-learning segmentation of bacterial cells labeled with membrane markers. Contains scripts that can use cellpose or Stardist home-trained to segment images of Bacillus Subtilis labeled with Nile Red. Also contains an analysis script that measures width and length of the corresponding masks.

Summary
-------

- run_analysis.py: a script with prompt that reads a series of masks contained in subfolders and extracts their width and length. Stores the results in a series of *csv files
- morphology_advanced.py: the method used to extract width and length from images
