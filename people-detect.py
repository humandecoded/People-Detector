
import cvlib    #high level module, uses YOLO model with the find_common_objects method
import cv2      #image/video manipulation, allows us to pass frames to cvlib
from argparse import ArgumentParser
import os
import sys
from datetime import datetime
from twilio.rest import Client  #used for texting if you'd like, flag is optional, 
import smtplib, ssl #for sending email alerts



#function takes a file name, checks that file for human objects
def humanChecker(video_name):
    #open video stream
    vid = cv2.VideoCapture(video_name)

    #get approximate frame count for video
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    
    #look at every nth frame of our file, run frame through detect_common_objects
    #Increase 'n' to examine fewer frames and increase speed. Might reduce accuracy though.
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
    parser.add_argument('--twilio', action='store_true', help='Flag to use Twilio text notification')
    parser.add_argument('--email', action='store_true', help='Flag to use email notification')
    args = vars(parser.parse_args())
    
    human_detected = False
    file_list = []     #list of files containing people

    #if the --twilio flag is used, this will look for environmental variables holding this needed information
    #you can hardcode this information here if you'd like though. It's less secure but if you're the only one
    #using this script it's probably fine
    if args['twilio']:
        try:
            TWILIO_TOKEN = os.environ['TWILIO_TOKEN']
            TWILIO_SID = os.environ['TWILIO_SID']
            TWILIO_FROM = os.environ['TWILIO_FROM']
            TWILIO_TO = os.environ['TWILIO_TO']
        except:
            print('Something went wrong with the Twilio variables. Either set your environmental variables or hardcode values in to script: TWILIO_TOKEN, TWILIO_SID, TWILIO_FROM, TWILIO_TO')
            sys.exit(1)

    #if the --email flag is used, this will look for environmental variables holding this needed information
    #you can hardcode this information here if you'd like though. It's less secure but if you're the only one
    #using this script it's probably fine
    if args['email']:
        try:
            SENDER_EMAIL = os.environ['ALERT_SENDER_EMAIL']
            SENDER_PASS = os.environ['ALERT_SENDER_PASS']
            RECEIVER_EMAIL = os.environ['ALERT_RECEIVER_EMAIL']
        except:
            print('Something went wrong with Email variables. Either set your environmental variables or hardcode values in to script')
            sys.exit(1)
    

    #create our log file and write the file names where we detect people
    time_stamp = datetime.now().strftime('%m%d%Y-%H:%M:%S') + '.txt'
    with open(time_stamp, 'w') as log_file:
        #loop through all our video files
        for current_file in getListOfFiles(args['directory'] + '/'):
            print(f'Working on {current_file}')
            if humanChecker(str(current_file)):
                human_detected = True
                print(f'Human detected in {current_file}')
                log_file.write(f'omg. intruder alert in {current_file} \n' )
                file_list.append(str(current_file))

    #if people are detected and --twilio flag has been set, send a text
    if args['twilio'] and human_detected:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=f"Human Detected. Check log files", from_=TWILIO_FROM, to=TWILIO_TO)
    
    #if people are detected and --email flag has been set, send an email
    if args['email'] and human_detected:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        message = '\n'.join(file_list)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)

        