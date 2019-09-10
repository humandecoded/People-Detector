# People-Detector
High level python script that looks at a folder of video files and tells you which files contain people. 

**Requirements and getting started:

This script relies on the work done on cvlib: https://github.com/arunponnusamy/cvlib/commits?author=arunponnusamy
cvlib offers us some high level methods to detect common objects within photos or video without any experience with machine learning.

To get started (recommend creating a virtual environment):
- pip install opencv-python
- pip install tensorflow
- pip install cvlib
When you first run this script it will reach out and download the pre-trained YOLO model as well.

After that it's as simple as:
python people-detector.py -d <path to folder with video files>
The script will use tensorflow to analyze your files for people. It will write the results to a .txt file in your 
current folder. A blank text file means no humans were found.
  
  
## Why use this script?
I wrote this script as an automated option for analyzing backyard security footage. 
Any number of things could be triggering the motion detector on my camera.
I'm only interested in reviewing footage if people are in my backyard. 


