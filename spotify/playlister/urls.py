from django.urls import path
from . import views
from .views import generate_image

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add_todo, name='add'),
    path('complete/<int:todo_id>/', views.complete_todo, name='complete'),
    path('joke', views.get_joke, name='get_joke'),
    path('generate-image/', generate_image, name='generate_image')
]