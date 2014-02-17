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
from taxiexpress.serializers import CarSerializer, DriverSerializer, TravelSerializer, CustomerProfileSerializer, DriverDataSerializer, LastTravelSerializer, CustomerCountryStateCitySerializer
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
from passlib.hash import sha256_crypt


PUSH_URL = 'http://ec2-54-84-17-105.compute-1.amazonaws.com:8080'

#Method to ramdomly generate an alphanumeric sessionID
def sessionID_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

#Method to login a customer and retrieve profile data
@csrf_exempt
@api_view(['POST'])
def loginUser(request):
    print request.POST
    if request.POST['email'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")
    try:
        customer = Customer.objects.get(email=request.POST['email'])  
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")
    if sha256_crypt.verify(request.POST['password'], customer.password):
        if customer.isValidated == False:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe validar la cuenta antes de conectarse")

        #Update customer data in database
        customer.sessionID = sessionID_generator()
        customer.pushID = request.POST['pushID']
        customer.save()
        #Check if there are unpaid travels
        unpaidTravels = customer.travel_set.filter(isPaid=False, appPayment=True)
        if unpaidTravels.count() > 0:
            #If there are unpaid travels sends pay notification
            travel = unpaidTravels[0]
            post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": travel.cost, "appPayment": "true"} 
            try:
                resp = requests.post(PUSH_URL+'/push', params=post_data)
            except requests.ConnectionError:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        #Send user info according to last update time
        response_data = {'sessionID': customer.sessionID}
        datetime_profile = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
        datetime_travels = datetime.strptime(request.POST['lastUpdateTravels'], '%Y-%m-%d %H:%M:%S')

        response_data['favlist'] = DriverSerializer(customer.favlist.all(), many=True).data

        #If user profile has changed since last login
        if customer.lastUpdate != datetime_profile:
            response_data.update(CustomerProfileSerializer(customer).data)
        #If travel history has changed since last login
        if customer.lastUpdateTravels !=  datetime_travels:
             response_data['travel_set'] = TravelSerializer(customer.travel_set.filter(isPaid=True).order_by('starttime'), many=True).data
             response_data['lastUpdateTravels'] = customer.lastUpdateTravels
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")


#Method to login a driver and retrieve profile data
@csrf_exempt
@api_view(['POST'])
def loginDriver(request):
    if request.POST['email'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar una dirección de email")
    try:
        driver = Driver.objects.get(email=request.POST['email'])  
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")
    if sha256_crypt.verify(request.POST['password'], driver.password):
        if driver.isValidated == False:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe validar la cuenta antes de conectarse")
        #Update driver data in database
        driver.pushID = request.POST['pushID']
        driver.save()
        driverNameSurname = DriverDataSerializer(driver).data
        driverNameSurname['appPayment'] = driver.car.appPayment
        driverNameSurname['available'] = driver.available
        driverNameSurname['model'] = driver.car.model
        driverNameSurname['company'] = driver.car.company
        driverNameSurname['plate'] = driver.car.plate
        driverNameSurname['license'] = driver.license
        return Response(driverNameSurname, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Credenciales incorrectas. Inténtelo de nuevo")


#Method to register a customer
@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        passtemp = sha256_crypt.encrypt(request.POST['password'])
        if (Customer.objects.filter(email=request.POST['email']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email que ha indicado ya está en uso")
        if (Customer.objects.filter(phone=request.POST['phone']).count() > 0):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El teléfono que ha indicado ya está en uso")
        else:
            try:
                #Create new customer with received data
                c = Customer(email=request.POST['email'], password=passtemp, phone=request.POST['phone'], lastUpdate=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'),lastUpdateTravels=datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S'), image="")
                code = random.randint(1000, 9999) #Generate validation code
                c.validationCode = code
                c.save()
                #Create account confirmation sms
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
        

#Method called by customer app to get a random taxi that meets his preferences and is nearby
@csrf_exempt
@api_view(['POST'])
def getClosestTaxi(request):
    if 'latitude' in request.POST:
        pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude'])) #Create a point item from received coordinates
        try:
            customer = Customer.objects.get(email=request.POST['email']) #Retrieve the user asking for a travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.POST['sessionID']: #Check if user is logged in
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        #Check if user has unpaid travels
        unpaidTravels = customer.travel_set.filter(isPaid=False)
        if unpaidTravels.count() > 0:
           return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No puedes pedir dos viajes a la vez")
        #Get a list with closest drivers meeting user filters
        closestDrivers = Driver.objects.distance(pointclient).filter(car__isfree=True, available=True, car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:5]
        if closestDrivers.count() == 0:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content="No se han encontrado taxis")
        elif closestDrivers.count() > 5:
            closestDrivers = closestDrivers[:5] #If mone than 5 drivers are found, reduce the list to 5 items
        pushIDS = {}        
        for i in range(1,closestDrivers.count()-1):
            pushIDS.append(closestDrivers[i].pushID)
        travel = Travel(customer=customer, startpoint=pointclient, origin=request.POST['origin'])
        travel.save()
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes)) #Calculate customer valuation (1..5) to send it to close drivers
        #Dictionary to be sent to PUSH server
        punto = ''
        punto += str(request.POST['latitude'])+','+str(request.POST['longitude'])
        post_data = {"pushId": pushIDS , "title" : "Viaje disponible" , "message" : 801 , "startpoint": punto, "travelID": travel.id, "customerID": customer.id, "phone": customer.phone} 
        try:
            resp = requests.post(PUSH_URL + '/push', params=post_data) #Send notify dictionary to PUSH server
        except requests.ConnectionError: #If push server is offline, delete travel and return 503
            travel.delete()
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        travel.save()
        #Return travelID to customer app
        response_data = {}
        response_data['travelID'] = travel.id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")


#Method called by customer app to ask for a selected taxi
@csrf_exempt
@api_view(['POST'])
def getSelectedTaxi(request):
    if 'latitude' in request.POST:
        pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude'])) #Create a point item from received coordinates
        try:
            customer = Customer.objects.get(email=request.POST['email']) #Retrieve the user asking for a travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.POST['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        #Check if user has unpaid travels
        unpaidTravels = customer.travel_set.filter(isPaid=False)
        if unpaidTravels.count() > 0:
	       return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No puedes pedir dos viajes a la vez")
        driver = Driver.objects.get(email=request.POST['driverEmail'])
        if (driver.available == False) or (driver.car.isfree == False):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista no está disponible actualmente")
        travel = Travel(customer=customer, startpoint=pointclient, origin=request.POST['origin'])
        travel.save()
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes)) #Calculate customer valuation (1..5) to send it to close drivers
        #Dictionary to be sent to PUSH server
        punto = ''
        punto += str(request.POST['latitude'])+','+str(request.POST['longitude'])
        post_data = {"pushId": driver.pushID , "title" : "Viaje disponible" , "message" : 802 , "startpoint": punto, "travelID": travel.id, "customerID": customer.id, "phone": customer.phone} 
        try:
            resp = requests.post(PUSH_URL + '/push', params=post_data) #Send notify dictionary to PUSH server
        except requests.ConnectionError: #If push server is offline, delete travel and return 503
            travel.delete()
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        travel.save()
        #Return travelID to customer app
        response_data = {}
        response_data['travelID'] = travel.id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Error al obtener la posicion")


