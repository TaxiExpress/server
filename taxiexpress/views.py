# -*- encoding: utf-8 -*-

from django import forms
from nexmo import NexmoMessage
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
#from django.forms import CharField,Form,PasswordInput
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car
from taxiexpress.serializers import CarSerializer, DriverSerializer, CustomerCompleteSerializer, CustomerTaxiesTravelsSerializer, CustomerTravelsSerializer, CustomerProfileSerializer, CustomerProfileTaxiesSerializer, CustomerProfileTravelsSerializer, CustomerTaxiesSerializer, DriverDataSerializer, TravelSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D
#from django.core import serializers
#from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import random
import string
import requests
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

def sessionID_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

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
        customer.sessionID = sessionID_generator()
        customer.save()
        datetime_profile = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
        datetime_taxies = datetime.strptime(request.POST['lastUpdateFavorites'], '%Y-%m-%d %H:%M:%S')
        datetime_travels = datetime.strptime(request.POST['lastUpdateTravels'], '%Y-%m-%d %H:%M:%S')
        upProfile = False
        upTaxies = False
        upTravels = False
        #primero comprobamos si necesitamos actualizar
        if customer.lastUpdate != datetime_profile:
            upProfile = True
        if customer.lastUpdateFavorites !=  datetime_taxies:
            upTaxies = True
        if customer.lastUpdateTravels !=  datetime_travels:
            upTravels = True
        #ahora comprobamos todos los casos posibles
        if upProfile:
            if upTaxies and upTravels:
                serialCustomer = CustomerCompleteSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            elif upTaxies and not upTravels:
                serialCustomer = CustomerProfileTaxiesSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            elif not upTaxies and upTravels:
                serialCustomer = CustomerProfileTravelsSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            else: # upTaxies y upTravels son False
                serialCustomer = CustomerProfileSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
        else: #upProfile es False
            if upTaxies and upTravels:
                serialCustomer = CustomerTaxiesTravelsSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            elif upTaxies and not upTravels:
                serialCustomer = CustomerTaxiesSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            elif not upTaxies and upTravels:
                serialCustomer = CustomerTravelsSerializer(customer)
                return Response(serialCustomer.data, status=status.HTTP_200_OK)
            else: # upTaxies y upTravels son False
                response_data = {}
                response_data['sessionID'] = customer.sessionID
                return HttpResponse(json.dumps(response_data), content_type="application/json")
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
        request.session['Customer'] = False
        driverNameSurname = DriverDataSerializer(driver)
        return Response(driverNameSurname.data, status=status.HTTP_200_OK)
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
                c = Customer(email=request.POST['email'], password=passtemp, phone=request.POST['phone'], lastUpdate=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'),lastUpdateFavorites=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'),lastUpdateTravels=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'), image="")
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
@api_view(['GET'])
def getClosestTaxi(request):
    if request.GET.get('latitud', "false") != "false":
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))
        try:
            customer = Customer.objects.get(email=request.GET['email'])
            if customer.sessionID != request.GET['sessionID']:
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
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
def getClosestTaxiBeta(request):
    if 'latitude' in request.GET:
        pointclient = Point(float(request.GET['latitude']), float(request.GET['longitude']))
        origin = request.GET['origin']
        try:
            customer = Customer.objects.get(email=request.GET['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.GET['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        closestDrivers = Driver.objects.distance(pointclient).filter(car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:5]
        if closestDrivers.count() == 0:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content="No se han encontrado taxis")
        elif closestDrivers.count() > 5:
            closestDrivers = closestDrivers[:5]
        travel = Travel(customer=customer, startpoint=pointclient, origin=request.GET['origin'])
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes))
        post_data = {"origin": origin, "startpoint": pointclient, "travelID": travel.id, "valuation": valuation, "phone": customer.phone, "device": "android"} 
        for i in range(closestDrivers.count()):
            post_data["pushId"+str(i)] = closestDrivers[i].pushID
        try:
            resp = requests.post('http://localhost:8080/sendClosestTaxi', params=post_data)
        except requests.ConnectionError:
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        travel.save()
        response_data = {}
        response_data['travelID'] = travel.id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")


