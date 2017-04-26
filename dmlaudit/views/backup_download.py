# -*- coding:utf-8 -*-
from django.http import StreamingHttpResponse #用于下载文件

from dmlaudit import constant
import os
from django.contrib.auth.decorators import login_required




@login_required(login_url="/")
def backup_download(request):
    downloadfilename=request.POST['downloadfilename']
    downloadfilename=str(downloadfilename)+".zip"
    full_filename=constant.backup_filepath+'/'+downloadfilename
    def file_iterator(file_name,chunk_size=512):
        f =open(file_name,"rb")
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
        f.close()

    response = StreamingHttpResponse(file_iterator(full_filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(downloadfilename)
    response['Content-Length'] = os.path.getsize(full_filename)#传输给客户端的文件大小
    return response

    #http://blog.csdn.net/w6299702/article/details/38777165
    #not work in Django 1.10.5
    #def readFile(fn, buf_size=262144):#大文件下载，设定缓存大小
    #    f = open(fn, "rb")
    #    while True:
    #        c = f.read(buf_size)
    #        if c:
    #            yield c
    #        else:
    #            break
    #    f.close()

    #response = HttpResponse(readFile(full_filename), content_type='APPLICATION/OCTET-STREAM') #设定文件头，这种设定可以让任意文件都能正确下载，而且已知文本文件不是本地打开
    #response['Content-Disposition'] = 'attachment; filename="{0}"'.format(downloadfilename)
    #response['Content-Length'] = os.path.getsize(full_filename)#传输给客户端的文件大小
    #return response
