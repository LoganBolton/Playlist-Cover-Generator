from django.shortcuts import render, redirect
from .models import TodoItem
from django.views.decorators.http import require_POST
from .utils import driver
import requests

def index(request):
    todo_list = TodoItem.objects.order_by('id')
    return render(request, 'playlister/index.html', {'todo_list': todo_list})

@require_POST
def add_todo(request):
    title = request.POST['title']
    TodoItem.objects.create(title=title)
    return redirect('index')

def complete_todo(request, todo_id):
    todo = TodoItem.objects.get(pk=todo_id)
    todo.completed = True
    todo.save()
    return redirect('index')

def get_joke(request):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    if response.status_code == 200:
        joke_data = response.json()
        joke = f"{joke_data['setup']} ... {joke_data['punchline']}"
    else:
        joke = "Failed to fetch a joke. Please try again later."
    
    todo_list = TodoItem.objects.order_by('id')
    return render(request, 'playlister/index.html', {'todo_list': todo_list, 'joke': joke})

def generate_image(request):
    image_url = driver(1234)  # Call the driver function to get the image URL
    
    return render(request, 'playlister/display_image.html', {'image_url': image_url})