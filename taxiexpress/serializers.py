from django.forms import widgets
from rest_framework import serializers
from taxiexpress.models import Customer, Country, State, City, Driver

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ('email', 'phone', 'first_name', 'last_name', 'image')

class TravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    class Meta:
        model = Travel
        fields = ('driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination')

class CustomerSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'first_name', 'last_name', 'lastUpdate', 'favlist', 'travel_set')