@csrf_exempt
@api_view(['POST'])
def acceptTravel(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        try:
            travel = Travel.objects.get(travel=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no está disponible")
        if travel.accepted:
            return HttpResponse(status=status.HTTP_409_CONFLICT, content="El viaje no está disponible")
        travel.driver = driver
        travel.accepted = True
        travel.save()
        driverpos = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        driver.car.isfree = False
        driver.geom = driverpos
        driver.save()
        post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "latitude": str(driverpos.x), "longitude": str(driverpos.y), "device": "android"} 
        resp = requests.post('http://localhost:8080/send', params=post_data)
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

@csrf_exempt
@api_view(['POST'])
def travelStarted(request):
    if 'travelID' in request.POST: 
        try:
            travel = Travel.objects.get(id=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.driver.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        travel.origin = request.POST['origin']
        travel.startpoint = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        travel.starttime = datetime.now()
        travel.save()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

@csrf_exempt
@api_view(['POST'])
def travelCompleted(request):
    if 'travelID' in request.POST: 
        try:
            travel = Travel.objects.get(id=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.driver.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        travel.destination = request.POST['destination']
        travel.endpoint = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        travel.endtime = datetime.now()
        travel.appPayment = (request.POST['appPayment'] == "true")
        travel.driver.car.isfree = True
        if not travel.appPayment:
            travel.isPaid = True
        travel.save()
        if travel.appPayment:
            post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "true","device": "android"} 
            resp = requests.post('http://localhost:8080/send', params=post_data)
        else:
            travel.isPaid = True
            travel.save()
            try:
                post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "false","device": "android"} 
                resp = requests.post('http://localhost:8080/send', params=post_data)
            except requests.ConnectionError:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

@csrf_exempt
@api_view(['POST'])
def travelPaid(request):
    if 'travelID' in request.POST:
        try:
            travel = Travel.objects.get(id=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.customer.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        if request.POST['sessionID'] != travel.customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        travel.isPaid = True
        travel.save()
        post_data = {"travelID": travel.id, "pushId": travel.driver.pushID, "paid": "true", "device": "android"}
        resp = requests.post('http://localhost:8080/send', params=post_data)
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

@csrf_exempt
@api_view(['POST'])
def cancelTravel(request):
    if 'travelID' in request.POST:
        try:
            travel = Travel.objects.get(id=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.customer.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        if request.POST['sessionID'] != travel.customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        travel.delete()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


@csrf_exempt
@api_view(['GET'])
def getLastTravel(request):
    if 'email' in request.GET:
        try:
            customer = Customer.objects.get(email=request.GET['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        travel = customer.travel_set.order_by('starttime')[0]
        return Response(TravelSerializer(travel).data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Email no válido")

@csrf_exempt
@api_view(['GET'])
def testPush(request):
    try:
        userdata = {"pushId": "APA91bHJRkpSjXvlFA7L94ybyalAeW0BxE0Z1K4g99onHvXLIFgptSJDhBIMXckY9HBzaBpEWo4Se9zUCd2KjzWUHCJ5TLac-qF-Hu8ozi7Uoe14ZFRg2_c82xmL4ZXgMfuhec4UUd-eu_SkYsMPRt2bqNZ0K5Uzgpwd2en9454w8-f3c7pyEK0", "title": "Pues que bien", "device": "android", "reqMessage": "world"}
        resp = requests.post('http://localhost:8080/send', params=userdata)
    except requests.ConnectionError:
        return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)
    print resp.status_code
    return HttpResponse(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def getNearestTaxies(request):
    if 'latitud' in request.GET:
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud']))
        try:
            customer = Customer.objects.get(email=request.GET['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.GET['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
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




#¿Estamos usando este metodo?
@csrf_exempt
@api_view(['POST'])
def updateProfile(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    customer.first_name = request.POST['firstName']
    customer.last_name = request.POST['lastName']
    customer.image = request.POST['newImage']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del usuario modificado correctamente")


@csrf_exempt
@api_view(['POST'])
def updateDriverPosition(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if 'latitude' in request.POST:
            pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude']))
            driver.geom = pointclient
            driver.save()
            return HttpResponse(status=status.HTTP_200_OK,content="Posicion del taxista actualizada")
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="punto inexistente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="email inexistente")


@csrf_exempt
@api_view(['POST'])
def updateDriverAvailable(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        driver.available = (request.POST['available'] == 'true')
        driver.save()
        return HttpResponse(status=status.HTTP_200_OK,content="Disponibilidad del taxista actualizada")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email inexistente")


@csrf_exempt
@api_view(['POST'])
def updateFilters(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    customer.fAccessible = (request.POST['accesible'] == 'true')
    customer.fAnimals = (request.POST['animals'] == 'true')
    customer.fAppPayment = (request.POST['appPayment'] == 'true')
    customer.fCapacity = request.POST['capacity']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Filtros actualizados")

    


@api_view(['POST'])
def validateUser(request):
    if 'phone' in request.POST:
        try:
            customer = Customer.objects.get(phone=request.POST['phone'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")
        if customer.isValidated == False:
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
        else:        
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Esta cuenta ya está validada.")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Teléfono incorrecto")
        

@csrf_exempt
@api_view(['POST'])
def changePassword(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
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


@csrf_exempt
@api_view(['POST'])
def changePasswordDriver(request):
    try:
        driver = Driver.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=401, content="El email introducido no es válido")
    if driver.password == request.POST['oldPass']:
        driver.password = request.POST['newPass']  
        driver.save()
        subject = 'Taxi Express: Su contraseña ha sido modificada'
        from_email = 'MyTaxiExpress@gmail.com'
        to = [driver.email]
        html_content = 'Le informamos de que su contraseña de Taxi Express ha sido modificada. En el caso en el que no tenga constancia de ello, póngase inmediantamente en contacto con MyTaxiExpress@gmail.com.'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()  
        return HttpResponse(status=200,content="La contraseña ha sido modificada correctamente")
    else:
        return HttpResponse(status=401, content="La contraseña actual es incorrecta")

@csrf_exempt
@api_view(['GET'])
def recoverPassword(request):
    if request.GET['email'] == '':
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
    if 'phone' in request.GET:   
        try:
            customer = Customer.objects.get(phone=request.GET['phone'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este usuario")
        try:
            emailCus = customer.email
            return HttpResponse(status=status.HTTP_200_OK,content=emailCus)
        except Exception:
            return HttpResponse(status=HTTP_400_BAD_REQUEST, content="Error al devolver el email")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un número de teléfono") 
        

@csrf_exempt
@api_view(['POST'])
def recoverValidationCodeCustomer(request):
    if 'phone' in request.POST:
        try:
            customer = Customer.objects.get(phone=request.POST['phone']) 
            if customer.isValidated == False:
                msg = {
                        'reqtype': 'json',
                        'api_key': '8a352457',
                        'api_secret': '460e58ff',
                        'from': 'Taxi Express',
                        'to': customer.phone,
                        'text': 'Su código de validación de Taxi Express es: ' + str( customer.validationCode)
                        }                
                sms = NexmoMessage(msg)
                sms.set_text_info(msg['text'])
                response = sms.send_request()                
                return HttpResponse(status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Usuario ya validado")
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Telefono incorrecto")  
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un numero de telefono")     
    
         
@csrf_exempt
@api_view(['POST'])
def recoverValidationCodeDriver(request):
    if 'phone' in request.POST:     
        try:
            driver = Driver.objects.get(phone=request.POST['phone']) 
            
            if driver.isValidated == False:
                msg = {
                        'reqtype': 'json',
                        'api_key': '8a352457',
                        'api_secret': '460e58ff',
                        'from': 'Taxi Express',
                        'to': driver.phone,
                        'text': 'Su código de validación de Taxi Express es: ' + str( driver.validationCode)
                        }                
                sms = NexmoMessage(msg)
                sms.set_text_info(msg['text'])
                response = sms.send_request()                
                return HttpResponse(status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Usuario ya validado")
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Telefono incorrecto")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un numero de telefono")    
        
    
    

@csrf_exempt
@api_view(['POST'])
def addFavoriteDriver(request):
    try:
        customer = Customer.objects.get(email=request.POST['customerEmail'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    try:
        driver = Driver.objects.get(email=request.POST['driverEmail'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista introducido no es válido")
    
    customer.lastUpdateFavorites = datetime.strptime(request.POST['lastUpdateFavorites'], '%Y-%m-%d %H:%M:%S')
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
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    try:
        driver = customer.favlist.get(email=request.POST['driverEmail'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista no se encuentra en su lista de favoritos")
    customer.favlist.remove(driver)
    customer.lastUpdateFavorites = datetime.strptime(request.POST['lastUpdateFavorites'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Taxista eliminado de la lista de favoritos")


@csrf_exempt
@api_view(['POST'])
def removeTravel(request):
    try:
        customer = Customer.objects.get(email=request.POST['email'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    try:
        travel = customer.travel_set.get(id=request.POST['travel_id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El trayecto no se encuentra en su lista de trayectos realizados")
    customer.lastUpdateTravels = datetime.strptime(request.POST['lastUpdateTravels'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    travel.delete()
    return HttpResponse(status=status.HTTP_200_OK ,content="Trayecto eliminado de la lista")




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
    dr = Driver(email="conductor@gmail.com", password="11111111", phone="+34656111112", first_name="Conductor", last_name="DePrimera", city=ci, validationCode=1234, positiveVotes=10, negativeVotes=3, car=car, geom=Point(43.2618425, -2.9327811), isValidated=True, image="")
    dr.save()
    car = Car(plate='2222BBB', model='Cooper', company='Mini', color='White', capacity=3, accessible=False, animals=False, isfree=True, appPayment=False)
    car.save()
    dr2 = Driver(email="conductor2@gmail.com", password="11111111", phone="+34656111113", first_name="Conductor", last_name="DeSegunda", city=ci, validationCode=1234, positiveVotes=2, negativeVotes=7, car=car, geom=Point(43.264116, -2.9237662), isValidated=True, image="")
    dr2.save()
    cu = Customer(email="gorka_12@hotmail.com", password="11111111", phone="+34656111111", first_name="Pepito", last_name="Palotes", city=ci, validationCode=1234, lastUpdate=datetime.strptime('1980-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), isValidated=True, image="")
    cu.save()
    cu.favlist.add(dr)
    cu.favlist.add(dr2)
    tr = Travel(customer=cu, driver=dr, starttime=datetime.strptime('2013-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, startpoint=Point(43.15457, -2.56488), origin='Calle Autonomía 35', endpoint=Point(43.16218, -2.56352), destination='Av de las Universidades 24')
    tr.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Cargado")


