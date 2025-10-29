from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        BASE_URL = 'http://localhost:8000'
        self.test_email = 'test@example.com'
        self.test_password = 'testpass123'
    
    def test_user_registration(self):
        url = '/auth/registration/'
        data = {
            'email': self.test_email,
            'password': self.test_password   
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.test_email).exists())
        user = User.objects.get(email=self.test_email)
        self.assertTrue(user.check_password(self.test_password))
        
    def test_user_registration_duplicate_email(self):
        User.objects.create_user(
            username='testuser1',
            email=self.test_email,
            password=self.test_password
        )
        url = '/auth/registration/'
        data = {
            'email': self.test_email,
            'password': 'differentpassword123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT])
        
    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            email=self.test_email,
            password=self.test_password
        )
        url = '/auth/login/'
        data = {
            'email': self.test_email,
            'password': self.test_password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_user_login_invalid_password(self):
        user=User.objects.create_user(
            username='testuser',
            email=self.test_email,
            password=self.test_password
        )
        url = '/auth/login/'
        data = {
            'email': self.test_email,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
        
    def test_user_login_nonexistent_email(self):
        url = '/auth/login/'
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
        
    def test_get_user_details_authenticated(self):
        user = User.objects.create_user(
            username='testuser',
            email=self.test_email,
            password=self.test_password
        )
        url = '/auth/login/'
        data = {
            'email': self.test_email,
            'password': self.test_password
        }
        login_response = self.client.post(url, data, format='json')
        
        if login_response.status_code == status.HTTP_200_OK:
            login_data = login_response.json()
            access_token = login_data.get('access')
            if access_token:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            else:
                self.fail(f"No access token found in response: {login_data}")
        else:
            self.fail(f"Login failed with status {login_response.status_code}: {login_response.content}")
                
        details_url = '/user/details/'
        details_response = self.client.get(details_url)
        
        self.assertEqual(details_response.status_code, status.HTTP_200_OK)
        details_data = details_response.json()
        self.assertEqual(details_data['email'], self.test_email)
        self.assertEqual(details_data['id'], user.id)
            
    def test_get_user_details_unauthenticated(self):
        url = '/user/details/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)