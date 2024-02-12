from django.contrib import admin
from django.urls import path
from Dashboard.views import fetch_trials, fetch_trials_csv, scrape_alsod_gene_list
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fetch_trials/', fetch_trials, name='fetch_trials'),
    path('fetch_trials_csv/', fetch_trials_csv, name='fetch_trials_csv'),
    path('scrape_alsod_gene_list/', scrape_alsod_gene_list, name='scrape_alsod_gene_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    scrape_alsod_gene_list