from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    #return HttpResponse("<h1>Johan Samuel Rico Nivia</h1>")
    return render(request, 'home.html', {'name': 'Johan Rico'})

def about(request):
    return HttpResponse("<h1>Welcome to the About Page</h1>")