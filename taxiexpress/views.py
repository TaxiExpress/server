from django import forms
from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse
from taxiexpress.models import Customer
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D

# Create your views here.

@csrf_exempt    
def loginUser(request):
    if request.method == "POST":
        try:
            customer = Customer.objects.get(username=request.POST['username'])  
        except ObjectDoesNotExist:
            return HttpResponse(status_code=401, reason_phrase="The username or password was not correct")
        if customer.password == request.POST['password']:
            request.session['username'] = customer.username
            request.session['user_id'] = customer.id
            response_data = {}
            response_data['username'] = customer.username
            response_data['first_name'] = customer.first_name
            response_data['last_name'] = customer.last_name
            response_data['email'] = customer.email
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponse(status_code=401, reason_phrase="The username or password was not correct")
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        if (Customer.objects.filter(username=request.POST['username']).count() > 0):
            return HttpResponse(status_code=401, reason_phrase="The username is in use")
        elif (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status_code=401, reason_phrase="The email is in use")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            c = Customer(username=request.POST['username'], password=passtemp, email=request.POST['email'], first_name=['first_name'], last_name=['last_name'])
            c.save()
            return HttpResponse(status_code=201,reason_phrase="Created")
    else:
        return HttpResponseBadRequest()

def getClosestTaxi(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))

        list_TaxiDrivers = Driver.objects.distance(pointclient).order_by('distance')[0]

        #return JSON with taxi info



