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
        fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')

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
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination','customervoted','drivervoted')

class LastTravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    lastUpdateTravels = serializers.SerializerMethodField('get_lastUpdateTravels')
    def get_lastUpdateTravels(self, obj):
        return obj.customer.lastUpdateTravels
    class Meta:
        model = Travel
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination', 'lastUpdateTravels','customervoted','drivervoted')


#Este serializer devuelve solo el perfil del Customer
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity', 'fDistance')


class CustomerCountryStateCitySerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField('get_countries')
    states = serializers.SerializerMethodField('get_states')
    cities = serializers.SerializerMethodField('get_cities')
    def get_countries(self, obj):
        return CountrySerializer(Country.objects.all().order_by('name'), many=True).data
    def get_states(self, obj):
        if obj.city == None:
            return ""
        else:
            return StateSerializer(obj.city.state.country.state_set.all().order_by('name'), many=True).data
    def get_cities(self, obj):
        if obj.city == None:
            return ""
        else:
            return CitySerializer(obj.city.state.city_set.all().order_by('name'), many=True).data
    class Meta:
        model = Customer
        fields = ('countries', 'states', 'cities', 'id', 'email', 'phone', 'first_name', 'last_name', 'postcode', 'image')

class DriverCountryStateCitySerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField('get_countries')
    states = serializers.SerializerMethodField('get_states')
    cities = serializers.SerializerMethodField('get_cities')
    def get_countries(self, obj):
        return CountrySerializer(Country.objects.all().order_by('name'), many=True).data
    def get_states(self, obj):
        if obj.city == None:
            return ""
        else:
            return StateSerializer(obj.city.state.country.state_set.all().order_by('name'), many=True).data
    def get_cities(self, obj):
        if obj.city == None:
            return ""
        else:
            return CitySerializer(obj.city.state.city_set.all().order_by('name'), many=True).data
    class Meta:
        model = Driver
        fields = ('countries', 'states', 'cities', 'id', 'email', 'phone', 'first_name', 'last_name', 'postcode', 'image', 'license', 'address')

class TravelSerializerDriver(serializers.ModelSerializer):
    customer= CustomerProfileSerializer()
    class Meta:
        model = Travel
        fields = ('id', 'customer', 'starttime', 'endtime', 'cost',  'origin',  'destination')