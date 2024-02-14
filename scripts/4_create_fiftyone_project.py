## Script to create a FiftyOne dataset from YOLO predictions using a JSON file

#this script relies on the following folder structure:
# /data: where images are stored (subfolders OK)
# /scripts: where this script is
# /results/name/labels/labels.json: file with predictions

#example usage: python3 scripts/4_create_fiftyone_project.py run1 run1_dataset

import fiftyone as fo
import os

def main(args):
    name=args.name
    datapath = os.path.join(args.dir, 'data/')
    labelspath = os.path.join(args.dir, 'results/', args.name, 'labels.json')
 
    print(f"Looking for images in {datapath}")
    print(f"Looking for labels in {labelspath}")
    print(f"Creating FiftyOne dataset named {name}")
  
    # Create the dataset
    dataset = fo.Dataset.from_dir(
        data_path=datapath,
        labels_path=labelspath,
        dataset_type=fo.types.COCODetectionDataset,
        label_field='predictions', #this is what to call it, not what it's called in the JSON
        name = name
    )

    # Launch app
    session = fo.launch_app(dataset)
    session.wait()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help='Name of project (name of folder in /results/)')
    parser.add_argument("--dir", type=str, default='', help='Directory location, e.g. both/ or .')
    parser.add_argument("project_name", type=str, default="test_dataset", help='Name for FiftyOne dataset')
    args = parser.parse_args()
    main(args)