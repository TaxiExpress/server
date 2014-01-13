# Create your views here.
from django import forms
#from django.forms import CharField,Form,PasswordInput
from django.shortcuts import render_to_response, redirect
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
import string
from datetime import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@csrf_exempt
@api_view(['POST'])
def updateProfileUserWeb(request):
    if request.POST['id'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un id cliente")
    try:
        customer = Customer.objects.get(id=request.POST['id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este cliente")
    customer.first_name = request.POST['first_name']
    customer.last_name = request.POST['last_name']
    customer.image = request.POST['image']
    customer.postcode = request.POST['postcode']
    customer.city = request.POST['city']
    customer.lastUpdate = datetime.strptime(request.POST['lastUpdate'], '%Y-%m-%d %H:%M:%S')
    customer.save()
    return HttpResponse(status=status.HTTP_200_OK,content="Perfil del cliente modificado correctamente")


@csrf_exempt
@api_view(['POST'])
def updateProfileDriverWeb(request):
    if request.POST['id'] is None:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="Debe ingresar un id taxista")
    try:
        driver = Driver.objects.get(id=request.POST['id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content="No es posible encontrar a este taxista")
    driver.first_name = request.POST['first_name']
    driver.last_name = request.POST['last_name']
    driver.image = request.POST['image']
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
def updateCarWeb(request):
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
@api_view(['GET'])
def logout(request):
    if request.session['email'] is not None:
        del request.session['email']
        del request.session['user_id']
        del request.session['Customer']
        request.session.modified = True
    return redirect('index')



