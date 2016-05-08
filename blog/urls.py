from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.BlogListView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/(?P<blog_link>[\w,-]*)$', views.BlogDetailView.as_view(), name='blog_detail'),
    url(r'^tags', views.TaglistView.as_view(), name='tag_list'),
    url(r'^tag/(?P<tag_name>\w+)$', views.BlogListView.as_view(), name='tag'),
    url(r'^archive', views.ArchiveListView.as_view(), name='archive'),
    url('^about/$', views.about, name='about')
]
