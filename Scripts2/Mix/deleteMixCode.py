#coding:utf-8
import os
import fileObject
import re

g_mix_class_dirs = ['DownloadEar','AapamoorEmojis','ShortestExpense','DisplayEntrance']
g_mix_class_type = ['.h', '.m']
g_src_class_type = ['.h', '.m', '.mm']
g_mix_method_pre = 'zymethod_'

def findMixClassPaths():
    allMixPaths = fileObject.allIncludeSrcFilePath(g_mix_class_dirs, g_mix_class_type)
    # print('\n'.join(allMixPaths))
    # print(len(allMixPaths))
    return allMixPaths

def findProjectPaths():
    allProPaths = fileObject.allFilePathsEndwith('.pbxproj')
    allPaths = []
    for path in allProPaths:
        if 'Pods/' not in path:
            allPaths.append(path)

    # print(allPaths)
    return allPaths

def removeProjectRefs():
    allProPaths = findProjectPaths()
    mixClassPaths = findMixClassPaths()
    for path in allProPaths:
        f = open(path, 'r')
        allLines = f.readlines()
        newLines = ''
        for line in allLines:
            isMixRef = False
            for mixPath in mixClassPaths:
                fileName = os.path.basename(mixPath)
                if fileName in line:
                    isMixRef = True
            if not isMixRef:
                newLines = newLines + line
        
        f.close()
        f = open(path, 'w+')
        f.write(newLines)
        f.close()

def removeMixFiles():
    mixClassPaths = findMixClassPaths()
    for classPath in mixClassPaths:
        os.remove(classPath)

def findAllSrcPaths():
    allSrcPaths = fileObject.allSrcFilePath([], g_src_class_type)
    # print(len(allSrcPaths))
    return allSrcPaths

def removeMixImports(allLines):
    allMixClassNames = []
    mixClassPaths = findMixClassPaths()
    for classPath in mixClassPaths:
        classBaseName = os.path.basename(classPath)
        className = os.path.splitext(classBaseName)[0]
        if className not in allMixClassNames:
            allMixClassNames.append(className)
    
    newAllLines = allLines
    allMixClassNames = sorted(allMixClassNames,key = lambda i:len(i),reverse=True)
    for className in allMixClassNames:
        oriCode = '#import "%s.h"\n'%(className)
        afterCode = ''
        newAllLines = newAllLines.replace(oriCode, afterCode)

    return newAllLines

def removeMixFuncsAndPros(allLines):
    rule = r'[+-]\s?\([ *<>\w]*\)%s.*?@end'%(g_mix_method_pre)
    newLines = re.sub(rule, '@end\n', allLines, 0, re.S)
    return newLines

def removeMixCodes():
    allSrcPaths = findAllSrcPaths()
    for srcPath in allSrcPaths:
        f = open(srcPath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        newAllLines = removeMixImports(allLines)
        newAllLines = removeMixFuncsAndPros(newAllLines)
        f.close()
        if newAllLines != allLines:
            f = open(srcPath, 'w+')
            f.write(newAllLines)
            f.close()

def removeAllMixs():
    removeMixCodes()
    removeProjectRefs()
    removeMixFiles()

removeAllMixs()
