"""PCBTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from PCBTracker import views

admin.autodiscover()

urlpatterns = [
    # View (single) boards
    url(r'^board/(?P<class_id>\d+)/$', views.boards),
    url(r'^board/detail/(?P<board_id>\d+)/$', views.board),
    url(r'^board/new/(?P<class_id>\d+)/$', views.add_board),
    url(r'^board/edit/(?P<board_id>\d+)/$', views.edit_board),
    url(r'^board/export_patches/(?P<status_id>\d+)/$', views.export_patches),
    url(r'^board/$', views.boards),

    # View (single) patches
    url(r'^patch/(?P<patch_id>\d+)/$', views.patch),
    url(r'^patch/new/(?P<class_id>\d+)/$', views.add_patch),
    url(r'^patch/edit/(?P<patch_id>\d+)/$', views.edit_patch),

    # Add new project
    url(r'^project/new/$', views.add_project),
    url(r'^project/edit/(?P<project_id>\d+)/$', views.edit_project),

    # Add new boardclass
    url(r'^boardclass/new/(?P<project_id>\d+)/$', views.add_boardclass),
    url(r'^boardclass/edit/(?P<class_id>\d+)/$', views.edit_boardclass),

    # Add new event for a board
    url(r'^event/new/(?P<board_id>\d+)/$', views.add_event),

    # Claim board (as user) or change location
    url(r'^claim/(?P<board_id>\d+)/$', views.claim_board),
    url(r'^newlocation/(?P<board_id>\d+)/$', views.add_location),

    # Search function with raw input
    url(r'^search_raw/(?P<searchstring>.+)$', views.raw_search),

    # Search function
    url(r'^search/$', views.search),

    # Login and registration
    url(r'^register/$', views.do_register),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'login.html' }),
    url(r'^accounts/logout/$', auth_views.logout, {'template_name': 'logout.html' }),

    url(r'^login/$', auth_views.login, {'template_name': 'login.html' }),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logout.html' }),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Fall through to Main Page
    url(r'^main/$', views.reset_index),

    url(r'^', views.index)
]
