# Segmentation
Cell segmentation is the hardest from an image analysis point of view. To do this, we use deep-learning models that were trained, by us and others. These models learned from a large amount of images to recognise cell outlines. There exist different **model architectures** which look for different patterns on images. In this program, the main architectures used are called **cellpose** and **omnipose**.

To properly segment an image, a deep-learning segmentation model needs to have been trained on similar images. For each architecture, we can use different models, for instance trained either on fluorescence or phase-contrast data. See below to choose the best-suited model for your data.

The commands to run segmentation can be found in the folder **1_segmentation**. You can find there several sub-folders, named after the available segmentation architectures. Pick the one you want (for instance, **omnipose**). Within this folder, place the images you want to segment in the folder to_process (as 2D images or 3D timelapses in the order t, x, y). Double click run_***.bat. A console should appear telling you about the progress. Once it is done, the masks will be placed alongside the original data in the to_process folder. The console should tell "Press any key to continue...". You can now close it by either pressing any key or using the "close" button.

Example input | Corresponding output, viewed in ImageJ | Overlay between raw data and segmentation with Napari
:---------------------------:|:-------------------------:|:-------------------------:
![Image of S. pneumoniae](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame.png) | ![Segmentation of S. pneumoniae image](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame_segmented.png) | ![Segmentation of S. pneumoniae image overlaid on raw data](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/protocol/frame_segmented_napari.png)

You can now inspect and if necessary edit the masks using the dedicated [napari plugin](https://github.com/aurelien-barbotin/napari-segment-update). It is also possible to use ImageJ but Napari is more convenient. IF necessary, simply do not forget to convert you masks to labels within Napari (if Napari does not display labels as colors).

## Omnipose
To run omnipose segmentation, choose the subfolder 1_segmentation/omnipose. Place your datasets in the subfolder to_process and press run. You will be asked which model to choose by picking a number: 1 for phase contrast and 2 for fluorescence. Below are some examples.

### Phase contrast

Phase-contrast images of S. pneumoniae by Dimitri Juillot.

Input |Segmented image
:---------------------------:|:-------------------------:
![Image of S. pneumoniae](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/segmentation/omnipose_raw.png) | ![Segmentation of S. pneumoniae image](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/segmentation/omnipose_segmented.png)

model name: 'bact_phase_omni'

### Fluorescence
P. aeruginosa cells by Merve Nur Tunc

Input |Segmented image
:---------------------------:|:-------------------------:
![Image of S. pneumoniae](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/segmentation/omnipose_fluo_raw.png) | ![Segmentation of S. pneumoniae image](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/segmentation/omnipose_fluo_segmented.png)

## Cellpose
Segmentation with cellpose is for now used only together with a custom model we developed with Louise Destouches. To segment B. subtilis cells in exponential phase, labeled with NileRed. 2 models are available: one trained on healthy cells, the other on cells targetted by antibiotics.
