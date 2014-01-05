from django.forms import widgets
from rest_framework import serializers
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('plate', 'model', 'company', 'capacity', 'accessible', 'animals', 'appPayment')

class DriverSerializer(serializers.ModelSerializer):
    valuation = serializers.SerializerMethodField('get_valuation')
    car = CarSerializer()

    def get_valuation(self, obj):
            return int(5*obj.positiveVotes/(obj.positiveVotes+obj.negativeVotes))
    class Meta:
        model = Driver
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'valuation', 'car', 'geom')

class TravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    class Meta:
        model = Travel
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination')

class CustomerSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'favlist', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity', 'travel_set')
