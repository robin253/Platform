# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



@login_required(login_url="/")
def dbause(request):
    return render(request, 'ddlaudit/dbause.html')