from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from students_api import urls as std_api_urls
from admin_api import urls as admin_api_urls
from lecturers_api import urls as lecturers_api_urls
from selc_core import urls as core_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('std-api/', include(std_api_urls)),
    path('admin-api/', include(admin_api_urls)),
    path('lecturers-api/', include(lecturers_api_urls)),
    path('core/', include(core_urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
