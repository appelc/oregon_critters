## Converts YOLO predictions text files to the following formats:
## - CSV
## - COCO json (compatible with many tools, e.g., creating a FiftyOne dataset)
## - TXT file used to create Njobvu-AI project

import pandas as pd
import json
import argparse
import os
import datetime
from PIL import Image

# Define function to get image dimensions
def get_image_dimensions(filepath):
    with Image.open(filepath) as img:
        return img.size
    
# Define function to extract image birthtime (*adds to runtime*)
def get_birthtime(filepath):
    birth_time = os.stat(filepath).st_birthtime
    birth_time_date = datetime.datetime.fromtimestamp(birth_time)
    return(birth_time_date)


# Define function to parse text files
def parse_text_files(results_dir):

    # Locate label files within results directory
    labels_dir = os.path.join(results_dir, 'labels')

    # Iterate through each text file in the directory
    data = []
    for file_name in os.listdir(labels_dir):
        file_path = os.path.join(labels_dir, file_name)
        with open(file_path, "r") as file:
            lines = file.readlines()
            # Process each line (row) in the file
            for line in lines:
                values = line.strip().split()
                data.append([file_name] + values) #each line has the filename + box values

    column_names = ["filename"] + ["class_id"] + ["x"] + ["y"] + ["width"] + ["height"] + ["confidence"]
    preds = pd.DataFrame(data, columns = column_names)
    preds['image_name'] = preds.filename.map(lambda x: x.strip('.txt'))
    preds = preds.astype({'filename': str, 'class_id': int, 'x': float, 'y': float, 'width': float, 'height': float, 'confidence': float, 'image_name': str})
    preds = preds.drop('filename', axis=1) #don't need this column anymore

    return preds

# Define function to format predictions as dataframe
def convert_to_csv(preds, all_images, class_ids):

    #read in list of all images and extract just the name
    img_list = pd.read_csv(all_images, header=None, names=['path'])
    img_list['image_name'] = img_list['path'].apply(lambda x: os.path.splitext(os.path.basename(x))[0])

    #merge image file paths with predictions
    preds_merged = preds.merge(img_list, on='image_name', how='left')

    #extract image dimensions and add to dataframe
    print("Extracting image dimensions...")
    for index, img_row in preds_merged.iterrows():
        if img_row['class_id'] is not None:
            dimensions = get_image_dimensions(img_row['path'])

            print(f"looking for file {img_row['path']}")

            preds_merged.at[index, 'img_width'] = int(dimensions[0])
            preds_merged.at[index, 'img_height'] = int(dimensions[1])

    #convert box dimensions from normalized (center origin)
    preds_merged['x_center'] = preds_merged['x'] * preds_merged['img_width']
    preds_merged['y_center'] = (preds_merged['y']) * preds_merged['img_height']
    preds_merged['w_box'] = (preds_merged['width']) * preds_merged['img_width']
    preds_merged['h_box'] = (preds_merged['height']) * preds_merged['img_height']

    #convert box dimensions from normalized (top-left origin)
    preds_merged['x_topleft'] = preds_merged['x_center'] - (preds_merged['w_box'] / 2)
    preds_merged['y_topleft'] = preds_merged['y_center'] - (preds_merged['h_box'] / 2)

    #now merge back with all image list so we capture the empty ones too
    imgs_merged = img_list.merge(preds_merged, on=['image_name','path'], how = 'left')

    #and add class names and convert NaN to 'empty'
    imgs_merged = imgs_merged.merge(class_ids, on='class_id', how='left')
    imgs_merged['class_name'] = imgs_merged['class_name'].where(pd.notna(imgs_merged['class_name']), 'empty')

    #sort alphabetically by filename
    imgs_merged = imgs_merged.sort_values(by='image_name')

    return imgs_merged


