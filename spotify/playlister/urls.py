from django.urls import path
from . import views
from .views import generate_image

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-image/<str:playlist_id>/', generate_image, name='generate_image'),
    path('playlists/', views.get_playlists, name='playlists'),
    
]