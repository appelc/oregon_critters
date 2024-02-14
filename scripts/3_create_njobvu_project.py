#!/usr/bin/python3
# Ashwin Subramanian
# This code creates a labeling tool project from photos and a class list CSV
# All the code here is hardcoded to work with the aviann server only 

# Modified by Cara Appel to work with local version of Njobvu-AI tool
# February 2024

import os
import sqlite3
import json
import re
import argparse
import shutil
import pandas as pd


## Define function to sort images
def custom_sort(value):
    match = re.search(r'__(\d{4}-\d{2}-\d{2})__(\d+-\d+-\d+\(\d+\))', value)
    if match:
        date = match.group(1)
        second_section = match.group(2)
        return (date, second_section)
    else:
        return ('', '')


## Define function to create project
def createProject(projectName, labels_path, class_list, image_dir, tool_path):

    #hard-code these project options/inputs for now:
    projects_dir = tool_path + '/public/projects/'
    db_dir = args.tool_path + '/db/'
    username = args.username #e.g., 'cara_mac'
    auto_save = '1' #0/1, no/yes
    project_description = 'Manually created'
    folderPath = image_dir

    #Fill in list of classes
    if os.path.exists(class_list): #find the CSV if it exists
        f = open(class_list)
        lines = f.readlines()
    else:
        print('classes.csv not found')        

    classList = []
    for line in lines:
        classList.append(line.strip())
    f.close()

    #Create initial folder
    fixedPath = projects_dir + username + '-' + projectName
    os.mkdir(fixedPath)
    os.mkdir(fixedPath + '/images')
    trainPath = fixedPath + '/training'

    os.mkdir(trainPath)
    os.mkdir(trainPath + '/logs')
    os.mkdir(trainPath + '/python')
    os.mkdir(trainPath + '/weights')

    # open(trainPath + '/darknetPaths.txt', 'w') #remove this?
    # open(trainPath + '/Paths.txt', 'w') #remove this?

    #db intialization
    db = sqlite3.connect(fixedPath + '/' + projectName + '.db')
    write = db.cursor()
    write.execute('''CREATE TABLE IF NOT EXISTS Classes (CName VARCHAR NOT NULL PRIMARY KEY)''')
    write.execute('''CREATE TABLE IF NOT EXISTS Images (IName VARCHAR NOT NULL PRIMARY KEY, reviewImage INTEGER NOT NULL DEFAULT 0)''')
    write.execute('''CREATE TABLE IF NOT EXISTS Labels (LID INTEGER PRIMARY KEY, CName VARCHAR NOT NULL, X INTEGER NOT NULL, Y INTEGER NOT NULL, W INTEGER NOT NULL, H INTEGER NOT NULL, IName VARCHAR NOT NULL, FOREIGN KEY(CName) REFERENCES Classes(CName), FOREIGN KEY(IName) REFERENCES Images(IName))''')
    write.execute("CREATE TABLE Validation (Confidence INTEGER NOT NULL, LID INTEGER NOT NULL PRIMARY KEY, CName VARCHAR NOT NULL, IName VARCHAR NOT NULL, FOREIGN KEY(LID) REFERENCES Labels(LID), FOREIGN KEY(IName) REFERENCES Images(IName), FOREIGN KEY(CName) REFERENCES Classes(CName))")

    #db class insertion
    for i,insert_class in enumerate(classList):
        insert_class = insert_class.strip()
        insert_class = insert_class.replace(' ', '_')
        insert_class = insert_class.replace('+', '+')
        if(insert_class != ''):
            print(i, insert_class)
            write.execute("INSERT OR IGNORE INTO CLASSES (CName) VALUES ('" + insert_class + "')")
    
    #Insert Labels
    if os.path.exists(labels_path): #find the CSV if it exists
        f = open(labels_path)
        data = json.load(f)
    else:
        print(f'labels_for_njobvu.txt not found. Looking in:{labels_path}')

    labelID = 0
    for line in data:
        if line['objects']:
            #height = 1440
            #width = 1920
            for obj in line['objects']:
                # img_width = obj['image_width']
                # img_height = obj['image_height']
                rc = obj['relative_coordinates']
                label_width = rc['width']
                label_height = rc['height']
                left_x = rc['topleft_x']
                bottom_y = rc['topleft_y']
                # label_width = img_width * rc['width']
                # label_height = img_height * rc['height']
                # left_x = rc['center_x'] * img_width - (label_width / 2)
                # bottom_y = rc['center_y'] * img_height - (label_height / 2)
                class_name = obj['name']
                labelID += 1
                filename = line['filename'].split('/')[-1]
                confidence = (float(obj['confidence'])*100) #removed * 100

                write.execute("INSERT INTO Labels (LID, CName, X, Y, W, H, IName) VALUES ('"+str(labelID)+"', '" + str(class_name) + "', '" + str(left_x) + "', '" + str(bottom_y) + "', '" + str(label_width) + "', '" + str(label_height) + "', '" + str(filename) + "')")
                write.execute("INSERT INTO Validation (Confidence, LID, CName, IName) VALUES ('" + str(confidence) + "', '" + str(labelID) +  "', '" + str(class_name) + "', '" + str(filename) + "')")
                # write.execute()
    f.close()

    # print(os.listdir(folderPath))

    #db and folder image insertion (this is for no nested subfolders b/c we handled that in 'main')
    for image in sorted(os.listdir(folderPath), key=custom_sort):
        insert_image = image.strip()
        insert_image = insert_image.replace(' ', '_')
        insert_image = insert_image.replace('+', '_')
        # os.symlink(folderPath + '/' + image, fixedPath + '/images/' + insert_image) #creates symbolic links
        shutil.copy2(folderPath + '/' + image, fixedPath + '/images/' + insert_image) #copies image files
        write.execute("INSERT INTO Images (IName, reviewImage) VALUES ('" +  insert_image + "', '" + str(0) + "')")

    # #if subfolders are not specified in 'main', use this chunk (it will search subfolders but put all images into one project)
    # for subfolder in sorted(os.listdir(folderPath), key=custom_sort):
    #     subfolder_path = os.path.join(folderPath, subfolder)
    #     if os.path.isdir(subfolder_path):
    #         for image in sorted(os.listdir(subfolder_path), key=custom_sort):
    #             full_path = os.path.join(subfolder_path, image)
    #             if os.path.isfile(full_path) and image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
    #                 insert_image = image.strip()
    #                 insert_image = insert_image.replace(' ', '_')
    #                 insert_image = insert_image.replace('+', '_')
    #                 # os.symlink(folderPath + '/' + image, fixedPath + '/images/' + insert_image) #creates symbolic links
    #                 shutil.copy2(full_path, fixedPath + '/images/' + insert_image) #copies image files
    #                 write.execute("INSERT INTO Images (IName, reviewImage) VALUES ('" +  insert_image + "', '" + str(0) + "')")

    db.commit()
    db.close()

    #change permissions so labeling_tool can use images
    # os.system('chown osulabel:osulabel ' + fixedPath)
    # os.system('chown -R osulabel:osulabel ' + fixedPath + '/*')

    #update manage.db database
    db = sqlite3.connect(db_dir + 'manage.db')
    write = db.cursor()
    write.execute("INSERT OR IGNORE INTO Projects (PName, PDescription, AutoSave, Admin) VALUES ('" + projectName + "', '" + project_description + "', '" + auto_save +"', '" + username + "')")
    write.execute("INSERT OR IGNORE INTO Access (Username, PName, Admin) VALUES ('"+username+"', '"+projectName+"', '"+username+"')")
    db.commit()
    db.close()



