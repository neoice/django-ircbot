from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Uncomment the next line to enable the admin:
	(r'^', include(admin.site.urls)),
)
