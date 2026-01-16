from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView
from .serializers import ChangePasswordSerializer, LoginSerializer, RegistrationSerializer, UserSerializer
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
User = get_user_model()


class RegisterUserView(CreateAPIView):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User Registration Successful"
        }, status=status.HTTP_201_CREATED)


class LoginUserView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                "message": "login Successful",
                "user": UserSerializer(user).data,
            })
        return Response({
            "message": "Login Failed"
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(LoginRequiredMixin, UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Password Changed Successfully"
        })