@csrf_exempt
@api_view(['GET'])
def getCustomerPublicData(request):
    if 'customerID' in request.GET:
        try:
            customer = Customer.objects.get(id=request.GET['customerID']) #Retrieve the user asking for a travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        valuation = 0
        if (customer.positiveVotes+customer.negativeVotes) > 0:
            valuation = int(5*customer.positiveVotes/(customer.positiveVotes+customer.negativeVotes)) #Calculate customer valuation (1..5) to send it to close drivers
        response_data = {}
        response_data['name'] = customer.first_name
        response_data['surname'] = customer.last_name
        response_data['image'] = customer.image
        response_data['valuation'] = valuation
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")

#Method called by driver app to accept a travel
@csrf_exempt
@api_view(['POST'])
def acceptTravel(request):
    if 'email' in request.POST:
        print request.POST
        try:
            driver = Driver.objects.get(email=request.POST['email']) #Retrieve the driver accepting the travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje ya no está disponible")
        if travel.accepted:
            return HttpResponse(status=status.HTTP_409_CONFLICT, content="El viaje ya no está disponible")
        #Update travel data
        travel.driver = driver
        travel.accepted = True
        travel.save()
        #Update driver coordinates and set isfree property to false
        driverpos = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        driver.car.isfree = False
        driver.geom = driverpos
        driver.save()
        #Dictionary to be sent to PUSH server
        post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "title" : "Solicitud aceptada", "message": 701, "latitude": str(driverpos.x), "longitude": str(driverpos.y)} 
        print post_data
        try:
            resp = requests.post(PUSH_URL+'/push', params=post_data) #Send notify dictionary to PUSH server
            print resp
        except requests.ConnectionError: #If push server is offline, delete travel and return 503
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by driver app when he picks up the customer and the travel starts
@csrf_exempt
@api_view(['POST'])
def travelStarted(request):
    print request.POST
    if 'travelID' in request.POST: 
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.driver.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        #Update travel data
        #travel.origin = request.POST['origin']
        #travel.startpoint = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        travel.starttime = datetime.now()
        travel.save()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by driver app when he reaches destination point of the travel
