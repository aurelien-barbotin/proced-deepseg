# proced-deepseg

A collection of Python scripts to perform deep-learning segmentation of bacterial cells and corresponding analysis. These scripts are mainly intended for members of the ProCeD lab who don't code, but can be used by others.

![Growth of S. pneumoniae cells automatically monitored with deep learning](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/illustration/illustration_1-1.gif)

## Usage

This offers workflows for
 - Image segmentation (folder 1_segmentation)
 - (optional) postprocessing (folder 1b_postprocessing): to remove masks on the edge of an image
 - Segmentation analysis (folder 2_analysis): to extract doubling times (requires extra processing on trackmate) or cell morpholgy

Scripts to run submethods are located in corresponding subfolders. For instance, to run segmentation with omnipose, copy the images to process in the folder 1_segmentation/omnipose/to_process/ (create it if it does not exist). Then double click on `run_segmentation.bat`. A terminal should open which gives update on the progress.

Information can be extracted from masks using scripts in 2_analysis. This information can be either the cellular morphology (and its variation with frames) or cellular doubling times. Extraction of doubling times requires tracking with Trackmate, a plugin available in Fiji. A complete protocol and exemple for cellular doubling time extraction can be found here:

[Cellular doubling time extraction](https://github.com/aurelien-barbotin/proced-deepseg/blob/main/protocols/protocol_divtimes.md)

## Install

This package contains several scripts that run in different virtual environments. Batch scripts can be found in subdirectories, which paths need to be updated when installed on a new computer. Installation of specific libraries within these virtualenvs is necessary. Virtual environments necessary to run these scripts include

It is required to install dl_for_mic in a virtual environment, typically using anaconda:

```
conda create -n dl_for_mic
conda activate dl_for_mic
pip install -e path
```

To avoid dependency conflicts, it is preferable to install the different segmentation libraries in different virtual environments. To run the segmentation methods with a batch script, it will be necessary to update the names and paths of virtual environments.

## Segmentation models

Image segmentation can be performed using one of three models:
 - Cellpose: either the general model, or our home-trained model on B. subtilis images labeled with NileRed
 - Omnipose: either the general model for phase contrast data, or the model for fluorescence imaging
 - delta

Each of these three methods runs in a different virtual environment (to avoid conflicts).

### omnipose
A Virtualenv necessary to run omnipose. Follow the instructions of the official page: https://pypi.org/project/omnipose/
Microsoft Visual C++ is necessary. Last checked, works for omnipose==0.4.4 but not for omnipose>1 For omnipose_custom, you also need to update the path to the custom omnipose model. Based on how it was trained, you also might need to change the parameter 'nchan'.

### cellpose
So far it is expecting a `deepseg` environment. The processing script also needs to know the path to the custom models.IT can be the same environment as dl_for_mic as cellpose is a requirement of dl_for_mic. This may change in a near future.

### delta
Expects a Virtualenv named `delta_env`. Installation is tricky and should follow the official instructions.
