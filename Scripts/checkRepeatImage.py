# -*- coding: utf-8 -*
import commands

def getAllImagePath():
    findAllImageCMD = 'find "$(cd ..; pwd)" -name "*.gif" -or -name "*.png" -or -name "*.jpg"'
    allImages = commands.getoutput(findAllImageCMD)
    imagesArray = allImages.split('\n')
    result = []
    for path in imagesArray:
        if "/Pods/" not in path:
            result.append(path)

    return result

def getFileMd5(filePath):
    md5Cmd = "md5 {}".format(filePath) + " | awk '{print $4}'"
    md5Str = commands.getoutput(md5Cmd)
    return md5Str


def createMD5(imageArray):
    imagesMD5Dict = {}
    for image in imageArray:
        md5 = getFileMd5(image)
        array = imagesMD5Dict.get(md5)
        if array is None:
            newArray = [image]
            imagesMD5Dict[md5] = newArray
        else:
            imagesMD5Dict[md5].append(image)

    return imagesMD5Dict


def checkRepeatImage(md5Dict):
    resut = {}
    for key, value in md5Dict.iteritems():
        if len(value) > 1:
            resut[key] = value
            for item in value:
                print item

            print '\n'

    desc = ''
    count = len(resut)
    if count == 0:
        desc = '项目没有重复图片哦'
    else:
        desc = '重复图片数量：' + str(count)
    print desc

def start():
    print '开始扫描重复图片...'

    allImagePath = getAllImagePath()
    md5Dict = createMD5(allImagePath)
    checkRepeatImage(md5Dict)

start()