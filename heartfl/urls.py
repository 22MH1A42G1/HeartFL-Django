from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index') if request.user.is_authenticated else redirect('accounts:login')),
    path('accounts/', include('accounts.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('federation/', include('federation.urls')),
    path('predictions/', include('predictions.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
