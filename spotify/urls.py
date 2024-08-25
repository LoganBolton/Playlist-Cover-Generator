from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('playlister.urls')),  # Replace 'myapp' with your actual app name
]
