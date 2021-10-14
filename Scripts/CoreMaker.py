#coding:utf-8
import os
import fileObject
import time
import subprocess
import sys
import threading
import re

projName = fileObject.projNameAndRootDir()[0]  #项目名
rootPath = fileObject.projNameAndRootDir()[1]  #项目根目录
projPath = rootPath

# 配置相关
coreMakerDir = os.path.expanduser(r'~/Desktop/CoreMaker')

pbFilePres = ['Yyp', 'Pb']
reqSuffix = ['Req']
respSuffix = ['Resp']
broadSuffixs = ['BC', 'Notice', 'UC', 'SC']

excludePBFiles = ['Common.pbobjc.h', 'TemplateCommon.pbobjc.h', 'Svga.pbobjc.h']
coreFilePre = 'MB'


# 全局变量

g_className = ''
g_maxType = -1
g_serverType = -1
g_req = []
g_resp = []
g_bc = []
g_method = []

def clearGlobalVars():
    global g_className
    global g_maxType
    global g_serverType
    global g_req
    global g_resp
    global g_bc
    global g_method

    g_className = ''
    g_maxType = -1
    g_serverType = -1
    g_req = []
    g_resp = []
    g_bc = []
    g_method = []




# 所有pb文件，按修改日期排序
def allPbFiles():
    dir_list = fileObject.allFilePathsEndwith('.pbobjc.h')
    dir_list = [x for x in dir_list if '/Pods/' not in x]     
    dir_list.sort(key = str.lower)

    allPbs = []
    for filePath in dir_list:
        subFile = os.path.split(filePath)[1]
        fileName = os.path.splitext(subFile)[0]
        fileType = os.path.splitext(subFile)[1]
        if fileType == '.h' and subFile not in excludePBFiles:
            allPbs.append(filePath)

    return allPbs

# 根据输入文件名查找文件路径
def inputFilePath():
    allPbs = allPbFiles()
    pbFileStrings = ''
    for index in range(len(allPbs)):
        filePath = allPbs[index]
        subFile = os.path.split(filePath)[1]
        pbString = subFile
        pbFileStrings += '序号:[%d] 文件:%s\n'%(index, pbString)

    allFilePaths = []    
    inputNo = input(pbFileStrings + '----------请输入要处理的文件序号----------\n单个处理：从以上pb文件选择一个序号(比如:0)\n多个处理：以逗号分开需要处理的文件（比如0,1,4,7）\n全部文件：输入小写字母a \n退出输入小写字母q \n' + ':')
    if inputNo.lower() == 'a':
        allFilePaths = allPbs
    elif inputNo.lower() == 'q':
        exit(0)
    elif inputNo.isdigit() and int(inputNo) >= 0 and int(inputNo) < len(allPbs):
        pbFilePath = allPbs[int(inputNo)]
        allFilePaths.append(pbFilePath)
    elif ',' in inputNo:
        NoArray = inputNo.split(',')
        for index in range(len(NoArray)):
            NoIndex = NoArray[index]
            if NoIndex.isdigit() and int(NoIndex) >= 0 and int(NoIndex) < len(allPbs):
                pbFilePath = allPbs[int(NoIndex)]
                if pbFilePath not in allFilePaths:
                    allFilePaths.append(pbFilePath)
            else:
                print('非法输入已过滤:' + NoIndex)
    else:
        print('输入非法，请输入0-%d之间的数字或者字符a'%(len(allPbs) - 1))

    return allFilePaths
        
# pb文件处理
def parsePbFile(pbFilePath):
    f = open(pbFilePath, 'r')
    allLines = f.read()
    parseClassName(allLines)
    parseServerType(allLines)
    parseBC(allLines)
    parseReq(allLines)
    parseResp(allLines)
    f.close()

# 处理类名
def parseClassName(allLines):
    matchObj = re.match(r'.*@interface\s+(\S+)Root\s+:\s+GPBRootObject.*', allLines, re.S)
    if matchObj:
        global g_className
        g_className = matchObj.group(1)

# 处理大小类
def parseServerType(allLines):
    matchObj = re.match((r'.*typedef GPB_ENUM.*\s+?(\S+_.*Max)\s+=\s+\d+.*\s+?(\S+_.*ServerType)\s+=\s+\d+.*'), allLines, re.S)
    if matchObj:
        global g_maxType
        global g_serverType
        g_maxType = matchObj.group(1)
        g_serverType = matchObj.group(2)
    else:
        print('⛔️⛔️ 没有找到大小类，请自行替换大小类 ⛔️⛔️')

# 处理广播
def parseBC(allLines):
    for broad in broadSuffixs:
        allBCs = re.findall(r'@interface\s+(\S+%s+)\s+:\s+GPBMessage'%(broad), allLines, re.S)
        for bc in allBCs:
            g_bc.append(bc)        

