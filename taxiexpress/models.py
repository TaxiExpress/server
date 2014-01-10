from django.db import models
from django.contrib.gis.db import models
from django.template.defaultfilters import escape
from datetime import datetime

#from django.core.urlresolvers import reverse

# Create your models here.

class Country(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class State(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    country = models.ForeignKey(Country)
    def __unicode__(self):
        return self.name

class City(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    state = models.ForeignKey(State)
    def __unicode__(self):
        return self.name

class Car(models.Model):
    plate = models.CharField(max_length=7, unique=True)
    model = models.CharField(max_length=80)
    company = models.CharField(max_length=80)
    color = models.CharField(max_length=80)
    capacity = models.IntegerField()
    accessible = models.BooleanField()
    animals = models.BooleanField()
    isfree = models.BooleanField()
    appPayment = models.BooleanField()
    def __unicode__(self):
        return self.plate


class Driver(models.Model):
    password = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    phone = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=80, blank=True, null=True)
    postcode = models.CharField(max_length=5, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)
    isValidated = models.BooleanField(default=False)
    validationCode = models.IntegerField(max_length=4, blank=True, null=True)
    positiveVotes = models.IntegerField(blank=True, default=0)
    negativeVotes = models.IntegerField(blank=True, default=0)
    car = models.ForeignKey(Car, null=True)
    image = models.TextField(blank=True, null=True)
    #Ponemos la licencia como unique? Y si cambia de dueno?
    license = models.IntegerField(blank=True, null=True)
    #Datos de pago
    bankAccount = models.CharField(max_length=20)
    recipientName = models.CharField(max_length=80)
    #Posicion
    geom = models.PointField(srid=4326, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.email

class Customer(models.Model):
    password = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    phone = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    postcode = models.CharField(max_length=5, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, null=True)
    lastUpdate = models.DateTimeField(default=datetime.now, blank=True)
    lastUpdateFavourites = models.DateTimeField(default=datetime.now, blank=True)
    lastUpdateTravels = models.DateTimeField(default=datetime.now, blank=True)
    isValidated = models.BooleanField(default=False)
    validationCode = models.IntegerField(max_length=4, blank=True, null=True)
    positiveVotes = models.IntegerField(blank=True, null=True)
    negativeVotes = models.IntegerField(blank=True, null=True)
    #Datos de pago
    favlist = models.ManyToManyField(Driver, related_name='+', blank=True, null=True)
    #FilterList
    fAccessible = models.BooleanField(default=False)
    fAnimals = models.BooleanField(default=False)
    fAppPayment = models.BooleanField(default=False)
    fCapacity = models.IntegerField(default=1)
    def __unicode__(self):
        return self.email


class Travel(models.Model):
    customer = models.ForeignKey(Customer)
    driver = models.ForeignKey(Driver)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    startpoint = models.PointField(srid=4326)
    origin = models.CharField(max_length=80, blank=True, null=True)
    endpoint = models.PointField(srid=4326)
    destination = models.CharField(max_length=80, blank=True, null=True)
    objects = models.GeoManager()
