import jwt
from django.shortcuts import render
from rest_framework import generics, status, views
from .serializer import UserSerializer
from django.contrib.auth.models import User
from django.core.mail import send_mail
from jwtintegration.settings import EMAIL_HOST_USER
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from .task import email_send
# Create your views here.


class RegisterUser(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # def perform_create(self, serializer):
    #     serializer.save(is_active=False)

    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(is_active=False)
        user=User.objects.get(email=request.data['email'])
        # test_task.delay()
        refresh = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request)
        relative_url = reverse('token_verify')
        absolute_url = 'http://' + current_site.domain + relative_url +'?token=' + str(refresh)
        email_body = f'Hello {request.data.get("username")},\n\n'\
            f'Thank you for registering to our site.\n'\
            f'Please click on the link below to verify your email address   {absolute_url}.\n\n'\

        email_subject = 'Verify your email address'
        email_to = user.email

        email_send.delay(email_subject, email_body, EMAIL_HOST_USER,
                  [email_to])
        return Response({'message': 'User created successfully. Please check your email to verify your account'}, status=status.HTTP_201_CREATED)

class TokenVerifyViews(views.APIView):
    
    def get(self, request):
        token = request.GET.get('token')
        print('payload ' + str(settings.SECRET_KEY))
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            return Response({'error': 'Activations link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
