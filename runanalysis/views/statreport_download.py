# -*- coding:utf-8 -*-

from django.http import StreamingHttpResponse #用于下载文件
from django.contrib.auth.decorators import login_required

import os
from runanalysis import constant



#下载文件
@login_required(login_url="/")
def statreport_download(request):
    filename=request.POST['filename']
    reportfile_path=constant.reportfile_path
    full_filename=reportfile_path+'/'+filename
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
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
    response['Content-Length'] = os.path.getsize(full_filename)#传输给客户端的文件大小
    return response
