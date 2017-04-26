# -*- coding:utf-8 -*-
from django.shortcuts import render

from dmlaudit import constant
import os
from django.contrib.auth.decorators import login_required,permission_required




@login_required(login_url="/")
@permission_required('dmlaudit.dmlbackup_access',login_url="/")
def backup(request):
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage','1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''

    #判断点击了【下一页】还是【上一页】
    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * constant.ONE_PAGE_OF_DATA
    endPos = startPos + constant.ONE_PAGE_OF_DATA
    list_file=[]
    
    #os.chdir(constant.backup_filepath)
    #curr_filepath=os.getcwd()    #获取当前路径
    curr_filepath=constant.backup_filepath#这样不会出现异常 os.chdir会出现异常
    #print curr_filepath


    for root,dirs,files in os.walk(curr_filepath):#获取当前路径下的文件夹和文件
        for file in files:
            #list_file.append(os.path.join(root,file))
            if file.endswith(".zip"):
                list_file.append(file.replace(".zip",""))
    list_file.sort()
    list_file.reverse()#排序 反转
    #print list_file
    list_showfilename = list_file[startPos:endPos]
    list_showfilename=tuple(list_showfilename)#前端按顺序
    


    #只在网页第一次加载的时候查询记录总数，计算出共需要分为几页
    if curPage == 1 and allPage == 1:
        allPostCounts = len(list_file)
        allPage = allPostCounts / constant.ONE_PAGE_OF_DATA
        if allPostCounts % constant.ONE_PAGE_OF_DATA >0:
            allPage += 1
    

    backup_info = {
        'list_showfilename':list_showfilename,
        'allPage':allPage,
        'curPage':curPage
    }
    return render(request,'dmlaudit/backup.html', backup_info)
