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
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

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
                'Certified_Request': package.objects.filter(packageid = trackingNumber),
                'tracking_number' : trackingNumber
            }
            return render(request, 'ups_show.html', context)
    else:
        form = UpsSearch()
    return render(request, 'ups.html', {'form':form})

class UpsUpdateView(LoginRequiredMixin, UpdateView):
    model = package
    fields = ['location_x', 'location_y']
    success_url = reverse_lazy('ups')
    success_message = "Your destination has been updated successfully"
    def form_valid(self, form):
        form.instance.account = self.request.user
        return super().form_valid(form)

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.account:
            return True
        return False