# 处理请求
def parseReq(allLines):
    allReqs = re.findall(r'(\/\*\*\n\s+\*[^\n]+\n(\s+\*[^\n]+\n)?\s+\*\*\/\n)?(@interface\s+\S+Req+\s+:\s+GPBMessage.*?@end)', allLines, re.S)
    for reqInfo in allReqs:
        comment = reqInfo[0]
        req = reqInfo[2]
        reqClassName = parseReqClassName(req)
        reqProps = parsePropertys(req)
        reqInfo = {'class' : reqClassName, 'props' : reqProps, 'comment' : comment}
        g_req.append(reqInfo)

# 处理回包resp
def parseResp(allLines):
    allResps = re.findall(r'@interface\s+\S+Resp+\s+:\s+GPBMessage.*?@end', allLines, re.S)
    for resp in allResps:
        respClassName = parseReqClassName(resp)
        respProps = parsePropertys(resp)
        respInfo = {'class' : respClassName, 'props' : respProps}
        g_resp.append(respInfo)

# 处理req/resp请求类名        
def parseReqClassName(lines):
    matchObj = re.match(r'.*@interface\s+(\S+)\s+:\s+GPBMessage.*', lines, re.S)
    reqClass = ''
    if matchObj:
        reqClass = matchObj.group(1)
    return reqClass

# 处理req/resp的属性
def parsePropertys(lines):
    propLines = re.findall(r'(@property.*?)\)\s+(\S+)\s+(\S+);', lines, re.S)
    allProps = []
    for prop in propLines:
        attr = prop[0]
        if 'readonly' in attr:
            continue
        type = prop[1]
        name = prop[2]
        if name.startswith('*'):
            type = type + ' *'
            name = name[1:]
        allProps.append({'type' : type, 'name' : name})
    return allProps

# pb文件名去除前缀，如YypRoom去除前缀后为Room
def removePbFilePre(pbFileName):
    for pbFilePre in pbFilePres:
        if pbFileName.startswith(pbFilePre):
            return pbFileName.replace(pbFilePre, '', 1)
    return pbFileName

# 根据pb文件路径取文件名，没有后缀
def pbName(pbPath):
    pbFile = os.path.basename(pbPath)
    pbFileName = os.path.splitext(pbFile)[0]
    pbFileName = os.path.splitext(pbFileName)[0]
    return pbFileName

# 创建core文件
def createCoreFiles(fileName):
    filePath = os.path.join(coreMakerDir, fileName)
    if not os.path.isdir(filePath):
        os.makedirs(filePath)

    coreFileName = coreFilePre + fileName + 'Core'
    coreHeaderFilePath = os.path.join(filePath, coreFileName + '.h')
    coreImplFilePath = os.path.join(filePath, coreFileName + '.m')

    open(coreHeaderFilePath, 'w').close()
    open(coreImplFilePath, 'w').close()

    return (coreHeaderFilePath, coreImplFilePath)

def alignWhiteSpaces(maxString, reqString):
    whiteLength = len('- (void)' + maxString) - len(reqString)
    whiteString = ''
    for i in range(whiteLength):
        whiteString += ' '
    return whiteString

def reqClassName(className):
    noPreClassName = removePbFilePre(className)
    noReqClassName = noPreClassName.replace('Req', '')
    return noReqClassName

def writeCoreHeader(filePath, noPreFileName, pbName):
    className = coreFilePre + noPreFileName + 'Core'
    f = open(filePath, 'r+')
    f.write('#import <Foundation/Foundation.h>\n#import \"%s\"\n\n'%(pbName))
    f.write('NS_ASSUME_NONNULL_BEGIN\n\n')
    f.write('@protocol I%s <NSObject>\n\n'%(className))
    for i in range(len(g_req)):
        req = g_req[i]
        resp = g_resp[i]
        reqClass = req['class']
        reqName = reqClassName(reqClass)
        reqProps = req['props']
        comment = req['comment']
        respClass = resp['class']
        
        allReqParams = []
        for prop in reqProps:
            type = prop['type']
            name = prop['name']
            code = '%s:(%s)%s'%(name, type, name)
            allReqParams.append(code)
        sucCode = 'success:(void (^)(%s *resp))success'%(respClass)
        allReqParams.append(sucCode)
        failCode = 'fail:(void (^)(NSString *errMsg))fail;\n'
        allReqParams.append(failCode)
        upperFirst = lambda x: x[0].upper() + x[1:]
        allReqParams[0] = '- (void)req%sWith%s'%(removePbFilePre(reqName), upperFirst(allReqParams[0]))
        genCode = genReqCode(allReqParams)
        if len(comment) > 0:
            genCode = comment + genCode
        f.write(genCode)
        g_method.append(genCode)
    f.write('@end\n\n')
    f.write('@interface %s : NSObject<I%s>\n\n@end\n\n'%(className, className))
    f.write('NS_ASSUME_NONNULL_END\n\n')
    f.close()

# 参数格式对齐
def genReqCode(allReqParams):
    index0 = allReqParams[0].index(':')
    codes = ''
    for reqLine in allReqParams:
        index = reqLine.index(':')
        if index >= index0:
            codes += '%s\n'%(reqLine)
        else:
            delta = index0 - index
            for i in range(delta):
                codes += ' '
            codes += '%s\n'%(reqLine)
    return codes

