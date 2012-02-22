from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('elin.views',
    url(r'^$', 'login'),
    url(r'^thanks$', 'thanks'),
)