#coding:utf-8
import os
import fileObject
import re
import shutil

g_linkmap_path = './solomix-LinkMap-normal-arm64.txt'
g_classname_pre = ['MB']
g_add_method_pre = 'sxfunc_'
g_add_method_suf = '_sxmethod'
g_ignore_dirs = ['Pods','LocalPods','UnUsedFiles','Scripts','ThirdParty','Resource','LibTool','LibThird','TiBeauty','klcAssets.xcassets','framework','.gitignore','.git']
g_ignore_header_dirs = ['Pods','LocalPods','Scripts','ThirdParty','LibTool','ThirdPay']
g_ignore_rename_dires = ['Pods','LocalPods','UnUsedFiles','Scripts','ThirdParty','Resource','LibTool','LibThird','TiBeauty','klcAssets.xcassets','framework','.git']
g_ignore_method_pre = [g_add_method_pre]
g_ios_publicapi_path = ['/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/Library/Frameworks',
'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/usr/include/objc']
g_rename_file_types = ['.h', '.m', '.mm', '.xib', '.storyboard']
g_xib_types = ['.xib', '.storyboard']



g_all_ivars = []
g_all_public_apis = []
g_ignore_header_methods = []
g_all_src_file_paths = []
g_ignore_getter_methods = []

def findAllTargetClasses():
    print('start to find all target classes...')
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_dirs, ['.m'])

    # print(len(allFilePaths))
    f = open('./renameMethods_AllClassPaths.txt', 'w+')
    f.write('\n'.join(allFilePaths))
    f.close()

    targetClasses = []
    for filePath in allFilePaths:
        g_all_src_file_paths.append(filePath)
        fileName = os.path.basename(filePath)
        fileClass = os.path.splitext(fileName)[0]
        targetClasses.append(fileClass)

    print(len(targetClasses))
    f = open('./renameMethods_AllClasses.txt', 'w+')
    f.write('\n'.join(targetClasses))
    f.close()
    return targetClasses

def findAllSystemPublicApis():
    for publicPath in g_ios_publicapi_path:
        filePaths = fileObject.recursiveDir(publicPath, ['.h'])
        for path in filePaths:
            # print(path)
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
    print('start to find ignore header files...')
    filePaths = fileObject.allIncludeSrcFilePath_2(g_ignore_header_dirs, ['.h', '.m', '.mm'])

    f = open('./renameMethods_ignoreFiles.txt', 'w+')
    f.write('\n'.join(filePaths))
    f.close()

    print(len(filePaths))

    print('start to find ignore header methods...')
    for path in filePaths:
        # print('ignoreFilePath: ' + path)

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

    f = open('./renameMethods_ignoreHeaderMethods.txt', 'w+')
    f.write('\n'.join(g_ignore_header_methods))
    f.close()

    print(len(g_ignore_header_methods))

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

    print('start to find all methods...')

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

            if methodName in allMethods:
                continue

            classFile = ''
            for path in g_all_src_file_paths:
                if className in path:
                    classFile = open(path).read()
                    break

            firstMethodName = methodName
            if ':' in methodName:
                firstMethodName = methodName.split(':')[0].strip() + ':'

            if className in allTargetClasses:
                if isNeededMethod(methodName, classFile):
                    # if className == 'ChatInputView' and methodName == 'createChatView':
                    #     print('----------')
                    if firstMethodName not in allMethods and firstMethodName not in g_ignore_getter_methods:
                        allMethods.append(firstMethodName)
                        # print(className + '->' + firstMethodName)
                else:
                    if firstMethodName in allMethods:
                        # print("remove methods >>>> "+methodName)
                        allMethods.remove(firstMethodName)

    
    allMethods = sorted(allMethods,key = lambda i:len(i),reverse=True)

    f = open('./renameMethods_AllMethods.txt', 'w+')
    f.write('\n'.join(allMethods))
    f.close()

    # print(allMethods)
    print('一共替换的函数个数:' + str(len(allMethods)))
    f.close()
    return allMethods

def isNeededMethod(methodName, classFile):
    isNeeded = True

    if isIgnorePreMethod(methodName):
        isNeeded = False
    elif isGetterSetterMethod(methodName, classFile):
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

