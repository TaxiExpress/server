from django.db import models
from django.contrib.gis.db import models
from django.template.defaultfilters import escape
#from django.core.urlresolvers import reverse

# Create your models here.

class City(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class State(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class Country(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name


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
    valuation = models.FloatField()
    votes = models.IntegerField()
    #Ponemos la licencia como unique? Y si cambia de dueno?
    license = models.IntegerField()
    licensepostcode = models.IntegerField()
    #Datos de pago
    #Posicion
    geom = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

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

    favlist = models.ManyToManyField(Driver, related_name='+')
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
    def __unicode__(self):
        return self.plate



class Travel(models.Model):
    client = models.ForeignKey(Client)
    driver = models.ForeignKey(Driver)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    cost = models.FloatField()
    startpoint = models.PointField(srid=4326)
    endpoint = models.PointField(srid=4326)
    objects = models.GeoManager()

class Report(models.Model):
    client = models.ForeignKey(Client)
    driver = models.ForeignKey(Driver)
    report = models.CharField(max_length=255)
