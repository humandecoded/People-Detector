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
`python people-detector.py -d <path to folder with video files> --twilio`

The twilio option requires you to have set up a twilio account and have an SID, a Token, a Twilio number and a verified number to send to. These values can either be hardcoded in to the script or referenced as environment variables. Functionally speaking, this feature is only useful if you're going to automate this script. 
For example: Every morning I have a cron job run that uses this script to analyze the nightime footage from my outdoor surveilance cameras. By using the --twilio flag I get a text if the script finds people on the footage and I can investigate further later.


The script will use tensorflow to analyze your files for people. It will write the results to a .txt file in your 
current folder. A blank text file means no humans were found.
  
  
## Why use this script?
I wrote this script as an automated option for analyzing backyard security footage. 
Any number of things could be triggering the motion detector on my camera.
I'm only interested in reviewing footage if people are in my backyard. 


