#coding:utf-8
import os
import fileObject
import re
import shutil

g_linkmap_path = './ZhuiYin-LinkMap-normal-arm64.txt'
g_classname_pre = ['MB']
g_add_method_pre = 'zyfunc_'
g_add_method_suf = '_method'
g_ignore_dirs = ['Pods','UnUsedFiles','NewWebApp','proto','ThirdParty','LeakCheck','MobEnt','originproto','OrangeFilter']
g_ignore_header_dirs = ['Pods','NewWebApp','proto','ThirdParty','LeakCheck','MobEnt','originproto','OrangeFilter']
g_ignore_rename_dires = ['Pods','UnUsedFiles','proto','originproto','OrangeFilter']
g_ignore_method_pre = ['mb_', 'zy_', 'zymethod_', g_add_method_pre]
g_ios_publicapi_path = ['/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/Library/Frameworks',
'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/usr/include/objc']
g_rename_file_types = ['.h', '.m', '.mm', '.xib', '.storyboard']
g_xib_types = ['.xib', '.storyboard']


g_all_ivars = []
g_all_public_apis = []
g_ignore_header_methods = []

def findAllTargetClasses():
    allFilePaths = fileObject.allSrcFilePath(g_ignore_dirs, ['.m'])
    targetClasses = []
    for filePath in allFilePaths:
        fileName = os.path.basename(filePath)
        for classPre in g_classname_pre:
            if fileName.startswith(classPre):
                fileClass = os.path.splitext(fileName)[0]
                targetClasses.append(fileClass)
                # print(fileClass)
    # print(len(targetClasses))
    return targetClasses

def findAllSystemPublicApis():
    for publicPath in g_ios_publicapi_path:
        filePaths = fileObject.recursiveDir(publicPath, ['.h'])
        for path in filePaths:
            f = open(path, 'rb')
            allLines = f.read()
            allLines = allLines.decode('utf-8', 'ignore')
            rule = r'[+-]\s?\([ *<>\w]*\).*?;'
            methods = re.findall(rule, allLines, re.S)
            for method in methods:
                rule2 = r'[+-]\s?\(.*?\)(\S+?)[; :].*'
                matchObj = re.match(rule2, method, re.S)
                if matchObj:
                    methodName = matchObj.group(1).lower().strip()
                    if methodName not in g_all_public_apis:
                        g_all_public_apis.append(methodName)
                        # print(methodName)

            f.close()
    # print(len(g_all_public_apis))
    # f = open('./api.txt', 'w+')
    # f.write('\n'.join(g_all_public_apis))
    # f.close()

