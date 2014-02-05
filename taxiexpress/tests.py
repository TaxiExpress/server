"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class IndexViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

class MapViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/map/')
        self.assertEqual(resp.status_code, 200)

class ClientViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/client/')
        self.assertEqual(resp.status_code, 200)

class DriverViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/driver/')
        self.assertEqual(resp.status_code, 200)

class FaqViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/faq/')
        self.assertEqual(resp.status_code, 200)

class LegalnoticeViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/legalnotice/')
        self.assertEqual(resp.status_code, 200)

class RegisterViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/register/')
        self.assertEqual(resp.status_code, 200)

class MantClientDataViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantclient_data/')
        self.assertEqual(resp.status_code, 302)

class MantClientChangePassViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantclient_changepassword/')
        self.assertEqual(resp.status_code, 302)

class MantClientPreferencesViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantclient_preferences/')
        self.assertEqual(resp.status_code, 302)

class MantClientTravelsViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantclient_travels/')
        self.assertEqual(resp.status_code, 302)

class MantDriverDataViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_data/')
        self.assertEqual(resp.status_code, 302)

class MantDriverChangePassViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_changepassword/')
        self.assertEqual(resp.status_code, 302)

class MantDriverCarViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_car/')
        self.assertEqual(resp.status_code, 302)

class MantDriverBankViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_bankaccount/')
        self.assertEqual(resp.status_code, 302)

class MantDriverTravelGrapiewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_travelgraphic/')
        self.assertEqual(resp.status_code, 302)

class MantDriverTravelsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/mantdriver_travels/')
        self.assertEqual(resp.status_code, 302)


class TermsofuseViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/termsofuse/')
        self.assertEqual(resp.status_code, 200)

class ContactViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/contact/')
        self.assertEqual(resp.status_code, 200)

class ValidateCodeViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/validatecode/')
        self.assertEqual(resp.status_code, 302)      

class LogoutViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/logout/')
        self.assertEqual(resp.status_code, 302)   

class UpdProfUserViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.post('/updateprofileuserweb/')
        self.assertEqual(resp.status_code, 401)

class UpdProfDriverViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.post('/updateprofiledriverweb/')
        self.assertEqual(resp.status_code, 401)

class UpdCarViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/updatecarweb/')
        self.assertEqual(resp.status_code, 401)

class RecoverValCodeViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/recovervalidationcode/')
        self.assertEqual(resp.status_code, 302)        

class RecoverValCodeViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/recovervalidationcode/')
        self.assertEqual(resp.status_code, 302)   

class GetCountriesViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/getcountries/')
        self.assertEqual(resp.status_code, 200)  

class GetStatesViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/getstates/')
        self.assertEqual(resp.status_code, 401)  

class GetCitiesViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/getcities/')
        self.assertEqual(resp.status_code, 401)  

class RememberPassViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/rememberpassword/')
        self.assertEqual(resp.status_code, 200) 

class TravelByMonthViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/statistics/gettravelsbymonth/')
        self.assertEqual(resp.status_code, 302)    

class TravelByLastYearViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/statistics/gettravelsbylastyear/')
        self.assertEqual(resp.status_code, 302) 

class TravelByLastMonthViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/statistics/gettravelsbylastmonth/')
        self.assertEqual(resp.status_code, 302) 

class TravelByDayViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/statistics/gettravelsbyday/')
        self.assertEqual(resp.status_code, 302)        

class TravelsCustomerViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/gettravelscustomer/')
        self.assertEqual(resp.status_code, 302)  

class TravelsDriverViewTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/gettravelsdriver/')
        self.assertEqual(resp.status_code, 302)

"""
TaxiExpress apps methods test classes
"""
    class ClientLoginViewTestCase(TestCase):
        def test_index(self):
            resp = self.client.get('/client/login/')
            self.assertEqual(resp.status_code, 200)

    class ClientRegisterViewTestCase(TestCase):
        def test_index(self):
            resp = self.client.get('/client/register')
            self.assertEqual(resp.status_code, 200)

