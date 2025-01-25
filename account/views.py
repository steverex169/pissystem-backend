from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import generics
from rest_framework import parsers
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from account.models import UserAccount
from django.shortcuts import redirect
from .serializers import RegisterSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from helpers.mail import send_mail
from datetime import datetime
import datetime
from django.contrib.auth.models import update_last_login
from organizationdata.models import Organization
from django.utils import timezone
# Redirect to admin


def redirect_to_admin_view(request):
    return redirect('/admin')

from rest_framework.response import Response

class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data
            user = UserAccount.objects.get(username=request.data['username'])
            UserAccount.objects.filter(username=request.data['username']).update(password_foradmins=request.data['password'])
            if request.data['account_type'] == "organization":
                user.save()
                Organization.objects.create(
                        account_id=user,
                    )
                user.is_active = True
                user.password_foradmins = request.data['password']
                user.save()
            # Activate user and set password_foradmins for 'patient' or 'samplecollector' accounts
            if request.data['account_type'] == "database-admin":
                user.save() 
                user.is_active = True
                user.password_foradmins = request.data['password']
                user.save()
                return Response(user_data, status=status.HTTP_201_CREATED)
            else:
                # Generate token for other account types
                token, _ = Token.objects.get_or_create(user=user)
                return Response(user_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

class VerifyEmail(APIView):
    def get(self, request, *args, **kwargs):
        token = Token.objects.get(key=request.GET.get('token'))

        # Activate the user account
        user = UserAccount.objects.get(id=token.user_id)
        user.is_active = 1
        user.save()

        return HttpResponseRedirect(redirect_to=settings.LINK_OF_REACT_APP + '/login')


# API for login user after verifying his credentials
class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    def post(self, request, *args, **kwargs):
        data = {}

        # Getting username in case if user enters email instead of username
        request.data._mutable = True  # Make data mutable first
        try:
            # Check if data entered by user in username field is email and if record exists then get username of that user
            user_account = UserAccount.objects.get(
                email=request.data['username'])
            request.data['username'] = user_account.username
        except:
            request.data['username'] = request.data['username']
        request.data._mutable = False  # All changes are done so immute data

        # Checks for Lab accounts login
        try:
            # Now that we have username in request.data we can search related user account using it
            user_account = UserAccount.objects.get(
                username=request.data['username'])

            if user_account.is_active == False:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your account is not verified. Please verify using the verification link sent on your email."})
           
        except:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No account found. Please provide correct Username or Register First."})

        # Send data to AuthTokenSerializer for validation
        serializer_class = self.serializer_class(
            data=request.data, context={'request': request})

        serializer_class.is_valid(raise_exception=True)

        user = serializer_class.validated_data['user']

        # If user is validated then create or get token for the user
        token, _ = Token.objects.get_or_create(user=user)
        token_dict = model_to_dict(token)
        update_last_login(None, token.user)
        # last_login = datetime.datetime.now()
        # print(last_login)


        # We need to return account type and token from API when status is 200
        data['user_id'] = user.id
        # data['last_login'] = user.last_login
        data['username'] = user.username
        data['is_active'] = user.is_active
        data['account_type'] = user.account_type
        data['token'] = token_dict['key']
        print("data", data)
        return Response({"status": status.HTTP_200_OK, "data": data})


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = UserAccount
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
