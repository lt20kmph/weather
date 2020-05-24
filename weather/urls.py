"""weather URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    /correlations/sfcWind/sun/ann
"""
from django.urls import path
from django.conf.urls import url

from maps import views

urlpatterns = [
    # url(r'^tasmax/ann/$', views.tasmaxAnn, name='tasmaxAnn'),
    # url(r'^tasmin/ann/$', views.tasminAnn, name='tasminAnn'),
    # url(r'^rainfall/ann/$', views.rainfallAnn, name='rainfallAnn'),
    # url(r'^sun/ann/$', views.sunAnn, name='sunAnn'),
    # url(r'^sfcWind/ann/$', views.sfcWindAnn, name='sfcWindAnn'),
    # url(r'^tasmax/mon/(?P<mon>1[0-1]|[0-9])/$', views.tasmaxMon, name='tasmaxMon'),
    # url(r'^tasmin/mon/(?P<mon>1[0-1]|[0-9])/$', views.tasminMon, name='tasminMon'),
    # url(r'^rainfall/mon/(?P<mon>1[0-1]|[0-9])/$', views.rainfallMon, name='rainfallMon'),
    # url(r'^sun/mon/(?P<mon>1[0-1]|[0-9])/$', views.sunMon, name='sunMon'),
    # url(r'^sfcWind/mon/(?P<mon>1[0-1]|[0-9])/$', views.sfcWindMon, name='sfcWindMon'),
    # url(r'^correlations/sun/ann/$', views.CSunAnn, name='CSunAnn'),
    # url(r'^correlations/tasmax/ann/$', views.CTasmaxAnn, name='CTasmaxAnn'),
    # url(r'^correlations/tasmin/ann/$', views.CTasminAnn, name='CTasminAnn'),
    # url(r'^correlations/rainfall/ann/$', views.CRainfallAnn, name='CRainfallAnn'),
    # url(r'^correlations/sfcWind/ann/$', views.CSfcWindAnn, name='CSfcWindAnn'),
    url(r'^correlations/(?P<stat1>\w*)/(?P<stat2>\w*)/ann/$',
        views.CorrelationViews2,
        {'t':'A'},
        name='correlations2',),
    url(r'^correlations/(?P<stat1>\w*)/(?P<stat2>\w*)/mon/(?P<t>1[0-1]|[0-9])/$',
        views.CorrelationViews2,
        name='correlations2_mon',),
    url(r'^correlations/(?P<stat>\w*)/ann/$',
        views.CorrelationViews,
        {'t':'A'},
        name='correlations',),
    url(r'^correlations/(?P<stat>\w*)/mon/(?P<t>1[0-1]|[0-9])/$',
        views.CorrelationViews,
        name='correlations_mon',),
    url(r'^(?P<stat>\w*)/ann/$',
        views.views,
        {'t':'A'},
        name='default',),
    url(r'^(?P<stat>\w*)/mon/(?P<t>1[0-1]|[0-9])/$',
        views.views,
        name='default_mon'),
    url(r'^$', views.home, name='home'),
    ]
