#coding:utf-8
import os
import fileObject
import re

g_mixclass_path = './MixClasses.txt'
g_mixclass_split = '<====>'

def findMixClasses():
    allMixClasses = {}
    f = open(g_mixclass_path, 'r')
    allLines = f.readlines()
    for line in allLines:
        if g_mixclass_split in line:
            splitList = line.split(g_mixclass_split)
            oriClass = splitList[0].strip()
            afterClass = splitList[1].strip()
            # print("%s : %s"%(oriClass, afterClass))
            allMixClasses[afterClass] = oriClass

    # print(len(allMixClasses))
    return allMixClasses

def findAllSrcPaths():
    allSrcPaths = fileObject.allSrcFilePath([], ['.h','.m', '.mm'])
    return allSrcPaths

def parseSrc(allLines):
    allMixClasses = findMixClasses()
    allAfterClasses = allMixClasses.keys()
    allAfterClasses = sorted(allAfterClasses,key = lambda i:len(i),reverse=True)
    newAllLines = allLines
    for afterClass in allAfterClasses:
        oriClass = allMixClasses[afterClass]
        rule = r'\n@implementation\s+%s'%(afterClass)
        exchangeCode = '\n/// ORICLASS:' + oriClass + '\n' + '@implementation ' + afterClass
        newAllLines = re.sub(rule, exchangeCode, newAllLines, 0, re.S)

        rule = r'\n@interface\s+%s\s+:'%(afterClass)
        exchangeCode = '\n/// ORICLASS:%s\n@interface %s :'%(oriClass, afterClass)
        newAllLines = re.sub(rule, exchangeCode, newAllLines, 0, re.S)
    
    return newAllLines

def addOriClassDesc():
    allSrcPaths = findAllSrcPaths()
    for srcPath in allSrcPaths:
        f = open(srcPath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        newAllLines = parseSrc(allLines)
        f.close()
        if newAllLines != allLines:
            f = open(srcPath, 'w+')
            f.write(newAllLines)
            f.close()


addOriClassDesc()

