#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import zipfile

#dmlaudit 
#制作txt备份文件
def Maketxt(filepath,filename,list_input):#[(1,2,3),(4,5,6)]形式
    fo = open(filepath+'/'+filename,"w+")#使用绝对路径 os.chdir在django里会报错 a+追加 w+覆盖
    for item in list_input:
        for i in item:
            fo.write(str(i)+" ")
        fo.write("\n")
    fo.close()

#压缩文件
def Makezip(filepath,zipfilename,list_filename):
    with zipfile.ZipFile(filepath+'/'+zipfilename,'w') as myzip:
        for filename in list_filename:
            myzip.write(filepath+'/'+filename,filename) 
            #myzip.write(filepath+'/'+filename) 没有加第二个参数的话 压缩包解压后会有几层路径文件夹
    
    #删除已被压缩的原文件
    for filename in list_filename:
            os.remove(filepath+'/'+filename)
#zipf = zipfile.ZipFile('test.zip', 'w')
#zipf.write('1.txt')
#zipf.write('2.txt')
#zipf.close()





