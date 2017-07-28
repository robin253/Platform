"""dbenvmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin

import cmdb.views
import dmlaudit.views
import ddlaudit.views
import runanalysis.views
import performance.views
import datatransfer.views
import usercontrol.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^newbee/', include('newbee.urls')),

    url(r'^$', usercontrol.views.home),
    url(r'^usercontrol/userlogout$', usercontrol.views.userlogout),
    url(r'^usercontrol/changepasswd$', usercontrol.views.changepasswd),

    url(r'^cmdb/getdatabase$', cmdb.views.getdatabase),
    url(r'^cmdb/getschema$', cmdb.views.getschema),
    url(r'^cmdb/getapp$', cmdb.views.getapp),

    url(r'^dmlaudit/audit$', dmlaudit.views.audit),
    url(r'^dmlaudit/backup$', dmlaudit.views.backup),
    url(r'^dmlaudit/backup/download$', dmlaudit.views.backup_download),
    url(r'^dmlaudit/checkresult$', dmlaudit.views.checkresult),
    url(r'^dmlaudit/dbause$', dmlaudit.views.dbause),
    url(r'^dmlaudit/dbause/changestatus$', dmlaudit.views.dbause_changestatus),
    url(r'^dmlaudit/dbause/execute$', dmlaudit.views.dbause_execute),
    url(r'^dmlaudit/report$', dmlaudit.views.report),
    url(r'^dmlaudit/faq$', dmlaudit.views.faq),
    url(r'^dmlaudit/errorcheck$', dmlaudit.views.errorcheck),

    url(r'^ddlaudit/audit$', ddlaudit.views.audit),
    url(r'^ddlaudit/checkresult$', ddlaudit.views.checkresult),
    url(r'^ddlaudit/structure$', ddlaudit.views.structure),
    url(r'^ddlaudit/dbause$', ddlaudit.views.dbause),
    url(r'^ddlaudit/report$', ddlaudit.views.report),
    url(r'^ddlaudit/faq$', ddlaudit.views.faq),


    url(r'^runanalysis/statreport/ash$', runanalysis.views.statreport_ash),
    url(r'^runanalysis/statreport/awr$', runanalysis.views.statreport_awr),
    url(r'^runanalysis/statreport/mysql$', runanalysis.views.statreport_mysql),
    url(r'^runanalysis/statreport/download$', runanalysis.views.statreport_download),
    url(r'^runanalysis/statreport/monthcheck$', runanalysis.views.statreport_monthcheck),

    url(r'^runanalysis/objectcheck$', runanalysis.views.objectcheck),
    url(r'^runanalysis/objectcheck/download$', runanalysis.views.objectcheck_download),
    url(r'^runanalysis/objectcheck/index$', runanalysis.views.objectcheck_index),

    url(r'^runanalysis/dbstatus$', runanalysis.views.dbstatus),

    url(r'^performance/sqlplanchange$', performance.views.sqlplanchange),
    url(r'^performance/sqlanalysis$', performance.views.sqlanalysis),
    url(r'^performance/sqlinefficient$', performance.views.sqlinefficient),
    url(r'^performance/sqlinefficient/changestatus$', performance.views.sqlinefficient_changestatus),

    url(r'^datatransfer/oradump/expdp$', datatransfer.views.oradump_expdp),
    url(r'^datatransfer/oradump/expdpcommand$', datatransfer.views.oradump_expdpcommand),
    url(r'^datatransfer/oradump/impdp$', datatransfer.views.oradump_impdp),
    url(r'^datatransfer/oradump/impdpcommand$', datatransfer.views.oradump_impdpcommand),
    url(r'^datatransfer/oraldr$', datatransfer.views.trans_oraldr),
    url(r'^datatransfer/mysqldump$', datatransfer.views.trans_mysqldump),
    url(r'^datatransfer/logicalbackup$', datatransfer.views.logicalbackup),
    url(r'^datatransfer/hisdata$', datatransfer.views.hisdata),

]
