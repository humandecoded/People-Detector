


import cvlib    #high level module, uses YOLO model with the find_common_objects method
import cv2      #image/video manipulation, allows us to pass frames to cvlib
from argparse import ArgumentParser
import os
from datetime import datetime

#function takes a file name, checks that file for human objects
def humanChecker(video_name):
    #open video stream
    vid = cv2.VideoCapture(video_name)

    #get approximate frame count for video
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    
    #look at every nth frame of our file, run frame through detect_common_objects
    n = 3
    for x in range(1, frame_count - 3, n):
        vid.set(cv2.CAP_PROP_POS_FRAMES, x)
        _ , frame = vid.read()
        _ , label, _ = cvlib.detect_common_objects(frame)

        if 'person' in label:
            return True
    return False

#takes a directory and returns all files and directories within
def getListOfFiles(dir_name):
    list_of_files = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in list_of_files:
        #ignore hidden files and directories
        if entry[0] != '.':
            # Create full path
            full_path = os.path.join(dir_name, entry)
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(full_path):
                all_files = all_files + getListOfFiles(full_path)
            else:
                all_files.append(full_path)              
    return all_files


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', required=True, help='Path to video folder')
    args = vars(parser.parse_args())

    #create our log file and write the file names where we detect people
    with open(datetime.now().strftime('%m%d%Y-%H:%M:%S') + '.txt', 'w') as w:
        for current_file in getListOfFiles(args['directory'] + '/'):
            print(f'Working on {current_file}')
            if humanChecker(str(current_file)):
                print(f'Human detected in {current_file}')
                w.write(f'omg. intruder alert in {current_file} \n' )