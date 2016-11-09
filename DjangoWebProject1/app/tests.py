"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from django.test import Client
from app.models import UserProfile
from app.models import Shed
from django.contrib.auth.models import User
from app.models import UserProfile
from app.models import Shed



# TODO: Configure your database in settings.py and sync before running tests.


class ViewTest(TestCase):
    """Tests for the application views."""

    # if django.VERSION[:2] >= (1, 7):
    #     # Django 1.7 requires an explicit setup() when running tests in PTVS
    #     @classmethod
    #     def setUpClass(cls):
    #         django.setup()

    # def test_home(self):
    #     """Tests the home page."""
    #     response = self.client.get('/')
    #     self.assertContains(response, 'Home Page', 1, 200)
    #
    # def test_contact(self):
    #     """Tests the contact page."""
    #     response = self.client.get('/contact')
    #     self.assertContains(response, 'Contact', 3, 200)
    #
    # def test_about(self):
    #     """Tests the about page."""
    #     response = self.client.get('/about')
    #     self.assertContains(response, 'About', 3, 200)

    def setUp(self):
        user = User.objects.create_user(first_name='Monty',
                                        last_name='Python',
                                        email='montypython@rit.edu',
                                        username='monty',
                                        password='python',
                                        )
        shed = Shed.objects.create(zipcode='14623',name='Rochester',address='1 Lamb memorial Dr.')

        user_profile = UserProfile.objects.create(address='Rochester Inst Of Techology',
                                                  gender='Male',
                                                  zipcode=shed,
                                                  user_id=user,
                                                  )

    def test_login_1(self):
        response = self.client.post('/login/', {'username': 'monty', 'password': 'python'})
        self.assertEquals(response.status_code, 302)

    def test_login_2(self):
        response = self.client.post('/login/', {'username': 'amit', 'password': 'aditya'})
        self.assertEquals(response.status_code, 200)

    def test_registration(self):
        response = self.client.post('/register/', data={'first_name': 'Monty',
                                                        'last_name': 'Python',
                                                        'address': 'RIT',
                                                        'zipcode': '14623',
                                                        'gender': 'Male',
                                                        'e-mail': 'monty@python.com',
                                                        'username': 'teammonty',
                                                        'password': 'python'}, follow=False)

        self.assertEqual(response.status_code, 302)

        # self.assertTemplateUsed('something.html')
        # self.assertRedirects(response, '/registerUser/')
        # response = self.client.post('/login/', {'username': 'teammonty', 'password': 'python'})
        # self.assertEqual(response.status_code, 302)

    def test_register_page(self):
        response = self.client.get('/registerUser/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertFalse('zipcode' in response.context)

    def test_register_page_user(self):
        response = self.client.post('/registerUser/',{'first_name':'Lumbardh','last_name':'Agaj','address':'Rochester',
                                                      'zipcode':'1452','gender':'Male','email':'lumbardh@mail.com','username':'lumbardh','password':'1234567'})
        self.assertEqual(response.status_code, 200)

        # Send no POST data.
        resp = self.client.post('/registerUser/')
        self.assertEqual(resp.status_code, 200)

        # Send junk POST data.
        resp = self.client.post('/registerUser/', {'foo': 'bar'})
        self.assertEqual(resp.status_code, 200)

class Register_tool(TestCase):

    def setUp(self):
        user_profile = UserProfile.objects.create(address='Rochester Inst Of Techology',
                                                  gender='Male',
                                                  zipcode=shed,
                                                  user_id=user,
                                                  )
    def test_register_tool(self):
        response = self.client.post('/registerTool',{'tool_name':'this tool','location':'Home','condition':'New',
                                                      'status':'Active','category':'Common use','special_instruction':'yaw dawg!',
                                                      'tool_owner_id':'user_profile','image':'C:\Users\kunalsetpal\Pictures','sharezone':'12344'})
        self.assertEqual(resp.status_code, 200)






