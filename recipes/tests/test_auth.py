from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
        
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
        self.asssertEqual(User.objects.filter(email=self.test_email).exists())
        user = User.objects.get(email=self.test_email)
        self.assertEqual(user.check_password(self.test_password))
        
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
            access_token = login_response.json().get('access_token')
            if access_token:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
                
        details_url = '/user/details/'
        details_response = self.client.get(details_url)
        
        self.assertEqual(details_response.status_code, status.HTTP_200_OK)
        self.assertEqual(details_response['email'], self.test_email)
        self.assertEqual(details_response['id'], user.id)
            
    def test_get_user_details_unauthenticated(self):
        url = '/user/details/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)