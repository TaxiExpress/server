# -*- encoding: utf-8 -*-

# Create your views here.
from django import forms
from django.core.mail import EmailMessage
#from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car
from taxiexpress.serializers import CarSerializer, DriverSerializer, CustomerCompleteSerializer, CustomerTaxiesTravelsSerializer, CustomerTravelsSerializer, CustomerProfileSerializer, CustomerProfileTaxiesSerializer, CustomerProfileTravelsSerializer, CustomerTaxiesSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
from django.core.exceptions import ValidationError
#import json
import random
import string
from datetime import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from taxiexpress.views import validateUser


@csrf_exempt
@api_view(['POST'])
def loginUser(request):
    if request.POST['email'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")
    try:
        customer = Customer.objects.get(email=request.POST['email'])  
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")
    if customer.password == request.POST['password']:
        if customer.isValidated == False:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Debe validar la cuenta antes de conectarse")
        request.session['email'] = customer.email
        request.session['user_id'] = customer.id
        request.session['Customer'] = True
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")


@csrf_exempt
@api_view(['POST'])
def loginDriver(request):
    if request.POST['email'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")
    try:
        driver = Driver.objects.get(email=request.POST['email'])  
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")
    if driver.password == request.POST['password']:
        if driver.isValidated == False:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Debe validar la cuenta antes de conectarse")
        request.session['email'] = driver.email
        request.session['user_id'] = driver.id
        request.session['Customer'] = False
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")


@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password']
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email que ha indicado ya está en uso")
        if (Customer.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El teléfono que ha indicado ya está en uso")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            try:
                c = Customer(email=request.POST['email'], password=passtemp, phone=request.POST['phone'])
                code = random.randint(1000, 9999)
                c.validationCode = code
                c.save()
                msg = {
                        'reqtype': 'json',
                        'api_key': '8a352457',
                        'api_secret': '460e58ff',
                        'from': 'Taxi Express',
                        'to': c.phone,
                        'text': 'Su código de validación de Taxi Express es: ' + str(code)
                    }                
                sms = NexmoMessage(msg)
                sms.set_text_info(msg['text'])
                response = sms.send_request()                
                return HttpResponse(status=status.HTTP_201_CREATED)
            except ValidationError:
                HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email no válido")
    else:
        HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def registerDriver(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        if (Driver.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=401, content="El email que ha indicado ya está en uso")
        if (Driver.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=401, content="El teléfono que ha indicado ya está en uso")
        else:
            try:
                #Car data
                car = Car(plate=request.POST['plate'], model=request.POST['model'],capacity=request.POST['capacity'],
                    accessible=request.POST['accessible'], animals=request.POST['animals'],appPayment=request.POST['appPayment'])
                car.save()

                #Driver data
                d = Driver(email=request.POST['email'], password=request.POST['password'], phone=request.POST['phone'],
                    first_name=request.POST['first_name'], last_name=request.POST['last_name'], license =request.POST['license'],
                    car = car)

                if (request.POST['appPayment'] == '1'):
                    d.bankAccount = request.POST['bankAccount']
                    d.recipientName = request.POST['recipientName']

                code = random.randint(1, 9999)
                d.validationCode = code
                d.save()
                
                msg = {
                        'reqtype': 'json',
                        'api_key': '8a352457',
                        'api_secret': '460e58ff',
                        'from': 'Taxi Express',
                        'to': d.phone,
                        'text': 'Su código de validación de Taxi Express es: ' + str(code)
                    }                
                sms = NexmoMessage(msg)
                sms.set_text_info(msg['text'])
                response = sms.send_request()                
                return HttpResponse(status=status.HTTP_201_CREATED)
            except ValidationError:
                HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email no válido")
    else:
        HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def updateProfileUserWeb(request):
    if request.session.get('user_id', False):   
        try:
            customer = Customer.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este cliente")
        customer.first_name = request.POST['first_name']
        customer.last_name = request.POST['last_name']
        customer.image = request.POST['image']
        customer.postcode = request.POST['postcode']
        #Comentado hasta saber como actualizar
        #customer.city = int(request.POST['city'])
        customer.lastUpdate = datetime.now()
        customer.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Perfil del cliente modificado correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esta operación")


@csrf_exempt
@api_view(['POST'])
def updateProfileDriverWeb(request):
    if request.session.get('user_id', False):
        try:
            driver = Driver.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este taxista")
        driver.first_name = request.POST['first_name']
        driver.last_name = request.POST['last_name']
        driver.image = request.POST['image']
        driver.address = request.POST['address']
        driver.postcode = request.POST['postcode']
        #Comentado hasta saber como actualizar
        #driver.city = int(request.POST['city'])
        driver.license = request.POST['license']
        #Habría que comprobar si appPayment == True antes de asignar estos campos. Se va a permitir actualizar appPayment en esta misma vista?
        #driver.bankAccount = request.POST['bankAccount']
        #driver.recipientName = request.POST['recipientName']
        driver.lastUpdate = datetime.now()
        driver.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Perfil del taxista modificado correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esa operación")

@csrf_exempt
@api_view(['POST'])
def updateCarWeb(request):
    if request.session.get('user_id', False):
        try:
            driver = Driver.objects.get(id=request.session['user_id'])
            car = driver.car
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Vehiculo no encontrado")
        car.plate = request.POST['plate']
        car.model = request.POST['model']
        car.company = request.POST['company']
        car.color = request.POST['color']
        car.capacity = request.POST['capacity']
        car.accessible = request.POST['accessible']
        car.animals = request.POST['animals']
        car.appPayment = request.POST['appPayment']
        car.driver.lastUpdate = datetime.now()
        car.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Coche modificado correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esa operación")


@csrf_exempt
@api_view(['GET'])
def getCountries(request):
    countries = Country.objects.all()
    serialCountries = CountrySerializer(countries, many=True)
    return Response(serialCountries.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
def getStates(request):
    if request.GET['country'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un codigo de provincia")
    try:
        country = Country.objects.get(code=request.GET['country'])
        serialStates = StateSerializer(country.state_set, many=True)
        return Response(serialStates.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado esta provincia")

@csrf_exempt
@api_view(['GET'])
def getCities(request):
    if request.GET['state'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un codigo de ciudad")
    try:
        state = State.objects.get(code=request.GET['state'])
        serialCities = CitySerializer(state.city_set, many=True)
        return Response(serialStates.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado esta ciudad")

@csrf_exempt
def logout(request):
    if request.session['email'] is not None:
        del request.session['email']
        del request.session['user_id']
        del request.session['Customer']
        request.session.modified = True
    return redirect('/')


@csrf_exempt
def validateCode(request):
    if request.POST['tipo'] == 'C':
        response = validateUser(request)
        if response.status_code == 201:
            customer = Customer.objects.get(phone=request.POST['phone'])
            request.session['email'] = customer.email
            request.session['user_id'] = customer.id
            request.session['Customer'] = True
            return redirect('mantclient_data') 
    else:
        response = validateDriver(request)
        if response.status_code == 201:
            driver = Driver.objects.get(phone=request.POST['phone'])
            request.session['email'] = driver.email
            request.session['user_id'] = driver.id
            request.session['Customer'] = False
            return redirect('mantdriver_data')
    return render(request, 'AppWeb/index.html', {'statusValidation': response.status_code, 'errorValidation': response.content, 
            'phone':request.POST['phone'], 'validationCode':request.POST['validationCode'], 'tipo': request.POST['tipo']}) 


@api_view(['POST'])
def validateDriver(request):
    if request.POST['phone'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Teléfono incorrecto")
    try:
        driver = Driver.objects.get(phone=request.POST['phone'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")
    if driver.validationCode == int(request.POST['validationCode']):
        driver.isValidated = True
        driver.save()
        subject = '¡Bienvenido a Taxi Express!'
        from_email = 'MyTaxiExpress@gmail.com'
        to = [driver.email]
        html_content = '¡Bienvenido a Taxi Express! <br> <br> Ya puede disfrutar de la app más completa para gestionar sus viajes en taxi.'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        return HttpResponse(status=status.HTTP_201_CREATED,content="La cuenta ha sido validada correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")

@csrf_exempt
def index(request):
    if request.method == "POST":
        if request.POST['tipo'] == "C":
            response = loginUser(request)
            if response.status_code == 200:
                return redirect('mantclient_data') 
        else:
            response = loginDriver(request)
            if response.status_code == 200:
                return redirect('mantdriver_data')
        return render(request, 'AppWeb/index.html', {'status': response.status_code, 'error': response.content, 
            'email':request.POST['email'], 'password':request.POST['password'], 'tipo':request.POST['tipo']}) 
    else:
        if request.session.get('user_id', False):
            if request.session['Customer'] == True:
               return redirect('mantclient_data') 
            else:
                return redirect('mantdriver_data')  
        else:
            return render(request, 'AppWeb/index.html')   

@csrf_exempt
def register(request):
    if request.method == "POST":
        codigo = 0
        if request.POST["tipo"] == 'C':
            response = registerUser(request)
            if response.status_code == 201:
                c = Customer.objects.get(email=request.POST['email'])
                codigo = c.validationCode 
        else:
            response = registerDriver(request)
            if response.status_code == 201:
                d = Driver.objects.get(email=request.POST['email'])
                codigo = d.validationCode 
   
        return render(request, 'AppWeb/register.html', {'status': response.status_code, 'error': response.content, 'codigo': codigo, 'tipo':request.POST['tipo']})
    return render(request, 'AppWeb/register.html')

def map(request):
    return render(request, 'AppWeb/map.html', {})   

def client(request):
    return render(request, 'AppWeb/client.html', {}) 

def driver(request):
    return render(request, 'AppWeb/driver.html', {})  

def faq(request):
    return render(request, 'AppWeb/faq.html', {}) 

def legalnotice(request):
    return render(request, 'AppWeb/legalnotice.html', {})  

def mantclient_data(request):   
    if request.method == "POST":
        response = updateProfileUserWeb(request)
        customer = get_object_or_404(Customer, id=request.session['user_id'])
        return render(request, 'AppWeb/mantclient_data.html', {'client':customer, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == True:
                customer = get_object_or_404(Customer, id=request.session['user_id'])
                return render(request, 'AppWeb/mantclient_data.html', {'client':customer}) 
            else:
                request.session['email'] = ''
                request.session['user_id'] = ''
                request.session['Customer'] = ''
                return redirect('/')    
        else:
            return redirect('/')

def mantclient_preferences(request):
    if 'user_id' in request.session:
        if request.session['Customer'] == True:
            customer = get_object_or_404(Customer, id=request.session['user_id'])
            return render(request, 'AppWeb/mantclient_preferences.html', {'client':customer})
        else:
            request.session['email'] = ''
            request.session['user_id'] = ''
            request.session['Customer'] = ''
            return redirect('/')               
    else:
        return redirect('/')

def mantdriver_data(request):
    if request.method == "POST":
        response = updateProfileDriverWeb(request)
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        return render(request, 'AppWeb/mantdriver_data.html', {'driver':driver, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == False:
                driver = get_object_or_404(Driver, id=request.session['user_id'])
                return render(request, 'AppWeb/mantdriver_data.html', {'driver':driver}) 
            else:
                request.session['email'] = ''
                request.session['user_id'] = ''
                request.session['Customer'] = ''
                return redirect('/')            
        else:
            return redirect('/')

def mantdriver_car(request):
    if 'user_id' in request.session:
        if request.session['Customer'] == False:
            driver = get_object_or_404(Driver, id=request.session['user_id'])
            car = get_object_or_404(Car, plate=driver.car)
            return render(request, 'AppWeb/mantdriver_car.html', {'car': car, 'email': driver.email}) 
        else:
            request.session['email'] = ''
            request.session['user_id'] = ''
            request.session['Customer'] = ''
            return redirect('/') 
    else:
        return redirect('/')

def mantdriver_bankAccount(request):
    if 'user_id' in request.session:
        if request.session['Customer'] == False:
            driver = get_object_or_404(Driver, id=request.session['user_id'])
            return render(request, 'AppWeb/mantdriver_bankAccount.html', {'driver':driver})
        else:
            request.session['email'] = ''
            request.session['user_id'] = ''
            request.session['Customer'] = ''
            return redirect('/')     
    else:
        return redirect('/')    

def termsofuse(request):
    return render(request, 'AppWeb/termsofuse.html', {}) 
