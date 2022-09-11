# -*- coding: utf-8 -*-

import csv
import json
from re import sub
import time
from pprint import pprint
from pytube import YouTube
import cv2
import os
from os.path import exists
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, './backend')
from extractor import SubtitleExtractor
import sys

IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
  print('*** INFO: Running on CoLab ***')
else:
  print('*** INFO: Not running on CoLab ***')

folderWrk = './bulk'
folderDownload = folderWrk + '/download'

fileList = folderWrk + '/list.csv'
fileDone = folderWrk + '/done.csv'
fileChannels = folderWrk + '/channels.csv'
fileVideoPath = folderWrk + '/video_path.tmp'

hasMargin = True
marginPercentage = 1
marginSize = 10

def signal_handler(signum, frame):
    print('You pressed Ctrl+C!')
    exit(0)
    
def searchFile(file_path, word):
    with open(file_path, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            # check if string present on a current line
            if line.find(word) != -1:
                return lines.index(line) + 1
    return False

def getChannels():
    with open(fileChannels, mode='r') as infile:
      readerChannels = csv.reader(infile)
      dictChannels = {rows[1]: dict(name=rows[0], id=rows[1], resolution=rows[2], margins=rows[3]) for rows in readerChannels}
    return dictChannels

def getChannelSubtitleArea(ytId, height):
    yt = YouTube('https://youtube.com/watch?v=' + ytId)
    print('--- %s --- %s --- %s ---' % (ytId, yt.title, yt.author))
    videoDetails = yt._vid_info['videoDetails']
    channelId = videoDetails['channelId']
    print(channelId)
    # pprint(vars(yt))
    # jsonInfo = json.loads(yt._vid_info)
    # jsonInfo = json.dumps(yt._vid_info, indent=4)
    # pprint(jsonInfo)
    
    channels = getChannels()
    if channelId not in channels:
      return False
    channel = channels[channelId]
    # pprint(channel)
    if int(channel['resolution']) != height:
      return False
    y_min, y_max, x_min, x_max = channel['margins'].split(',')
    
    return (int(y_min), int(y_max), int(x_min), int(x_max))
  
def getSubtitleArea(video_path, ytId):
    vid = cv2.VideoCapture(video_path)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

    y_min=0
    y_max=int(height)
    x_min=0
    x_max=int(width)
    
    
    subtitle_area = getChannelSubtitleArea(ytId, height)
    if not subtitle_area:
      print('Get Default Subtitle Area')
      subtitle_area = (y_min, y_max, x_min, x_max) # full area
      
      if hasMargin and marginPercentage > 0:
        marginSizeY = int(y_max * marginPercentage / 100)
        marginSizeX = int(x_max * marginPercentage / 100)
        y_min = 0 + marginSizeY
        y_max = y_max - marginSizeY
        x_min = 0 + marginSizeX
        x_max = x_max - marginSizeX
        subtitle_area = (y_min, y_max, x_min, x_max)
    else:
      print('Channel found with Subtitle Area')

    # (224,988,0,1920)
    # subtitle_area = (224, 988, 0, 1920)
    # subtitle_area = None    
    
    y_min, y_max, x_min, x_max = subtitle_area
    print('Area:\t\ty_min\ty_max\tx_min\tx_max')
    print('Values:\t\t' + str(y_min) + '\t' + str(y_max) + '\t' + str(x_min) + '\t' + str(x_max))
    
    return subtitle_area


def extractSubs(ytId, lang):
    if not exists(fileVideoPath):
      print('No video path found in: ' + fileVideoPath)
      exit()
      
    with open(fileVideoPath, 'r') as file:
      video_path = file.read().rstrip()
    print('Video path: ' + video_path)

    subtitle_area = getSubtitleArea(video_path, ytId)
    se = SubtitleExtractor(video_path, subtitle_area, lang[0:2])
    se.run()
    
def downloadYT(ytId, fileMp4):
    if exists(fileMp4):
      print('File exists, no need to download: ' + fileMp4)
      return True
    else:
      print('Download file: ' + fileMp4)
      
      try:
        # YouTube('https://youtu.be/' + ytId).streams.first().download()
        yt = YouTube('https://youtube.com/watch?v=' + ytId)
        # resolucoes = yt.streams.all()
        # for i in resolucoes:  # mostra as resoluções disponíveis
        #   print(i)
        # exit()
  
        # yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(folderDownload, ytId + '.mp4')
        yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first().download(folderDownload, ytId + '.mp4')
        
        print('Download complete YT: %s to: %s' % (ytId, fileMp4))
        return True
      except:
        print('XXX Warning: Download failed YT: %s to: %s' % (ytId, fileMp4))
      
    return False

def processYT(ytId, lang):
    print('Processing YT: ' + ytId)

    fileSrtTmp = folderDownload + '/' + ytId + '.srt'
    fileSrt = fileSrtTmp
    fileMp4 = folderDownload + '/' + ytId + '.mp4'
    if lang and lang != "":
      fileSrt = folderDownload + '/' + ytId + '.' + lang + '.srt'
    
    downloadSuccess = downloadYT(ytId, fileMp4)
    
    if not downloadSuccess:
      return False            

    with open(fileVideoPath, 'w') as fd:
        fd.write(fileMp4)
    
    print('Written video path in: ' + fileVideoPath)
    
    if exists(fileSrt):
      print('File exists, no need to extract: ' + fileSrt)
      return False
    else:
      print('Extracting file: ' + fileSrt)
      extractSubs(ytId, lang)
      print('Waiting for 5 seconds')
      time.sleep(5)
      os.rename(fileSrtTmp, fileSrt)
      
    if exists(fileSrt):
      print('Extraction complete: ' + fileSrt)
      
      if IN_COLAB:
        from google.colab import files
        files.download(fileSrt) 

      os.remove(fileMp4)
      os.remove(fileVideoPath)
      with open(fileDone, 'a') as fd:
          fd.write(ytId + "\n") 
    else:
      print('Extraction failed: ' + fileSrt)
      exit()
