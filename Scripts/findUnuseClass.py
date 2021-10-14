# -*- coding: utf-8 -*
#!/usr/bin/python

import os
import re
import sys
import commands

def verified_app_path(path):
    if path.endswith('.app'):
        appname = path.split('/')[-1].split('.')[0]
        path = os.path.join(path, appname)
    if not os.path.isfile(path):
        return None
    if not os.popen('file -b ' + path).read().startswith('Mach-O'):
        return None
    return path


def pointers_from_binary(line, binary_file_arch):
    if len(line) < 16:
        return None
    line = line[16:].strip().split(' ')
    pointers = set()
    if binary_file_arch == 'x86_64':
        #untreated line example:00000001030cec80	d8 75 15 03 01 00 00 00 68 77 15 03 01 00 00 00
        if len(line) != 16:
            return None
        pointers.add(''.join(line[4:8][::-1] + line[0:4][::-1]))
        pointers.add(''.join(line[12:16][::-1] + line[8:12][::-1]))
        return pointers
    #arm64 confirmed,armv7 arm7s unconfirmed
    if binary_file_arch.startswith('arm'):
        #untreated line example:00000001030bcd20	03138580 00000001 03138878 00000001
        if len(line) != 4:
            return None
        pointers.add(line[1] + line[0])
        pointers.add(line[3] + line[2])
        return pointers
    return None


def class_ref_pointers(path, binary_file_arch):
    print 'Get class ref pointers...'
    ref_pointers = set()
    lines = os.popen('/usr/bin/otool -v -s __DATA __objc_classrefs %s' % path).readlines()
    for line in lines:
        pointers = pointers_from_binary(line, binary_file_arch)
        if not pointers:
            continue
        ref_pointers = ref_pointers.union(pointers)
    if len(ref_pointers) == 0:
        exit('Error:class ref pointers null')
    return ref_pointers


def class_list_pointers(path, binary_file_arch):
    print 'Get class list pointers...'
    list_pointers = set()
    lines = os.popen('/usr/bin/otool -v -s __DATA __objc_classlist %s' % path).readlines()
    for line in lines:
        pointers = pointers_from_binary(line, binary_file_arch)
        if not pointers:
            continue
        list_pointers = list_pointers.union(pointers)
    if len(list_pointers) == 0:
        exit('Error:class list pointers null')
    return list_pointers


def class_symbols(path):
    print 'Get class symbols...'
    symbols = {}
    #class symbol format from nm: 0000000103113f68 (__DATA,__objc_data) external _OBJC_CLASS_$_TTEpisodeStatusDetailItemView
    re_class_name = re.compile('(\w{16}) .* _OBJC_CLASS_\$_(.+)')
    lines = os.popen('nm -nm %s' % path).readlines()
    for line in lines:
        result = re_class_name.findall(line)
        if result:
            print line
            (address, symbol) = result[0]
            symbols[address] = symbol
    if len(symbols) == 0:
        exit('Error:class symbols null')
    return symbols

def filter_super_class(unref_symbols):
    re_subclass_name = re.compile("\w{16} 0x\w{9} _OBJC_CLASS_\$_(.+)")
    re_superclass_name = re.compile("\s*superclass 0x\w{9} _OBJC_CLASS_\$_(.+)")
    #subclass example: 0000000102bd8070 0x103113f68 _OBJC_CLASS_$_TTEpisodeStatusDetailItemView
    #superclass example: superclass 0x10313bb80 _OBJC_CLASS_$_TTBaseControl
    lines = os.popen("/usr/bin/otool -oV %s" % path).readlines()
    subclass_name = ""
    superclass_name = ""
    for line in lines:
        subclass_match_result = re_subclass_name.findall(line)
        if subclass_match_result:
            subclass_name = subclass_match_result[0]
        superclass_match_result = re_superclass_name.findall(line)
        if superclass_match_result:
            superclass_name = superclass_match_result[0]

        if len(subclass_name) > 0 and len(superclass_name) > 0:
            if superclass_name in unref_symbols and subclass_name not in unref_symbols:
                unref_symbols.remove(superclass_name)
            superclass_name = ""
            subclass_name = ""
    return unref_symbols

