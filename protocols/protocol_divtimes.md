# Extraction of cellular division time from microscopy movies

This protocol describes how to extract cellular division times from microscopy movies of bacterial cells.

Input: microscopy timelapse | Detection of division events (magenta squares) by the algorithm | Output: an Excel sheet with division speeds
:---------------------------:|:-------------------------:|:-------------------------:
![S. pneumoniae cells growing under the Microscope](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/illustration_1_noprocessing.gif) | ![Growth of S. pneumoniae cells automatically monitored with deep learning](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/illustration_1.gif) | ![Growth of S. pneumoniae cells automatically monitored with deep learning](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/example_track_output.png)

To get the information from the movie on the left to the division times on the right, you need to follow these steps:

1. Segmentation
2. (optional): postprocessing, to remove masks located on the edges of the video
3. Cell tracking (using trackmate, an ImageJ plugin)
4. Division time extraction

All these steps except tracking are performed in this program. More detailed instructions can be found below:

## Segmentation
This part is the hardest from an image analysis point of view. To do this, we use deep-learning models that were trained, by us and others. These models learned from a large amount of images to recognise cell outlines. There exist different **model architectures** which look for different patterns on images. In this program, the main architectures used are called **cellpose** and **omnipose**.

To properly segment an image, a deep-learning segmentation model needs to have been trained on similar images. For each architecture, we can use different models, for instance trained either on fluorescence or phase-contrast data. See [choosing a segmentation model](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/protocols/segmentation_models.md) to choose the best-suited model for your data.

The commands to run segmentation can be found in the folder **1_segmentation**. You can find there several sub-folders, named after the available segmentation architectures. Pick the one you want (for instance, **omnipose**). Within this folder, place the images you want to segment in the folder to_process (as 2D images or 3D timelapses in the order t, x, y). Double click run_***.bat. A console should appear telling you about the progress. Once it is done, the masks will be placed alongside the original data in the to_process folder. The console should tell "Press any key to continue...". You can now close it by either pressing any key or using the "close" button.

Example input | Corresponding output, viewed in ImageJ | Overlay between raw data and segmentation with Napari
:---------------------------:|:-------------------------:|:-------------------------:
![Image of S. pneumoniae](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame.png) | ![Segmentation of S. pneumoniae image](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame_segmented.png) | ![Segmentation of S. pneumoniae image overlaid on raw data](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame_segmented_napari.png)

You can now inspect and if necessary edit the masks using the dedicated [napari plugin](https://github.com/aurelien-barbotin/napari-segment-update). It is also possible to use ImageJ but Napari is more convenient. IF necessary, simply do not forget to convert you masks to labels within Napari (if Napari does not display labels as colors).


## Postprocessing
This step is optional but recommended: it simply removes all masks that touch an image's edge. As a result, cells that are not completely in the field of view will be discarded from analysis.

Before postprocessing | After postprocessing
:---------------------------:|:-------------------------:
![Segmentation before postprocessing](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/segment_edges.png) | ![Segmentation of S. pneumoniae image](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/segment_noedges.png)

A new file for each mask will be generated, with the same name ending with '_edgesrem'

## Tracking
Tracking consists in linking individual masks across frames. If a mask is found in frame 1 and a mask at a very similar position in frame 2, it is safe to assume that these two masks correspond to the same cell at different timepoints. To do this, we use [Trackmate](https://imagej.net/plugins/trackmate/).

Open a timelapses of mask generated in the previous steps thenrun Trackmate. A welcome screen with the reference of the paper summarises your data
1. Click next
2. In the field "Select a **detector**", choose Label Image detector and click next
3. You can click preview to see if all is fine or click next (3 times, no need to update anything)
4. "Set filters on spots": still nothing to do here, click next
5. "Select a **tracker**": choose Overlap tracker. You can try others if overlap does not work for you and if you know what you are doing. To know what you are doing, you can read [this](https://imagej.net/plugins/trackmate/trackers/). Click next and validate the tracking parameters. Parameters that worked well in the past: IoU calculation: Precise, min IoU: 0.3, Scale factor: 1 (default parameters)
6. You should see a summary of tracking results. Click next. Tracks will also be displayed above the masks, you can inspect them.
7. "Set filters on tracks": you can ignore and click next.
8. You now should see now a "Display options" window. This is where you will get the data of interest: the tracking data. For this, click on the button "Tracks" at the bottom of the screen. A "Track tables" window opens. You can now export to csv both the tabs **Spots** and **Edges**. Save them as respectively spots.csv and edges.csv in a folder containing uniquely the masks stack and (optionally) the original data.

![Exporting tracking data from Trackmate](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/trackmate_annotated.png)

You are done with tracking, you can get back to proced_deepseg to exploit these results.

## Division speed extraction
Using tracking data from trackmate, we can now measure when cells divide. To extract a doubling time becomes easy: we just need to measure the time between two divisions. For each cell, the algorithm first detects when the first division occurs. It notes down the frame number and then measures the time it takes until the next division. We have now one measurement point: the frame number (first frame after division) and Division time.

To get this information, visit the folder **2_analysis/division_speeds_trackmate**. Place in the folder 'to_process' the data to analyse. The input data is placed in individual subfolders. For instance, if the raw data stack was named 1_control.tif, the masks might be named 1_control_cp_masks_edgesrem.tif (see previous steps). For this dataset, you generated two tracking files: edges.csv and spots.csv. Create a folder named as you wish (for instance, stack1) and place these 4 files in it. Note that the original data stack (1_control.tif) is optional and if placed in the folder, a movie summarising the analysis will be generated. The file structure looks like this:
```
2_analysis
|	to_process
|	|_______stack1
|		|	1_control.tif
|		|	1_control_cp_masks_edgesrem.tif
|		|	edges.csv
|		|	spots.csv
|		stack2
|		|	...
		
```

Press **run**: a console appears, asking you about the pixel size (several times). Voilà! The results are stored in Excel files. You get both division times vs frame numbers and cell size before division.

