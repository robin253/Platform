#!/usr/bin/python
# -*- coding: UTF-8 -*-
#字典的处理

#mergedict函数
#将两个字典的内容合并

from list_manipulation import delRepeat    #删除列表中的重复项  相同项只保留一个

def mergedict (inputdict1,inputdict2):
    list1=inputdict1.keys()
    list2=inputdict2.keys()
    listsum=list1+list2
    listsum=delRepeat(listsum)
    #print listsum
    dictsum={}

    for item in listsum:
        tmp1=inputdict1.get(item)
        tmp2=inputdict2.get(item)
        if tmp1==None and  tmp2==None:
            tmpsum=''
        #elif tmp1==tmp2 and tmp1!=None:
        #    tmpsum=tmp1
        elif tmp1==None:
            tmpsum=tmp2
        elif tmp2==None:
            tmpsum=tmp1
        else:
            tmp1=str(tmp1)
            tmp2=str(tmp2)
            tmpsum=tmp1+","+tmp2
        dictsum[item]=tmpsum
    return dictsum


#dict1 = {'a':'1,2','c':3}
#dict2 = {'a':5,'b':6,'c':'fd','d':'x'}
#dictre=mergedict(dict1,dict2)
#print dictre

#{'a': '1,2,5', 'c': '3,fd', 'b': 6, 'd': 'x'}