def writeCoreImpl(filePath, noPreFileName):
    className = coreFilePre + noPreFileName + 'Core'
    f = open(filePath, 'r+')
    f.write('#import \"%s.h\"\n'%(className))
    f.write('#import \"MBRequestHelper.h\"\n\n')
    f.write('@interface %s ()\n\n@end\n\n'%(className))
    f.write('@implementation %s\n\n'%(className))

    if len(g_bc) > 0:
        f.write('- (instancetype)init\n')
        f.write('{\n')
        f.write('\tself = [super init];\n')
        f.write('\tif (self) {\n')
        f.write('\t\t[self addBroadcastObserver];\n')
        f.write('\t}\n')
        f.write('\treturn self;\n')
        f.write('}\n\n')
        f.write('- (void)addBroadcastObserver\n')
        f.write('{\n')
        f.write('\t[[MBRequestHelper sharedInstance].receivePBBrocastSubject subscribeNext:^(MBResponsePBModel *response) {\n')
        for index in range(len(g_bc)):
            bc = g_bc[index]
            if index == 0:
                f.write('\t\tif ([response.responseModel isKindOfClass:[%s class]]) {\n'%(bc))
            else:
                f.write(' else if ([response.responseModel isKindOfClass:[%s class]]) {\n'%(bc))
            f.write('\t\t\t%s *bc = (%s *)response.responseModel;\n'%(bc, bc))
            f.write('\t\t\t/*TODO*/\n')
            f.write('\t\t}')
        f.write('\n\t}];\n}\n\n')
    
    for i in range(len(g_req)):
        req = g_req[i]
        resp = g_resp[i]
        reqClass = req['class']
        reqName = reqClassName(reqClass)
        reqProps = req['props']
        respClass = resp['class']
        methodCode = g_method[i].replace(';\n', '')
        f.write(methodCode)
        f.write('{\n')
        f.write('\t%s *req = [%s new];\n'%(reqClass, reqClass))

        for prop in reqProps:
            type = prop['type']
            name = prop['name']
            f.write('\treq.%s = %s;\n'%(name, name))
        f.write('\n')

        f.write('\tMBRequestPBModel *requestModel = [MBRequestPBModel configWithRequestModel:req maxType:%s serverType:%s];\n'%(g_maxType, g_serverType))
        f.write('\t[[MBRequestHelper sharedInstance] requestByPBModel:requestModel success:^(MBResponsePBModel *response) {\n')
        f.write('\t\tif (response.code == 0 && [response.responseModel isKindOfClass:[%s class]]) {\n'%(respClass))
        f.write('\t\t\t%s *resp = (%s *)(response.responseModel);\n'%(respClass, respClass))
        f.write('\t\t\tSafetyCallblock(success, resp);\n')
        f.write('\t\t} else {\n')
        f.write('\t\t\tSafetyCallblock(fail, response.errMsg ?: @"请求失败，请重试");\n')
        f.write('\t\t}\n')
        f.write('\t} fail:^(NSError *error) {\n')
        f.write('\t\tSafetyCallblock(fail, STRINGHASVALUE(error.localizedDescription) ? error.localizedDescription : @"请求失败，请重试");\n')
        f.write('\t}];\n}\n\n')
    
    f.write('@end\n\n')
    f.close()

def handlePbPath(pbPath):
    clearGlobalVars()
    pbFileName = os.path.basename(pbPath)
    print('开始处理文件:%s... 😇 😇 '%(pbFileName))
    parsePbFile(pbPath)
    if len(g_req) == len(g_resp):
        noPreFileName = removePbFilePre(g_className)
        filePaths = createCoreFiles(noPreFileName)
        coreHeaderFilePath = filePaths[0]
        coreImplFilePath = filePaths[1]
        writeCoreHeader(coreHeaderFilePath, noPreFileName, pbFileName)
        writeCoreImpl(coreImplFilePath, noPreFileName)
    else:
        print('⛔️⛔️解析失败：req个数和resp个数不一致⛔️⛔️')
    print('文件%s处理完成！🍺 🍺\n'%(pbFileName))

def openCoreMakerDir(pbPaths):
    pbCount = len(pbPaths)
    coreDir = ''
    if pbCount == 0:
        return
    else:
        coreDir = coreMakerDir

    if len(coreDir) > 0:
        print('----------查看文件 📂 📂 ----------\n')
        print('已打开生成的Core文件所存放本地目录，请自行添加到项目工程并根据需要修改')
        subprocess.call(['open', coreDir])

def main():
    if sys.version_info[0] < 3:
        print('当前Python版本信息:' + sys.version)
        print('请先升级到Python 3运行此脚本!')
        return

    allPbs = allPbFiles()
    if len(allPbs) == 0:
        print('没找到.pbobjc.h结尾的文件！')
        return

    pbPaths = inputFilePath()
    if len(pbPaths) == 0:
        return

    print('\n----------开始处理 ☕️ ☕️ ----------\n')

    for pbPath in pbPaths:
        handlePbPath(pbPath)
    
    print('----------处理完成 ☕️ ☕️ ----------\n')

    t = threading.Timer(1, openCoreMakerDir, (pbPaths,))
    t.start()
        
main()

    