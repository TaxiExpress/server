from django import forms
from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
import json

# Create your views here.

@csrf_exempt    
def loginUser(request):
    if request.method == "POST":
        if request.POST['email'] is None:
            return HttpResponse(status=401, content="Email not received")
        try:
            customer = Customer.objects.get(email=request.POST['email'])  
        except ObjectDoesNotExist:
            return HttpResponse(status=401, content="The email or password was not correct")
        if customer.password == request.POST['password']:
            request.session['email'] = customer.email
            request.session['user_id'] = customer.id
            response_data = {}
            response_data['email'] = customer.email
            if customer.first_name != "":
                response_data['first_name'] = customer.first_name
            if customer.last_name != "":
                response_data['last_name'] = customer.last_name
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponse(status=401, content="The email or password was not correct")
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=401, content="The email is in use")
        if (Customer.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=401, content="The phone number is in use")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            c = Customer(username=request.POST['email'], password=passtemp, phone=['phone'])
            c.save()
            return HttpResponse(status=201,content="Created")
    else:
        return HttpResponseBadRequest()

def getClosestTaxi(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))

        list_TaxiDrivers = Driver.objects.distance(pointclient).order_by('distance')[0]

        #return JSON with taxi info



