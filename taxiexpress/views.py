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
from taxiexpress.serializers import CarSerializer, DriverSerializer, CustomerTravelsSerializer, CustomerProfileSerializer, CustomerTaxiesSerializer, DriverDataSerializer, LastTravelSerializer, CustomerCountryStateCitySerializer
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
from web.LoadComboInf import loadCombo


PUSH_URL = 'http://ec2-54-84-17-105.compute-1.amazonaws.com:8080'


def sessionID_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


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
        customer.sessionID = sessionID_generator()
        customer.pushID = request.POST['pushID']
        customer.device = request.POST['pushDevice']
        customer.save()
        #Check if there are unpaid travels
        unpaidTravels = customer.travel_set.filter(isPaid=False, appPayment=True)
        if unpaidTravels.count() > 0:
            #If there are unpaid travels sends pay notification
            travel = unpaidTravels[0]
            post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "true","device": customer.device} 
            try:
                resp = requests.post(PUSH_URL+'/sendTravelCompleted', params=post_data)
            except requests.ConnectionError:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)
                

        response_data = {'sessionID': customer.sessionID}
        datetime_profile = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
        datetime_travels = datetime.strptime(request.POST['lastUpdateTravels'], '%Y-%m-%d %H:%M:%S')

        response_data.update(CustomerTaxiesSerializer(customer).data)
        
        if customer.lastUpdate != datetime_profile:
            response_data.update(CustomerProfileSerializer(customer).data)
        if customer.lastUpdateTravels !=  datetime_travels:
            response_data.update(CustomerTravelsSerializer(customer).data)
        return Response(response_data, status=status.HTTP_200_OK)
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
        driver.pushID = request.POST['pushID']
        driver.device = request.POST['pushDevice']
        driver.available = True
        driver.save()
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
@api_view(['POST'])
def getClosestTaxi(request):
    if 'latitude' in request.POST:
        pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.POST['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        closestDrivers = Driver.objects.distance(pointclient).filter(car__isfree=True, available=True, car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:5]
        if closestDrivers.count() == 0:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content="No se han encontrado taxis")
        elif closestDrivers.count() > 5:
            closestDrivers = closestDrivers[:5]
        travel = Travel(customer=customer, startpoint=pointclient, origin=request.POST['origin'])
        travel.save()
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes))
        post_data = {"origin": request.POST['origin'], "startpoint": pointclient, "travelID": travel.id, "valuation": valuation, "phone": customer.phone}
        post_data_ios = {"device": 'IOS'}
        post_data_ios.update(post_data)
        post_data_android = {"device": 'ANDROID'}
        post_data_android.update(post_data)
        ioscount = 0
        androidcount = 0
        for i in range(closestDrivers.count()):
            if closestDrivers[i].device == 'IOS':
                post_data_ios["pushId"+str(ioscount)] = closestDrivers[i].pushID
                ioscount += 1
            elif closestDrivers[i].device == 'ANDROID':
                post_data_android["pushId"+str(androidcount)] = closestDrivers[i].pushID
                androidcount += 1
        if ioscount < 5:
            for i in range(ioscount, 4):
                post_data_ios["pushId"+str(i)] = ""
        if androidcount < 5:
            for i in range(androidcount, 4):
                post_data_android["pushId"+str(i)] = ""
        try:
            resp_ios = requests.post(PUSH_URL+'/sendClosestTaxi', params=post_data_ios)
            resp_android = requests.post(PUSH_URL+'/sendClosestTaxi', params=post_data_android)
        except requests.ConnectionError:
            travel.delete()
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        response_data = {}
        response_data['travelID'] = travel.id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")

@csrf_exempt
@api_view(['POST'])
def getSelectedTaxi(request):
    if 'sessionID' in request.POST:
        pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.POST['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        driver = Driver.objects.get(email=request.POST['driverEmail'])
        if (driver.available == False) or (driver.car.isfree == False):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista no está disponible actualmente")
        travel = Travel(customer=customer, startpoint=pointclient, origin=request.POST['origin'])
        travel.save()
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes))
        post_data = {"pushId": driver.pushID ,"origin": request.POST['origin'], "startpoint": pointclient, "travelID": travel.id, "valuation": valuation, "phone": customer.phone, "device": driver.device} 
        try:
            resp = requests.post(PUSH_URL+'/sendSelectedTaxi', params=post_data)
        except requests.ConnectionError:
            travel.delete()
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
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
            travel = Travel.objects.get(id=request.POST['travelID'])
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
        post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "latitude": str(driverpos.x), "longitude": str(driverpos.y), "device": travel.customer.device} 
        print post_data
        try:
            resp = requests.post(PUSH_URL+'/sendAcceptTravel', params=post_data)
            print resp
        except requests.ConnectionError:
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

