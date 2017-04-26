#!/bin/env python
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect


#认证相关
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


#根目录访问登陆页面 通过这个函数确定是否登陆成功 
#失败还是原目录  没必要多一个view函数


def home(request):#不要命名为login 会冲突

    if request.user.is_authenticated:#检测是否登陆
        return HttpResponseRedirect('/dmlaudit/audit')
    else:
        if request.method=="GET":
            return render(request,'usercontrol/home.html')

        if request.method == 'POST':
            username = request.POST.get('account_name', '')
            password = request.POST.get('account_passwd', '')
            user = authenticate(username=username,password=password)#利用django.contrib.auth验证用户信息
            if user is not None:
                login(request,user)#登陆了
                return HttpResponseRedirect('/dmlaudit/audit')

            else:
                return render(request,'usercontrol/home.html',{'error':True})




@login_required(login_url="/")
def userlogout(request):#不要命名为logout 会冲突
    logout(request)#当调用该函数时，当前请求的session信息会全部清除
    return HttpResponseRedirect('/')#跳到登陆页面  



@login_required(login_url="/")
def changepasswd(request):
    if request.method == 'POST':
        passwd = request.POST.get('passwd', '')
        new_passwd = request.POST.get('new_passwd', '')
        new_passwd2 = request.POST.get('new_passwd2','')
        #print "==",new_passwd
        #print "===",new_passwd2
        if str(new_passwd)!=str(new_passwd2):
            return render(request, 'usercontrol/changepasswd.html',{'failinfo':"两次新密码输入不一致"})
        elif len(new_passwd)<8:
            return render(request, 'usercontrol/changepasswd.html',{'failinfo':"新密码长度需大于等于八位"})
        else:
            user = authenticate(username=request.user.username,password=passwd)#利用django.contrib.auth验证用户信息
            if user is not None:
                user.set_password(new_passwd)
                user.save()
                return render(request, 'usercontrol/changepasswd.html',{'sucinfo':"密码重置成功"})
            else:
                return render(request, 'usercontrol/changepasswd.html',{'failinfo':"原始密码不正确"})
    else:
        return render(request, 'usercontrol/changepasswd.html')