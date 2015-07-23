from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from search import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^results/$', views.results, name='results'),
    url(r'^search/$', views.search, name='search'),
    url(r'^refresh/$', views.refresh, name='refresh'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
)
