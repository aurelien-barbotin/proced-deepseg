## Cell tracking and division speed extraction
Input: a segmented stack. Optionally: the original dataset

Output: Division times for each cell that was detected, and cell sizes before division. Stored in Excel files.

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

Press **run**: a console appears, asking you about the pixel size (several times). Voilà! The results are stored in Excel files. You get division times vs frame numbers, cell size before division, and time of first division. In more details:

* cellarea_vs_division: this has two columns, 'frame' and 'area in µm2'. Each line corresponds to the state of a cell before division. For instance, if 'frame' value is 7 and  'area in µm2' is 50, it means that at frame 7 there is a cell with an area of 50µm² that divided in the next frame
* division_times: this is the measure of the time interval between two divisions. It has also 2 columns, 'Frame' and 'Division time'. For instance, if 'frame' value is 9 and 'Division time' is 31, it means that a cell that appeared after a division at frame 9 divided again between frame 31 and 32.
* first_division_times: this corresponds to the time at which cells present at the beginning of the acquisition divided for the first time.

