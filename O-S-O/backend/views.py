from django.http import HttpResponse

def home(request):
    return HttpResponse("OSO backend is running 🚀")
