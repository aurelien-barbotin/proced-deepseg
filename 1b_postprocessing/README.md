# Segmentation post-processing

This step is optional: you can use it to remove any mask that touches the edge of the image. It is interesting to use for instance if you want to measure morphologies, as masks of cells on the edge of an image will be incomplete.

To use, place the images you want to process in the 

	to_process
	
folder and double click on 

	run_postprocessing.bat
	
This will create new masks which names end with '_edgesrem.tif'. E.g a copy of 'mask1.tif' will be created with cells on the edges removed and named 'mask1_edgesrem.tif'.
