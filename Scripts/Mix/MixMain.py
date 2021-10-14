#coding:utf-8
import os

def mixMain():
    print('start renameMethods...')
    os.system('python3 ./renameMethods.py')
    print('start renamePodMethods...')
    os.system('python3 ./renamePodMethods.py')
    print('start MixClass...')
    os.system('python3 ./MixClass.py')
    print('start parseMixClasses...')
    os.system('python3 ./parseMixClasses.py')
    print('finish mix!')

mixMain()


