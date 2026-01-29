#!/usr/bin/env python
#coding:utf-8
import os
import fileObject
import re

g_proj_type = '.pbxproj'
g_ignore_rename_dires = ['Pods','LocalPods','UnUsedFiles','proto','originproto','Resource','LibOther','framework','.gitignore','.git','.DS_Store','Solomix.xcworkspace']
g_format_file_types = ['.h', '.m', '.mm']

def findAllFileTargets():
    
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_rename_dires, g_format_file_types)

    curPath = os.getcwd()
    logFileName = 'ClangFormat.log'
    logFilePath = os.path.join(curPath, logFileName)


    # 先删除原来的 log 文件
    os.remove(logFilePath)

    f = open(logFilePath, 'w+')
    for filePath in allFilePaths:
        f.writelines(filePath + '\n')
    return allFilePaths
    

def formatCode():
    allFilePaths = findAllFileTargets()

    for filePath in allFilePaths:
        os.system("clang-format -i %s -style=File" %(filePath))
    

formatCode()

