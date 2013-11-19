from django.db import models
from django.contrib.gis.db import models
from django.template.defaultfilters import escape
#from django.core.urlresolvers import reverse

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    birthdate = models.DateField()
    address = models.CharField(max_length=80)
    postcode = models.IntegerField()
    city = models.ForeignKey(City)
    state = models.ForeignKey(State)
    country = models.ForeignKey(Country)
    email = models.EmailField(max_length=80)
    phone = models.IntegerField()
    #Datos de pago
    cardno = models.IntegerField()
    carddate = models.DateField()
    cvv = models.IntegerField()
    #favlist = ??
    def __unicode__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class Car(models.Model):
    plate = models.CharField(max_length=7)
    model = models.CharField(max_length=80)
    company = models.CharField(max_length=80)
    color = models.CharField(max_length=80)
    capacity = models.IntegerField()
    accessible = models.BooleanField()
    animals = models.BooleanField()
    def __unicode__(self):
        return self.plate

class Driver(models.Model):
    name = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    birthdate = models.DateField()
    address = models.CharField(max_length=80)
    postcode = models.IntegerField()
    city = models.ForeignKey(City)
    state = models.ForeignKey(State)
    country = models.ForeignKey(Country)
    email = models.EmailField(max_length=80)
    phone = models.IntegerField()
    #valuation = ???
    license = models.IntegerField()
    licensepostcode = models.IntegerField()
    #Datos de pago
    #cardno = models.IntegerField()
    #carddate = models.DateField()
    #cvv = models.IntegerField()
    def __unicode__(self):
        return self.name