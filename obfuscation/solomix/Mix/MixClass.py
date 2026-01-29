#coding:utf-8
import os
import fileObject
import re
import random

g_linkmap_path = './solomix-LinkMap-normal-arm64.txt'
g_mixclass_path = './mixClass_allClass.txt'
g_keyword_file_path = './CustomKeywords.txt'
g_mixclass_split = '<====>'
g_mixprotocol_split = '<================>'
g_oriClass_pres = ['IM', 'CAuthority', 'OOO', 'OTO', 'O2O', 'OTM', 'APP', 'SVIP', 'VIP']
g_needMix_pres = ['MP', 'KLC', 'SV', 'PLay', 'DY', 'ME', 'ZQ', 'GK', 'ZGQ', 'YH', 'SD', 'PG']
g_mix_pre = 'SX'
g_proj_type = '.pbxproj'
# g_ignore_class_dires = ['Pods','LocalPods','UnUsedFiles','ThirdParty','LibTools','LibThird','framework']
g_ignore_rename_dires = ['Pods','LocalPods','UnUsedFiles','Scripts','ThirdParty','Resource','LibTools','LibThird','klcAssets.xcassets','framework','.git']
g_rename_file_types = ['.h', '.m', '.mm', '.xib', '.storyboard', g_proj_type, '.pch']
g_ios_publicapi_path = ['/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/Library/Frameworks',
'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/usr/include/objc']

g_all_system_classes = []
g_all_mix_class_map = {}
g_all_mix_protocol_map = {}

def loadMixClassMap():
    if os.path.exists(g_mixclass_path):
        f = open(g_mixclass_path, 'r')
        allLines = f.readlines()
        for line in allLines:
            if g_mixclass_split in line:
                splitList = line.split(g_mixclass_split)
                oriClass = splitList[0].strip()
                afterClass = splitList[1].strip()
                g_all_mix_class_map[oriClass] = afterClass
            elif g_mixprotocol_split in line:
                splitList = line.split(g_mixprotocol_split)
                oriProtocol = splitList[0].strip()
                afterProtocol = splitList[1].strip()
                g_all_mix_protocol_map[oriProtocol] = afterProtocol

    print('读取类名混淆映射文件，class数量：', len(g_all_mix_class_map), 'protocol数量：', len(g_all_mix_protocol_map))


def getClassMixName(className):
    oriClassName = className
    findOriPre = ''
    for pre in g_oriClass_pres:
        if className.startswith(pre):
            oriClassName = className.removeprefix(pre)
            findOriPre = pre
    if findOriPre == '':
        for pre in g_needMix_pres:
            if className.startswith(pre):
                oriClassName = className.removeprefix(pre)
    tmp = split_on_uppercase(oriClassName)
    mixClassName = randomWord(len(tmp))
    if findOriPre:
        mixClassName = g_mix_pre + findOriPre + mixClassName
    else:
        mixClassName = g_mix_pre + mixClassName
    return mixClassName

def getProtocolMixName(protocolName):
    oriProtocolName = protocolName
    tmp = split_on_uppercase(oriProtocolName)
    mixProtocolName = randomWord(len(tmp))
    mixProtocolName = g_mix_pre + mixProtocolName
    return mixProtocolName

def findMixClasses():
    oldClassNum = len(g_all_mix_class_map)

    print('start to find all mix classes...')
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_rename_dires, ['.m'])

    allClass = []
    for path in allFilePaths:
        f = open(path, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        rule = r'@implementation\s(\w+)'
        classNames = re.findall(rule, allLines, re.S)
        for className in classNames:
            if className not in allClass and className not in g_all_system_classes:
                allClass.append(className)
        f.close()

    for originName in allClass:
        if originName not in g_all_mix_class_map.keys():
            mixName = getClassMixName(originName)
            g_all_mix_class_map[originName] = mixName

    newAddNum = len(g_all_mix_class_map) - oldClassNum
    print('所有class数量：' + str(len(allClass)))
    print('新增混淆class数量：', newAddNum)


def findMixProtocols():
    oldProtocolNum = len(g_all_mix_protocol_map)

    print('start to find all mix protocols...')
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_rename_dires, ['.h'])

    # 查找要重命名的 protocol
    allProtocols = []
    for path in allFilePaths:
        f = open(path, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        rule = r'@protocol\s(\w+)\s[<]+'
        protocolNames = re.findall(rule, allLines, re.S)
        for protocolName in protocolNames:
            if protocolName not in allProtocols:
                allProtocols.append(protocolName)
        f.close()

    for originName in allProtocols:
        if originName not in g_all_mix_protocol_map.keys():
            mixName = getProtocolMixName(originName)
            g_all_mix_protocol_map[originName] = mixName

    newAddNum = len(g_all_mix_protocol_map) - oldProtocolNum
    print('所有protocol数量：' + str(len(allProtocols)))
    print('新增混淆protocol数量：', newAddNum)


def rewriteMapToFile():
    allLines1 = []
    for (oriName, mixName) in g_all_mix_class_map.items():
        line = oriName + '  ' + g_mixclass_split + '  ' + mixName
        allLines1.append(line)
    allLines2 = []
    for (oriName, mixName) in g_all_mix_protocol_map.items():
        line = oriName + '  ' + g_mixprotocol_split + '  ' + mixName
        allLines2.append(line)

    f = open(g_mixclass_path, 'w+')
    f.write('👉👉👉👉👉👉👉👉👉👉类名混淆映射列表👈👈👈👈👈👈👈👈👈👈' + '\n')
    f.write('\n'.join(allLines1))
    f.write('\n\n')
    f.write('👉👉👉👉👉👉👉👉👉👉Protocol混淆映射列表👈👈👈👈👈👈👈👈👈👈' + '\n')
    f.write('\n'.join(allLines2))
    f.close()


def findAllSrcFileTargets():
    print('start to find all target classes...')
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_rename_dires, g_rename_file_types)
    # print('\n'.join(allFilePaths))
    print(len(allFilePaths))

    f = open('./mixClass_AllSrcPaths.txt', 'w+')
    f.write('\n'.join(allFilePaths))
    f.close()

    return allFilePaths

