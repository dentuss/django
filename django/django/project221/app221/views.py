from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def hello(request):
    return HttpResponse("Hello World!")

def index(request):
    template = loader.get_template('index.html')
    context = {
        'x': 10,
        'str': 'the string'
    }
    return HttpResponse(template.render(context, request))

def intro(request):
    now = datetime.now()
    timestamp = now.strftime("%H:%M %d.%m.%Y")
    context = {
        'load_time': timestamp
    }
    template = loader.get_template('intro.html')
    return HttpResponse(template.render(context,request))

def privacy(request):
    template = loader.get_template('privacy.html')
    return HttpResponse(template.render({}, request))

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            messages.success(request, f'Акаунт для {username} успішно створено! Тепер ви можете увійти.')
            return redirect('register') 
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})