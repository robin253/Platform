# -*- coding:utf-8 -*-
from django.http import StreamingHttpResponse #用于下载文件
from django.shortcuts import render

from runanalysis import constant
import os
from django.contrib.auth.decorators import login_required




@login_required(login_url="/")
def objectcheck_download(request):
    if request.POST.has_key('downloadfilename'):
        downloadfilename=request.POST['downloadfilename']
        reportfile_path=constant.reportfile_path
        full_filename=reportfile_path+'/'+downloadfilename
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


    else:
        return render(request, 'runanalysis/objectcheck.html')

     