def findAllIgnoreMethods():
    filePaths = fileObject.allIncludeSrcFilePath(g_ignore_header_dirs, ['.h', '.m', '.mm'])
    for path in filePaths:
        f = open(path, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        rule = r'[+-]\s?\([ *<>\w]*\).*?;'
        methods = re.findall(rule, allLines, re.S)
        for method in methods:
            if ':' not in method:
                rule2 = r'[+-]\s?\(.*?\)(\S+?)[; :].*'
                matchObj = re.match(rule2, method, re.S)
                if matchObj:
                    methodName = matchObj.group(1).lower().strip()
                    if methodName not in g_ignore_header_methods:
                        g_ignore_header_methods.append(methodName)
                        # print(methodName)
            else:
                replaceMethod = method[(method.index(')') + 1):]
                rule2 = r'(\S+)\s*:\s*\('
                allMethodNames = re.findall(rule2, replaceMethod, re.S)
                for methodName in allMethodNames:
                    tempMethodName = methodName.lower().strip()
                    if tempMethodName not in g_ignore_header_methods:
                        g_ignore_header_methods.append(tempMethodName)
                        # print(tempMethodName)

        f.close()
    # print(len(g_ignore_header_methods))


def findAllIVars():
    f = open(g_linkmap_path, 'rb')
    allLines = f.read()
    allLines = allLines.decode('utf-8', 'ignore')
    for line in allLines:
        rule = r'.*_OBJC_IVAR_.*\._(\S+)\s+'
        matchObj = re.match(rule, line, re.S)
        if matchObj:
            varName = matchObj.group(1).lower()
            if varName not in g_all_ivars:
                g_all_ivars.append(varName)                

    # print(len(g_all_ivars))
    f.close()

def findAllMethods():
    findAllSystemPublicApis()
    findAllIgnoreMethods()
    allTargetClasses = findAllTargetClasses()

    f = open(g_linkmap_path, 'rb')
    allLines = f.readlines()
    allMethods = []
    for line in allLines:
        line = line.decode('utf-8', 'ignore')
        rule = r'.*[-+]\[(\S+)\s(\S+)\].*'
        matchObj = re.match(rule, line, re.S)
        if matchObj:
            className = matchObj.group(1)
            methodName = matchObj.group(2)
            if className in allTargetClasses and isNeededMethod(methodName):
                print(methodName)
                firstMethodName = methodName.split(':')[0].strip() + ':'
                if firstMethodName not in allMethods:
                    allMethods.append(firstMethodName)
                # print(className + '->' + methodName)             
    
    allMethods = sorted(allMethods,key = lambda i:len(i),reverse=True)  
    # print(allMethods)
    print('一共替换的函数个数:' + str(len(allMethods)))
    f.close()
    return allMethods

def isNeededMethod(methodName):
    isNeeded = True

    if isIgnorePreMethod(methodName):
        isNeeded = False
    elif isGetterSetterMethod(methodName):
        isNeeded = False
    elif isInitMethod(methodName):
        isNeeded = False
    elif isSystemMethod(methodName):
        isNeeded = False
    elif isIgnoreFileMethod(methodName):
        isNeeded = False

    return isNeeded

def isIgnorePreMethod(methodName):
    isIgnore = False
    for ignoreMethodPre in g_ignore_method_pre:
        if methodName.startswith(ignoreMethodPre):
            isIgnore = True
    return isIgnore

def isGetterSetterMethod(methodName):
    isGetterSetter = False
    if methodName.startswith('set'):
        isGetterSetter = True
    if ':' not in methodName:
        isGetterSetter = True
    return isGetterSetter

def isInitMethod(methodName):
    if methodName.startswith('init'):
        return True
    return False

def isSystemMethod(methodName):
    firstMethodName = methodName.split(':')[0]
    if firstMethodName.lower() in g_all_public_apis:
        # print(firstMethodName)
        return True
    return False

def isIgnoreFileMethod(methodName):
    firstMethodName = methodName.split(':')[0]
    if firstMethodName.lower() in g_ignore_header_methods:
        # print(firstMethodName)
        return True
    return False

def renameMethods():
    allMethods = findAllMethods()
    allFilePaths = fileObject.allSrcFilePath(g_ignore_rename_dires, g_rename_file_types)
    print(len(allFilePaths))

    for filePath in allFilePaths:
        f = open(filePath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        fileName = os.path.basename(filePath)
        fileType = os.path.splitext(fileName)[1]
        isXib = fileType in g_xib_types

        newLines = allLines
        f.close()
        for method in allMethods:
            replacedName = replacedMethodName(method)
            if isXib:
                originMethod = 'selector="%s'%(method)
                newMethod = 'selector="%s'%(replacedName)
                newLines = newLines.replace(originMethod, newMethod)
            else:
                originMethod = '@selector(' + method
                newMethod = '@selector(' + replacedName
                newLines = newLines.replace(originMethod, newMethod)

                originMethod = ')' + method
                newMethod = ')' + replacedName
                newLines = newLines.replace(originMethod, newMethod)

                originMethod = ']' + method
                newMethod = ']' + replacedName
                newLines = newLines.replace(originMethod, newMethod)

                originMethod = ',' + method
                newMethod = ',' + replacedName
                newLines = newLines.replace(originMethod, newMethod)

                originMethod = ':' + method
                newMethod = ':' + replacedName
                newLines = newLines.replace(originMethod, newMethod)

                originMethod = ' ' + method
                newMethod = ' ' + replacedName
                newLines = newLines.replace(originMethod, newMethod)
        

        if allLines != newLines:
            f = open(filePath, 'w+')
            f.write(newLines)
            f.close()
            print(filePath)
        
def replacedMethodName(methodName):
    if ':' not in methodName:
        return (g_add_method_pre + methodName + g_add_method_suf)
    else:
        tempName = methodName.replace(':', '')
        return (g_add_method_pre + tempName + g_add_method_suf + ':')


renameMethods()


        






    