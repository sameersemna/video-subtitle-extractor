# -*- coding: utf-8 -*-

import signal
import csv
import multiprocessing
from common import searchFile, processYT, fileList, fileDone, signal_handler

signal.signal(signal.SIGINT, signal_handler)

def processList(inputList):
    fileData = open(inputList)
    dataLen = len(fileData.readlines())
    
    with open(inputList, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        rowNo = 0
        for row in datareader:
            rowNo = rowNo + 1
            ytId = row[0]
            lang = row[1]
            print('*************** %s / %s %s (%s) ***************' % (rowNo, dataLen, ytId, lang))
            
            lineNum = searchFile(fileDone, ytId)
            if lineNum != False:
                print('Processed earlier, found YT: %s, in Done list at Line No. %s' % (ytId, lineNum))
                continue
            
            processSuccess = processYT(ytId, lang)
            
            if not processSuccess:
              continue
                
            # exit()
            
if __name__ == '__main__':
  multiprocessing.set_start_method("spawn")
  processList(fileList)