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
from labowner.models import Lab, SampleCollector
from staff.models import Marketer, Staff
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
from staff.models import Staff
from organization.models import Organization
from django.utils import timezone
from labowner.models import Lab
# Redirect to admin


def redirect_to_admin_view(request):
    return redirect('/admin')

from rest_framework.response import Response

class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        # Check if the serializer data is valid
        if serializer.is_valid():
            # Check if the email already exists in UserAccount table
            email_exists = UserAccount.objects.filter(email=request.data['email']).exists()
            if email_exists:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "error": "Email already exists."})
            # email_exists = UserAccount.objects.filter(email=request.data['email']).exists()
            # if email_exists:
            #     return Response({"status": status.HTTP_400_BAD_REQUEST, "error": "Email already exists."})

            # Proceed with saving the serializer data
            serializer.save()

            user_data = serializer.data
            user = UserAccount.objects.get(username=request.data['username'])
            

            # Update password_foradmins
            UserAccount.objects.filter(username=request.data['username']).update(password_foradmins=request.data['password'])
            # Participant registration
            if request.data['account_type'] == "labowner":
                user.email = request.data['email']
                user.save()
                # organization = Organization.objects.get(account_id = request.data['added_by'])
                staff = Staff.objects.get(account_id = request.data['added_by'])
                # Retrieve the organization associated with the staff user
                organization = staff.organization_id
                # print("emaillllll", request.data['email'], request.data['added_by'], organization)
                Lab.objects.create(
                    
                   account_id=user,
                    # organization_id=request.data['added_by'],
                    user_name=request.data['username'],
                    city=request.data['city'],
                    name=request.data['name'],
                    department=request.data['department'],
                    # organization_id = organization,
                    organization_id = organization,
                    staff_id = staff,
                    country=request.data['country'],
                    # address=request.data['address'],
                    district=request.data['district'],
                    # Select_schemes=request.data['Select_schemes'],
                    province = request.data['province'],
                    # state = request.data['state'],
                    billing_address = request.data['billing_address'],
                    shipping_address = request.data['shipping_address'],
                    email=request.data['email'],   
                    email_participant=request.data['email_participant'],
                    lab_staff_name=request.data['lab_staff_name'],
                    # lab_staff_designation=request.data['lab_staff_designation'],
                    landline_registered_by=request.data['landline_registered_by'],
                    website=request.data['website'],
                   
                )
            
            
           
            # Additional logic for creating Organization instance
            if request.data['account_type'] == "organization":
                user.email = request.data['email']
                user.save()
                print("djd emial", request.data['email'])
                Organization.objects.create(
                    account_id=user,
                    name=request.data['name'],
                    user_name=request.data['username'],
                    website=request.data['website'],
                    country=request.data['country'],
                    photo=request.data['logo'],
                    registered_at=datetime.datetime.now()
                )
             
            # Activate user and set password_foradmins for 'patient' or 'samplecollector' accounts
            if request.data['account_type'] == "database-admin" or request.data['account_type'] == "registration-admin" or request.data['account_type'] == "CSR":
                user.email = request.data['email']
                user.save()
                print("organization and user", user, request.data['added_by'])
                organization = Organization.objects.get(account_id=request.data['added_by'])
                print("organization and user", organization.id, user)
                Staff.objects.create(
                    account_id=user,
                    organization_id=organization,
                    name=request.data['name'],
                    cnic=request.data['cnic'],
                    photo=request.data['photo'],
                    user_name=request.data['username'],
                    email=request.data['email'],
                    staff_type=request.data['account_type'],
                    phone=request.data['phone'],
                    city=request.data['city'],
                    registered_at=datetime.datetime.now()

                )  
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
            else:
                # We need to apply limitations on lab's login if it is blocked by us or its approval is pending
                if user_account.account_type == "labowner":
                    try:
                        lab = Lab.objects.get(account_id=user_account.id)

                        data['lab_name'] = lab.name

                        if lab.is_blocked == "Yes":
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your lab is blocked by the admins. Please contact them for further details."})
                        elif lab.status == "Pending":
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your lab is pending for approval. Please contact admins for further details."})
                        elif lab.status == "Unapproved":
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your lab account is not approved by NHS NEQAS. Please contact our customer care for further details."})
                    except:
                        UserAccount.objects.get(id=user_account.id).delete()
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})

            
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
        # user.last_login_time = last_login_time
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