# Define function to convert predictions to COCO
def convert_to_coco(preds_labels, class_ids):

    # Create empty COCO dictionaries
    coco_data = {
        "info": {},
        "licenses": {},
        "categories": [],
        "images": [],
        "annotations": []
    }

    # Format 'categories' dictionary
    for index, row in class_ids.iterrows():
        coco_data['categories'].append({
            'name': row['class_name'],
            'id': row['class_id'],
            'supercategory': 'object',
        })

    # Initialize counters
    image_id_counter = 1
    annotation_id_counter = 1

    # Keep track of unique image_ids
    unique_image_ids = set()
    
    # Add suffix back to image name
    preds_labels['image_name'] = preds_labels['image_name'] + '.JPG' 

    # Convert NAs to 'None' for JSON format
    preds_labels = preds_labels.where(pd.notna(preds_labels), None)

    # For each entry (row), extract 'images' and 'annotations' info
    for pred_index, pred_row in preds_labels.iterrows():

        # Extract image dimensions and datetime
        # dimensions = get_image_dimensions(pred_row.path)
        # birthtime = get_birthtime(pred_row.path)

        # Add image info (first check if it has been added already)
        if pred_row['image_name'] not in unique_image_ids:
            coco_data["images"].append({
                "id": image_id_counter,
                "file_name": pred_row.path.split('data/')[1],
                "width": pred_row['img_width'],
                "height": pred_row['img_height'],
                # "width": int(dimensions[0]),
                # "height": int(dimensions[1]),
                #"date_captured": str(birthtime),
            })

            # Increment counters and mark image_id as complete
            image_id_counter += 1
            unique_image_ids.add(pred_row['image_name'])

        # Add annotation info (only if image has a predicted box)
        if pred_row['class_name'] == 'empty':
            coco_data["annotations"].append(None)   
        else:
            coco_data["annotations"].append({
                "id": annotation_id_counter,
                "image_id": image_id_counter - 1,
                "name": pred_row["class_name"],
                "category_id": int(pred_row["class_id"]),
                "bbox": [pred_row['x_topleft'], pred_row['y_topleft'], pred_row['w_box'], pred_row['h_box']],
                "area": float(pred_row['w_box']*pred_row['h_box']),
                "score": pred_row["confidence"],
                "iscrowd": 0,
            })
        #remove empty annotation entries
        coco_data["annotations"] = [ann for ann in coco_data['annotations'] if ann is not None]

        #Increment counters
        annotation_id_counter += 1

    return coco_data

    
# Define function to convert prediction to Njobvu TXT input 
def convert_to_njobvu(entry):

    # Create empty dicitonary
    njobvu_data = {
        "frame_id": 1,
        "filename": entry['path'].split('data/')[1],
        "objects": []
    }

    # Add object info (only if image has a predicted box)
    if  entry['class_name'] == 'empty':
        njobvu_data["objects"].append(None)   
    else:
        njobvu_data["objects"].append({
                "class_id": int(entry["class_id"]),
                "name": entry["class_name"],
                "image_width": entry["img_width"],
                "image_height": entry["img_height"],
                "relative_coordinates": {
                    # "center_x": entry["x_center"],
                    # "center_y": entry["y_center"],
                    "topleft_x": entry["x_topleft"],
                    "topleft_y": entry["y_topleft"],
                    "width": entry["w_box"],
                    "height": entry["h_box"],
                },
                "confidence": float(entry["confidence"])
            })
    # Remove empty annotation entries
    njobvu_data["objects"] = [ann for ann in njobvu_data['objects'] if ann is not None]

    return njobvu_data


# Main
def main():
    
    #load class list (looks for classes.csv in current directory)
    if os.path.exists('classes.csv'):
        class_ids = pd.read_csv('classes.csv', header=None, names=['class_name'])
        class_ids['class_id'] = range(len(class_ids))
        print('Found classes.csv')
    else:
        print('classes.csv not found')

    #locate results text files based on run name argument
    print(f"Looking for text files in results/{args.name}...")
    results_dir = os.path.join('results/', args.name)

    #load results text files and format them
    preds = parse_text_files(results_dir)

    print("Finished parsing text files.")
    print("Creating CSV...")

    ## Format predictions and save as CSV
    pred_labels = convert_to_csv(preds, args.image_list, class_ids)
    csv_output_path = os.path.join(results_dir, 'predictions.csv')
    pred_labels.to_csv(csv_output_path)

    print("Converting to JSON...")
    
    ## Convert to COCO format and save as JSON
    coco_data = convert_to_coco(pred_labels, class_ids)
    coco_output_path = os.path.join(results_dir, "labels.json")
    with open(coco_output_path, "w") as coco_output_file:
        json.dump(coco_data, coco_output_file, indent=4)

    print("Converting to Njobvu-AI input...")

    ## Convert to NJOBVU format and save as TXT
    yolo_data = pred_labels
    yolo_data['dict_entry'] = yolo_data.apply(convert_to_njobvu, axis=1)
    dict_entries = yolo_data['dict_entry'].tolist() #convert to a list for saving
    text_output_path = os.path.join(results_dir, "labels_for_njobvu.txt")
    with open(text_output_path, 'w') as txt_file:
        txt_file.write("[\n")  
        for i, entry in enumerate(dict_entries):
            txt_file.write(json.dumps(entry, indent=2))  
            if i < len(dict_entries) - 1:
                txt_file.write(',\n')  
            else:
                txt_file.write('\n')  
        txt_file.write("]\n") 

    ##Save NJOBVU output as JSON (not necessary)
    # json_output_path = os.path.join(results_dir, "labels_for_njobvu.json")
    # with open(json_output_path, 'w') as json_file:
    #     json.dump(dict_entries, json_file)

    print("")
    print("Done!")
    print("Predictions saved to:")
    print(csv_output_path) 
    print(coco_output_path)
    print(text_output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YOLO predictions to JSON and TXT files")
    parser.add_argument("name", type=str, help="Name of project (name of folder in /results/)")
    parser.add_argument("--image_list", type=str, default='image_list_cleaned.txt', help='Path to image list')
    args = parser.parse_args()

    main()

