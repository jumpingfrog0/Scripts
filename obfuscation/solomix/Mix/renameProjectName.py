#coding:utf-8
import os
import shutil
import fileObject

g_preProjName = 'klcOtoVoice'
g_ignoreFileAndDir = ['Pods','Scripts','Podfile.lock','xcworkspace','.git']
g_replaceNameMap = {'klcOtoVoice':'Solomix'}
g_contentTextsPch = ['klcOtoVoice']
g_contentTextsPodfile = ['klcOtoVoice']
g_contentTextsProj = ['klcOtoVoice','klcOtoVoice.','klcOtoVoice-','klcOtoVoice/','klcOtoVoice ','klcOtoVoice;', '/klcOtoVoice']
g_subXcodeprojNames = ['klcOtoVoice.xcodeproj','klcOtoVoice.xcodeproj']
g_modifyDirNames = ['klcOtoVoice']
g_xcworkspaceName = 'klcOtoVoice.xcworkspace'

def filePathsWithTypeAndName(fileTypes, fileNames):
    allPaths = fileObject.allSrcFilePath(g_ignoreFileAndDir, fileTypes)
    # print(allPaths)
    matchedPaths = []
    for filePath in allPaths:
        subFile = os.path.split(filePath)[1]
        fileName = os.path.splitext(subFile)[0]
        # print(fileName)
        isMatched = False
        for name in fileNames:
            if name in fileName:
                isMatched = True
                break
        if isMatched:
            print(filePath)
            matchedPaths.append(filePath)
    return matchedPaths

def dirPathsWithDirName(extDirNames):
    rootDir = fileObject.projNameAndRootDir()[1]
    dirPaths = []
    for parent, dirnames, filenames in os.walk(rootDir, topdown=False):
        for dirname in dirnames:
            if dirname in extDirNames:
                srcDir = os.path.join(parent, dirname)
                dirPaths.append(srcDir)
                print(srcDir)
                continue
    return dirPaths
            
def replaceName(name):
    retName = name
    for key in g_replaceNameMap.keys():
        if key in retName:
            value = g_replaceNameMap[key]
            retName = retName.replace(key, value, 1)
    # print(retName)
    return retName
        
def modifyFileContent(filePaths, replaceTexts):
    for filePath in filePaths:
        f = open(filePath, 'r')
        allLines = f.read()
        for text in replaceTexts:
            repText = replaceName(text)
            allLines = allLines.replace(text, repText)
        f.close()
        f = open(filePath, 'w')
        f.write(allLines)
        f.close()

def modifyFileOrDirName(filePaths, replaceTexts):
    for filePath in filePaths:
        subFile = os.path.split(filePath)[1]
        newSubFile = subFile
        for text in replaceTexts:
            repText = replaceName(text)
            newSubFile = newSubFile.replace(text, repText)
        if subFile != newSubFile:
            newFilePath = os.path.join(os.path.split(filePath)[0], newSubFile)
            print('oriFilePath = %s newFilePath = %s'%(filePath, newFilePath))
            os.rename(filePath, newFilePath)


def handleModifyContent():
    podfilePaths = filePathsWithTypeAndName([''],['Podfile'])
    modifyFileContent(podfilePaths, g_contentTextsPodfile)
    pchPaths = filePathsWithTypeAndName(['.pch'],[g_preProjName])
    modifyFileContent(pchPaths, g_contentTextsPch)
    xcschemePaths = filePathsWithTypeAndName(['.xcscheme'],[g_preProjName])
    modifyFileContent(xcschemePaths, [g_preProjName])
    projPaths = filePathsWithTypeAndName(['.pbxproj'],['project'])
    modifyFileContent(projPaths, g_contentTextsProj)

def handleModifyFile():
    filePaths = filePathsWithTypeAndName(['.xcconfig','.entitlements','.plist','.pch','.xcscheme'],[g_preProjName])
    modifyFileOrDirName(filePaths, [g_preProjName])
    projDirPaths = dirPathsWithDirName(g_subXcodeprojNames)
    modifyFileOrDirName(projDirPaths, [g_preProjName])

def handleModifyDir():
    dirPaths = dirPathsWithDirName(g_modifyDirNames)
    modifyFileOrDirName(dirPaths, [g_preProjName])

def deleteOriXcworkspace():
    xcworkspcePath = dirPathsWithDirName([g_xcworkspaceName])
    shutil.rmtree(xcworkspcePath[0])

    
# matchedPaths = filePathsWithTypeAndName(['.xcconfig','.entitlements','.plist','.pch','.xcscheme'],['Piko'])
# modifyFileOrDirName(matchedPaths, ['Piko'])
# dirPaths = dirPathsWithDirName(['Piko.xcodeproj','PikoCore.xcodeproj','PikoFramework.xcodeproj','PikoWidget','PikoNotificationService','PikoFramework','PikoCore','Piko'])
# modifyFileOrDirName(dirPaths, ['Piko'])
# retName = replaceName('PikoTest')
# xcworkspce = dirPathsWithDirName(['Piko.xcworkspace'])
# filePathsWithTypeAndName(['.pbxproj'],['project'])

def main():
    handleModifyContent()
    handleModifyFile()
    handleModifyDir()
    deleteOriXcworkspace()
        

if __name__ == '__main__':
    main()