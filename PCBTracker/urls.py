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
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from tracker import views

admin.autodiscover()

urlpatterns = [
    # View (single) boards
    re_path(r'^board/(?P<class_id>\d+)/$', views.boards, name='board'),
    re_path(r'^board/detail/(?P<board_id>\d+)/$', views.board, name='board-details'),
    re_path(r'^board/new/(?P<class_id>\d+)/$', views.add_board, name='board-new'),
    re_path(r'^board/edit/(?P<board_id>\d+)/$', views.edit_board, name='board-edit'),
    re_path(r'^board/export_patches/(?P<status_id>\d+)/$', views.export_patches, name='patches-export'),
    re_path(r'^board/$', views.boards, name='boards'),

    # View (single) patches
    re_path(r'^patch/(?P<patch_id>\d+)/$', views.patch, name='patch'),
    re_path(r'^patch/new/(?P<class_id>\d+)/$', views.add_patch, name='patch-new'),
    re_path(r'^patch/edit/(?P<patch_id>\d+)/$', views.edit_patch, name='patch-edit'),

    # Add new project
    re_path(r'^project/new/$', views.add_project, name='project-new'),
    re_path(r'^project/edit/(?P<project_id>\d+)/$', views.edit_project, name='project-edit'),

    # Add new boardclass
    re_path(r'^boardclass/new/(?P<project_id>\d+)/$', views.add_boardclass, name='boardclass-new'),
    re_path(r'^boardclass/edit/(?P<class_id>\d+)/$', views.edit_boardclass, name='boardclass-edit'),

    # Add new event for a board
    re_path(r'^event/new/(?P<board_id>\d+)/$', views.add_event, name='event-new'),

    # Claim board (as user) or change location
    re_path(r'^claim/(?P<board_id>\d+)/$', views.claim_board, name='claim'),
    re_path(r'^newlocation/(?P<board_id>\d+)/$', views.add_location, name='location-new'),

    # Search function with raw input
    re_path(r'^search_raw/(?P<searchstring>.+)$', views.raw_search, name='search-raw'),

    # Search function
    re_path(r'^search/$', views.search, name='search'),

    # Login and registration
    re_path(r'^register/$', views.do_register, name='register'),
    re_path(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html' ), name='accounts-login'),
    re_path(r'^accounts/logout/$', auth_views.LogoutView.as_view(template_name='logout.html' ), name='accounts-logout'),

    re_path(r'login/$', auth_views.LoginView.as_view(template_name='login.html' ), name='login'),
    re_path(r'logout/$', auth_views.LogoutView.as_view(template_name='logout.html' ), name='logout'),

    # Uncomment the next line to enable the admin:
    re_path(r'admin/', admin.site.urls),

    # Fall through to Main Page
    re_path(r'main/$', views.reset_index, name='main'),

    re_path(r'^', views.index, name='index')
]