#A Push notification is sent to the customer with payment data
@csrf_exempt
@api_view(['POST'])
def travelCompleted(request):
    if 'travelID' in request.POST: 
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.driver.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        #Update travel data
        travel.destination = request.POST['destination']
        travel.endpoint = Point(float(request.POST['latitude']), float(request.POST['longitude']))
        travel.endtime = datetime.now()
        travel.cost = request.POST['cost']
        travel.appPayment = (request.POST['appPayment'] == "true")
        travel.driver.car.isfree = True
        travel.save()
        if travel.appPayment:
            #Dictionary to be sent to PUSH server
            post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "true", "title": "Pago en mano", "message" : 702} 
            try:
                resp = requests.post(PUSH_URL+'/push', params=post_data) #Send notify dictionary to PUSH server
            except requests.ConnectionError: #If push server is offline, delete travel and return 503
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        else:
            travel.isPaid = True #If payment is done directly to the driver, we consider the travel paid
            travel.customer.lastUpdateTravels = datetime.now()
            travel.save()
            try:
                #Dictionary to be sent to PUSH server
                post_data = {"travelID": travel.id, "pushId": travel.customer.pushID, "cost": request.POST['cost'], "appPayment": "false", "title": "Pago en mano", "message" : 702} 
                resp = requests.post(PUSH_URL+'/push', params=post_data) #Send notify dictionary to PUSH server
            except requests.ConnectionError: #If push server is offline, delete travel and return 503
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by customer app when he pays the travel with the app
@csrf_exempt
@api_view(['POST'])
def travelPaid(request):
    if 'travelID' in request.POST:
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.customer.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        if request.POST['sessionID'] != travel.customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        #Update travel data
        travel.isPaid = True
        travel.customer.lastUpdateTravels = datetime.now()
        travel.save()
        print travel.isPaid
        #Dictionary to be sent to PUSH server
        post_data = {"travelID": travel.id, "pushId": travel.driver.pushID, "paid": "true" , "title" : "Viaje " , "message": 803}
        try:
            resp = requests.post(PUSH_URL+'/push', params=post_data) #Send notify dictionary to PUSH server
        except requests.ConnectionError: #If push server is offline, delete travel and return 503
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        print resp
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by customer app to cancel a travel before it has been accepted
@csrf_exempt
@api_view(['POST'])
def cancelTravelCustomer(request):
    if 'travelID' in request.POST:
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.customer.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        if request.POST['sessionID'] != travel.customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        if travel.accepted: #If travel has already been accepted, return 401
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El viaje ha sido aceptado")
        travel.delete() #If cancellation is possible, delete the travel
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by driver app to cancel a travel after he has accepted it
@csrf_exempt
@api_view(['POST'])
def cancelTravelDriver(request):
    if 'travelID' in request.POST:
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if request.POST['email'] != travel.driver.email:
            return HttpResponse(status=status.HTTP_401_BAD_REQUEST, content="Email incorrecto")
        #Dictionary to be sent to PUSH server
        post_data = {"travelID": travel.id, "pushId": travel.customer.pushID , "title": "El taxista ha cancelado el viaje" , "message" : 703}
        try:
            resp = requests.post(PUSH_URL+'/push', params=post_data) #Send notify dictionary to PUSH server
            if resp.status_code == 404:
                return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        except requests.ConnectionError: #If push server is offline, delete travel and return 503
            return HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content="Servicio no disponible")
        travel.delete()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Parámetros incorrectos")


