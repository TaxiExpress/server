# -*- encoding: utf-8 -*-

# Create your views here.
from django import forms
from taxiexpress.nexmo import NexmoMessage
from django.core.mail import EmailMessage
#from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car, Observation
from taxiexpress.serializers import TravelSerializer, TravelSerializerDriver, CarSerializer, DriverSerializer, CustomerProfileSerializer, CountrySerializer, StateSerializer, CitySerializer,CustomerCountryStateCitySerializer,DriverCountryStateCitySerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
from django.core.exceptions import ValidationError
import json
import random
import string
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from taxiexpress.views import validateUser, changePassword, changePasswordDriver, recoverValidationCodeCustomer, recoverValidationCodeDriver,recoverPassword


@csrf_exempt
@api_view(['POST'])
def loginUser(request):
    if 'email' in request.POST:     
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
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")


@csrf_exempt
@api_view(['POST'])
def loginDriver(request):
    if 'email' in request.POST:
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
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")


@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password']
        tmpPhone = '+34' + request.POST['phone']
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email que ha indicado ya está en uso")
        if (Customer.objects.filter(phone=tmpPhone).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El teléfono que ha indicado ya está en uso")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            try:
                c = Customer(email=request.POST['email'], password=passtemp, phone=tmpPhone, image="")
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
                #response = sms.send_request()                
                return HttpResponse(status=status.HTTP_201_CREATED)
            except ValidationError:
                HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email no válido")
    else:
        HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def registerDriver(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        tmpPhone = '+34' + request.POST['phone']
        if (Driver.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email que ha indicado ya está en uso")
        if (Driver.objects.filter(phone=tmpPhone).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El teléfono que ha indicado ya está en uso")
        else:
            try:
                #Car data
                if (Car.objects.filter(plate=request.POST['plate']).count() > 0):
                    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="La matrícula que ha indicado ya está en uso")
                else:
                    
                    car = Car(plate=request.POST['plate'], model=request.POST['model'],capacity=request.POST['capacity'])
                    car.save()

                    #Driver data
                    
                    d = Driver(email=request.POST['email'], password=request.POST['password'], phone=tmpPhone,
                        first_name=request.POST['first_name'], last_name=request.POST['last_name'], license =request.POST['license'],
                        car = car)

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
                    #response = sms.send_request()                
                    return HttpResponse(status=201)
            except ValidationError:
                HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email no válido")
    else:
        HttpResponse(status=status.HTTP_401_UNAUTHORIZED)



@csrf_exempt
@api_view(['POST'])
def updateProfileUserWeb(request):
    if 'user_id' in request.session: 
        try:
            customer = Customer.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este cliente")
        customer.first_name = request.POST['first_name']
        customer.last_name = request.POST['last_name']
        customer.image = request.POST['image']
        customer.postcode = request.POST['postcode']
        if 'country' in request.POST and 'state' in request.POST and 'city' in request.POST:
            if request.POST['country'] != '0' and request.POST['state'] != '0' and request.POST['city'] != '0' : 
                state = State.objects.filter(country_id=request.POST['country'], id=request.POST['state'])
                city = City.objects.filter(state_id=state, id=request.POST['city'])
                tmpCity = City.objects.get(id=city)
            else:
                tmpCity= None
        else:
                tmpCity= None
        customer.city=tmpCity
        customer.lastUpdate = datetime.now()
        customer.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Perfil del cliente modificado correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esta operación")

@csrf_exempt
#@api_view(['POST'])
def updateFiltersWeb(request):
    if 'user_id' in request.session:
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este cliente")
        if 'accessible' in request.POST:
            customer.fAccessible = True
        else:
            customer.fAccessible = False
        if 'animals' in request.POST:
            customer.fAnimals = True
        else:
            customer.fAnimals = False
        if 'appPayment' in request.POST:
            customer.fAppPayment = True
        else:
            customer.fAppPayment = False

        customer.fCapacity = request.POST['capacity']
        customer.fDistance = request.POST['filters_distance']
        customer.lastUpdate = datetime.now()
        customer.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Filtros actualizados")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esa operación")    

@csrf_exempt
@api_view(['POST'])
def updateProfileDriverWeb(request):
    if 'user_id' in request.session:
        try:
            driver = Driver.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            return HttpResponse(status=401, content="No es posible encontrar a este taxista")
        driver.first_name = request.POST['first_name']
        driver.last_name = request.POST['last_name']
        driver.image = request.POST['image']
        driver.address = request.POST['address']
        driver.postcode = request.POST['postcode']
        if 'country' in request.POST and 'state' in request.POST and 'city' in request.POST:
            if request.POST['country'] != '0' and request.POST['state'] != '0' and request.POST['city'] != '0' : 
                state = State.objects.filter(country_id=request.POST['country'], id=request.POST['state'])
                city = City.objects.filter(state_id=state, id=request.POST['city'])
                tmpCity = City.objects.get(id=city)
            else:
                tmpCity= None
        else:
                tmpCity= None   
        driver.city=tmpCity
        driver.license = request.POST['license']
        driver.lastUpdate = datetime.now()
        driver.save()
        return HttpResponse(status=200,content="Perfil del taxista modificado correctamente")
    else:
        return HttpResponse(status=401, content="Debe estar conectado para realizar esa operación")
@csrf_exempt
#@api_view(['POST'])
def updateBankAccountWeb(request):
    if 'user_id' in request.session:
        try:
            driver = Driver.objects.get(id=request.session['user_id'])
            car = Car.objects.get(plate=driver.car)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este taxista")

        if 'appPayment' in request.POST:
            car.appPayment = True
            car.save()
            driver.bankAccount = request.POST['bankAccount']
            driver.recipientName = request.POST['recipientName']
            driver.lastUpdate = datetime.now()
            driver.car = car
            driver.save()
        else:
            car.appPayment = False
            car.save()
            driver.bankAccount = ""
            driver.recipientName = ""
            driver.lastUpdate = datetime.now()
            driver.car = car
            driver.save()
            
        return HttpResponse(status=status.HTTP_200_OK,content="Datos bancarios modificados correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esa operación") 

@csrf_exempt
#@api_view(['POST'])
def updateCarWeb(request):
    if 'user_id' in request.session:
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
        if 'accessible' in request.POST:
            car.accessible = True
        else:
            car.accessible = False
        if 'animals' in request.POST:
            car.animals = True
        else:
            car.animals = False
        if 'appPayment' in request.POST:
            car.appPayment = True
        else:
            car.appPayment = False
        car.lastUpdate = datetime.now()
        car.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Vehículo modificado correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe estar conectado para realizar esa operación")

@csrf_exempt
@api_view(['GET'])
def getCountries(request):
    countries = Country.objects.all().order_by('name')
    serialCountries = CountrySerializer(countries, many=True)
    return Response(serialCountries.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
def getStates(request):
    if 'country' in request.GET:  
        try:
            country = Country.objects.get(code=request.GET['country'])
            serialStates = StateSerializer(country.state_set.all().order_by('name'), many=True)
            return Response(serialStates.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado el país")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe introducir un codigo de país")

@csrf_exempt
@api_view(['GET'])
def getCities(request):
    if 'state' in request.GET:
        try:
            state = State.objects.get(id=request.GET['state'])
            serialCities = CitySerializer(state.city_set.all().order_by('name'), many=True)
            return Response(serialCities.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado la provincia")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe introducir un codigo de provincia")

@csrf_exempt
def logout(request):
    if 'user_id' in request.session:
        del request.session['email']
        del request.session['user_id']
        del request.session['Customer']
        request.session.modified = True
    return redirect('/')


@csrf_exempt
def validateCode(request):
    if request.is_ajax():
        try:
            if request.POST['tipo'] == 'C':
                response = validateUser(request)
                if response.status_code == 201:
                    customer = Customer.objects.get(phone=request.POST['phone'])
                    request.session['email'] = customer.email
                    request.session['user_id'] = customer.id
                    request.session['Customer'] = True
                    return HttpResponse(response.status_code) 
            else:
                response = validateDriver(request)
                if response.status_code == 201:
                    driver = Driver.objects.get(phone=request.POST['phone'])
                    request.session['email'] = driver.email
                    request.session['user_id'] = driver.id
                    request.session['Customer'] = False
                    return HttpResponse(response.status_code)
            return HttpResponse(response.content) 
        except KeyError:
            return HttpResponse('Error')  
    else:
        return redirect('/')

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
        return render(request, 'AppWeb/index.html', {'status': response.status_code, 'error': response.content}) 
    else:
        if 'user_id' in request.session:
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
   
        return render(request, 'AppWeb/register.html', {'status': response.status_code, 'error': response.content, 'codigo': codigo})
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
       
        customer = Customer.objects.get(id=request.session['user_id'])
        serialCustomer=CustomerCountryStateCitySerializer(customer)

        if customer.city is not None:
            city = customer.city.id
            state = customer.city.state.id
            country = customer.city.state.country.code
        else:
            city = 0
            state = 0
            country = 0
        return render(request, 'AppWeb/mantclient_data.html', {'client':serialCustomer.data, 'error':response.content, 'country': country, 'state': state, 'city': city})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == True:
                customer = Customer.objects.get(id=request.session['user_id'])
                serialCustomer=CustomerCountryStateCitySerializer(customer)
                if customer.city is not None:
                    city = customer.city.id
                    state = customer.city.state.id
                    country = customer.city.state.country.code
                else:
                    city = 0
                    state = 0
                    country = 0
                return render(request, 'AppWeb/mantclient_data.html', {'client':serialCustomer.data, 'country': country, 'state': state, 'city': city}) 
            else:
                logout(request)    
        else:
            return redirect('/')

def mantclient_changePassword(request):   
    if request.method == "POST":
        response = changePassword(request)
        customer = get_object_or_404(Customer, id=request.session['user_id'])
        return render(request, 'AppWeb/mantclient_changePassword.html', {'client':customer, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == True:
                customer = get_object_or_404(Customer, id=request.session['user_id'])
                return render(request, 'AppWeb/mantclient_changePassword.html', {'client':customer}) 
            else:
                logout(request)    
        else:
            return redirect('/')

def mantclient_preferences(request):
    if request.method == "POST":
        response = updateFiltersWeb(request)
        customer = get_object_or_404(Customer, id=request.session['user_id'])
        return render(request, 'AppWeb/mantclient_preferences.html', {'client':customer, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == True:
                customer = get_object_or_404(Customer, id=request.session['user_id'])
                return render(request, 'AppWeb/mantclient_preferences.html', {'client':customer})
            else:
                logout(request)               
        else:
            return redirect('/')

def mantclient_travels(request):   
    if 'user_id' in request.session:
        if request.session['Customer'] == True:
            customer = get_object_or_404(Customer, id=request.session['user_id'])
            return render(request, 'AppWeb/mantclient_travels.html', {'client':customer}) 
        else:
            logout(request)    
    else:
        return redirect('/')

def mantdriver_data(request):
    if request.method == "POST":
        response = updateProfileDriverWeb(request)
       
        driver = Driver.objects.get(id=request.session['user_id'])
        serialDriver=DriverCountryStateCitySerializer(driver)

        if driver.city is not None:
            city = driver.city.id
            state = driver.city.state.id
            country = driver.city.state.country.code
        else:
            city = 0
            state = 0
            country = 0
        return render(request, 'AppWeb/mantdriver_data.html', {'driver':serialDriver.data, 'error':response.content, 'country': country, 'state': state, 'city': city})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == False:
                driver = Driver.objects.get(id=request.session['user_id'])
                serialDriver=DriverCountryStateCitySerializer(driver)
                if driver.city is not None:
                    city = driver.city.id
                    state = driver.city.state.id
                    country = driver.city.state.country.code
                else:
                    city = 0
                    state = 0
                    country = 0
                return render(request, 'AppWeb/mantdriver_data.html', {'driver':serialDriver.data, 'country': country, 'state': state, 'city': city}) 
            else:
                logout(request)            
        else:
            return redirect('/')

def mantdriver_changePassword(request):
    if request.method == "POST":
        response = changePasswordDriver(request)
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        return render(request, 'AppWeb/mantdriver_changePassword.html', {'driver':driver, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == False:
                driver = get_object_or_404(Driver, id=request.session['user_id'])
                return render(request, 'AppWeb/mantdriver_changePassword.html', {'driver':driver}) 
            else:
                logout(request)            
        else:
            return redirect('/')

def mantdriver_car(request):
    if request.method == "POST":
        response = updateCarWeb(request)
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        car = get_object_or_404(Car, plate=driver.car)
        return render(request, 'AppWeb/mantdriver_car.html', {'car': car, 'driver': driver, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == False:
                driver = get_object_or_404(Driver, id=request.session['user_id'])
                car = get_object_or_404(Car, plate=driver.car)
                return render(request, 'AppWeb/mantdriver_car.html', {'car': car, 'driver': driver}) 
            else:
                logout(request) 
        else:
            return redirect('/')

def mantdriver_bankAccount(request):
    if request.method == "POST":
        response = updateBankAccountWeb(request)
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        car = get_object_or_404(Car, plate=driver.car)
        return render(request, 'AppWeb/mantdriver_bankAccount.html', {'car': car, 'driver': driver, 'error':response.content})
    else:
        if 'user_id' in request.session:
            if request.session['Customer'] == False:
                driver = get_object_or_404(Driver, id=request.session['user_id'])
                car = get_object_or_404(Car, plate=driver.car)
                return render(request, 'AppWeb/mantdriver_bankAccount.html', {'car': car, 'driver':driver})
            else:
                logout(request)     
        else:
            return redirect('/')    

def mantdriver_TravelGraphic(request):
    if 'user_id' in request.session:
        if request.session['Customer'] == False:
            driver = get_object_or_404(Driver, id=request.session['user_id'])
            return render(request, 'AppWeb/mantdriver_TravelGraphic.html', {'driver':driver})
        else:
            logout(request)    
    else:
        return redirect('/')  

def mantdriver_travels(request):   
    if 'user_id' in request.session:
        if request.session['Customer'] == False:
            driver = get_object_or_404(Driver, id=request.session['user_id'])
            return render(request, 'AppWeb/mantdriver_travels.html', {'driver':driver}) 
        else:
            logout(request)    
    else:
        return redirect('/') 

def getTravelsByMonth(request):
    if 'user_id' in request.session:
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        travels = driver.travel_set.filter(isPaid=True)
        total = travels.count()
        response_data = {}
        for i in range(1,13):
            response_data[i] = (travels.filter(starttime__month=i).count()*100)/total
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return redirect('/')

def getTravelsByLastYear(request):
    if 'user_id' in request.session:
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        #travels = driver.travel_set.filter(starttime=datetime.now()-timedelta(days=365))
        today = datetime.now()
        lastYear = datetime.now()-relativedelta(years=1)
        travels = driver.travel_set.filter(isPaid=True, starttime__range=[lastYear, today])
        #travels = driver.travel_set.filter(starttime__year__gte=datetime.now().year,starttime__year__lte=datetime.now().year-1)
        response_data = {}
        for i in range(1,13):
            response_data[i] = travels.filter(starttime__month=i).count()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return redirect('/')

def getTravelsByLastMonth(request):
    if 'user_id' in request.session:
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        #travels = driver.travel_set.filter(starttime=datetime.now()-timedelta(days=365))
        today = datetime.now()
        lastYear = datetime.now()-relativedelta(months=1)
        travels = driver.travel_set.filter(isPaid=True, starttime__range=[lastYear, today])
        #travels = driver.travel_set.filter(starttime__year__gte=datetime.now().year,starttime__year__lte=datetime.now().year-1)
        response_data = {}
        for i in range(1,32):
            response_data[i] = travels.filter(starttime__day=i).count()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return redirect('/')

def getTravelsByDay(request):
    if 'user_id' in request.session:
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        travels = driver.travel_set.filter(isPaid=True)
        total = travels.count()
        response_data = {}
        response_data[0] = (travels.filter(starttime__week_day=2).count()*100)/total
        response_data[1] = (travels.filter(starttime__week_day=3).count()*100)/total
        response_data[2] = (travels.filter(starttime__week_day=4).count()*100)/total
        response_data[3] = (travels.filter(starttime__week_day=5).count()*100)/total
        response_data[4] = (travels.filter(starttime__week_day=6).count()*100)/total
        response_data[5] = (travels.filter(starttime__week_day=7).count()*100)/total
        response_data[6] = (travels.filter(starttime__week_day=1).count()*100)/total
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return redirect('/')

def termsofuse(request):
    return render(request, 'AppWeb/termsofuse.html', {}) 

def recoverValidationCodeWeb(request):
    if request.is_ajax():
        try:
            if request.POST["tipo"] == 'C':
                response = recoverValidationCodeCustomer(request)  
            else:
                response = recoverValidationCodeDriver(request)
            
            if response.status_code == 201:
                msg = 'Se ha enviado un SMS con el código de validación a su teléfono'
            else:
                msg = response.content 
       
            return HttpResponse(msg)
        except KeyError:
            return HttpResponse('Error')  
    else:
        return redirect('/')  

def contact(request):   
    if request.method == "POST":
        if 'phone' in request.POST:
            tmpPhone = '+34' + request.POST['phone']
        else:
            tmpPhone = ""
        o = Observation(name = request.POST['name'], phone = tmpPhone, email = request.POST['email'], 
            tipo = request.POST['tipo'], observations = request.POST['observations'])
        
        o.save()    
 
        subject = 'Recibidida Petición'
        from_email = 'MyTaxiExpress@gmail.com'
        to = [o.email]
        html_content =  '¡Muchas gracias ' + str(o.name) + ' por ponerse en contacto con nosotros! <br> <br> Su petición ha sido correctamente registrada y será estudiada por nuestro equipo.'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        return redirect('/')

    else:
        return render(request, 'AppWeb/contact.html', {})  

def rememberPassword(request):   
    if 'tipo' in request.GET:
        if request.GET['tipo'] == "C":
            response = recoverPassword(request)
            if response.status_code == 201:
                return redirect('/') 
        else:
            response = recoverPasswordDriver(request)
            if response.status_code == 201:
                return redirect('/')
        return render(request, 'AppWeb/rememberpassword.html', {'status': response.status_code, 'error': response.content}) 
    else:
        return render(request, 'AppWeb/rememberpassword.html', {})  

def recoverPasswordDriver(request):
    if request.GET['email'] == '':
        return HttpResponse(status=401, content="Debe ingresar una dirección de email")
    try:
        driver = Driver.objects.get(email=request.GET['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=401, content="No es posible encontrar a este usuario")
    subject = 'Taxi Express: Recuperar contraseña'
    from_email = 'MyTaxiExpress@gmail.com'
    to = [driver.email]
    html_content = 'Su password es ' + driver.password + '. <br> <br> Un saludo de parte del equipo de Taxi Express.'
    msg = EmailMessage(subject, html_content, from_email, to)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return HttpResponse(status=201,content="Se ha enviado la contraseña a su cuenta de email.")

@csrf_exempt
@api_view(['GET'])
def getTravelsCustomer(request):
    if 'user_id' in request.session:
        customer = get_object_or_404(Customer, id=request.session['user_id'])
        SerialTravel = TravelSerializer(customer.travel_set.filter(isPaid=True), many=True)
        return Response(SerialTravel.data, status=status.HTTP_200_OK)
    else:
        return redirect('/')

@csrf_exempt
@api_view(['GET'])
def getTravelsDriver(request):
    if 'user_id' in request.session:
        driver = get_object_or_404(Driver, id=request.session['user_id'])
        SerialTravel = TravelSerializerDriver(driver.travel_set.filter(isPaid=True), many=True)
        return Response(SerialTravel.data, status=status.HTTP_200_OK)
    else:
        return redirect('/')
