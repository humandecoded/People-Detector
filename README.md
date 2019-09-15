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
`python people-detector.py -d <path to folder with video files>`
or
`python people-detector.py -d <path to folder with video files> --twilio --email`

The twilio option requires you to have set up a twilio account and have an SID, a Token, a Twilio number and a verified number to send to. These values can either be hardcoded in to the script or referenced as environment variables.

The email option requires you to have a gmail account set to allow "less secure" sign ins. I reccomend setting up a separate account you will only use for sending yourself logs. You can learn more about this here:
https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development

Functionally speaking, the email and twilio options only make sense if you intend to use this script in an automated workflow. See below for how I use it. 

The script will use tensorflow to analyze your files for people. It will write the results to a .txt file in your 
current folder. A blank text file means no humans were found. 
  
## Why use this script?
I wrote this script as an automated option for analyzing backyard security footage. 
Any number of things could be triggering the motion detector on my camera.
I'm only interested in reviewing footage if people are in my backyard. 

## How do I use this script?
I have an old imac I use as a dvr for my camera system. Every morning I have a script that does the following:
- use rsync to pull in all new footage from my dvr(imac) on to my main home machine
- filter out any unwanted footage based off camera location and time stamp, leaving me with only my backyard night footage
- run this script on that footage, sending me a text and email alert if it detects a person in my backyard at night



