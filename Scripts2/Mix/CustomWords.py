# #coding:utf-8
import os
import fileObject
import re

g_file_type = ['.m', '.mm']
g_classPre = 'FM'
g_ignore_words = ['.m', '.mm', 'MB', 'Char', 'Copy', 'Model', 'New', 'View', 'String', 'Controller', 'UI', '+', ' ', '-', 'Cell', 'Core', 'JSON', 'IAP', 'Pay', 'Store', 'Buy', 'Vip', 'App', 'Localized', 'Log', 'Font', 'Public', 'Xml', 'Svc', 'Lpf', 'Enums']
g_allWords = []

def findAllFilePaths():
    allFiles = fileObject.allSrcFilePath([], g_file_type)
    return allFiles

def findAllWords():
    allFilePaths = findAllFilePaths()
    for filePath in allFilePaths:
        fileName = os.path.basename(filePath)
        if fileName.startswith(g_classPre):
            handleFileName(fileName)

def handleFileName(fileName):
    oriFileName = fileName
    for ignoreWord in g_ignore_words:
        oriFileName = oriFileName.replace(ignoreWord, '', 1)
    splitFileName(oriFileName)

def splitFileName(fileName):
    splitNames = re.findall('[A-Z][^A-Z]*', fileName)
    for name in splitNames:
        if len(name) >= 3 and name not in g_allWords and '.' not in name:
            g_allWords.append(name)
            print(name)

def writeWordsToFile():
    f = open("CustomKeywords.txt", "w+")
    for word in g_allWords:
        f.write(word.lower())
        f.write(',')
    f.close()

findAllWords()
writeWordsToFile()

print(len(g_allWords))
        






    
