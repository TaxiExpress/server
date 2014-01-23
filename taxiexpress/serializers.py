from django.forms import widgets
from rest_framework import serializers
from taxiexpress.models import Customer, Country, State, City, Driver, Travel, Car

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('plate', 'model', 'company', 'capacity', 'accessible', 'animals', 'appPayment')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('code', 'name')

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('code', 'name')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('code', 'name')

class DriverDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ('first_name', 'last_name')

class DriverSerializer(serializers.ModelSerializer):
    valuation = serializers.SerializerMethodField('get_valuation')
    car = CarSerializer()
    def get_valuation(self, obj):
            if (obj.positiveVotes+obj.negativeVotes == 0):
                return 0
            else:
                return int(5*obj.positiveVotes/(obj.positiveVotes+obj.negativeVotes))
    class Meta:
        model = Driver
        fields = ('email', 'phone', 'sessionID', 'first_name', 'last_name', 'image', 'valuation', 'car', 'geom')

class TravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    class Meta:
        model = Travel
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination')

class LastTravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    lastUpdateTravels = serializers.SerializerMethodField('get_lastUpdateTravels')
    def get_lastUpdateTravels(self, obj):
        return obj.customer.lastUpdateTravels
    class Meta:
        model = Travel
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination', 'lastUpdateTravels')


#Este serializer devuelve el perfil del Customer + taxistas favoritos + lista de viajes
class CustomerCompleteSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'sessionID', 'first_name', 'last_name', 'image', 'lastUpdate','lastUpdateFavorites','lastUpdateTravels', 'favlist', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity', 'travel_set')

#Este serializer devuelve la lista de taxistas favoritos + lista de viajes
class CustomerTaxiesTravelsSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('sessionID', 'favlist', 'travel_set','lastUpdateFavorites','lastUpdateTravels')

#Este serializer devuelve la lista de viajes
class CustomerTravelsSerializer(serializers.ModelSerializer):
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('sessionID', 'travel_set','lastUpdateTravels')

#Este serializer devuelve solo el perfil del Customer
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('sessionID', 'email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve el perfil del Customer + lista de taxistas
class CustomerProfileTaxiesSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('sessionID', 'favlist','email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate','lastUpdateFavorites', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve el perfil del Customer + lista de viajes
class CustomerProfileTravelsSerializer(serializers.ModelSerializer):
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('sessionID', 'travel_set','email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate','lastUpdateTravels', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve solo la lista de taxistas favoritos
class CustomerTaxiesSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('sessionID', 'favlist','lastUpdateFavorites')
