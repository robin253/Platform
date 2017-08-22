# -*- coding:utf-8 -*-
from django.http import StreamingHttpResponse #用于下载文件
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ddlaudit import models


@login_required(login_url="/")
def download(request):
    if request.POST.has_key('downloadresult'):
        audit_batch=request.POST['downloadresult']
        #print audit_batch

        try:
            audit_detail=models.T_DDLAUDIT_BATCH_INFO.objects.get(audit_batch=audit_batch)
            re_detail=audit_detail.t_ddlaudit_batch_detail_set.all().order_by('sqlnum') 
            #关联查询 注意大小写是默认的方法   查询关联表数据 re_detail[0].audit_batch.audit_user
        except:
            return render(request, 'ddlaudit/audit.html')
        else:
            i=0
            for item in re_detail:
                if i==0:
                    audit_content="======="+item.audit_batch.audit_batch+"批次审核结果=======\n"
                    audit_content=audit_content+"应用模块:"+item.audit_batch.app_name+"  审核结果:"+item.audit_batch.batch_status+"\n"+"\n"+"\n"
                    
                i=i+1
                audit_content= audit_content+   str(item.sqlnum)+"."+str(item.sqltext)+"\n" #+str(item.sqltype)
                for item in  eval(item.audit_result):
                    if item[0]==0:
                        tmpstr="[通过]"
                    elif item[0]==1:
                        tmpstr="[警告]"
                    elif item[0]==2:
                        tmpstr="[错误]"
                    else:
                        tmpstr="[信息]"
                    audit_content= audit_content+   tmpstr+str(item[1])+"\n"
                audit_content=audit_content+"\n"


       

        response = StreamingHttpResponse(audit_content)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(audit_batch+".txt")
        return response


    else:
        return render(request, 'ddlaudit/audit.html')

     