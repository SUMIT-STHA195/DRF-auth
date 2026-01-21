
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView, GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_q.tasks import async_task

from .utils import generate_otp, send_otp_email
from .serializers import ChangePasswordSerializer, LoginSerializer, PasswordResetRequestSerializer, RegistrationSerializer, ResetPasswordVerifySerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging

# Create your views here.
User = get_user_model()

# Detail true false in decorators


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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # login(request, user) for session auth
        # for jwt token auth
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "login Successful",
            "tokens": {"refresh-token": str(refresh),
                       "access-token": str(refresh.access_token)
                       },
            "user": UserSerializer(user).data,
        })


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]  # ensures valid JWT is present

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Password Changed Successfully"
        })


class ResetPasswordRequest(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        validated_email = serializer.validated_data['email']
        otp = generate_otp(validated_email)
        print(f"OTP---------------{otp}")
        if otp:
            try:
                async_task(send_otp_email, otp, validated_email)
                # send_otp_email(otp, validated_email)
                return Response({
                    "message": f"otp sent to {validated_email}"
                })
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.exception(str(e))
                return Response({
                    "message": "Error sending mail"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"message": "Failed to generate OTP"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordVerify(UpdateAPIView):
    serializer_class = ResetPasswordVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Password Changed Successfully"
        })