@csrf_exempt
@api_view(['POST'])
def travelStarted(request):
    print request.POST
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
            post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "true","device": travel.customer.device} 
            try:
                resp = requests.post(PUSH_URL+'/sendTravelCompleted', params=post_data)
            except requests.ConnectionError:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        else:
            travel.isPaid = True
            travel.customer.lastUpdateTravels = datetime.now()
            travel.save()
            try:
                post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "false","device": travel.customer.device} 
                resp = requests.post(PUSH_URL+'/sendTravelCompleted', params=post_data)
            except requests.ConnectionError:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
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
        travel.customer.lastUpdateTravels = datetime.now()
        travel.save()
        post_data = {"travelID": travel.id, "pushId": travel.driver.pushID, "paid": "true", "device": travel.driver.device}
        try:
            resp = requests.post(PUSH_URL+'/sendTravelPaid', params=post_data)
        except requests.ConnectionError:
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        print resp
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
        if travel.accepted:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El viaje ha sido aceptado")
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
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El usuario no existe")
        if request.GET['sessionID'] != customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        travel = customer.travel_set.order_by('-starttime')[0]
        serialTravel = LastTravelSerializer(travel)
        return Response(serialTravel.data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Email no válido")

@csrf_exempt
@api_view(['POST'])
def voteDriver(request):
    if 'email' in request.POST:
        try:
            customer = Customer.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El usuario no existe")
        if request.POST['sessionID'] != customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        try:
            travel = Travel.objects.get(id=request.POST['travelID'])
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if travel.customervoted == True:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Ya has votado")
        travel.customervoted = True
        driver = travel.driver
        if request.POST['vote'] == 'positive':
            driver.positiveVotes += 1
        else:
            driver.negativeVotes += 1
        driver.save()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Email no válido")

@csrf_exempt
@api_view(['GET'])
def testPush(request):
    try:
        userdata = {"pushId": "APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4", "travelID": "1", "device": "ANDROID", "origin": "Calle Autonomía 35", "startpoint": "POINT (43.1545699999999997 -2.5648800000000000)", "valuation": "2", "phone": "656112233"}
        resp = requests.post(PUSH_URL+'/sendSelectedTaxi', params=userdata)
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
        closestDrivers = Driver.objects.distance(pointclient).filter(car__isfree=True, available=True, car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:10]
        serialDriver = DriverSerializer(closestDrivers, many=True)
        return Response(serialDriver.data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")


@csrf_exempt
@api_view(['GET'])
def test(request):
    cu = Customer.objects.get(email='gorka_12@hotmail.com')
    lista = CustomerCountryStateCitySerializer(cu)
    return Response(lista.data, status=status.HTTP_200_OK)




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
            return HttpResponse(status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Punto inexistente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email inexistente")


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
        return HttpResponse(status=status.HTTP_200_OK)
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
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Taxista eliminado de la lista de favoritos")



@csrf_exempt
@api_view(['GET'])
def loadData(request):
    loadCombo(request)
    car = Car(plate='1111AAA', model='Laguna', company='Renault', color='White', capacity=4, accessible=True, animals=False, isfree=True, appPayment=True)
    car.save()
    dr = Driver(email="conductor@gmail.com", password="11111111", phone="+34656111112", first_name="Conductor", last_name="DePrimera", city = City.objects.get(id=34), validationCode=1234, positiveVotes=10, negativeVotes=3, car=car, geom=Point(43.2618425, -2.9327811), isValidated=True, image="", pushID='APA91bHJRkpSjXvlFA7L94ybyalAeW0BxE0Z1K4g99onHvXLIFgptSJDhBIMXckY9HBzaBpEWo4Se9zUCd2KjzWUHCJ5TLac-qF-Hu8ozi7Uoe14ZFRg2_c82xmL4ZXgMfuhec4UUd-eu_SkYsMPRt2bqNZ0K5Uzgpwd2en9454w8-f3c7pyEK0')
    dr.save()
    car = Car(plate='2222BBB', model='Cooper', company='Mini', color='White', capacity=3, accessible=False, animals=False, isfree=True, appPayment=False)
    car.save()
    dr2 = Driver(email="conductor2@gmail.com", password="11111111", phone="+34656111113", first_name="Conductor", last_name="DeSegunda", city = City.objects.get(id=54), validationCode=1234, positiveVotes=2, negativeVotes=7, car=car, geom=Point(43.264116, -2.9237662), isValidated=True, image="", pushID='APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4')
    dr2.save()
    cu = Customer(email="gorka_12@hotmail.com", password="11111111", phone="+34656111111", first_name="Pepito", last_name="Palotes", city = City.objects.get(id=20), validationCode=1234, lastUpdate=datetime.strptime('1980-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), isValidated=True, image="", pushID='APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4')
    cu.save()
    cu.favlist.add(dr)
    cu.favlist.add(dr2)
    tr = Travel(customer=cu, driver=dr, starttime=datetime.strptime('2013-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, startpoint=Point(43.15457, -2.56488), origin='Calle Autonomía 35', endpoint=Point(43.16218, -2.56352), destination='Av de las Universidades 24')
    tr.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Cargado")


