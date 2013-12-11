from django import forms
from django.core.mail import EmailMessage
from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
from django.core import serializers
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
            response_data['phone'] = customer.phone
            if customer.first_name != "":
                response_data['first_name'] = customer.first_name
            if customer.last_name != "":
                response_data['last_name'] = customer.last_name
            if not (customer.favlist.count() == 0):
                response_data['favlist'] = customer.favlist
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
            email = EmailMessage('Hello', 'World', to=[request.POST['email']])
            email.send()
            
            return HttpResponse(status=201,content="Created")
    else:
        return HttpResponseBadRequest()

def testEmail(request):
    email = EmailMessage('Hello', 'World', to=['gorka_12@hotmail.com'])
    email.send()
    return HttpResponse(status=200,content="OK")

def getClosestTaxi(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))

        list_TaxiDrivers = Driver.objects.distance(pointclient).order_by('distance')[0]

        #return JSON with taxi info

def loadData(request):
    co = Country(code = 108,name='Espana')
    co.save()
    s = State(code = 48, name = 'Bizkaia', country = co)
    s.save()
    ci = City(code = 013, name = 'Barakaldo', state = s)
    ci.save()
    ci = City(code = 015, name = 'Basauri', state = s)
    ci.save()
    ci = City(code = 016, name = 'Berango', state = s)
    ci.save()
    ci = City(code = 017, name = 'Bermeo', state = s)
    ci.save()
    ci = City(code = 020, name = 'Bilbao', state = s)
    ci.save()
    ci = City(code = 027, name = 'Durango', state = s)
    ci.save()
    ci = City(code = 036, name = 'Galdakao', state = s)
    ci.save()
    ci = City(code = 040, name = 'Gatika', state = s)
    ci.save()
    ci = City(code = 043, name = 'Gorliz', state = s)
    ci.save()
    ci = City(code = 044, name = 'Getxo', state = s)
    ci.save()
    ci = City(code = 046, name = 'Gernika-Lumo', state = s)
    ci.save()
    ci = City(code = 054, name = 'Leioa', state = s)
    ci.save()
    ci = City(code = 057, name = 'Lekeitio', state = s)
    ci.save()
    ci = City(code = 065, name = 'Ugao-Miraballes', state = s)
    ci.save()
    ci = City(code = 78, name = 'Portugalete', state = s)
    ci.save()
    ci = City(code = 81, name = 'Lezama', state = s)
    ci.save()
    ci = City(code = 82, name = 'Santurtzi', state = s)
    ci.save()
    ci = City(code = 84, name = 'Sestao', state = s)
    ci.save()
    ci = City(code = 85, name = 'Sopelana', state = s)
    ci.save()
    ci = City(code = 89, name = 'Urduliz', state = s)
    ci.save()
    dr = Driver(email="conductor@gmail.com", password="1111", phone="656111112", first_name="Conductor", last_name="DePrimera", city=ci)
    dr.save()
    dr2 = Driver(email="conductor2@gmail.com", password="1111", phone="656111113", first_name="Conductor", last_name="DeSegunda", city=ci)
    dr2.save()
    cu = Customer(email="gorka_12@hotmail.com", password="1111", phone="656111111", first_name="Pepito", last_name="Palotes", city=ci)
    cu.save()
    cu.favlist.add(dr)
    cu.favlist.add(dr2)
    return HttpResponse(status=201,content="Loaded")

