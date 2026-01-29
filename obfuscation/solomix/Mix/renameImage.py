from io import BufferedReader
import os
import json
from posix import listdir
from posixpath import basename
import shutil
import fileObject
import re
import time
from typing import Counter
import random

import subprocess

ori_name_pre = ['me_', 'bl_']
new_name_pre = 'sx_'
new_name_suffix = '_sxSuff'
replace_split = '   ======   '
ignore_names = ['AppIcon', 'LaunchImage', 'Pods', 'Assets.xcassets']
# g_ignore_dires = ['Pods','UnUsedFiles','NewWebApp','proto','ThirdParty','LeakCheck','MobEnt','originproto','OrangeFilter', 'XCConfig', 'Scripts', 'SwiftBase', 'MENotificationService']
g_ignore_dires = ['Pods','LocalPods','UnUsedFiles','Scripts','ThirdParty','framework','.git']
g_rename_file_types = ['.h', '.m', '.mm', '.xib', '.storyboard','.c']
g_xib_types = ['.xib', '.storyboard']

g_mixImage_path = './renameImage_RenameImage.txt'
g_keyword_file_path = './CustomKeywords.txt'

g_replace_assets = []

all_files = []

all_rename_files = []

def createMap():
    mapString = ''
    newFileNames = []
    for path in g_replace_assets:
        findImageset(path)
    for file in all_rename_files:
        name = os.path.splitext(os.path.basename(file))[0]
        # print(name)
        # newName = ''
        # ori_pre = ''
        # for pre in ori_name_pre:
        #     if name.startswith(pre):
        #         ori_pre = pre
        #         break
        # newName = new_name_pre + name[len(ori_pre):]
        newName = new_name_pre + name

        # 处理以数字结尾的
        partterns = re.match(r'(.*[\D]+)(\d+)$', newName, re.S)
        if partterns and len(partterns.group(1)) > 0:
            newName = partterns.group(1) + new_name_suffix + partterns.group(2)
        else:
            # newName = newName + new_name_suffix + randomWord(1)
            newName = newName + new_name_suffix

        duplic = False
        # 检查新命名是否与原有文件、已经新命名的文件重名，如果重名，循环加后缀到没有为止
        # 因为跑过脚本又用git还原之后常常出现sl_开头的空文件夹，加一个是否含有json等文件的判断
        # 如果名字以数字结尾，把后缀插入到数字结尾前的字符后方，以防止代码中有遍历文件名+数字结尾的写法会出问题
        duplicFile = ''
        while True:
            for ori_file in all_files:
                if newName in ori_file:
                    duplic = True
                    duplicFile = ori_file 
                    break
            if newName in newFileNames:
                duplic = True
            if duplic:
                print("may be duplic:"+newName)
                if len(duplicFile):
                    hadImageItem = False
                    for item in os.listdir(duplicFile):
                        if item.endswith('json') or item.endswith('png') or item.endswith('jpg') or item.endswith('jpeg'):
                            hadImageItem = True
                    if not hadImageItem:
                        duplic = False
                        break

                print("real duplic:"+newName)
                
                partterns = re.match(r'(.*[\D]+)(\d+)$', newName, re.S)
                if partterns and len(partterns.group(1)) > 0:
                    newName = partterns.group(1) + new_name_suffix + partterns.group(2)
                else:
                    newName = newName + new_name_suffix
                duplic = False
            else:
                break

        newFileNames.append(newName)

        mapString += name + replace_split + newName + '\n'
    f = open(g_mixImage_path,'w')
    f.write(mapString)
    f.close


def findAssetPath(curPath):
    for dir in os.listdir(curPath):
        if dir in ignore_names:
            continue
        dirpath = os.path.join(curPath, dir)
        if os.path.isdir(dirpath):
            if dir.endswith('.xcassets'):
                g_replace_assets.append(dirpath)
            else:
                findAssetPath(dirpath)
    pass


def findImageset(path):
    for dir in os.listdir(path):
        if dir in ignore_names:
            continue
        dirpath = os.path.join(path, dir)
        if os.path.isdir(dirpath):
            if dir.endswith('imageset'):
                # 保存所有的imageset文件夹用于判断重名
                all_files.append(dirpath)
                # 实际要改前缀的文件名另外存起来
                # if not dir.startswith(new_name_pre):
                all_rename_files.append(dirpath)
            else:
                findImageset(dirpath)
    pass


def replaceImageName():
    allImages = {}
    f = open(g_mixImage_path, 'r')
    allLines = f.readlines()
    for line in allLines:
        if replace_split in line:
            splitList = line.split(replace_split)
            oriName = splitList[0].strip()
            newName = splitList[1].strip()
            allImages[oriName] = newName

    for dir in all_rename_files:
        name = os.path.splitext(os.path.basename(dir))[0]
        newFileName = allImages[name]
        jsonFile = open(os.path.join(dir, 'Contents.json'),'r')
        dict = json.load(jsonFile)
        images = dict['images']
        for fileItem in images:
            if 'filename' in fileItem:
                filename = fileItem["filename"]
                if len(filename) > 0:
                    ext = os.path.splitext(filename)[1]
                    fileItem["filename"] = newFileName + fileItem["scale"] + ext
                    os.renames(os.path.join(dir, filename), os.path.join(dir, fileItem["filename"]))
                    # print('will rename file:',(os.path.join(dir, filename), os.path.join(dir, fileItem["filename"])))
        jsonFile.close()
        jsonFile = open(os.path.join(dir, 'Contents.json'),'w')
        json.dump(dict, jsonFile, indent=4)
        jsonFile.close()
        newPath = os.path.join(os.path.dirname(dir), newFileName+'.imageset')
        if os.path.exists(newPath):
            # if not listdir(newPath):
            #     for item in listdir(newPath):
            #         print('>>>' + item)
            shutil.rmtree(newPath)
        os.renames(dir, newPath)
        # print('will rename imageset:',(dir, os.path.join(os.path.dirname(dir), newFileName+'.imageset')))


