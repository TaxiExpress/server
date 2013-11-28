from django import forms
from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse
from taxiexpress.models import Client
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

# Create your views here.

@csrf_exempt    
def loginClient(request):
    if request.method == "POST":
        try:
            user = Client.objects.get(username=request.POST['user'])  
        except ObjectDoesNotExist:
            return HttpResponse(status_code=401, reason_phrase="The username or password was not correct")
        if user.password == request.POST['password']:
            request.session['user'] = user.username
            request.session['user_id'] = user.id
            return HttpResponse(status_code=200,reason_phrase="Loged In")
        else:
            return HttpResponse(status_code=401, reason_phrase="The username or password was not correct")
    else:
        return HttpResponse(status_code=400, reason_phrase="Bad request")