#Method called by customer app to retrieve last travel data
@csrf_exempt
@api_view(['GET'])
def getLastTravel(request):
    if 'email' in request.GET:
        try:
            customer = Customer.objects.get(email=request.GET['email']) #Retrieve the customer item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El usuario no existe")
        if request.GET['sessionID'] != customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        travel = customer.travel_set.order_by('-starttime')[0] #Get customer's last travel by start time
        serialTravel = LastTravelSerializer(travel)
        return Response(serialTravel.data, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Email no válido")


#Method called by customer app to vote a driver from one of his completed travels
@csrf_exempt
@api_view(['POST'])
def voteDriver(request):
    if 'email' in request.POST:
        try:
            customer = Customer.objects.get(email=request.POST['email']) #Retrieve the customer item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El usuario no existe")
        if request.POST['sessionID'] != customer.sessionID:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if travel.customervoted == True: #If driver has already been voted for that travel, return 400
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Ya has votado")
        travel.customervoted = True
        travel.save()
        #Update driver votes
        driver = travel.driver
        if request.POST['vote'] == 'positive':
            driver.positiveVotes += 1
        else:
            driver.negativeVotes += 1
        driver.save()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Email no válido")


#Method called by driver app to vote a customer from one of his completed travels
@csrf_exempt
@api_view(['POST'])
def voteCustomer(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email']) #Retrieve the driver item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El usuario no existe")
        try:
            travel = Travel.objects.get(id=request.POST['travelID']) #Retrieve referenced travel
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El viaje no existe")
        if travel.drivervoted == True: #If customer has already been voted for that travel, return 400
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="Ya has votado")
        travel.drivervoted = True
        travel.save()
        #Update driver votes
        customer = travel.customer
        if request.POST['vote'] == 'positive':
            customer.positiveVotes += 1
        else:
            customer.negativeVotes += 1
        customer.save()
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

#Method called by customer app to get a random taxi list meeting his preferences
@csrf_exempt
@api_view(['GET'])
def getNearestTaxies(request):
    if 'latitud' in request.GET:
        pointclient = Point(float(request.GET['latitud']), float(request.GET['longitud'])) #Create a point item from received coordinates
        try:
            customer = Customer.objects.get(email=request.GET['email']) #Retrieve the customer item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if customer.sessionID != request.GET['sessionID']:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
        #Get a list with closest drivers meeting user filters
        closestDrivers = Driver.objects.distance(pointclient).filter(car__isfree=True, available=True, car__accessible__in=[customer.fAccessible, True], car__animals__in=[customer.fAnimals, True], car__appPayment__in=[customer.fAppPayment, True], car__capacity__gte=customer.fCapacity).order_by('distance')[:10]
        serialDriver = DriverSerializer(closestDrivers, many=True) #Serialize driver list
        return Response(serialDriver.data, status=status.HTTP_200_OK) #Send the serialized list to customer
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
        customer = Customer.objects.get(email=request.POST['email']) #Retrieve the customer item
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    #Update customer data
    customer.first_name = request.POST['firstName']
    customer.last_name = request.POST['lastName']
    customer.image = request.POST['newImage']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del usuario modificado correctamente")


#Method called by driver app to update his position every time he moves
@csrf_exempt
@api_view(['POST'])
def updateDriverPosition(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email']) #Retrieve the driver item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        if 'latitude' in request.POST:
            #Update driver position in Database
            pointclient = Point(float(request.POST['latitude']), float(request.POST['longitude']))
            driver.geom = pointclient
            driver.save()
            return HttpResponse(status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Punto inexistente")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email inexistente")


#Method called by driver app when his available status changes
@csrf_exempt
@api_view(['POST'])
def updateDriverAvailable(request):
    if 'email' in request.POST:
        try:
            driver = Driver.objects.get(email=request.POST['email']) #Retrieve the driver item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
        #Update driver available status
        driver.available = (request.POST['available'] == 'true')
        driver.save()
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Email inexistente")


#Method called by customer app when he changes any search filter in the app
@csrf_exempt
@api_view(['POST'])
def updateFilters(request):
    try:
        customer = Customer.objects.get(email=request.POST['email']) #Retrieve the customer item
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    #Update filters in database with values from the app
    customer.fAccessible = (request.POST['accesible'] == 'true')
    customer.fAnimals = (request.POST['animals'] == 'true')
    customer.fAppPayment = (request.POST['appPayment'] == 'true')
    customer.fCapacity = request.POST['capacity']
    customer.fDistance = request.POST['distance']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Filtros actualizados")

    

#Method called by customer app to verify an account once it has been registered and validation code has been received in phone
@api_view(['POST'])
def validateUser(request):
    if 'phone' in request.POST:
        try:
            customer = Customer.objects.get(phone=request.POST['phone']) #Retrieve the customer item
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Error al validar esta cuenta. Inténtelo de nuevo")
        if customer.isValidated == False:
            if customer.validationCode == int(request.POST['validationCode']):
                #If customer isn't validated and posted validation code is correct, update validation status in database and send confirmation email to customer
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
        else: #If customer is already validated send 401 error
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Esta cuenta ya está validada.")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Teléfono incorrecto")
        

#Method called by customer app to change account password
@csrf_exempt
@api_view(['POST'])
def changePassword(request):
    try:
        customer = Customer.objects.get(email=request.POST['email']) #Retrieve the customer item
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El email introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    if sha256_crypt.verify(request.POST['oldPass'], customer.password):
        #If old password verification succeeds, update password on database and send confirmation email
        customer.password = sha256_crypt.encrypt(request.POST['newPass'])
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


#Method called by customer app to recover email address from associated phone
@csrf_exempt
@api_view(['GET'])
def recoverEmail(request):
    if 'phone' in request.GET:   
        try:
            customer = Customer.objects.get(phone=request.GET['phone']) #Retrieve the driver item by phone number
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este usuario")
        return HttpResponse(status=status.HTTP_200_OK,content=customer.email) #Return email address
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un número de teléfono") 
        

#Method called by customer app to recover validation code in case it hasn't been received
@csrf_exempt
@api_view(['POST'])
def recoverValidationCodeCustomer(request):
    if 'phone' in request.POST:
        try:
            customer = Customer.objects.get(phone=request.POST['phone']) #Retrieve the customer item by phone number
            if customer.isValidated == False:
                #If customer isn't already validated send sms with validation code
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
            else: # If customer is already validated send 401 error
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Usuario ya validado")
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Telefono incorrecto")  
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un numero de telefono")     
    

#Method called by driver app to recover validation code in case it hasn't been received
@csrf_exempt
@api_view(['POST'])
def recoverValidationCodeDriver(request):
    if 'phone' in request.POST:     
        try:
            driver = Driver.objects.get(phone=request.POST['phone']) #Retrieve the driver item by phone number
            if driver.isValidated == False:
                #If driver isn't already validated send sms with validation code
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
            else: #If driver is already validated send 401 error
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Usuario ya validado")
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Telefono incorrecto")
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un numero de telefono")    
        
    
    
#Method called by customer app to add a specific driver to favourite list
@csrf_exempt
@api_view(['POST'])
def addFavoriteDriver(request):
    try:
        customer = Customer.objects.get(email=request.POST['customerEmail']) #Retrieve the customer calling the method
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    try:
        driver = Driver.objects.get(email=request.POST['driverEmail']) #Retrieve the driver to be added to favourite list
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista introducido no es válido")
    #Add driver item to customer's favourite list
    customer.favlist.add(driver)
    customer.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Taxista añadido a la lista de favoritos")


#Method called by customer app to remove a driver from favourite list
@csrf_exempt
@api_view(['POST'])
def removeFavoriteDriver(request):
    try:
        customer = Customer.objects.get(email=request.POST['customerEmail']) #Retrieve the customer calling the method
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="El usuario introducido no es válido")
    if customer.sessionID != request.POST['sessionID']:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debes estar conectado para realizar esta acción")
    try:
        driver = customer.favlist.get(email=request.POST['driverEmail']) #Search in favourite list for the driver to be removed
    except ObjectDoesNotExist: #If driver is not found in customer's favourite list, send 400 error
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content="El taxista no se encuentra en su lista de favoritos")
    #Remove driver from customer's favoutite list
    customer.favlist.remove(driver)
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Taxista eliminado de la lista de favoritos")


