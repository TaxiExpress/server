# -*- encoding: utf-8 -*-

from django import forms
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
from django.core import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import random
from datetime import datetime


# Create your views here.

@csrf_exempt    
def loginUser(request):
    if request.method == "POST":
        if request.POST['email'] is None:
            return HttpResponse(status=401, content="Debes ingresar una dirección de email")
        try:
            customer = Customer.objects.get(email=request.POST['email'])  
        except ObjectDoesNotExist:
            return HttpResponse(status=401, content="Credenciales incorrectas")
        if customer.password == request.POST['password']:
            request.session['email'] = customer.email
            request.session['user_id'] = customer.id
            if customer.phone != request.POST['phone']
                customer.phone = request.POST['phone']
                customer.save()
            datetime_request = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
            if customer.lastUpdate > datetime_request:
                response_data = {}
                response_data['email'] = customer.email
                response_data['phone'] = customer.phone
                if customer.first_name != "":
                    response_data['name'] = customer.first_name
                if customer.last_name != "":
                    response_data['surname'] = customer.last_name
                response_data['lastUpdate'] = customer.lastUpdate
                #if not (customer.favlist.count() == 0):
                #    response_data['favlist'] = list(customer.favlist.all())
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse(status=200,content="OK")
        else:
            return HttpResponse(status=401, content="Credenciales incorrectas")
    else:
        return HttpResponseBadRequest(content="Petición POST esperada")

@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=401, content="Email en uso")
        if (Customer.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=401, content="Teléfono en uso")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            try:
                validate_email( request.POST['email'] )
                c = Customer(username=request.POST['email'], password=passtemp, phone=request.POST['phone'], lastUpdate=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'))
                c.save()
                code = random.randint(1, 999999)
                c.validationCode = code
                c.save()
                #email = EmailMessage('Confirma tu cuenta de Taxi Express', '¡Bienvenido a Taxi Express! Para comenzar a utilizar nuestros servicios deveras confirmar tu direccion de correo eletronico haciendo click en el siguiente enlace:  ', to=[request.POST['email']])
                #email.send()
                
                subject, from_email, to = 'Confirma tu cuenta de Taxi Express', 'MyTaxiExpress@gmail.com', [request.POST['email']]
                html_content = 'Bienvenido a Taxi Express! <br> <br> Para comenzar a utilizar nuestros servicios deberás confirmar tu dirección de correo eletrónico haciendo click en el siguiente enlace: <br> <br> <a href="https://manage.stripe.com/confirm_email?t=z5roGRDbZdRbvknLfTZHCUSCyvPeznIw"> <br> <br> Un saludo de parte del equipo de Taxi Express.'
                msg = EmailMessage(subject, html_content, from_email, [to])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()  
                
                
                return HttpResponse(status=201,content="Creado")
            except ValidationError:
                HttpResponse(status=401, content="Email no válido")
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

def test(request):
    cu = Customer.objects.get(email='gorka_12@hotmail.com')
    lista = cu.favlist.all()
    return HttpResponse(status=201,content=lista)

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
    return HttpResponse(status=201,content="Cargado")
    

    def validateUser(request, email,validationCode):
    if request.method == "POST":
        if request.POST['email'] is None:
            return HttpResponse(status=401, content="Dirección incorrecta")
        try:
            customer = Customer.objects.get(email=request.POST['email'])  
        except ObjectDoesNotExist:
            return HttpResponse(status=401, content="No es posible validar a este usuario")
        if customer.validationCode == request.POST['validationCode']:
            customer.isValidated == true
            return HttpResponse(status=201,content="El usuario ha sido validado correctamente")
        else:
            return HttpResponse(status=401, content="No es posible validar a este usuario")


    def changePassword(request, email, newPassword):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=401, content="El email introducido no es valido")
    customer.password = newPassword
    return HttpResponse(status=201,content="La contraseña ha sido modificada correctamente")

    def updateProfile(request, email, firstName, lastName, newImage):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=401, content="El email introducido no es valido")
    customer.first_name = firstName
    customer.last_name = lastName
    customer.image = newImage
    return HttpResponse(status=201,content="Perfil del usuario modificado correctamente")
 


