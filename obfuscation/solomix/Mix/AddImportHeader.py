# #coding:utf-8
import os
import fileObject
import re
import shutil

g_file_type = ['.m', '.mm']

def addImport():
    allFilePaths = fileObject.allSrcFilePath([], g_file_type)
    allCount = 0
    for filePath in allFilePaths:
        f = open(filePath, 'r')
        allLines = f.read()
        isUnimport = False
        if "#import" not in allLines:
            print(os.path.basename(filePath))
            isUnimport = True
            allCount += 1
        f.close()
        if isUnimport:
            handleImport(filePath)
    print(allCount)

def handleImport(filePath):
    f = open(filePath, 'r+')
    allLines = f.readlines()
    contents = ''
    isLastLineComment = True
    for line in allLines:
        if line.startswith('//'):
            contents += line
        else:
            if isLastLineComment:
                importCode = '\n#import \"%s.h\"\n'%(os.path.splitext(os.path.basename(filePath))[0])
                contents += importCode
            isLastLineComment = False
            contents += line
    f.close()
    f = open(filePath, 'w+')
    f.write(contents)
    f.close()

addImport()

        






    