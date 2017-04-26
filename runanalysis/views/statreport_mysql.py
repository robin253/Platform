# -*- coding:utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required




@login_required(login_url="/")
def statreport_mysql(request):
    return render(request, 'runanalysis/statreport_mysql.html')