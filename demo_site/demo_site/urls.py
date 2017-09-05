"""demo_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from demo_site import views as demo_site_views
admin.autodiscover()

# Customize Django admin
admin.site.site_header = 'Django Aliyun OSS Storage'

urlpatterns = [
    url(r'^$', demo_site_views.home, name='home'),
    #url(r'^login/$', auth_views.login, name='login'),
    url(r'^admin/', include(admin.site.urls)),
]