#Method called to load test data every time Database is reset
@csrf_exempt
@api_view(['GET'])
def loadData(request):
    loadCombo(request)
    car = Car(plate='1111AAA', model='Laguna', company='Renault', color='White', capacity=4, accessible=True, animals=False, isfree=True, appPayment=True)
    car.save()
    dr = Driver(email="conductor@gmail.com", password=sha256_crypt.encrypt("11111111"), phone="+34656111112", first_name="Conductor", last_name="DePrimera", city = City.objects.get(id=34), validationCode=1234, positiveVotes=10, negativeVotes=3, car=car, geom=Point(43.2618425, -2.9327811), isValidated=True, image="", pushID='APA91bHJRkpSjXvlFA7L94ybyalAeW0BxE0Z1K4g99onHvXLIFgptSJDhBIMXckY9HBzaBpEWo4Se9zUCd2KjzWUHCJ5TLac-qF-Hu8ozi7Uoe14ZFRg2_c82xmL4ZXgMfuhec4UUd-eu_SkYsMPRt2bqNZ0K5Uzgpwd2en9454w8-f3c7pyEK0')
    dr.save()
    car = Car(plate='2222BBB', model='Cooper', company='Mini', color='White', capacity=3, accessible=False, animals=False, isfree=True, appPayment=False)
    car.save()
    dr2 = Driver(email="conductor2@gmail.com", password=sha256_crypt.encrypt("11111111"), phone="+34656111113", first_name="Conductor", last_name="DeSegunda", city = City.objects.get(id=54), validationCode=1234, positiveVotes=2, negativeVotes=7, car=car, geom=Point(43.264116, -2.9237662), isValidated=True, image="", pushID='APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4')
    dr2.save()
    cu = Customer(email="gorka_12@hotmail.com", password=sha256_crypt.encrypt("11111111"), phone="+34656111111", first_name="Pepito", last_name="Palotes", city = City.objects.get(id=20), validationCode=1234, lastUpdate=datetime.strptime('1980-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), isValidated=True, image="", pushID='APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4')
    cu.save()
    cu.favlist.add(dr)
    cu.favlist.add(dr2)
    tr = Travel(customer=cu, driver=dr, starttime=datetime.strptime('2013-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, startpoint=Point(43.15457, -2.56488), origin='Calle Autonomía 35', endpoint=Point(43.16218, -2.56352), destination='Av de las Universidades 24')
    tr.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Cargado")

@csrf_exempt
@api_view(['GET'])
def loadTravels(request):
    cu1 = Customer(email="laura@gmail.com", password=sha256_crypt.encrypt("11111111"), phone="+34656222222", first_name="laura", last_name="linacero", city = City.objects.get(id=56), validationCode=1234, lastUpdate=datetime.strptime('1980-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), isValidated=True, image="", pushID='APA91bHTypZCKvUdXYd-lhimPaLbolkEvZU8o9o5FWhRW0tIx5JpcIS3mdNYza0o5F0d-lBzn3xYw2RBZWfJEy_wdOLIZVwefcUsRtG_PpGXyauJ0EnnOND-zS0dOOAcb_xG2QhqodKQchzJgV6-z41y8zsPwMzJrNY2Bj-kCeUsm-Ca3kKH0j4')
    cu1.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-01-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-01-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-01-02 12:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-01-02 12:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-01-03 23:23:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-01-03 23:40:01','%Y-%m-%d %H:%M:%S'), cost=15.10, origin='Calle Mi calle', destination='Tu calle', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-02-01 11:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-02-01 11:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-01-02 12:45:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-01-02 13:10:46','%Y-%m-%d %H:%M:%S'), cost=14.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-03-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-03-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-03 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-03 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-04 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-04 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-05 00:48:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-05 01:10:15','%Y-%m-%d %H:%M:%S'), cost=6.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-02-01 20:00:30','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-02-01 20:10:52','%Y-%m-%d %H:%M:%S'), cost=30.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-11 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-11 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-12 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-12 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-13 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-13 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-14 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-14 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-03-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-03-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-03 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-03 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-04 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-04 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-05 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-05 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-02-01 20:00:30','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-02-01 20:10:52','%Y-%m-%d %H:%M:%S'), cost=30.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-11 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-11 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-12 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-12 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-13 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-13 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-14 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-14 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-14 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-14 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-03-01 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-03-01 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-03 19:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-03 19:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-04 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-04 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-04-05 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-04-05 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2014-02-01 20:00:30','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2014-02-01 20:10:52','%Y-%m-%d %H:%M:%S'), cost=30.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-11 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-11 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-12 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-12 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor@gmail.com"), starttime=datetime.strptime('2013-11-13 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-13 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    tr = Travel(customer=Customer.objects.get(email="laura@gmail.com"), driver=Driver.objects.get(email="conductor2@gmail.com"), starttime=datetime.strptime('2013-11-14 00:00:01','%Y-%m-%d %H:%M:%S'), endtime=datetime.strptime('2013-11-14 00:10:01','%Y-%m-%d %H:%M:%S'), cost=20.10, origin='Calle Autonomía 35', destination='Av de las Universidades 24', isPaid = True, startpoint=Point(43.15457, -2.56488), endpoint=Point(43.16218, -2.56352))
    tr.save()
    return HttpResponse(status=status.HTTP_201_CREATED,content="Cargado")
