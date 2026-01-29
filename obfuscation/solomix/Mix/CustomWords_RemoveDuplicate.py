# #coding:utf-8
import os

g_file_path = './CustomKeywords.txt'

def removeDuplicate():
    f = open(g_file_path, 'r')
    allText = f.read()
    allTextArray = allText.split(',')
    newTextArray = []
    for text in allTextArray:
        if text not in newTextArray:
            newTextArray.append(text)
            print(text)
        else:
            # print(text)
            pass
    print('oriCount = %s, newCont = %s, delta = %s'%(len(allTextArray), len(newTextArray), len(allTextArray) - len(newTextArray)))
    f.close()
    newTexts = ','.join(newTextArray)
    f = open(g_file_path, 'w+')
    f.write(newTexts)
    f.close()

removeDuplicate()
        






    
