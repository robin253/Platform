# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from common import seq_generator

@login_required(login_url="/")
def creation(request):
    return render(request, 'ddlaudit/creation.html')


@login_required(login_url="/")
def creation_schema(request):
    try:
        schema_name = request.GET['schema_name']
    except:
        return render(request, 'ddlaudit/creation.html')
    else:
        schema_password=seq_generator.GenerateRandomPasswd(8)
        schemaapp_password=seq_generator.GenerateRandomPasswd(8)
        schemaread_password=seq_generator.GenerateRandomPasswd(8)
        tmpsrt= render_to_string("sql/oracle/generate.schema.vm",
            {"schema_name":schema_name.upper(),
            "schema_password":schema_password,
            "schemaapp_password":schemaapp_password,
            "schemaread_password":schemaread_password})
        #print tmpsrt
        return HttpResponse(tmpsrt)



@login_required(login_url="/")
def creation_grant(request):
    try:
        grantinfo=request.GET['grantinfo']
        objectstr=grantinfo.split(":")[-1]
        schema=grantinfo.split(":")[0]
        list_object=objectstr.upper().split(",")


    except:
        return render(request, 'ddlaudit/creation.html')
    else:
        tmpsrt= render_to_string("sql/oracle/generate.grant.vm",
            {"schema":schema.upper(),
            "list_object":list_object})
        tmpsrt.replace("\n","")
        #print tmpsrt

        return HttpResponse(tmpsrt)
