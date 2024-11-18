from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # URL para a administração do Django
    path('', include('social_django.urls', namespace='social')),
    path('', include('core.urls')),  # Inclui as URLs do app 'core'
]
