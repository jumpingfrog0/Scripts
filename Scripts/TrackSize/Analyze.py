#!/usr/bin/env python
#coding:utf-8

import os
import fileObject
import sys

# 查询项目中所有文件类型
def allProjFileTypes():
    allTypes = []

    allFilePaths = fileObject.allProjFilePaths()
    for filePath in allFilePaths:
        fileType = os.path.splitext(filePath)[1]
        if fileType not in allTypes:
            allTypes.append(fileType)
    print(allTypes)

def fileSizeDesc(fileBytes):
    kilo = 1000
    desc = ''
    if fileBytes < kilo:
        desc = str(fileBytes) + 'Bytes'
    elif fileBytes < kilo * kilo:
        fileKB = (int)(fileBytes / kilo)
        desc = str(fileKB) + 'KB'
    elif fileBytes < kilo * kilo * kilo:
        fileMB = round((fileBytes/ (kilo * kilo)), 1)
        desc = str(fileMB) + 'MB'
    else:
        fileGB = round((fileBytes/ (kilo * kilo * kilo)), 2)
        desc = str(fileGB) + 'GB'
    return desc

def analyzeProjFile():
    if sys.version_info[0] < 3:
        print('当前Python版本信息:' + sys.version)
        print('请先升级到Python 3运行此脚本!')
        return

    largeImageSize = 50 * 1000 #大图片尺寸定义：50KB
    allTypes = [
        {'src' : ['.h', '.m', '.mm', '.swift', '.c', '.cpp']},
        {'image' : ['.png', '.jpg', '.jpeg', '.gif', '.webp']},
        {'audio' : ['.mp3', '.wav', '.aac']},
        {'video' : ['.mp4', '.mov', '.avi', '.rmvb']},
        {'xib' : ['.xib', '.storyboard', '.nib']},
        {'svga' : ['.svga']},
        {'lib' : ['.a']},
        {'h5' : ['.js', '.html']},
        {'text' : ['.md', '.txt', '.markdown']},
        {'font' : ['.otf', '.ttf']},
        {'shell' : ['.sh', '.py', '.rb']},
        ]
    
    newTypeList = []

    largeSizeImageList = []

    for mainTypeDict in allTypes:
        mainType = list(mainTypeDict.keys())[0]
        subTypes = list(mainTypeDict.values())[0]
        subTypeList = []
        for subType in subTypes:
            subTypeDict = {subType : []}
            subTypeList.append(subTypeDict)
        newMainTypeDict = {mainType : subTypeList}
        newTypeList.append(newMainTypeDict)

    allFilePaths = fileObject.allProjFilePaths()
    for filePath in allFilePaths:
        fileType = os.path.splitext(filePath)[1] # fileType eg:.h
        for newTypeDict in newTypeList: # newTypeDict eg:{'src': [{'.h': []}, {'.m': []}, {'.mm': []}, {'.swift': []}, {'.c': []}, {'.cpp': []}]}
            newTypeKey = list(newTypeDict.keys())[0] # newTypeKey eg:src
            allNewSubTypeList = list(newTypeDict.values())[0] # newSubTypeList eg:[{'.h': []}, {'.m': []}, {'.mm': []}, {'.swift': []}, {'.c': []}, {'.cpp': []}]
            for newSubTypeDict in allNewSubTypeList: #newSubTypeDict eg:{'.h': []}
                newSubType = list(newSubTypeDict.keys())[0] #newSubType eg:.h
                newSubTypeList = list(newSubTypeDict.values())[0] 
                if newSubType == fileType:
                    fileSize = os.path.getsize(filePath)
                    fileInfo = {'size' : fileSize, 'path' : filePath}
                    newSubTypeList.append(fileInfo)

                    if newTypeKey == 'image' and fileSize >= largeImageSize:
                        largeSizeImageList.append(fileInfo)
    
    mainTypeList = []
    for mainTypeDict in newTypeList:
        mainTypeKey = list(mainTypeDict.keys())[0]  # mainTypKey eg:src
        mainTypeCount = 0
        mainTypeSize = 0
        typeList = list(mainTypeDict.values())[0]
        subTypeInfoList = []
        for subTypeDict in typeList:
            subTypeKey = list(subTypeDict.keys())[0]  #subTypeKey eg:.m
            subTypeSize = 0
            subTypeList = list(subTypeDict.values())[0]
            subTypeCount = len(subTypeList)
            mainTypeCount = mainTypeCount + subTypeCount
            if subTypeCount > 0 :
                for fileInfo in subTypeList:
                    fileSize = fileInfo['size']
                    subTypeSize = subTypeSize + fileSize
                    mainTypeSize = mainTypeSize + fileSize
                subTypeInfo = [subTypeKey, subTypeCount, subTypeSize]
                subTypeInfoList.append(subTypeInfo)
        if len(subTypeInfoList) > 0:
            mainTypeInfo = [mainTypeKey, mainTypeCount, mainTypeSize, subTypeInfoList]
            mainTypeList.append(mainTypeInfo)
    
    print('=============工程文件归类统计===============')

    for mainTypeInfo in mainTypeList:
        mainTypeKey = mainTypeInfo[0]
        mainTypeCount = mainTypeInfo[1]
        mainTypeSize = fileSizeDesc(mainTypeInfo[2])
        subTypeInfoList = mainTypeInfo[3]
        print('* %s %s个 %s'%(mainTypeKey.upper(), mainTypeCount, mainTypeSize))
        for subTypeInfo in subTypeInfoList:
            subTypeKey = subTypeInfo[0]
            subTypeCount = subTypeInfo[1]
            subTypeSize = fileSizeDesc(subTypeInfo[2])
            print('    * %s %s个 %s'%(subTypeKey, subTypeCount, subTypeSize))
        print('------------------------')


    if len(largeSizeImageList) > 0 :
        print('=============大图片资源===============')
        largeSizeImageList.sort(key=lambda x:x.get('size', 0), reverse=True)
        for fileInfo in largeSizeImageList:
            fileSize = fileInfo['size']
            filePath = fileInfo['path']
            sizeDesc = fileSizeDesc(fileSize)
            fileIndex = largeSizeImageList.index(fileInfo) + 1
            print('%s、图片大小:%s 路径:%s'%(fileIndex, sizeDesc, filePath))


analyzeProjFile()
    