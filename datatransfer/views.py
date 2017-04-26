#!/bin/env python
# -*- coding: UTF-8 -*-
from django.shortcuts import render



#page view
def transfer(request):
    
    return render(request, 'datatransfer/logicbackup.html')



#page view
def history(request):
    
    return render(request, 'datatransfer/logicbackup.html')


#page view
def logicalbackup(request):
    
    return render(request, 'datatransfer/logicbackup.html')

