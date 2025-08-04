from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from ..serializers import RegisterSerializer

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user details"""
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'has_profile': hasattr(user, 'profile')
        })
        
    def update(self, request):
        """Update user details"""
        user = request.user
        allowed_fields = ['first_name', 'last_name', 'email'] 
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                
        user.save()
        return Response({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })