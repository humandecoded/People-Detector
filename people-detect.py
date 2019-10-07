
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



#function takes a file name(full path), checks that file for human shaped objects
#saves the frames with people detected into directory named 'save_directory'
def humanChecker(video_file_name, save_directory, yolo='yolov3', continuous=False, nth_frame=10, confidence=.65):
    #open video stream
    vid = cv2.VideoCapture(video_file_name)

    #tracking if we've found a human or not
    is_human_found = False 

    #get approximate frame count for video
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'{frame_count} frames')

    #we'll need to increment every time a person is detected
    person_detection_counter = 0   

    #look at every nth_frame of our video file, run frame through detect_common_objects
    #Increase 'nth_frame' to examine fewer frames and increase speed. Might reduce accuracy though.
    for frame_number in range(1, frame_count - 3, nth_frame):
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        _ , frame = vid.read()
        bbox , labels, conf = cvlib.detect_common_objects(frame, model=yolo, confidence=confidence)
        
        if 'person' in labels:
            person_detection_counter += 1
            is_human_found = True

            #create image with bboxes showing objects and save
            marked_frame = cvlib.object_detection.draw_bbox(frame, bbox, labels, conf, write_conf=True)
            save_file_name = os.path.basename(os.path.normpath(video_file_name)) + '-' + str(person_detection_counter) + '.jpeg'
            cv2.imwrite(save_directory + '/' + save_file_name , marked_frame)

            if continuous == False:
                break
            
    return is_human_found




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




def twilioAlertSender(human_detected, TWILIO_TOKEN, TWILIO_SID, TWILIO_FROM, TWILIO_TO):
     #if people are detected and --twilio flag has been set, send a text
    if human_detected:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=f"Human Detected. Check log files", from_=TWILIO_FROM, to=TWILIO_TO)
    else:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=f"All Clear.", from_=TWILIO_FROM, to=TWILIO_TO)




def emailAlertSender(save_directory, SENDER_EMAIL, SENDER_PASS, RECEIVER_EMAIL):
    
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
        
    #set up our message body as contents of log file
    with open(save_directory + '/' + save_directory + '.txt' ) as f:
        msg = EmailMessage()
        msg.set_content(f.read())

    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = 'Intruder Alert'
    
    list_of_files = os.listdir(save_directory)
    #add our attachments, ignoring the .txt file
    for image_file_name in list_of_files:
        if image_file_name[-3:] != 'txt':
            with open(save_directory + '/' + image_file_name, 'rb') as image:
                img_data = image.read()
            msg.add_attachment(img_data, maintype='image', subtype=imghdr.what(None, img_data), filename=image_file_name)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.send_message(msg)




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

    every_nth_frame = args['frames']
    confidence_percent = args['confidence'] / 100

    #create a directory to hold snapshots and log file
    time_stamp = datetime.now().strftime('%m%d%Y-%H:%M:%S')
    os.mkdir(time_stamp)
    
    print('Beginning Detection')
    print(f'Directory {time_stamp} has been created')
    print(f"Email notifications set to {args['email']}. Text notification set to {args['twilio']}.")
    print(f"Confidence threshold set to {args['confidence']}%")
    print(f'Examining every {every_nth_frame} frames.')
    print(f"Continous examination is set to {args['continuous']}")
    print('\n\n')

    human_detected = False
    
    #open a log file and loop over all our video files
    with open(time_stamp + '/' + time_stamp +'.txt', 'w') as log_file:
        
        video_directory_list = getListOfFiles(args['directory'] + '/')
        
        #what video we are on
        working_on_counter = 1
        
        for video_file in video_directory_list:
            print(f'Working on {video_file}: {working_on_counter} of {len(video_directory_list)}: {int((working_on_counter/len(video_directory_list)*100))}%    ', end='')
            
            #check for people
            if humanChecker(str(video_file), time_stamp, yolo=yolo_string, nth_frame=every_nth_frame, confidence=confidence_percent, continuous=args['continuous']):
                human_detected = True
                print(f'Human detected in {video_file}')
                log_file.write(f'{video_file} \n' )
            working_on_counter += 1
    
    if args['twilio']:
        twilioAlertSender(human_detected, TWILIO_TOKEN, TWILIO_SID, TWILIO_FROM, TWILIO_TO)
    
    if args['email'] and human_detected:
        emailAlertSender(time_stamp, SENDER_EMAIL, SENDER_PASS, RECEIVER_EMAIL)
    

    
    
    

            

        