# oregon critters
A computer vision model for classifying camera trap images from western Oregon -- created by Cara Appel @appelc

** Please note that this repository is in active development. Feel free to reach out to let me know if you are using it.

### Intro
This repository contains the trained model weights file (**oregoncritters_V1.pt**), a list of species classes that the model is trained to identify (**classes.csv**), and a folder with several scripts to process images and format predictions for further review. 

### Requirements
This model uses python scripts and relies on the _ultralytics_ package for deploying the YOLOv8 model. See installation instructions here: https://docs.ultralytics.com/quickstart/#install-ultralytics. Processing can be done on CPU or GPUs.

### Workflow overview
1. Rename your images, if necessary. Filenames must be unique within a folder, so rename them if you need to. I like the renaming workflow in the camtrapR package: https://jniedballa.github.io/camtrapR/
2. Download or clone this repository (using the "CODE" button at top right) 
3. Create a folder called _/data/_ within the repository folder and put your images here. Subfolders are okay (e.g., "data/site1", "/data/site2" or even "data/site1/check1")
4. Run the predictions script **scripts/1_predict.py**
5. Run the formatting script **scripts/2_format_predictions.py** to generate inputs for various post-processing programs

### Post-processing options
- Njobvu-AI (an open-source browser-based tool): https://github.com/sullichrosu/Njobvu-AI
    -- To use Njobvu-AI locally, follow installation instructions from GitHub repo
    -- Then, to create a project in Njobvu-AI with your images, run **scripts/3_create_njobvu_project.py**
- FiftyOne (a browser-based tool): https://docs.voxel51.com/
    -- Follow installation instructions from FiftyOne
    -- Then, to create a project on FiftyOne with your images, run **scripts/4_create_firtyone_project.py**
