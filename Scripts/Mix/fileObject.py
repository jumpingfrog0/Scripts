# -*- coding: utf-8 -*-

import os

def getFile(dicPath,fileExten=[]):
    if not os.path.isdir(dicPath):
        error = dicPath+'dicPath is not dir'
        raise IOError(error)
        return None
    dirList = [dicPath]
    fileList = []
    for path in dirList:
        allFile = [path+'/'+thisFile for thisFile in os.listdir(path) if not thisFile.startswith('.')]
        dirList.extend([thisFile for thisFile in allFile if os.path.isdir(thisFile)])
        if len(fileExten) == 0:
            print(fileExten)
            fileList.extend(allFile)
        else:
            fileList.extend([thisFile for thisFile in allFile if os.path.splitext(thisFile)[1][1:] in fileExten])
    print('\n===========================================\n\n')
    print(fileList)
    print('\n===========================================\n')
    return fileList

# 根据文件夹查询项目名
def getProjName(dir):
    for file in os.listdir(dir):
        if file.endswith('.xcodeproj'):
           projName = os.path.splitext(file)[0]
           return projName

    return '' 
            
# 查询项目名和根目录
def projNameAndRootDir():
    curPath = os.getcwd()
    while (getProjName(curPath) == ''):
        curPath = os.path.dirname(curPath)
    projName = getProjName(curPath)
    return (projName, curPath)



defaultExcludeSrcDir = ["Pods","Scripts","proto","UnUsedFiles",".gitignore",".git",".DS_Store","ZhuiYin.xcworkspace"]
defaultSrcTypes = ['.h', '.m', '.mm']
allSrcFilePaths = []

# 排除掉excludeDir目录名(数组)符合targetTypes(数组)类型的所有文件目录，传空数组则用默认定义
def allSrcFilePath(excludeDir, targetTypes):
    allSrcFilePaths.clear()
    rootDir = projNameAndRootDir()[1]
    recursiveSrcFilePath(rootDir, excludeDir, targetTypes)
    return allSrcFilePaths      

def recursiveSrcFilePath(rootPath, excludeDir, targetTypes):
    isDir = os.path.isdir(rootPath)
    if isDir:
        for file in os.listdir(rootPath):
            exclude = defaultExcludeSrcDir
            if len(excludeDir) > 0:
                exclude = excludeDir
            if file in exclude:
                continue
            filePath = os.path.join(rootPath, file)
            recursiveSrcFilePath(filePath, excludeDir, targetTypes)
    else:
        fileType = os.path.splitext(rootPath)[1]
        srcTypes = defaultSrcTypes
        if len(targetTypes) > 0:
            srcTypes = targetTypes
        if fileType in srcTypes:
            allSrcFilePaths.append(rootPath)

allFilePaths = []

# 工程下所有文件路径，有缓存
def allProjFilePaths():
    if len(allFilePaths) > 0 :
        return allFilePaths
    
    rootDir = projNameAndRootDir()[1]
    recursiveFilePath(rootDir)
    return allFilePaths


def recursiveFilePath(path):
    isDir = os.path.isdir(path)
    if isDir:
        for fileName in os.listdir(path):
            recursiveFilePath(os.path.join(path, fileName))
    else:
        allFilePaths.append(path)

# 工程下所有以<name>结尾的文件路径
def allFilePathsEndwith(name):
    dir_list = []

    if len(name) == 0:
        return dir_list
    
    filePaths = allProjFilePaths()
    for filePath in filePaths:
        fileName = os.path.split(filePath)[1]
        if fileName.endswith(name):
            dir_list.append(filePath)
    
    return dir_list

def _recursiveDic(dirPath, file_list, ext_list):
    for dir in os.listdir(dirPath):

        file_path = os.path.join(dirPath, dir)

        if os.path.isdir(file_path):
            _recursiveDic(file_path, file_list, ext_list)

        else :

            fileName, fileExt = os.path.splitext(file_path)
            if fileExt in ext_list:
                file_list.append(file_path);


def recursiveDir(path, extList):
    fileList = []
    isDir = os.path.isdir(path)
    if isDir:
        _recursiveDic(path, fileList, extList)

    return fileList

def allIncludeSrcFilePath(includeDir, targetTypes):
    allIncludeSrcFilePaths = []
    filePaths = allProjFilePaths()
    for filePath in filePaths:
        for dirName in includeDir:
            aDirName = dirName + '/'
            if aDirName in filePath:
                allIncludeSrcFilePaths.append(filePath)
    return allIncludeSrcFilePaths;    

def walkFilesInPath(rootDir, fileHandler, handlerArgs = (), fileExtList = defaultSrcTypes, excludeDir = defaultExcludeSrcDir):
    for dir in os.listdir(rootDir):
        if dir in excludeDir:
            continue

        path = os.path.join(rootDir, dir)

        if os.path.isdir(path):
            walkFilesInPath(path, fileHandler, handlerArgs, fileExtList, excludeDir)
        else :
            fileName, fileExt = os.path.splitext(path)
            if fileExt in fileExtList:
                fileHandler(path, handlerArgs)


