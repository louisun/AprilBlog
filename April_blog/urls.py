from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from blog.views import BlogListView

urlpatterns = [

                  url(r'^admin/', admin.site.urls),
                  url(r'^blog/', include('blog.urls', namespace='blog')),
                  url(r'^$', BlogListView.as_view(), name='index'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'April_blog.views.handle404'