def class_unref_symbols(path, filter_prefix_list):
    #binary_file_arch: distinguish Big-Endian and Little-Endian
    #file -b output example: Mach-O 64-bit executable arm64
    binary_file_arch = os.popen('file -b ' + path).read().split(' ')[-1].strip()
    unref_pointers = class_list_pointers(path, binary_file_arch) - class_ref_pointers(path, binary_file_arch)
    if len(unref_pointers) == 0:
        exit('Finish:class unref null')

    symbols = class_symbols(path)
    unref_symbols = set()
    for unref_pointer in unref_pointers:
        if unref_pointer in symbols:
            unref_symbol = symbols[unref_pointer]
            for prefix in filter_prefix_list:
                if unref_symbol.startswith(prefix):
                    unref_symbols.add(unref_symbol)

    if len(unref_symbols) == 0:
        exit('Finish:class unref null')
    return filter_super_class(unref_symbols)


def getProjectName():
    pwdCMD = 'cd .. && pwd'
    currentDir = commands.getoutput(pwdCMD)
    allFiles = os.listdir(currentDir)
    projectName = None
    for file in allFiles:
        if file.endswith('.xcworkspace'):
            projectName = file.split('.')[0]

    return projectName

def getProductPath():
    currentUserDir = commands.getoutput("cd ~ && pwd")
    derivedDataDir = currentUserDir + '/Library/Developer/Xcode/DerivedData/'
    lsDerivedDataDirFilesCMD = 'ls ' + derivedDataDir
    files = commands.getoutput(lsDerivedDataDirFilesCMD).split('\n')
    projectName = getProjectName()
    if projectName is not None:
        for file in files:
            if file.startswith(projectName):
                productDir = derivedDataDir + file + '/Build/Products/Debug-iphonesimulator/'
                lsCMD = 'ls ' + productDir
                allFiles = commands.getoutput(lsCMD).split('\n')
                for item in allFiles:
                    if item.endswith('.app'):
                        path = productDir + item
                        return path

    return None

def isClassRef(className):
    if len(className) > 0:
        projectName = getProjectName()
        grepCMD = "grep " + "'" + className + "'" + " .. -r --exclude-dir={Pods,Scripts," + "'*" + ".xcodeproj" + "'" + "," + "'*" + ".xcworkspace" + "'" + "}" + " | grep -v '//\|\#import' | wc -l"
        countStr = commands.getoutput(grepCMD).strip()
        # desc = className + ":" + countStr
        # print desc
        if len(countStr) and int(countStr) > 2:
            return True

    return False

if __name__ == '__main__':

    productPath = getProductPath()
    if productPath is not None:
        path = verified_app_path(productPath)
        if not path:
            sys.exit('Error:invalid app path')

        filter_prefix_list = ['MB', 'PK', 'GV']
        unref_symbols = class_unref_symbols(path, filter_prefix_list)
        script_path = sys.path[0].strip()
        filters = ','.join(filter_prefix_list)
        file = open(script_path + '/unuseClassResult.txt','w')
        result = []
        for unref_symbol in unref_symbols:
            isRef = isClassRef(unref_symbol)
            if not isRef:
                result.append(unref_symbol)
                desc = '无用类：' + unref_symbol
                print desc
                file.write(unref_symbol + "\n")
        unuseClassCount = len(result)
        file.write('classunrefs count: %d\n' % unuseClassCount)
        file.write('filter class startwiths \'%s\'.\n\n' % filters)
        file.close()

        print 'Done! unuseClassResult.txt already stored in script dir.'

        desc = '无用类数量：' + str(unuseClassCount) + '  ' + "过滤前缀：" + filters
        print desc
