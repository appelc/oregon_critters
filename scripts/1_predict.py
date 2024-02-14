#!/raid1/home/fw/appelc/local/envs/yolov8/bin/python3
 
# Run YOLO predictions as if in command line

import subprocess
import argparse

# Parse arguments
def parse_args():
    parser = argparse.ArgumentParser(description = "Script to run predictions from trained YOLOv8 model")
    parser.add_argument("model", type=str, help="Path and name to pretrained model (.pt file)")
    parser.add_argument("name", type=str, help="Provide a name for the model run (this will be the name of the folder in /results/)")
    parser.add_argument("--source", type=str, default='image_list_cleaned.txt', help="Image list text file")
    parser.add_argument("--imgsz", type=int, default=640, help="Image dimensions, e.g., 320 or 640")
    parser.add_argument("--conf", type=int, default=0.1, help="Confidence threshold")
    parser.add_argument("--iou", type=int, default=0.7, help="IOU threshold for bboxes")
    parser.add_argument("--device", type=str, default='cpu', help="Device(s), e.g., 0 or 1 or 'cpu' or 'mps'")
    parser.add_argument("--save_imgs", action='store_true', help="Save images with predicted boxes?")
    
    return parser.parse_args()

# Define main function
def main():

    # Parse arguments
    args = parse_args()

    # Locate image input list
    filepath = args.source
    with open(filepath, 'r') as file:
        line_count = sum(1 for line in file)

    print(f'Generating predictions on {line_count} images...')

    # Build the YOLO predict command
    command = f"yolo predict model={args.model} source='{filepath}' save_txt=True save={args.save_imgs} save_conf=True imgsz={args.imgsz} iou={args.iou} conf={args.conf} device={args.device} project='results' name={args.name}"

    # Execute the command using subprocess
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        print("Predictions complete", result.stdout.decode())
        print(f"Results text files saved to /results/{args.name}/labels")
    except subprocess.CalledProcessError as e:
        # result
        print("Error:", e.stderr.decode())


if __name__ == "__main__":
    main()
