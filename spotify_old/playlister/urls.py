from django.urls import path
from . import views
from .views import generate_image
from .controllers import spotify_auth

urlpatterns = [
    path('', views.get_playlists, name='index'),
    path('generate-image/<str:playlist_id>/', generate_image, name='generate_image'),
    path('playlists/', views.get_playlists, name='playlists'),
    path('spotify/auth/', spotify_auth.spotify_auth, name='spotify_auth'),
    path('callback/', spotify_auth.spotify_callback, name='spotify_callback'),
    path('spotify/logout/', spotify_auth.spotify_logout, name='spotify_logout'),
]