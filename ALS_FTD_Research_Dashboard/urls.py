from django.contrib import admin
from django.urls import path
from Dashboard.views import process_and_save_trials_data
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('process_and_save_trials_data/', process_and_save_trials_data, name='process_and_save_trials_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
