# oregon critters
A computer vision model for classifying camera trap images from western Oregon
- created by Cara Appel

Please note that this repository is in active development. I'd love to hear from you if you try using the model!

Below are steps to run predictions on your images and view them using several options for external software.

### Requirements
This model uses python scripts and relies on the ultralytics package for deploying the YOLOv8 model. See installation instructions here: https://docs.ultralytics.com/quickstart/#install-ultralytics

### Workflow overview
- Rename your images, if necessary. Filenames must be unique within a folder, so rename them if you need to. I like the renaming workflow in the camtrapR package: https://jniedballa.github.io/camtrapR/
- Set up directory with your images. Subfolders are okay (e.g., "site1", "site2" or "site1/check1")
- Download or clone this repository (using the "CODE" button at top right)
- Run predictions script <scripts/1_predict.py>
- Run formatting script <scripts/2_format_predictions.py> to generate inputs for various post-processing programs

### Post-processing options
- Njobvu-AI (open-source browser-based tool): https://github.com/sullichrosu/Njobvu-AI
    -- To use Njobvu-AI locally, follow installation instructions from GitHub repo
    -- To create a project in Njobvu-AI with your images, run <scripts/3_create_njobvu_project.py>
- FiftyOne (browser-based tool): https://docs.voxel51.com/
    -- Follow installation instructions from FiftyOne
    -- To create a project on FiftyOne with your images, run <scripts/4_create_firtyone_project.py>
