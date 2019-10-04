
import cvlib    #high level module, uses YOLO model with the find_common_objects method
import cv2      #image/video manipulation, allows us to pass frames to cvlib
from argparse import ArgumentParser
import os
import sys
from datetime import datetime
from twilio.rest import Client  #used for texting if you'd like, flag is optional, 
import smtplib, ssl #for sending email alerts
from email.message import EmailMessage
import imghdr



#function takes a file name, checks that file for human objects
#saves the frames with people detected into directory named 'time_stamp'
def humanChecker(video_name, time_stamp, yolo='yolov3', continuous = False, n=10, confidence=.65):
    #open video stream
    vid = cv2.VideoCapture(video_name)
    #tracking if we've found a human or not
    human_found = False 
    #get approximate frame count for video
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'{frame_count} frames')

    #in 'continuous mode' we'll need to increment every time a person is detected
    person_counter = 0   
    #look at every nth frame of our file, run frame through detect_common_objects
    #Increase 'n' to examine fewer frames and increase speed. Might reduce accuracy though.
    for x in range(1, frame_count - 3, n):
        vid.set(cv2.CAP_PROP_POS_FRAMES, x)
        _ , frame = vid.read()
        bbox , labels, conf = cvlib.detect_common_objects(frame, model=yolo, confidence=confidence)
        
        
        if 'person' in labels:
            person_counter += 1
            human_found = True
            #create a folder for our images, save frame with detected human
            cwd = os.getcwd()
            #create image with bboxes showing objects and save
            marked_frame = cvlib.object_detection.draw_bbox(frame, bbox, labels, conf, write_conf=True)
            file_name = os.path.basename(os.path.normpath(video_name))
            cv2.imwrite(cwd + '/' + time_stamp + '/' + file_name + '-' + str(person_counter) + '.jpeg', marked_frame)
            
            if continuous == False:
                break
            
    return human_found

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

#############################################################################################################################
if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', required=True, help='Path to video folder')
    parser.add_argument('--twilio', action='store_true', help='Flag to use Twilio text notification')
    parser.add_argument('--email', action='store_true', help='Flag to use email notification')
    parser.add_argument('--tiny_yolo', action='store_true', help='Flag to indicate using YoloV3-tiny model instead of the full one. Will be faster but less accurate.')
    parser.add_argument('--continuous', action='store_true', help='This option will go through entire video file and save all frames with people. Default behavior is to stop after first person sighting.')
    parser.add_argument('--confidence', type=int, choices=range(1,100), default=65, help='Input a value between 1-99. This represents the percent confidence you require for a hit. Default is 65')
    parser.add_argument('--frames', type=int, default=10, help='Only examine every nth frame. Default is 10')
    args = vars(parser.parse_args())
    
    #decide which model we'll use, default is 'yolov3-tiny', faster but less accurate
    if args['tiny_yolo']:
        yolo_string = 'yolov3-tiny'
    else:
        yolo_string = 'yolov3'

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

    number_of_frames = args['frames']
    confidence_percent = args['confidence'] / 100

    #create our log file, create a directory to hold snapshots 
    time_stamp = datetime.now().strftime('%m%d%Y-%H:%M:%S')
    os.mkdir(time_stamp)
    print('Beginning Detection')
    print(f'Directory {time_stamp} has been created')
    print(f"Email notifications set to {args['email']}. Text notification set to {args['twilio']}.")
    print(f"Confidence threshold set to {args['confidence']}%")
    print(f'Examining every {number_of_frames} frames.')
    print(f"Continous examination is set to {args['continuous']}")
    print('\n\n')

    human_detected = False
    detection_list = []    #list of files with detected humnans
    
    #open a log file and loop over all our video files
    with open(time_stamp + '/' + time_stamp +'.txt', 'w') as log_file:
        #loop through all our video files
        video_dir = getListOfFiles(args['directory'] + '/')
        counter = 1
        for current_file in video_dir:
            print(f'Working on {current_file}: {counter} of {len(video_dir)}: {int((counter/len(video_dir)*100))}%    ', end='')
            #check for people
            if humanChecker(str(current_file), time_stamp, yolo=yolo_string, n=number_of_frames, confidence=confidence_percent, continuous=args['continuous']):
                human_detected = True
                print(f'Human detected in {current_file}')
                log_file.write(f'{current_file} \n' )
                detection_list.append(str(current_file))
            counter += 1

    #if people are detected and --twilio flag has been set, send a text
    if args['twilio'] and human_detected:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=f"Human Detected. Check log files", from_=TWILIO_FROM, to=TWILIO_TO)
    if args['twilio'] and not human_detected:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=f"All Clear.", from_=TWILIO_FROM, to=TWILIO_TO)
    
    #if people are detected and --email flag has been set, send an email
    # tyring to add ability to attach images to email
    if args['email'] and human_detected:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        
        #set up our message
        with open(time_stamp + '/' + time_stamp + '.txt' ) as f:
            msg = EmailMessage()
            msg.set_content(f.read())
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = 'Intruder Alert'
        
        list_of_files = os.listdir(time_stamp)
        #add our attachments, ignoring the .txt file
        for x in list_of_files:
            if x[-3:] != 'txt':
                with open(time_stamp + '/' + x, 'rb') as fp:
                    img_data = fp.read()
                msg.add_attachment(img_data, maintype='image', subtype=imghdr.what(None, img_data), filename=x)
        
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)

            

        