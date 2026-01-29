# #coding:utf-8
import os
import fileObject
import re
import shutil

g_file_type = ['.m', '.mm', '.xib', '.storyboard']
g_unsedDir_name = 'UnUsedFiles' #未引用文件存放目录，需要先手动创建
rootPath = fileObject.projNameAndRootDir()[1]  #项目根目录
unsedDir = os.path.join(rootPath,g_unsedDir_name) #这里放在根目录下，可根据需要修改

def findAllRefFiles():
    allProjFilePaths = fileObject.allSrcFilePath([], ['.pbxproj'])
    allRefFiles = []
    for projFilePath in allProjFilePaths:
        print(projFilePath)
        f = open(projFilePath, 'r')
        allLines = f.readlines()
        for line in allLines:
            for fileType in g_file_type:
                allFileNames = re.findall(r'\/\*\s+(.*%s)\s+in.*isa = PBXBuildFile'%(fileType), line, re.S)
                if len(allFileNames) > 0:
                    fileName = allFileNames[0]
                    if fileName not in allRefFiles:
                        allRefFiles.append(fileName)
        f.close()
    
    return allRefFiles

def findAllFilePaths():
    allFiles = fileObject.allSrcFilePath(["Pods","Scripts","proto","UnUsedFiles","LocalPods"], g_file_type)
    return allFiles

def moveFileToUnsedDir(filePath):
    shutil.move(filePath, unsedDir)

def findUnRefFiles():
    allRefFiles = findAllRefFiles()
    print(len(allRefFiles))
    allFilePaths = findAllFilePaths()
    print(len(allFilePaths))
    allUnRefFilePaths = []
    for filePath in allFilePaths:
        fileName = os.path.basename(filePath)
        if fileName not in allRefFiles:
            if fileName not in allUnRefFilePaths:
                allUnRefFilePaths.append(filePath)
                moveFileToUnsedDir(filePath)
                if fileName.endswith('.m'):
                    fileHeaderPath = filePath.replace('.m', '.h')
                    if not os.path.exists(fileHeaderPath):
                        print(fileHeaderPath)
                    else:
                        moveFileToUnsedDir(fileHeaderPath)
                # print(filePath)
    print(len(allUnRefFilePaths))

findUnRefFiles()






    