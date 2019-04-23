from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import package, truck
from .form import UserRegisterForm, UpsSearch
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.


def register(request):
    if request.method == 'POST':  # data sent by user
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # this will save Car info to database
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form':form})

@login_required
def ups(request):
    if request.method == 'POST':
        form = UpsSearch(request.POST)
        if form.is_valid():
            trackingNumber = form.cleaned_data.get('TrackingNumber')
            context = {
                'Certified_Request': package.objects.filter(packageid = 222),
            }
            return render(request, 'ups_show.html', context)
    else:
        form = UpsSearch()
    return render(request, 'ups.html', {'form':form})