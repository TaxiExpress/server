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
            if (obj.positiveVotes+obj.negativeVotes == 0):
                return 0
            else:
                return int(5*obj.positiveVotes/(obj.positiveVotes+obj.negativeVotes))
    class Meta:
        model = Driver
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'valuation', 'car', 'geom')

class TravelSerializer(serializers.ModelSerializer):
    driver= DriverSerializer()
    class Meta:
        model = Travel
        fields = ('id', 'driver', 'starttime', 'endtime', 'cost', 'startpoint', 'origin', 'endpoint', 'destination')


#Este serializer devuelve el perfil del Customer + taxistas favoritos + lista de viajes
class CustomerCompleteSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'favlist', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity', 'travel_set')

#Este serializer devuelve la lista de taxistas favoritos + lista de viajes
class CustomerTaxiesTravelsSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('favlist', 'travel_set')

#Este serializer devuelve la lista de viajes
class CustomerTravelsSerializer(serializers.ModelSerializer):
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('travel_set')

#Este serializer devuelve solo el perfil del Customer
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve el perfil del Customer + lista de taxistas
class CustomerProfileTaxiesSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('favlist','email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve el perfil del Customer + lista de viajes
class CustomerProfileTravels(serializers.ModelSerializer):
    travel_set = TravelSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('travel_set','email', 'phone', 'first_name', 'last_name', 'image', 'lastUpdate', 'fAccessible', 'fAnimals', 'fAppPayment', 'fCapacity')

#Este serializer devuelve solo la lista de taxistas favoritos
class CustomerTaxiesSerializer(serializers.ModelSerializer):
    favlist = DriverSerializer(many=True)
    class Meta:
        model = Customer
        fields = ('favlist')