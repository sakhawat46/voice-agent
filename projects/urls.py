from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),

    # add by sakhawat
    path('api/', include('apps.users.urls')),
    path('', include('apps.voice.urls')),
    path('test_chat.html', TemplateView.as_view(template_name='test_chat.html')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)