def isGetterSetterMethod(methodName, classFile):
    isGetterSetter = False
    if methodName.startswith('set'):
        isGetterSetter = True
    elif ':' not in methodName:
        isGetterSetter = isGetterMethod(methodName, classFile)
    return isGetterSetter

def isGetterMethod(methodName, classFile):
    if ':' in methodName:
        return False
    rule = r'\(void\)'+methodName+'[\s;]'
    result = re.findall(rule, classFile, re.MULTILINE)
    if len(result) > 0:
        return False
    if methodName not in g_ignore_getter_methods:
        g_ignore_getter_methods.append(methodName)
    return True

def isInitMethod(methodName):
    if methodName.startswith('init'):
        return True
    return False

def isSystemMethod(methodName):
    firstMethodName = methodName.split(':')[0]
    if firstMethodName.lower() in g_all_public_apis:
        # print('isSystemMethod ========== ' + firstMethodName)
        return True
    return False

def isIgnoreFileMethod(methodName):
    firstMethodName = methodName.split(':')[0]
    if firstMethodName.lower() in g_ignore_header_methods:
        # print('isIgnoreFileMethod ========== ' + firstMethodName)
        return True
    return False

def renameMethods():
    allMethods = findAllMethods()

    print('start to find all src file paths...')
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_rename_dires, g_rename_file_types)
    print(len(allFilePaths))

    print('start to rename methods...')

    for filePath in allFilePaths:
        fileName = os.path.basename(filePath)
        fileType = os.path.splitext(fileName)[1]
        isXib = fileType in g_xib_types

        f = open(filePath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')

        newLines = allLines
        f.close()
        for method in allMethods:
            if method not in allLines:
                continue
            # print("test replace:"+method)
            replacedName = replacedMethodName(method)
            if isXib:
                if method.endswith(':'):
                    originMethod = 'selector="%s'%(method)
                    newMethod = 'selector="%s'%(replacedName)
                else:
                    originMethod = 'selector="%s"'%(method)
                    newMethod = 'selector="%s"'%(replacedName)
                newLines = newLines.replace(originMethod, newMethod)
            else:
                if method.endswith(':'):
                    rule1 = '@selector\('+method  # @selector(method
                    rule2 = '\)'+method       # )method
                    rule3 = '\]'+method       # ]method
                    rule4 = '\,'+method       # ,method
                    rule5 = '\:'+method       # :method
                    rule6 = ' '+method        #  method
                    rule6 = '[ \t]'+method        #  method
                    rule = r''+rule1+'|'+rule2+'|'+rule3+'|'+rule4+'|'+rule5+'|'+rule6
                else:
                    #\(\w+\)fetchRoomUserInfo\s|\) *fetchRoomUserInfo *]| *fetchRoomUserInfo *]
                    rule1 = '[-+] *\(\w+\)'+method+'[\s;]'      # - (returnType)method;
                    rule2 = '\)[ \t]*'+method+' *]'                 # ) method]
                    rule3 = '][ \t]*'+method+' *]'                  # ] method]
                    rule4 = '\w+[ \t]+'+method+' *]'                # object method]
                    rule5 = '@selector\( *'+method+' *\)'       # @selector(method)
                    rule =  r''+rule1+'|'+rule2+'|'+rule3+'|'+rule4+'|'+rule5

                results = re.findall(rule,newLines,re.MULTILINE)
                for text in results:
                    newText = text.replace(method, replacedName)
                    newLines = newLines.replace(text, newText)

        if allLines != newLines:
            f = open(filePath, 'w+')
            f.write(newLines)
            f.close()
            print(filePath)
        
def replacedMethodName(methodName):
    midText = methodName
    if len(methodName) > 5:
        midIndex = int(len(methodName)/2)
        strArr = list(methodName)
        strArr.insert(midIndex, 'SOLOMIX')
        midText = ''.join(strArr)

    if ':' not in methodName:
        return (g_add_method_pre + midText + g_add_method_suf)
    else:
        tempName = midText.replace(':', '')
        return (g_add_method_pre + tempName + g_add_method_suf + ':')


renameMethods()
   