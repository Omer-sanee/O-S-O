# backend/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to OSO!</h1><p>Your app is live!</p>")
