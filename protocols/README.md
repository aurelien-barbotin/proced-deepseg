# Protocols
A step-by-step guide for the different image analysis protocols you can perform with this library

## Extraction of cellular division time from microscopy movies

This protocol describes how to extract cellular division times from microscopy movies of bacterial cells.

Input: microscopy timelapse | Detection of division events (magenta squares) by the algorithm | Output: an Excel sheet with division speeds
:---------------------------:|:-------------------------:|:-------------------------:
![S. pneumoniae cells growing under the Microscope](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/illustration_1_noprocessing.gif) | ![Growth of S. pneumoniae cells automatically monitored with deep learning](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/illustration_1.gif) | ![Growth of S. pneumoniae cells automatically monitored with deep learning](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/example_track_output.png)

To get the information from the movie on the left to the division times on the right, you need to follow these steps:

1. [Segmentation](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/1_segmentation/)
2. (optional): [postprocessing](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/1b_postprocessing), to remove masks located on the edges of the video
3. [Cell tracking and extraction of division times](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/2_analysis/division_speeds_trackmate/)

## Extraction of cell morphology in movies

1. [Segmentation](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/1_segmentation/)
2. (optional): [postprocessing](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/1b_postprocessing), to remove masks located on the edges of the video
3. [Morphology extraction](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/2_analysis/extract_cell_morphology/)
