from django.conf.urls import include, url
# from django.contrib import admin
from newbee.webui import views
from newbee.webui.forms import LoginForm
# from info_api.models import List
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = [
    # url(r'^mission/create/$',views.CreateMissionView,name='mission-create'),
    #edit by guziqiang
    url(r'^$',views.index,name='newbeeindexurl'),
    # url(r'^mysql_list/$',login_required(views.Mysql_listViewSet.as_view()),name='mysql_list'),
    url(r'host/$',login_required(views.HostViewSet.as_view(),login_url='/'),name='newbeehosturl'),
    url(r'role/$',login_required(views.RoleViewSet.as_view(),login_url='/'),name='newbeeroleurl'),
    url(r'^exe_group/$',login_required(views.Exe_groupViewSet.as_view(),login_url='/'),name='newbee_exegroup'),
    url(r'^host_exe_group/$',login_required(views.Host_exe_groupViewSet.as_view(),login_url='/'),name='host_exe_group'),
    url(r'^mission/$',login_required(views.MissionViewSet.as_view(), login_url='/'),name='newbee_mission'),

    # url(r'^mission/\?status=0$',login_required(views.MissionViewSet.as_view()),name='mission_status'),
    url(r'^finished_mission/$',login_required(views.Finished_missionViewSet.as_view()),name='newbee_donemission'),
    # url(r'^finished_mission/\?status=1$',login_required(views.Finished_missionViewSet.as_view()),name='finished_mission_status'),




    # url(r'^mission/create/$',login_required(views.CreateMissionView.as_view()),name='mission-create'),
    # url(r'^mission/update/(?P<mark>[0-9a-z-]+)/$',login_required(views.UpdateMissionView.as_view()),name='mission-update'),
    # url(r'^mission/delete/(?P<mark>[0-9a-z-]+)/$',login_required(views.DeleteMissionView.as_view()),name='mission-delete'),
    # url(r'^mission/update/(?P<mark>\s+)/$',login_required(views.CreateMissionView.as_view()),name='mission-update'),
    # url(r'^login/$',
        # 'django.contrib.auth.views.login',
        # {
            # 'template_name': 'login.html',
            # 'authentication_form': LoginForm,

        # },
        # name='login'),
    # Django Select2
    url(r'^select2/', include('django_select2.urls')),

    # url(r'^logout/$',
        # 'django.contrib.auth.views.logout',
        # {
            # 'next_page': '/',
        # },
        # name='logout'),
]
