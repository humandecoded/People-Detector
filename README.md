# People-Detector
High level python script that looks at a folder and tells you which video and/or image files contain people. Saves snapshots of those detections and a log file of all detections. Note: It is recursive. You can scan a folder of folders. This will skip over non-image/video files.
Check out a demo at: https://youtu.be/q_o1P9zzW1o
Update: This script can now take advantage of a CUDA capable gpu. I've put together a how to in a separate blog post: https://humandecoded.io/tensorflow-2-1-and-opencv-4-2-running-on-gpu/

## Why I made this script?
I wrote this script after having my backyard shed broken in to as well as the car in my driveway. After each break-in I placed a motion activated camera in the respective area. My goal here is not to catch people "in the act" but instead be alerted that people have been creeping around my backyard or checking the cars in my driveway for unlocked doors. There is way too much natural motion in these areas for me to review footage every time the camera detects motion. This script will automate the "busy work" and let me know what clips I might want to look in to.
 
My hope hear is to catch a pattern of behavior. For example, "Every Sunday night someone tries the car doors in my driveway"

## How do I use this script?
I have an old Imac I use as a dvr for my camera system. Every morning I have a shell script that does the following:
- use rsync to pull in all new footage from my dvr(imac) on to my main home machine
- filter out any unwanted footage based off camera location and time stamp, leaving me with only my backyard and driveway night footage.
- run this script on that footage, sending me a text and email alert if it detects a person shaped object in any of that footage along with screenshots of the "people" it detects.

## Requirements and getting started:

This script relies on the work done on cvlib: https://github.com/arunponnusamy/cvlib
cvlib offers us some high level methods to detect common objects within photos or videos without any experience with machine learning.

## Tensorflow 2 does not yet support Python 3.8. Tensorflow 2.2 will add 3.8 support. You will want to create a virtual environment for python 3.7 before getting started. If you try to ` pip install tensorflow` from Python 3.8 it will not find tensorflow

## Requirements 
* First, activate your Python 3.7 virtual env
* `pip install tensorflow`
* `pip install cvlib`
* `pip install opencv-python`
* `pip install twilio`

When you first run this script it will reach out and download the pre-trained YOLO model as well.

After that it's as simple as:
* `python people-detect.py -d <path to folder>`
* or
* `python people-detect.py -f <path to file>`

There are a number of optional flags outlined below.

The default ML model is 'yolov3'. This model is big and CPU intensive. The `--tiny_yolo` flag will give you the smaller model that is faster but less accurate.

The `--twilio` flag allows you to send text alerts but requires you to have set up a twilio account and have an SID, a Token, a Twilio number and a verified number to send to. You can learn more about this here: https://www.twilio.com/docs/sms/quickstart/python. These values can either be hardcoded in to the script or referenced as environment variables. Examine the script for where this happens.

The `--email` option requires you to have a gmail account set to allow "less secure" sign ins. I recommend setting up a separate account you will only use for sending yourself logs. You can learn more about this here:
https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
You can hard code your credentials in to the script but I recommend referencing env variables instead. Print out of log file is placed in body. Screenshots of detected humans are attached to the email.

The `--continuous` flag will examine the entire clip for human detections. The default behavior is to stop after first detection. 

The `--frames n`  flag sets the program to examine every `n`th frame. The default is every 10th frame.

The `--confidence n`  flag will adjust the confidence threshold that trips a detection alert to `n`. The default is 65.


Functionally speaking, the email and twilio options only make sense if you intend to use this script in an automated workflow. See above for how I use it. 

When ran, this script creates a folder named after the current date and time. As it finds frames with people in them it will save a jpeg of that frame in to the folder. It includes a border box around common objects as well as a confidence percentage. This gives you a good idea of what it thinks are people and how confident it is. At the end it will also save a log file of all video files containing people. 

I recommend testing in your selected environment(s) and time(s) of day to make sure it will work for you. So far, the yolov3-tiny model has not proved accurate enough for me. The default is the full yolo model.
  
Check out a demo at: https://youtu.be/q_o1P9zzW1o 





