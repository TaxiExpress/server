from django.db import models
from django.contrib.gis.db import models
from django.template.defaultfilters import escape
from datetime import datetime

#from django.core.urlresolvers import reverse

# Create your models here.

class Country(models.Model):
    class Meta:
        verbose_name_plural = "Countries"
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name

class State(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=80)
    country = models.ForeignKey(Country)
    def __unicode__(self):
        return self.name

class City(models.Model):
    class Meta:
        verbose_name_plural = "Cities"
    code = models.IntegerField()
    name = models.CharField(max_length=80)
    state = models.ForeignKey(State)
    def __unicode__(self):
        return self.name

class Car(models.Model):
    plate = models.CharField(max_length=7, unique=True)
    model = models.CharField(max_length=80)
    company = models.CharField(max_length=80, default="", blank=True)
    color = models.CharField(max_length=80, default="", blank=True)
    capacity = models.IntegerField(default=3)
    accessible = models.BooleanField(default=False)
    animals = models.BooleanField(default=False)
    isfree = models.BooleanField(default=True)
    appPayment = models.BooleanField(default=False)
    def __unicode__(self):
        return self.plate


class Driver(models.Model):
    password = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    phone = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80, default="", blank=True)
    last_name = models.CharField(max_length=80, default="", blank=True)
    address = models.CharField(max_length=80, default="", blank=True)
    postcode = models.CharField(max_length=5, default="", blank=True)
    city = models.ForeignKey(City, blank=True, null=True)
    isValidated = models.BooleanField(default=False)
    validationCode = models.IntegerField(max_length=4, blank=True, null=True)
    positiveVotes = models.IntegerField(blank=True, default=0)
    negativeVotes = models.IntegerField(blank=True, default=0)
    car = models.ForeignKey(Car, null=True)
    image = models.TextField(blank=True, null=True)
    available = models.BooleanField(default=True)
    #Ponemos la licencia como unique? Y si cambia de dueno?
    license = models.IntegerField(blank=True, null=True)
    #Datos de pago
    bankAccount = models.CharField(max_length=20, default="", blank=True)
    recipientName = models.CharField(max_length=80, default="", blank=True)
    pushID = models.TextField(blank=True, null=True)
    device = models.CharField(max_length=7, default='ANDROID', blank=True)
    sessionID = models.CharField(max_length=10, blank=True, null=True)
    #Posicion
    geom = models.PointField(srid=4326, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.email

class Customer(models.Model):
    password = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    phone = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80, default="", blank=True)
    last_name = models.CharField(max_length=80, default="", blank=True)
    postcode = models.CharField(max_length=5, default="", blank=True)
    image = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, null=True)
    lastUpdate = models.DateTimeField(default=datetime.now, blank=True)
    lastUpdateFavorites = models.DateTimeField(default=datetime.now, blank=True)
    lastUpdateTravels = models.DateTimeField(default=datetime.now, blank=True)
    isValidated = models.BooleanField(default=False)
    validationCode = models.IntegerField(max_length=4, blank=True, null=True)
    positiveVotes = models.IntegerField(default=0)
    negativeVotes = models.IntegerField(default=0)
    #Datos de pago
    favlist = models.ManyToManyField(Driver, related_name='+', blank=True, null=True)
    #FilterList
    fAccessible = models.BooleanField(default=False)
    fAnimals = models.BooleanField(default=False)
    fAppPayment = models.BooleanField(default=False)
    fCapacity = models.IntegerField(default=1)
    pushID = models.TextField(blank=True, null=True)
    device = models.CharField(max_length=7, default='ANDROID', blank=True)
    sessionID = models.CharField(max_length=10, blank=True, null=True)
    def __unicode__(self):
        return self.email


class Travel(models.Model):
    customer = models.ForeignKey(Customer)
    driver = models.ForeignKey(Driver, blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    startpoint = models.PointField(srid=4326)
    origin = models.CharField(max_length=80, blank=True, null=True)
    endpoint = models.PointField(srid=4326, blank=True, null=True)
    destination = models.CharField(max_length=80, blank=True, null=True)
    appPayment = models.BooleanField(default=False)
    isPaid = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    customervoted = models.BooleanField(default=False)
    drivervoted = models.BooleanField(default=False)
    objects = models.GeoManager()

class Observation(models.Model):
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(max_length=80)
    tipo = models.IntegerField(max_length=2)
    observations = models.TextField(max_length=200)
    def __unicode__(self):
        return self.email
