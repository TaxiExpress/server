# -*- encoding: utf-8 -*-

from django import forms
from nexmo import NexmoMessage
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
#from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car
from taxiexpress.serializers import CustomerSerializer, DriverSerializer, CustomerTaxiesTravelsSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
#from django.core import serializers
#from django.core.validators import validate_email
from django.core.exceptions import ValidationError
#import json
import random
import string
import pytz
from datetime import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


# Create your views here.
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
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe validar la cuenta antes de conectarse")
        request.session['email'] = customer.email
        request.session['user_id'] = customer.id
        request.session['Customer'] = True
        datetime_request = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
        utc=pytz.UTC
        now_aware = utc.localize(datetime_request)
        if customer.lastUpdate > now_aware:
            serialCustomer = CustomerSerializer(customer)
            return Response(serialCustomer.data, status=status.HTTP_200_OK)
        else:
            serialCustomer = CustomerTaxiesTravelsSerializer(customer)
            return Response(serialCustomer.data, status=status.HTTP_200_OK)
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
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe validar la cuenta antes de conectarse")
        request.session['email'] = driver.email
        request.session['user_id'] = driver.id
        return Response(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")

@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = request.POST['password'];
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email que ha indicado ya está en uso")
        if (Customer.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El teléfono que ha indicado ya está en uso")
        #elif (passtemp.length() < 4)
        #   return HttpResponse("shortpassword", content_type="text/plain")
        else:
            try:
                c = Customer(email=request.POST['email'], password=passtemp, phone=request.POST['phone'], lastUpdate=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'))
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
@api_view(['GET'])
def getClosestTaxi(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))
        try:
            customer = Customer.objects.get(email=request.GET['email'])
            closestDriver = Driver.objects.distance(pointclient).filter(car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[0]
            serialDriver = DriverSerializer(closestDriver)
            return Response(serialDriver.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        except IndexError:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content="No se han encontrado taxis")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")

@csrf_exempt
@api_view(['GET'])
def getNearestTaxies(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))
        try:
            customer = Customer.objects.get(email=request.GET['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")

        closestDrivers = Driver.objects.distance(pointclient).filter(car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:10]
        serialDriver = DriverSerializer(closestDrivers, many=True)
        return Response(serialDriver.data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")


@csrf_exempt
@api_view(['GET'])
def test(request):
    cu = Customer.objects.get(email='gorka_12@hotmail.com')
    lista = cu.favlist.all()
    return HttpResponse(status=status.HTTP_200_OK,content=lista)


@csrf_exempt
@api_view(['POST'])
def recoverValidationCode(request):
    if request.POST['phone'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un numero de telefono")
    try:
        c = Customer.objects.get(phone=request.POST['phone']) 
        msg = {
                'reqtype': 'json',
                'api_key': '8a352457',
                'api_secret': '460e58ff',
                'from': 'Taxi Express',
                'to': c.phone,
                'text': 'Su código de validación de Taxi Express es: ' + str( c.validationCode)
                }                
        sms = NexmoMessage(msg)
        sms.set_text_info(msg['text'])
        response = sms.send_request()                
        return HttpResponse(status=status.HTTP_201_CREATED)
    except ValidationError:
         return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Telefono incorrecto")


@api_view(['POST'])
def validateUser(request):
    if request.POST['phone'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Teléfono incorrecto")
    try:
        customer = Customer.objects.get(phone=request.POST['phone'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")
    if customer.validationCode == int(request.POST['validationCode']):
        customer.isValidated = True
        customer.save()
        subject = '¡Bienvenido a Taxi Express!'
        from_email = 'MyTaxiExpress@gmail.com'
        to = [customer.email]
        html_content = '¡Bienvenido a Taxi Express! <br> <br> Ya puede disfrutar de la app más completa para gestionar sus viajes en taxi.'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        return HttpResponse(status=status.HTTP_201_CREATED,content="La cuenta ha sido validada correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")


@csrf_exempt
@api_view(['POST'])
def changePassword(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    if customer.password == request.POST['oldPass']:
        customer.password = request.POST['newPass']  
        customer.save()
        subject = 'Taxi Express: Su contraseña ha sido modificada'
        from_email = 'MyTaxiExpress@gmail.com'
        to = [customer.email]
        html_content = 'Le informamos de que su contraseña de Taxi Express ha sido modificada. En el caso en el que no tenga constancia de ello, póngase inmediantamente en contacto con MyTaxiExpress@gmail.com.'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()  
        return HttpResponse(status=status.HTTP_200_OK,content="La contraseña ha sido modificada correctamente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="La contraseña actual es incorrecta")

#¿Estamos usando este metodo?
@csrf_exempt
@api_view(['POST'])
def updateProfileMobile(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    customer.first_name = request.POST['firstName']
    customer.last_name = request.POST['lastName']
    customer.image = request.POST['newImage']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del usuario modificado correctamente")


@csrf_exempt
@api_view(['POST'])
def updateProfileUser(request):
    if request.POST['id'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un id cliente")
    try:
        customer = Customer.objects.get(id=request.POST['id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este cliente")
    customer.first_name = request.POST['first_name']
    customer.last_name = request.POST['last_name']
    customer.postcode = request.POST['postcode']
    customer.city = request.POST['city']
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del cliente modificado correctamente")


@csrf_exempt
@api_view(['POST'])
def updateProfileDriver(request):
    if request.POST['id'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un id taxista")
    try:
        driver = Driver.objects.get(id=request.POST['id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este taxista")
    driver.first_name = request.POST['first_name']
    driver.last_name = request.POST['last_name']
    driver.address = request.POST['address']
    driver.postcode = request.POST['postcode']
    driver.city = request.POST['city']
    driver.license = request.POST['license']
    driver.bankAccount = request.POST['bankAccount']
    driver.recipientName = request.POST['recipientName']
    driver.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del taxista modificado correctamente")


@csrf_exempt
@api_view(['POST'])
def updateCar(request):
    if request.POST['plate'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una matricula")
    try:
        car = Car.objects.get(plate=request.GET['plate'])
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
    car.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Coche modificado correctamente")


@csrf_exempt
@api_view(['GET'])
def recoverCountries(request):
    countries = Country.objects.all()
    return HttpResponse(status=status.HTTP_200_OK,content=countries)    


@csrf_exempt
@api_view(['GET'])
def recoverStates(request):
    if request.GET['country'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un codigo de pais")
    try:
        states = State.objects.get(country=request.GET['country'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado este pais")
    return HttpResponse(status=status.HTTP_200_OK,content=states)

@csrf_exempt
@api_view(['GET'])
def recoverCities(request):
    if request.GET['state'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un codigo de provincia")
    try:
        cities = City.objects.get(state=request.GET['state'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No se ha encontrado esta provincia")
    return HttpResponse(status=status.HTTP_200_OK,content=cities)

@csrf_exempt
@api_view(['GET'])
def recoverPassword(request):
    if request.GET['email'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")
    try:
        customer = Customer.objects.get(email=request.GET['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este usuario")
    subject = 'Taxi Express: Recuperar contraseña'
    from_email = 'MyTaxiExpress@gmail.com'
    to = [customer.email]
    html_content = 'Su password es ' + customer.password + '. <br> <br> Un saludo de parte del equipo de Taxi Express.'
    msg = EmailMessage(subject, html_content, from_email, to)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Se ha enviado la contraseña a su cuenta de email.")

@csrf_exempt
@api_view(['GET'])
def recoverEmail(request):
    if request.GET['phone'] is None:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un número de teléfono")
    try:
        customer = Customer.objects.get(phone=request.GET['phone'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este usuario")
    try:
        emailCus = customer.email
        return HttpResponse(status=status.HTTP_200_OK,content=emailCus)
    except Exception:
        return HttpResponser(status=HTTP_400_BAD_REQUEST, content="Error al devolver el email")    
    
    
@csrf_exempt
@api_view(['POST'])
def addFavoriteDriver(request):
    try:
        customer = Customer.objects.get(email=request.POST['customerEmail'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    try:
        driver = Driver.objects.get(email=request.POST['driverEmail'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista introducido no es válido")
    customer.favlist.add(driver)
    customer.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Taxista añadido a la lista de favoritos")


@csrf_exempt
@api_view(['POST'])
def removeFavoriteDriver(request):
        try:
            customer = Customer.objects.get(email=request.POST['customerEmail'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
        try:
            driver = customer.favlist.get(email=request.POST['driverEmail'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista no se encuentra en su lista de favoritos")
        customer.favlist.remove(driver)
        customer.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Taxista eliminado de la lista de favoritos")


@csrf_exempt
@api_view(['POST'])
def removeTravel(request):
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
        try:
            travel = Travel.objects.get(id=request.POST['travel_id'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El trayecto no se encuentra en su lista de trayectos realizados")
        travel.delete()
        return HttpResponse(status=status.HTTP_200_OK ,content="Trayecto eliminado de la lista")


@csrf_exempt
@api_view(['POST'])
def updateFilters(request):
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
        customer.fAccessible = (request.POST['accesible'] == 'true')
        customer.fAnimals = (request.POST['animals'] == 'true')
        customer.fAppPayment = (request.POST['appPayment'] == 'true')
        customer.fCapacity = request.POST['capacity']
        customer.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Filtros actualizados")


@csrf_exempt
@api_view(['GET'])
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
    car = Car(plate='1111AAA', model='Laguna', company='Renault', color='White', capacity=4, accessible=True, animals=False, isfree=True, appPayment=True)
    car.save()
    dr = Driver(email="conductor@gmail.com", password="11111111", phone="656111112", first_name="Conductor", last_name="DePrimera", city=ci, positiveVotes=10, negativeVotes=3, car=car)
    dr.save()
    car = Car(plate='2222BBB', model='Cooper', company='Mini', color='White', capacity=3, accessible=False, animals=False, isfree=True, appPayment=False)
    car.save()
    dr2 = Driver(email="conductor2@gmail.com", password="11111111", phone="656111113", first_name="Conductor", last_name="DeSegunda", city=ci, positiveVotes=2, negativeVotes=7, car=car)
    dr2.save()
    cu = Customer(email="gorka_12@hotmail.com", password="11111111", phone="656111111", first_name="Pepito", last_name="Palotes", city=ci, lastUpdate=datetime.strptime('1980-01-01 00:00:01','%Y-%m-%d %H:%M:%S'))
    cu.save()
    cu.favlist.add(dr)
    cu.favlist.add(dr2)
    tr = Travel(customer=cu, driver=dr, starttime=datetime.strptime('2013-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, startpoint=Point(43.15457, -2.56488), origin='Calle Autonomía 35', endpoint=Point(43.16218, -2.56352), destination='Av de las Universidades 24')
    tr.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Cargado")