## Define main                
def main(tool_path, project_name, image_dir):

    #load classes (looks for classes.csv in current directory)
    classes = 'classes.csv'

    #load labels (looks for labels_for_njobvu.txt in the specified directory -- this is the default in args but can be modified)
    results_dir = os.path.join('results/', args.name)
    labels_path = results_dir + '/labels_for_njobvu.txt'
    # labels_path = labels_file

    #See if there are multiple sites (subfolders) and if so, create a project for each
    #Could also include an argument, e.g., keepSubProjects=True

    #are there subfolders?
    subfolders = [subfolder for subfolder in os.listdir(image_dir) if os.path.isdir(os.path.join(image_dir, subfolder)) and not subfolder.startswith('.')]

    #if so, create a new project for each subfolder (site)
    if len(subfolders) > 1:
        for dir in subfolders:
            name_site = project_name + '_' + dir #or just dir if sites are named BMM_SD-SP_02 instead of just SD-SP_02, e.g.
            image_dir_site = image_dir + '/' + dir
            createProject(name_site, labels_path, classes, image_dir_site, tool_path)
    else:
        createProject(project_name, labels_path, classes, image_dir, tool_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Njobvu-AI project with classified images")
    parser.add_argument("tool_path", type=str, help='Path to main labeling tool folder')
    parser.add_argument("name", type=str, help='Name of project (name of folder in /results/)')
    parser.add_argument("project_name", type=str, help='Desired name of project')
    parser.add_argument("username", type=str, help="Your Njobvu-AI username")
    parser.add_argument("--image_dir", type=str, default='data/', help="Directory of image locations (relative to paths in labels_for_njobvu.txt)")
    # parser.add_argument("--labels_file", type=str, default='labels_for_njobvu.txt', help='Path to "labels_for_njobvu.txt" file')
    args = parser.parse_args()

    # Call the main function with the provided arguments
    main(args.tool_path, args.project_name, args.image_dir)