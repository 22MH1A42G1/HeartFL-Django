"""
HeartFL URL Configuration
Main URL routing for the Heart Disease Prediction using Federated Learning application
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from heartfl.admin import heartfl_admin_site

urlpatterns = [
    # Admin panel - Using custom HeartFL admin site
    path('admin/', heartfl_admin_site.urls),
    
    # App URLs
    path('', include('core.urls')),              # Home, About, Contact
    path('accounts/', include('accounts.urls')), # Login, Register, Logout
    path('hospitals/', include('hospitals.urls')), # Hospital management
    path('predict/', include('prediction.urls')), # Prediction interface
    path('federated/', include('federated.urls')), # FL Dashboard
]

# Serve static and media files in development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
