# Extraction of cell morphology from movies

Extracts morphology (width, length and area) from the segmentation results of a microscopy movie (t, x, y). This script finds the rectangle of smallest area containing each detected cell to extract its width and length, and simply counts the number of pixels per mask to extract area.

Insert the masks (segmented images) you want to process in the folder 'to_process' then click run. You will be prompted in a console to enter the pixel size. The results will be stored in an excel file.
