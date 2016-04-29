from django.conf.urls import include, url
from shielddash.api.views import RetentionView
from django.contrib import admin

urlpatterns = [
    url(r'^retention/', RetentionView.as_view(), name='retention'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('googleauth.urls')),
]
