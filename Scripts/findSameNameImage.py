#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import fileObject
import re
import json

num = 0

def startFindSameImageDir(inputDir, originImgName):
    for fileName in os.listdir(inputDir):
        filePath = os.path.join(inputDir, fileName)
        if fileName.endswith('.imageset'):
           if fileName == originImgName:
           	  global num
           	  num = num + 1
           	  if num > 1:
           	  	print(fileName + '  -----------')

        elif '.' not in fileName: #文件夹
           # print(filePath)
           startFindSameImageDir(filePath, originImgName)
           #if fileName != 'emojis':
             # startFindSameImageDir(filePath, originImgName)
        else: # .DS_Store、 .appiconset、 .json
           continue   


def enumerateImageDir(inputDir):
    for fileName in os.listdir(inputDir):
        filePath = os.path.join(inputDir, fileName)
        if fileName.endswith('.imageset'):
           #print(fileName + '  -----------')
           global num
           num = 0
           startFindSameImageDir(inputDir, fileName)
        elif '.' not in fileName: #文件夹
           if fileName != 'emojis':
              enumerateImageDir(filePath)
        else: # .DS_Store、 .appiconset、 .json
           continue   

inputDir = '../Piko/Images.xcassets' #raw_input('请输入图片所在目录路径')
if not os.path.isdir(inputDir):
    print('请输入正确的路径')
else:
	enumerateImageDir(inputDir)
	print('处理完成！')		
