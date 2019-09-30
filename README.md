# People-Detector
High level python script that looks at a folder of video files and tells you which files contain people. Note: It is recursive. you can have a folder of video folders as well. 

**Requirements and getting started:**

This script relies on the work done on cvlib: https://github.com/arunponnusamy/cvlib
cvlib offers us some high level methods to detect common objects within photos or video without any experience with machine learning.

To get started (recommend creating a virtual environment):
- `pip install opencv-python`
- `pip install tensorflow`
- `pip install cvlib`
- `pip install twilio`

When you first run this script it will reach out and download the pre-trained YOLO model as well.

After that it's as simple as:
- `python people-detector.py -d <path to folder with video files>`

There are a number of optional flags outlined below.

The default model is 'yolov3'. This model is CPU intensive. The `--tiny_yolo` flag will give you the smaller model that is faster but less accurate.

The `--twilio` flag requires you to have set up a twilio account and have an SID, a Token, a Twilio number and a verified number to send to. These values can either be hardcoded in to the script or referenced as environment variables. Examine the script for where this happens.

The `--email` option requires you to have a gmail account set to allow "less secure" sign ins. I reccomend setting up a separate account you will only use for sending yourself logs. You can learn more about this here:
https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
You can hard code your credentials in to the script but I recommend referencing env variables instead. Print out of log file is placed in body. Screenshots of detected humans are attached to the email.

The `--continuous` flag will examine the entire clip for human detections. The default behavior is to stop after first detection. 

The `--frames` flag sets the program to examine every nth frame. The default is every 10th frame.

The `--confidence` flag will adjust the confidence level that trips a detection alert. The default is 65%.


Functionally speaking, the email and twilio options only make sense if you intend to use this script in an automated workflow. See below for how I use it. 

The script will use tensorflow to analyze your files for people. It creates a folder named after the current date and time. As it finds frames with people in them it will save a jpeg of that frame in to that folder. It includes a border box around common objects as well as a confidence percentage. This gives you a good idea of what it thinks are people and how confident it is. At the end it will also save a log file of all video files containing people. 

I recommend testing in your selected environment(s) and time(s) of day to make sure it will work for you. So far, the yolov3-tiny model has not proved accurate enough for me. The default is the full yolo model.
  
## Why use this script?
I wrote this script as an automated option for analyzing outdoor security footage. 

Any number of things could be triggering the motion detector on my camera.

I'm only interested in reviewing footage containing people around my house. 

## How do I use this script?
I have an old Imac I use as a dvr for my camera system. Every morning I have a script that does the following:
- use rsync to pull in all new footage from my dvr(imac) on to my main home machine
- filter out any unwanted footage based off camera location and time stamp, leaving me with only my backyard and driveway night footage
- run this script on that footage, sending me a text and email alert if it detects a person shaped object in any of that footage



