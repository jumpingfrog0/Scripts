#coding:utf-8
import os
import fileObject
import re

g_mixclass_path = './MixClasses.txt'
g_mixclass_split = '<====>'
g_oriClass_pre = 'MB'
g_proj_type = '.pbxproj'
g_ignore_rename_dires = ['Pods','LocalPods','UnUsedFiles','proto','originproto','OrangeFilter']
g_rename_file_types = ['.h', '.m', '.mm', '.xib', '.storyboard', g_proj_type, '.pch']


def findMixClasses():
    allMixClasses = {}
    f = open(g_mixclass_path, 'r')
    allLines = f.readlines()
    for line in allLines:
        if g_mixclass_split in line:
            splitList = line.split(g_mixclass_split)
            oriClass = splitList[0].strip()
            afterClass = splitList[1].strip()
            if oriClass.startswith(g_oriClass_pre):
                # print("%s : %s"%(oriClass, afterClass))
                allMixClasses[oriClass] = afterClass

    print(len(allMixClasses))
    return allMixClasses

def findAllClassTargets():
    allFilePaths = fileObject.allSrcFilePath(g_ignore_rename_dires, g_rename_file_types)
    # print('\n'.join(allFilePaths))
    # print(len(allFilePaths))
    return allFilePaths

def renameMixClass():
    allFilePaths = findAllClassTargets()
    allMixClasses = findMixClasses()
    allOriClasses = allMixClasses.keys()
    allOriClasses = sorted(allOriClasses,key = lambda i:len(i),reverse=True)

    for filePath in allFilePaths:
        fileName = os.path.basename(filePath)
        # fileClassName = os.path.splitext(fileName)[0]
        f = open(filePath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        f.close()
        newAllLines = allLines

        mixFilePath = filePath
        for oriClassName in allOriClasses:
            mixClassName = allMixClasses[oriClassName]
            if fileName.endswith(g_proj_type):
                newAllLines = newAllLines.replace(oriClassName, mixClassName)
            else:
                newAllLines = newAllLines.replace(oriClassName, mixClassName)

            mixFilePath = mixFilePath.replace(oriClassName, mixClassName)

        if newAllLines != allLines:
            f = open(filePath, 'w+')
            f.write(newAllLines)
            f.close()
            # print(filePath)

        if mixFilePath != filePath:
            # print('%s -> %s'%(filePath, mixFilePath))
            os.renames(filePath, mixFilePath)
            pass

renameMixClass()