def replaceAllFileText():
    allFilePaths = fileObject.allSrcFilePath_2(g_ignore_dires, g_rename_file_types)
    print(len(allFilePaths))
    print("replace begin:", time.time())
    print("\n")
    count = len(allFilePaths)
    i = 0
    allImages = {}
    f = open(g_mixImage_path, 'r')
    allLines = f.readlines()
    for line in allLines:
        if replace_split in line:
            splitList = line.split(replace_split)
            oriName = splitList[0].strip()
            newName = splitList[1].strip()
            allImages[oriName] = newName
            
    for filePath in allFilePaths:
        # if "MERoomTypes.m" not in filePath:
        #     continue
        f = open(filePath, 'rb')
        allLines = f.read()
        allLines = allLines.decode('utf-8', 'ignore')
        fileName = os.path.basename(filePath)
        fileType = os.path.splitext(fileName)[1]
        isXib = fileType in g_xib_types
        
        newLines = allLines
        f.close()
        for name in allImages.keys():
            newName = allImages[name]
            
            if isXib:
                originText = 'image="%s'%(name)
                newText = 'image="%s'%(newName)
                newLines = newLines.replace(originText, newText)
            else:
                # 判断是否以数字结尾，有些代码会把例如 imagename_001 以类似 @"imagename_%d" 的方式调用
                # 遇到这种情况只替换结尾数字前的文本，且不管后面的双引号
                partterns = re.match(r'(.*[\D]+)(\d+)$', newName, re.S)
                if partterns and len(partterns.group(1)) > 0:
                    ori_partt = re.match(r'(.*[\D]+)(\d+)$', name, re.S)
                    originText = '@\"'+ori_partt.group(1)
                    newText = '@\"'+partterns.group(1)
                    # print("number suffix:"+name+' oriText:'+originText+ '->'+newText)
                else:
                    originText = '@\"'+name+'\"'
                    newText = '@\"'+newName+'\"'
                newLines = newLines.replace(originText, newText)
                # print("will replace text:",(originText, newText))
        

        if allLines != newLines:
           f = open(filePath, 'w+')
           f.write(newLines)
           f.close()

        i+=1
        print("\rreplace:%d/%d"%(i,count), end='')
        #    print("replace once end:", time.time())
        #    print(filePath)
    print("\n")
    print("replace end:", time.time())
    
#用于清理用了脚本又用git还原之后遗留下的带替换后前缀的空文件夹，最好单独运行
def cleanEmtpyNewPreDir():
    all_files.clear()
    for path in g_replace_assets:
        findImageset(path)
    for path in all_files:
        if os.path.basename(path).startswith(new_name_pre):
            hadImageItem = False
            for item in os.listdir(path):
                if item.endswith('json') or item.endswith('png') or item.endswith('jpg') or item.endswith('jpeg'):
                    hadImageItem = True
            if not hadImageItem:
                shutil.rmtree(path) 
                print('-----------')


def changeHash():

    ret = subprocess.run('where magick',shell=True, executable='/bin/zsh')
    if ret.returncode != 0:
        print('install imagemagick using brew...')
        ret = subprocess.run('brew install imagemagick',shell=True)
    
    all_files.clear()
    for path in g_replace_assets:
        findImageset(path)
    for path in all_files:
        for file in os.listdir(path):
            if file.endswith('png'):
                # imagePath = os.path.join(path, file)
                # print(os.popen('shasum '+ '\"'+imagePath+'\"').read())
                print(os.popen('find '+ '\"'+ path + '\"'+' -iname \"'+ file +'\" -exec echo {} \; -exec convert {} -resize 80%  -resize 125% {} \;').read())
            
                # print(os.popen('shasum '+ '\"'+imagePath+'\"').read())

        

def renameImage():
    startTime = time.time()
    print('start process...')

    curPath = os.getcwd()
    curPath = os.path.dirname(curPath)
    curPath = os.path.dirname(curPath)

    findAssetPath(curPath)
    print('Asset folder path: ', g_replace_assets)

    createMap()
    replaceImageName()
    replaceAllFileText()
    # changeHash()
    print('finish mix! used time:',time.time() - startTime)

    cleanEmtpyNewPreDir()

# def readKeyWords():
#     f = open(g_keyword_file_path, 'r')
#     allText = f.read()
#     global g_all_words;
#     g_all_words = allText.split(',')

# def randomWord(count):
#     result = ''
#     allWordsNum = len(g_all_words)
#     for i in range(0, count):
#         index = random.randint(0, allWordsNum-1)
#         word = g_all_words[index]
#         word = word.capitalize()
#         result += word
#     return result

# readKeyWords()
renameImage()



