#!/usr/bin/python
# -*- coding: UTF-8 -*-
#列表的处理

#delRepeat函数
#删除列表中的重复项 相同项只保留一个
def delRepeat(inputlist):
    for item in inputlist:
        while inputlist.count(item)>1:          #查看某个项出现的次数 
            del inputlist[inputlist.index(item)]  #查看某个项第一次出现的位置  删除这个位置的项
    return inputlist


#analyseRepeat函数
#统计列表中的重复项 返回一个字典
def analyseRepeat(inputlist):
    tmp_dict={}
    for item in inputlist:
        if tmp_dict.has_key(item):
            tmp_dict[item]+=1
        else:
            tmp_dict[item]=1
    return tmp_dict





#comparetwolists函数
#对比两个列表,将差异返回为一个元祖（两个列表） 输入的列表不要有重复项
def comparetwolists(list1,list2):
    tmp_list1=[]
    tmp_list2=[]
    tmp_list1=tmp_list1+list1
    tmp_list2=tmp_list2+list2
    for item in list1:
        if list2.count(item)>0:
            tmp_list1.remove(item)
            tmp_list2.remove(item)
    return tmp_list1,tmp_list2

#list1=['ENDTIME', 'BEGIN', 'FILE_ID','NAME', 'ID','']
#list2=['ID', 'NAME', 'ENDTIME','COOL','']
#re=comparetwolists(list1,list2)
#print re  #(['BEGIN', 'FILE_ID'], ['COOL'])
#print re[0] #['BEGIN', 'FILE_ID'] list1的多余项
#print re[1] #['COOL']  list2的多余项

#removeoneitem函数
#删除列表中的某个项 符合这个项的全部删除
def removeoneitem(orilist,inputstr):
    tmp_list=[]
    tmp_list=tmp_list+orilist
    for item in orilist:
        if item==inputstr:
            tmp_list.remove(item)
    return tmp_list
    

#removesomeitems函数
#删除列表中的一些项，删除项来自列表remove_list  符合这些项的全部删除
def removesomeitems(orilist,remove_list):
    remove_list=delRepeat(remove_list)
    for item in remove_list:
        orilist=removeoneitem(orilist,item)
    return orilist
        

#removetheoneafter函数
#删除列表中某个项的后面一项
def removetheoneafter(orilist,removestr):
    i=0
    for item in orilist:
        if item==removestr:
            del orilist[i+1]
        i=i+1
    return orilist