def findAllSystemPublicClass():
    print('start to find all system public classes...')
    for publicPath in g_ios_publicapi_path:
        filePaths = fileObject.recursiveDir(publicPath, ['.h'])
        for path in filePaths:
            # print(path)
            f = open(path, 'rb')
            allLines = f.read()
            allLines = allLines.decode('utf-8', 'ignore')
            rule = r'@interface\s(\w+)\s[<:{]+'
            classNames = re.findall(rule, allLines, re.S)
            for className in classNames:
                if className not in g_all_system_classes:
                    g_all_system_classes.append(className)
            f.close()
    print(len(g_all_system_classes))
    # f = open('./mixClass_systemClass.txt', 'w+')
    # f.write('\n'.join(g_all_system_classes))
    # f.close()

def renameMixClass():
    findAllSystemPublicClass()
    loadMixClassMap()
    findMixClasses()
    findMixProtocols()
    rewriteMapToFile()

    allFilePaths = findAllSrcFileTargets()

    # 合并2个map
    combined_map = {**g_all_mix_class_map, **g_all_mix_protocol_map}

    allOriClasses = combined_map.keys()
    allOriClasses = sorted(allOriClasses,key = lambda i:len(i),reverse=True)

    print('start to rename classes...')
    print(len(allOriClasses))

    ff = open('./mixClass_log.txt', 'w+')
    # for key in allOriClasses:
    #     val = combined_map[key]
    #     log = key + ' -> ' + val
    #     ff.write(log + '\n')
    # ff.close()
    
    for filePath in allFilePaths:
        print('正在处理 ', filePath)
        fileName = os.path.basename(filePath)
        f = open(filePath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        f.close()
        newAllLines = allLines

        mixFilePath = filePath
        for oriClassName in allOriClasses:
            mixClassName = combined_map[oriClassName]
            if fileName.endswith(g_proj_type):
                newAllLines = newAllLines.replace(oriClassName, mixClassName)
            else:
                newAllLines = newAllLines.replace(oriClassName, mixClassName)

            mixFilePath = mixFilePath.replace(oriClassName, mixClassName)

        if newAllLines != allLines:
            f = open(filePath, 'w+')
            f.write(newAllLines)
            f.close()
            # if mixClassName == 'SXApdaterBadgeTitlePeipei':
            #     print('----' + filePath)
            #     print(oriClassName + mixClassName)

        if mixFilePath != filePath:
            log = filePath + ' -> ' + mixFilePath
            ff.write(log + '\n')
            # print('%s -> %s'%(filePath, mixFilePath))
            os.renames(filePath, mixFilePath)


def split_on_uppercase(s):
    return ''.join([' ' + c if c.isupper() else c for c in s]).strip().split()

def readKeyWords():
    f = open(g_keyword_file_path, 'r')
    allText = f.read()
    global g_all_words;
    g_all_words = allText.split(',')

def randomWord(count):
    result = ''
    allWordsNum = len(g_all_words)
    for i in range(0, count):
        index = random.randint(0, allWordsNum-1)
        word = g_all_words[index]
        word = word.capitalize()
        result += word
    return result

def handleSpecialLogic():
    curPath = os.getcwd()
    curPath = os.path.dirname(curPath)
    curPath = os.path.dirname(curPath)

    path = '/Library/LibTool/LibTools/LibTools/BaseMacroDefinition.h'
    filePath = curPath + path;

    print(filePath)

    f = open(filePath, 'rb')
    allLines = f.read()
    allLines = allLines.decode('utf-8', 'ignore')
    f.close()
    newAllLines = allLines

    key = 'KLCAppConfig'
    val = g_all_mix_class_map[key]
    newAllLines = newAllLines.replace(key, val)

    if newAllLines != allLines:
        f = open(filePath, 'w+')
        f.write(newAllLines)
        f.close()


readKeyWords()
renameMixClass()
handleSpecialLogic()

# _OBJC_CLASS_$_AppDelegate
# __OBJC_PROTOCOL_$_UICollectionViewDelegate
# l_OBJC_PROTOCOL_$_NSCopying
# __OBJC_$_INSTANCE_METHODS_UIView(Blocks|SafeLayout|AdjustFrame|Gradient|Extend)
# __OBJC_$_CLASS_METHODS_UIView(Blocks|SafeLayout|AdjustFrame|Gradient|Extend)