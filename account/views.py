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


# Redirect to admin


def redirect_to_admin_view(request):
    return redirect('/admin')

from rest_framework.response import Response

class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        # Check if the email entered by the user already exists
        user = UserAccount.objects.filter(username=request.data['username']).update(password_foradmins=request.data['password'])
        email_exists = UserAccount.objects.filter(
            username=request.data['username']).exists()
        # If the username exists then check the account type
        if email_exists:
            account = UserAccount.objects.get(username=request.data['username'])

            # Check if the record of that account exists in the respective user's table (patient/lab)
            # If not then it means user did not complete the registration so delete the record from account
            if request.data['account_type'] == "labowner":
                # account.password_foradmins=request.data['password']
                # account.save()
                print("user",request.data['password'], user)
                try:
                    lab = Lab.objects.get(account_id=account.id)
                    # user = UserAccount.objects.filter(id=lab.account_id).update(password_foradmins=request.data['password'])
                except:
                    account.delete()
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "error": "Your account registration was incomplete last time. If you want to re-register, click Next button. After completing the step 2 of registration, please ignore previous verification email sent to you and verify on new email you have received."})
            elif request.data['account_type'] == "CSR" or request.data['account_type'] == "auditor" or request.data['account_type'] == "finance-officer":
                try:
                    Staff.objects.get(account_id=account.id)
                except:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "error": "Did not Exist Your Email or Username."})

        if serializer.is_valid():
            serializer.save()

            user_data = serializer.data
            user = UserAccount.objects.get(username=request.data['username'])
            user1 = UserAccount.objects.filter(username=request.data['username']).update(password_foradmins=request.data['password'])
            print(user1)
            if request.data['account_type'] == "patient" or request.data['account_type'] == "samplecollector":
                user.is_active = 1
                user.password_foradmins = request.data['password']
                user.save()

                return Response(user_data, status=status.HTTP_201_CREATED)
            else:
                token, _ = Token.objects.get_or_create(user=user)
                print(token)
                return Response(user_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})


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
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your lab account is not approved by Lab Hazir. Please contact our customer care for further details."})
                    except:
                        UserAccount.objects.get(id=user_account.id).delete()
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})

                # if user_account.account_type == "patient":
                #     try:
                #         patient = Patient.objects.get(account_id=user_account.id)
                #         data['patient_name'] = patient.name
                #         data['employee_id_card'] = patient.employee_id_card
                #         data['is_associate_with_any_corporate'] = patient.is_assosiatewith_anycorporate
                        
                #         if data['employee_id_card']:
                #                 employee_data = EmployeeData.objects.get(employee_code=patient.employee_id_card)
                #                 print("employee data exists:", employee_data)
                #                 if employee_data and employee_data.status == "Inactive":
                #                     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your account is inactive by the Corporation."})

                #         if 'guest_id' in request.data and request.data['guest_id'] != "undefined":
                #             try:
                #                 cart = Cart.objects.filter(guest_id=request.data['guest_id']).update(patient_id=patient.id)
                #             except Cart.DoesNotExist:
                #                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No Cart against this guest id"})
                #     except Patient.DoesNotExist:
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Patient data not found."})

                # if user_account.account_type == "b2bclient":
                #     b2b_client = B2BClient.objects.get(
                #         account_id=user_account.id)
                #     try:
                #         b2b_client = B2BClient.objects.get(
                #             account_id=user_account.id)

                #         if b2b_client.is_blocked == "Yes":
                #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your b2b account is blocked by the admins. Please contact them for further details."})
                #         elif b2b_client.status == "Pending":
                #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your b2b account is pending for approval. Please contact admins for further details."})
                #         elif b2b_client.status == "Unapproved":
                #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your b2b account is not approved by Lab Hazir. Please contact our customer care for further details."})
                #     except:
                #         UserAccount.objects.get(id=user_account.id).delete()
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})

                # Registration of Sample Collector
                # if user_account.account_type == "samplecollector":
                #     try:
                #         sample_collector = SampleCollector.objects.get(
                #             account_id=user_account.id)
                #         data['sample_collector_name'] = sample_collector.name
                #     except:
                #         UserAccount.objects.get(id=user_account.id).delete()
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})

                # if user_account.account_type == "donor":
                #     try:
                #         donor = Donor.objects.get(
                #             account_id=user_account.id)
                #         if donor.is_blocked == "Yes":
                #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your account is blocked by the admins. Please contact them for further details."})
                #     except:
                #         UserAccount.objects.get(id=user_account.id).delete()
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})

                # if user_account.account_type == "marketer-admin":
                #     try:
                #         marketeradmin = Advertisement.objects.get(
                #             account_id=user_account.id)
                #         if marketeradmin.is_blocked == "Yes":
                #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your account is blocked by the admins. Please contact them for further details."})
                #     except:
                #         UserAccount.objects.get(id=user_account.id).delete()
                #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Your registration was not completed properly. Please register again."})
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
