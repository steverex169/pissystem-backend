import imp
import datetime
import re
from ssl import CertificateError
from sys import audit

import shortuuid
import requests
from django.db.models import Max
from django.db.models import Min
from django.db.models import Avg
from django.db.models import Q
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from account.models import UserAccount
from django.urls import reverse
from accountstatement.serializers import AccountStatementSerializer
from financeofficer.models import PaymentIn
from financeofficer.serializers import PaymentInSerializer
from helpers.mail import send_mail
from labowner.models import FINANCIAL_SETTLEMENT, Result, ActivityLog, Lab, LabCorporate, OfferedTest, Pathologist, SampleCollector


# from medicaltest.models import Test, Unit
from labowner.serializers import ResultSerializer, ActivityLogSerializer, LabCorporateSerializer, LabInformationSerializer, LabPaymentSerializer, PathologistSerializer, SampleCollectorSerializer, OfferedTestSerializer
from django.conf import settings

from staff.models import Marketer, Staff
from staff.serializers import MarketerSerializer
from datetime import timedelta

from territories.models import Territories
from django.db.models import Count
from django.db.models import Q

# Create your views here.
# API for storing information of a lab
class LabInformationView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Post request to store data of the lab
    def post(self, request, format=None, *args, **kwargs):
        try:
            account = UserAccount.objects.get(id=kwargs.get('account_id'))
            print("idddddddddd",kwargs.get('account_id'), account.id)
            
            try: 
                email_exists = UserAccount.objects.filter(
                    email=request.data['email']).exists()
                print(email_exists, request.data['email'])
                # email_exists = UserAccount.objects.filter(email=request.data['email']).exclude(account_type='Lab').exists()
                print("lab type email exist", email_exists)

            # If the email exists then check the account type
                if email_exists:
                    print("vvvvvvvvv")
                    # account = UserAccount.objects.get(email=request.data['email'])
                    if account.username != 'admin':
                        
                        lab_account = Lab.objects.filter(
                            account_id=account.id).count()
                        
                        staff_account = Staff.objects.filter(
                            account_id=account.id).count()

                        # Check if this account id is associated with any of the user and if so return error message
                        if  lab_account == 0 and staff_account == 0:
                            request.data._mutable = True  # Make data mutable first
                            request.data['account_id'] = kwargs.get('account_id')
                            request.data['user_name'] = account.username
                        

                            # Remove hash sign if there is any in the address (Google Map API doesn't work if address has hash sign)
                            request.data['address'] = request.data['address']

                            # Set date of lab registration
                            request.data['registered_at'] = datetime.datetime.now()

                            # Check if the lab type is collection point

                            # Check if lab is registered by the marketer
                            if request.data['registered_by'] == 'Marketer':

                                # Check if marketer is registering any lab for the first time
                                if request.data['is_registering_for_first_time'] == 'Yes':
                                    marketer_data = {}
                                    marketer_data['name'] = request.data['marketer_name']
                                    marketer_data['cnic'] = request.data['marketer_cnic']
                                    marketer_data['email'] = request.data['marketer_email']
                                    marketer_data['phone'] = request.data['marketer_phone']
                                    marketer_data['city'] = request.data['marketer_city']
                                    marketer_data['district']= marketer_data['city']
                                    marketer_data['registered_at'] = datetime.datetime.now(
                                    )

                                    marketer_serializer_class = MarketerSerializer(
                                        data=marketer_data)

                                    # Check if incoming data of marketer is valid (i.e, email and cnic is unique)
                                    # Otherwise throw error of record already exists
                                    if marketer_serializer_class.is_valid():
                                        marketer_serializer_class.save()
                                    else:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Marketer record already exist."})

                                    # Get newly created marketer record to get id and link lab with that marketer
                                    try:
                                        marketer = Marketer.objects.get(
                                            email=request.data['marketer_email'])

                                        request.data['marketer_id'] = marketer.id

                                    except:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No markter record exists."})

                                # If marketer has not registered for the first time then
                                else:
                                    marketer_data = {}

                                    # Get marketer record through that email
                                    try:
                                        marketer = Marketer.objects.get(
                                            email=request.data['marketer_email'])

                                        # Increment the count and total count
                                        marketer_data['count'] = marketer.count + 1
                                        marketer_data['total_count'] = marketer.total_count + 1

                                        # Update the record of the marketer
                                        marketer_serializer_class = MarketerSerializer(
                                            marketer, data=marketer_data, partial=True)

                                        if marketer_serializer_class.is_valid():
                                            marketer_serializer_class.save()
                                        else:
                                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": marketer_serializer_class._errors})

                                        # Get marketer id and connect lab with the marketer
                                        request.data['marketer_id'] = marketer.id

                                    except:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No markter record exists."})

                            # All changes are done so immute data
                            request.data._mutable = False

                            lab_serializer_class = LabInformationSerializer(
                                data=request.data)
                            account = UserAccount.objects.get(account_type="registration-admin")
                            print(account.email)
                                # print(staff.name)
                            subject, from_email, to = 'Lab Approval', settings.EMAIL_HOST_USER, account.email
                            data = {
                                            'lab_name': request.data['name'],
                                        }

                            send_mail(subject, "lab-approval.html", from_email, to, data)

                            if lab_serializer_class.is_valid():
                                lab_serializer_class.save()
                                user = UserAccount.objects.get(username=request.data['user_name'])
                                user.email = request.data['email'] 
                                user.save()
                                print(user)
                                current_site = get_current_site(request).domain
                                relativeLink = reverse('email-verify')
                                print(current_site, relativeLink)

                                token, _ = Token.objects.get_or_create(user=user)
                                print(token)

                                absurl = 'http://' + current_site + \
                                    relativeLink + "?token=" + str(token)
                                print(absurl)

                                subject, from_email, to = 'Verify your Email', settings.EMAIL_HOST_USER, request.data['email']

                                data = {
                                    'user': user.username,
                                    'terms_conditions': 'http://' + current_site + "/media/public/labhazir_terms_conditions.pdf",
                                    'verification_link': absurl,
                                    'account_type': user.account_type,
                                }

                                send_mail(subject, "registration-mail.html", from_email, to, data)
                                return Response({"status": status.HTTP_200_OK, "data": lab_serializer_class.data, "message": "Lab information added successfully."})
                                    
                            else:
                                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": lab_serializer_class.errors})

                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id already exists."})

                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Admin can't have other accounts."})


                # Check if account id is of admin, if yes then return error message otherwise proceed
                else: 
                    print("pppppppppppppppp")
                    if account.username != 'admin':
                        lab_account = Lab.objects.filter(
                            account_id=account.id).count()                
                        print("lab acount", lab_account)

                        staff_account = Staff.objects.filter(
                            account_id=account.id).count()

                        # Check if this account id is associated with any of the user and if so return error message
                        if lab_account == 0 and staff_account == 0:
                            request.data._mutable = True  # Make data mutable first
                            request.data['account_id'] = kwargs.get('account_id')
                            request.data['user_name'] = account.username
                            print("lab acount id", kwargs.get('account_id'), account.username)
                        

                            # Remove hash sign if there is any in the address (Google Map API doesn't work if address has hash sign)
                            request.data['address'] = request.data['address']

                            # Set date of lab registration
                            request.data['registered_at'] = datetime.datetime.now()
                            print("lab acount id", request.data['address'], request.data['registered_at'])
                            # Check if the lab type is collection point
                            # If so then add logo, experience and ntn # from its main lab
                            
                            # Check if lab is registered by the marketer
                            if request.data['registered_by'] == 'Marketer':

                                # Check if marketer is registering any lab for the first time
                                if request.data['is_registering_for_first_time'] == 'Yes':
                                    marketer_data = {}
                                    marketer_data['name'] = request.data['marketer_name']
                                    marketer_data['cnic'] = request.data['marketer_cnic']
                                    marketer_data['email'] = request.data['marketer_email']
                                    marketer_data['phone'] = request.data['marketer_phone']
                                    marketer_data['city'] = request.data['marketer_city']
                                    marketer_data['district']= marketer_data['city']
                                    marketer_data['registered_at'] = datetime.datetime.now(
                                    )

                                    marketer_serializer_class = MarketerSerializer(
                                        data=marketer_data)

                                    # Check if incoming data of marketer is valid (i.e, email and cnic is unique)
                                    # Otherwise throw error of record already exists
                                    if marketer_serializer_class.is_valid():
                                        marketer_serializer_class.save()
                                    else:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Marketer record already exist."})

                                    # Get newly created marketer record to get id and link lab with that marketer
                                    try:
                                        marketer = Marketer.objects.get(
                                            email=request.data['marketer_email'])

                                        request.data['marketer_id'] = marketer.id

                                    except:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No markter record exists."})

                                # If marketer has not registered for the first time then
                                else:
                                    marketer_data = {}

                                    # Get marketer record through that email
                                    try:
                                        marketer = Marketer.objects.get(
                                            email=request.data['marketer_email'])

                                        # Increment the count and total count
                                        marketer_data['count'] = marketer.count + 1
                                        marketer_data['total_count'] = marketer.total_count + 1

                                        # Update the record of the marketer
                                        marketer_serializer_class = MarketerSerializer(
                                            marketer, data=marketer_data, partial=True)

                                        if marketer_serializer_class.is_valid():
                                            marketer_serializer_class.save()
                                        else:
                                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": marketer_serializer_class._errors})

                                        # Get marketer id and connect lab with the marketer
                                        request.data['marketer_id'] = marketer.id

                                    except:
                                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No markter record exists."})

                            # All changes are done so immute data
                            request.data._mutable = False

                            lab_serializer_class = LabInformationSerializer(
                                data=request.data)
                            # account = UserAccount.objects.get(account_type="registration-admin")
                            # print("accont email ",account.email)
                            #     # print(staff.name)
                            # subject, from_email, to = 'Lab Approval', settings.EMAIL_HOST_USER, account.email
                            # data = {
                            #                 'lab_name': request.data['name'],
                            #             }

                            # send_mail(subject, "lab-approval.html", from_email, to, data)

                            if lab_serializer_class.is_valid():
                                lab_serializer_class.save()
                                user = UserAccount.objects.get(username=request.data['user_name'])
                                user.email = request.data['email'] 
                                user.save()
                                print("aaaaaaaaaaaaaa",user)
                                current_site = get_current_site(request).domain
                                relativeLink = reverse('email-verify')
                                print("bbbbbbbbbbbbbbbb",current_site, relativeLink)

                                token, _ = Token.objects.get_or_create(user=user)
                                print("cccccccccccccccccccccc",token)

                                absurl = 'http://' + current_site + \
                                    relativeLink + "?token=" + str(token)
                                print("ddddddddddddddddd",absurl)

                                subject, from_email, to = 'Verify your Email', settings.EMAIL_HOST_USER, request.data['email']

                                data = {
                                    'user': user.username,
                                    'terms_conditions': 'http://' + current_site + "/media/public/labhazir_terms_conditions.pdf",
                                    'verification_link': absurl,
                                    'account_type': user.account_type,
                                }

                                send_mail(subject, "registration-mail.html", from_email, to, data)
                                return Response({"status": status.HTTP_200_OK, "data": lab_serializer_class.data, "message": "Lab information added successfully."})
                                    
                            else:
                                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": lab_serializer_class.errors})

                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id already exists."})

                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Admin can't have other accounts."})
            except UserAccount.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "This email is already in use. Please use a different email."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this doesn't exist. Please create account first."})



# API for showing and changing information of a lab
class LabProfileView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Get request to get data of the lab
    def get(self, request, *args, **kwargs):
        lab_detail = {}
        try:
            lab = Lab.objects.get(account_id=kwargs.get('account_id'))
            serializer_class = LabInformationSerializer(lab, many=False)
           
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Lab record doesn't exist."})

    
    # Patch request to update data of the Lab information
    def put(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('account_id'))
            print(lab.account_id.id)

            request.data._mutable = True  # Make data mutable first
            if request.data['email']:
                email_exists = UserAccount.objects.exclude(id=lab.account_id.id).filter(email=request.data['email']).exists()
                if email_exists:
                    return Response({"message": "email error"})
                else:
                    print("emsilkcdkd", email_exists)
                    request.data['email'] = request.data['email']
                    print("account email", request.data['email'])
                    ad = UserAccount.objects.filter(id=lab.account_id.id).update(email=request.data['email'])
                    print("email in useraccount", ad)
            
            # Remove hash sign if there is any in the address (Google Map API doesn't work if address has hash sign)
            request.data['address'] = request.data['address']
            
            request.data._mutable = False  # All changes are done so immute data

            print(type(lab))
            serializer = LabInformationSerializer(lab, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})


# API for showing and changing information of a lab
class LabSettingsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Get request to get data of the lab
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))

            serializer_class = LabInformationSerializer(lab, many=False)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Lab record doesn't exist."})

    # Patch request to update data of the Lab information

    def put(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            print ("old lab experience:", lab.lab_experience)
            print ("lab rating:", lab.rating)
            max_experience = Lab.objects.aggregate(Max('lab_experience'))['lab_experience__max']
            print ("max lab experience",max_experience)
            # min_experience = Lab.objects.aggregate(Min('lab_experience'))['lab_experience__min']
            min_experience=0
            lab_experience = lab.lab_experience
            min_target_experience = 0
            max_target_experience = 1.0

            # lab_experience_scaling_factor = (max_target_experience - min_target_experience) / (max_experience - min_experience)
            # lab_experience_number_scaled = (lab_experience - min_experience) * lab_experience_scaling_factor + min_target_experience
            # lab.rating = lab_experience_number_scaled
            # For old lab experience
            print ("old lab rating", lab.rating)
            lab_experience_scaling_factor = (max_target_experience - min_target_experience) / (max_experience - min_experience)
            print ("old_lab_experience_scaling_factor",lab_experience_scaling_factor)
            lab_experience_number_scaled = (lab_experience - min_experience) * lab_experience_scaling_factor + min_target_experience
            lab.rating = lab.rating - lab_experience_number_scaled
            print ("old scaling value:", lab_experience_number_scaled)
            print("lab rating minus old experience", lab.rating)
            lab.save()

            request.data._mutable = True

            if request.data['health_dept_certified'] == "":
                request.data['registration_no'] = ''
                request.data['license_no'] = ''
                request.data['health_dept_certificate'] = ''

            if request.data['is_247_opened'] == "true":
                request.data['opening_time'] = '00:00:00'
                request.data['closing_time'] = '00:00:00'

            if not request.data['home_sampling_charges']:
                request.data['home_sampling_charges'] = 0

            if not request.data['state_sampling_charges']:
                request.data['state_sampling_charges'] = 0

            request.data._mutable = False

            serializer = LabInformationSerializer(
                        lab, data=request.data, partial=True)

            if serializer.is_valid():
                # Save lab information
                # with transaction.atomic():
                serializer.save()

                # Update lab rating after saving
                max_experience = Lab.objects.aggregate(Max('lab_experience'))['lab_experience__max']
                new_lab = Lab.objects.get(account_id=kwargs.get('id'))
                new_lab_experience = new_lab.lab_experience
                print ("new lab experience;", new_lab_experience)
                # lab_experience_scaling_factor = (max_target_experience - min_target_experience) / (max_experience - min_experience)
                # new_lab_experience_number_scaled = (new_lab_experience - min_experience) * lab_experience_scaling_factor + min_target_experience
                # print ("New scaling value:", new_lab_experience_number_scaled)
                # new_lab.rating = new_lab.rating + new_lab_experience_number_scaled
                # For new lab experience
                new_lab_experience_scaling_factor = (max_target_experience - min_target_experience) / (max_experience - min_experience)
                print ("new_lab_experience_scaling_factor",new_lab_experience_scaling_factor)
                new_lab_experience_number_scaled = (new_lab_experience - min_experience) * new_lab_experience_scaling_factor + min_target_experience
                new_lab.rating = new_lab.rating + new_lab_experience_number_scaled
                print ("New scaling value:", new_lab_experience_number_scaled)
                print("new lab rating after new experience:", new_lab.rating)
                new_lab.save()

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create an account first."})

# API for offered test list
class LabListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            labs = Lab.objects.filter(type = "Main Lab")
            serializer_class = LabInformationSerializer(
                labs, many=True)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# API for offered test list
class OfferedTestListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id)
                print(offered_test_list)
                date_today= datetime.datetime.now().date()
                for i in offered_test_list:
                    if i.end_date.date()<=date_today:
                            i.discount=0
                    if i.test_id.end_date.date()<=date_today:
                            i.test_id.discount=0
                    if i.end_date_by_labhazir.date()<=date_today:
                            i.discount_by_labhazir=0
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)

                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
                    serializer_class.data[i]['test_details'] = offered_test_list[i].test_id.test_details
                    serializer_class.data[i]['description_in_english'] = offered_test_list[i].test_id.description_in_english
                    serializer_class.data[i]['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
                    serializer_class.data[i]['sample_type'] = offered_test_list[i].sample_type
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['lab_logo'] = str(
                        offered_test_list[i].lab_id.logo)
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

class OfferedTestDiscountListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id, shared_percentage__gt=0, is_active="Yes")
                date_today= datetime.datetime.now().date()
                for i in offered_test_list:
                    if i.end_date.date()<=date_today:
                            i.discount=0
                    if i.test_id.end_date.date()<=date_today:
                            i.test_id.discount=0
                    if i.end_date_by_labhazir.date()<=date_today:
                            i.discount_by_labhazir=0
                print(offered_test_list)
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)

                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
                    # serializer_class.data[i]['discount_by_labhazir'] = offered_test_list[i].test_id.discount
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                    serializer_class.data[i]['lab_logo'] = str(
                        offered_test_list[i].lab_id.logo)
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# API for offered test list
class OfferedTestShareListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    # def get(self, request, *args, **kwargs):
    #     try:
    #         lab = Lab.objects.get(account_id=kwargs.get('id'))
    #         try:
    #             offered_test_list = OfferedTest.objects.filter(lab_id=lab.id, shared_percentage__gt=0, test_type="Test", is_active="Yes")            
    #             print(offered_test_list)   
    #             date_today= datetime.datetime.now().date()
    #             for i in offered_test_list:
    #                 if i.end_date.date()<=date_today:
    #                         i.discount=0
    #                 if i.test_id.end_date.date()<=date_today:
    #                         i.test_id.discount=0
    #                 if i.end_date_by_labhazir.date()<=date_today:
    #                         i.discount_by_labhazir=0
    #             serializer_class = OfferedTestSerializer(
    #                 offered_test_list, many=True)  
    #             for i in range(0, len(offered_test_list)):
    #                 serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
    #                 serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
    #                 serializer_class.data[i]['description_in_english'] = offered_test_list[i].test_id.description_in_english
    #                 serializer_class.data[i]['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
    #                 serializer_class.data[i]['sample_type'] = offered_test_list[i].test_id.sample_type
    #                 serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
    #                 serializer_class.data[i]['test_details'] = offered_test_list[i].test_id.test_details
    #                 serializer_class.data[i]['all_discount_by_labhazir'] = offered_test_list[i].test_id.discount
    #                 print("lab hazir discounts", serializer_class.data[i]['discount_by_labhazir'], offered_test_list[i].discount)
    #                 serializer_class.data[i]['lab_account_id'] = offered_test_list[i].lab_id.account_id.id
    #                 serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
    #                 serializer_class.data[i]['rating'] = offered_test_list[i].lab_id.rating
    #                 serializer_class.data[i]['lab_logo'] = str(
    #                     offered_test_list[i].lab_id.logo)
                
               
    #             # for i in offered_test_list:
    #             #     if i.end_date_by_labhazir<=date_today:
    #             #             i.discount_by_labhazir=0 
    #             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
    #         except OfferedTest.DoesNotExist:
    #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    #     except Lab.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

class CorporateOfferedTestShareListView(APIView):
    permission_classes = (AllowAny,)

class CorporateProfileShareListView(APIView):
    permission_classes = (AllowAny,)


class CorporatePackagesShareListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list

class CorporateRadiologysShareListView(APIView):
    permission_classes = (AllowAny,)



# API for offered test list
class OfferedProfileShareListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id, shared_percentage__gt=0, test_type="Profile", is_active="Yes")            
                print(offered_test_list)   
                date_today= datetime.datetime.now().date()
                for i in offered_test_list:
                    if i.end_date.date()<=date_today:
                            i.discount=0
                    if i.test_id.end_date.date()<=date_today:
                            i.test_id.discount=0
                    if i.end_date_by_labhazir.date()<=date_today:
                            i.discount_by_labhazir=0
            
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)  
                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
                    serializer_class.data[i]['description_in_english'] = offered_test_list[i].test_id.description_in_english
                    serializer_class.data[i]['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
                    serializer_class.data[i]['sample_type'] = offered_test_list[i].test_id.sample_type
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['test_details'] = offered_test_list[i].test_id.test_details
                    serializer_class.data[i]['all_discount_by_labhazir'] = offered_test_list[i].test_id.discount
                    print("lab hazir discounts", serializer_class.data[i]['discount_by_labhazir'])
                    serializer_class.data[i]['lab_account_id'] = offered_test_list[i].lab_id.account_id.id
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                    serializer_class.data[i]['rating'] = offered_test_list[i].lab_id.rating
                    serializer_class.data[i]['lab_logo'] = str(
                        offered_test_list[i].lab_id.logo)
                
               
                # for i in offered_test_list:
                #     if i.end_date_by_labhazir<=date_today:
                #             i.discount_by_labhazir=0 
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# API for offered test list
class OfferedPackageShareListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id, shared_percentage__gt=0, test_type="Package", is_active="Yes")            
                print(offered_test_list)   
                date_today= datetime.datetime.now().date()
                for i in offered_test_list:
                    if i.end_date<=date_today:
                            i.discount=0
            
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)  
                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
                    serializer_class.data[i]['description_in_english'] = offered_test_list[i].test_id.description_in_english
                    serializer_class.data[i]['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
                    serializer_class.data[i]['sample_type'] = offered_test_list[i].test_id.sample_type
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['test_details'] = offered_test_list[i].test_id.test_details
                    serializer_class.data[i]['all_discount_by_labhazir'] = offered_test_list[i].test_id.discount
                    print("lab hazir discounts", serializer_class.data[i]['discount_by_labhazir'])
                    serializer_class.data[i]['lab_account_id'] = offered_test_list[i].lab_id.account_id.id
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                    serializer_class.data[i]['rating'] = offered_test_list[i].lab_id.rating
                    serializer_class.data[i]['lab_logo'] = str(
                        offered_test_list[i].lab_id.logo)
                
               
                # for i in offered_test_list:
                #     if i.end_date_by_labhazir<=date_today:
                #             i.discount_by_labhazir=0 
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# API for offered test list
class OfferedRadiologyShareListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id, shared_percentage__gt=0, test_type="Radiology", is_active="Yes")            
                print(offered_test_list)   
                date_today= datetime.datetime.now().date()
                for i in offered_test_list:
                    if i.end_date<=date_today:
                            i.discount=0
            
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)  
                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_type'] = offered_test_list[i].test_id.type
                    serializer_class.data[i]['description_in_english'] = offered_test_list[i].test_id.description_in_english
                    serializer_class.data[i]['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
                    serializer_class.data[i]['sample_type'] = offered_test_list[i].test_id.sample_type
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['test_details'] = offered_test_list[i].test_id.test_details
                    serializer_class.data[i]['all_discount_by_labhazir'] = offered_test_list[i].test_id.discount
                    print("lab hazir discounts", serializer_class.data[i]['discount_by_labhazir'])
                    serializer_class.data[i]['lab_account_id'] = offered_test_list[i].lab_id.account_id.id
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                    serializer_class.data[i]['rating'] = offered_test_list[i].lab_id.rating
                    serializer_class.data[i]['lab_logo'] = str(
                        offered_test_list[i].lab_id.logo)
                
               
                # for i in offered_test_list:
                #     if i.end_date_by_labhazir<=date_today:
                #             i.discount_by_labhazir=0 
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# API for storing information of a offered tests
class OfferedTestView(APIView):
    permission_classes = (AllowAny, )

    # Get request to get data of the offered test
    def get(self, request, *args, **kwargs):
        try:
            offered_test = OfferedTest.objects.get(id=kwargs.get('id'))
            serializer_class = OfferedTestSerializer(offered_test, many=False)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such offered test exists for this lab."})

# Post request to store data of the offered test
    # def post(self, request, *args, **kwargs):
    #     try:
    #         # Here what we are getting as id from header is the user account id
    #         lab = Lab.objects.get(account_id=kwargs.get('id'))
    #         # Search test record through test id in Test table if doesn't exist throw exception
    #         try:
    #             test = Test.objects.get(id=request.data['test_id'])
    #             # Search unit record through unit id in Unit table if doesn't exist throw exception
    #             try:
    #                 # Check if offered test exist then, then return error message otherwise proceed
    #                 does_test_id_exist = OfferedTest.objects.filter(
    #                     test_id=request.data['test_id'], lab_id=lab.id).count()
    #                 if does_test_id_exist == 0:
    #                     request.data._mutable = True  # Make data mutable first
    #                     request.data['lab_id'] = lab.id
    #                     request.data['test_id'] = test.id
    #                     # print(test.id)
    #                     request.data['test_type'] = test.type
    #                     request.data['sample_type'] = test.sample_type
    #                     request.data['test_details'] = test.test_details
    #                     # request.data['description_in_english'] = test.description_in_english
    #                     # request.data['description_in_urdu'] = test.description_in_urdu
    #                     # request.data['unit_id'] = unit.id
    #                     request.data._mutable = False  # All changes are done so immute data

    #                     serializer_class = OfferedTestSerializer(
    #                         data=request.data)

    #                     if serializer_class.is_valid():
    #                         offered_test=serializer_class.save()
                            
    #                         # Make the request data mutable
    #                         request.data._mutable = True
    #                         if test.type == "Test":
    #                             lab.offered_tests= 1
    #                             lab.save()
    #                             print("done")
    #                         if test.type == "Profile":
    #                             lab.offered_profiles= 1
    #                             lab.save()
    #                             print("done")
    #                         if test.type == "Package":
    #                             lab.offered_packages = 1
    #                             lab.save()
    #                             print("done")
    #                         if test.type == "Radiology":
    #                             lab.offered_radiologies = 1
    #                             lab.save()
    #                             print("done")
    #                         # # Check if lab.offered_tests is 1
    #                         # if lab.offered_tests == 1:
    #                         #     # Filter OfferedTest objects with test_type "Test"
    #                         #     tests = OfferedTest.objects.filter(test_type="Test")
    #                         #     print("test", tests)
    #                         #     # Save all the filtered tests
    #                         #     for test in tests:
    #                         #         lab.offered_tests.add(test)
    #                         #     # Save the lab object after adding tests
    #                         #     lab.save()

    #                         # # Check if lab.offered_profiles is 1
    #                         # if lab.offered_profiles == 1:
    #                         #     # Filter OfferedTest objects with test_type "Profile"
    #                         #     profiles = OfferedTest.objects.filter(test_type="Profile")
    #                         #     print("test", profiles)
    #                         #     # Save all the filtered profiles
    #                         #     for profile in profiles:
    #                         #         lab.offered_profiles.add(profile)
    #                         #     # Save the lab object after adding profiles
    #                         #     lab.save()

    #                         # # Check if lab.offered_packages is 1
    #                         # if lab.offered_packages == 1:
    #                         #     # Filter OfferedTest objects with test_type "Package"
    #                         #     packages = OfferedTest.objects.filter(test_type="Package")
    #                         #     print("test", packages)
    #                         #     # Save all the filtered packages
    #                         #     for package in packages:
    #                         #         lab.offered_packages.add(package)
    #                         #     # Save the lab object after adding packages
    #                         #     lab.save()

    #                         # # Check if lab.offered_radiologies is 1
    #                         # if lab.offered_radiologies == 1:
    #                         #     # Filter OfferedTest objects with test_type "Radiology"
    #                         #     radiologies = OfferedTest.objects.filter(test_type="Radiology")
    #                         #     print("test", radiologies)
    #                         #     # Save all the filtered radiologies
    #                         #     for radiology in radiologies:
    #                         #         lab.offered_radiologies.add(radiology)
    #                         #     # Save the lab object after adding radiologies
    #                         #     lab.save()

    #                         # Make the request data immutable again
    #                         request.data._mutable = False
    #                         account = UserAccount.objects.get(account_type="registration-admin")
    #                         print(account.email)
    #                         # print(staff.name)
    #                         subject, from_email, to = 'Test Approval', settings.EMAIL_HOST_USER, account.email
    #                         data = {
    #                             'lab_name': lab.name,
    #                             'test_name': test.name,
    #                         }

    #                         send_mail(subject, "test-approval.html", from_email, to, data)
    #                         ActivityLog.objects.create(
    #                         offered_test_id=offered_test,
    #                         user_id=request.user.id,
    #                         actions= "Added"
    #                         )
    #                         try:
    #                             branches = Lab.objects.filter(main_lab_account_id=lab.account_id, main_lab_tests=True)
    #                             # print("Branches:", branches)
    #                             for branch in branches:
    #                                 request.data._mutable = True  # All changes are done so immute data
    #                                 request.data['lab_id'] = branch.id
    #                                 request.data._mutable = False
    #                                 branch_serializer = OfferedTestSerializer(data=request.data)
    #                                 if branch_serializer.is_valid():
    #                                     branch_serializer.save()
    #                             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Offered Test information added successfully."})
    #                         except:
    #                             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No branch exists."})
                                
    #                 #  return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Offered Test information added successfully."})
    #                     else:
    #                         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer_class.errors})

    #                 else:
    #                     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Test already exists."})

    #             except Unit.DoesNotExist:
    #                 return Response(
    #                     {"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such Unit exist in our database."})

    #         except Test.DoesNotExist:
    #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such Test exist in our database."})

    #     except Lab.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

    def put(self, request, *args, **kwargs):
        try:
            offered_test = OfferedTest.objects.get(id=kwargs.get('id'))
            serializer = OfferedTestSerializer(
                offered_test, data=request.data, partial=False)

            if serializer.is_valid():
                old_values = {field: getattr(offered_test, field) for field in serializer.fields}
                print("old",old_values)
                serializer.save()
                new_values = {field: getattr(offered_test, field) for field in serializer.fields}
                print("old",new_values)
                for field, value in serializer.data.items():
                    if field in ["price", "sample_type", "duration_required", "duration_type", "is_eqa_participation", "is_home_sampling_available", "is_test_performed", "is_active",] and old_values.get(field) != value:
                        ActivityLog.objects.create(
                            offered_test_id=offered_test, 
                            field_name=field, 
                            old_value=old_values.get(field), 
                            new_value=value,
                            user_id= request.user.id,
                            actions= "Updated"
                        )
                # Check if the lab has any branches
                branch_labs = Lab.objects.filter(main_lab_account_id=offered_test.lab_id.account_id.id)
                print(branch_labs)
                print(offered_test.test_id)
                if branch_labs:
                    for branch_lab in branch_labs:
                        print("branch_lab ", branch_lab, branch_lab.id)
                        # Get the offered test for the branch lab
                        #when we use get, we need serializer and only one item is updated, if item doesnt exist, it doesnt check 2nd item, so use filter
                        offered_test_branch = OfferedTest.objects.filter(lab_id=branch_lab.id, test_id=offered_test.test_id).update(price=request.data['price'])
                        print("hellooo",offered_test_branch)
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such test is being offered."})
    # Delete request to delete data of the offered tests
    def delete(self, request, *args, **kwargs):
        # try:
            offered_test = OfferedTest.objects.get(id=kwargs.get('id'))
            print(offered_test.test_id)
            print(offered_test.test_id.id)
            branch_labs = Lab.objects.filter(main_lab_account_id=offered_test.lab_id.account_id.id)
            print("branches",branch_labs)
            if branch_labs:
                for branch_lab in branch_labs:
                    print("branch_lab ", branch_lab, branch_lab.id)
                    try:
                        offered_test_branches = OfferedTest.objects.filter(lab_id=branch_lab.id, test_id=offered_test.test_id)
                        print("hellooo",offered_test_branches)
                        offered_test_branches.delete()
                    except OfferedTest.DoesNotExist:
                        return Response({"status": status.HTTP_200_OK, "message": "No such test exist in branch lab."})
            # activity_log = ActivityLog.objects.create(
            #     offered_test=offered_test, 
            #     field_name="All fields", 
            #     old_value="", 
            #     new_value="",
            #     user_id= offered_test.lab_id.id,
            #     actions="Deleted"
            # )
            # activity_log.save()
            offered_test.delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        # except OfferedTest.DoesNotExist:
        #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such test to delete."})

# API for sample collector
class SampleCollectorView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the lab
    def get(self, request, *args, **kwargs):
        try:
            sample_collector = SampleCollector.objects.get(id=kwargs.get('id'))
            serializer_class = SampleCollectorSerializer(
                sample_collector, many=False)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except SampleCollector.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such sample collector exist."})

    # Delete request to delete data of the sample collactor
    def delete(self, request, *args, **kwargs):
        try:
            SampleCollector.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except SampleCollector.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})

    # Put request to update data of the sample collactor
    def put(self, request, *args, **kwargs):
        try:
            # Here what we are getting as id is the id of offered test record to be updated
            sample_collector = SampleCollector.objects.get(id=kwargs.get('id'))

            serializer = SampleCollectorSerializer(
                sample_collector, data=request.data, partial=False)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Sample collector updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except SampleCollector.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

    # Post request to store data of the sample collector
    def post(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))

            request.data._mutable = True  # Make data mutable first
            request.data['lab_id'] = lab.id
            request.data._mutable = False  # Immute after making changes

            serializer_class = SampleCollectorSerializer(data=request.data)

            if serializer_class.is_valid():
                serializer_class.save()
                request.data._mutable = True
                lab.sample_collectors = 1
                lab.save()
                request.data._mutable = False
                if request.data['gender'] == "Female":
                    request.data._mutable = True
                    lab.female_collectors = "Yes"
                    lab.save()
                    request.data._mutable = False
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Sample Collector added successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer_class.errors})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab exists."})


# API for sample test list
class SampleCollectorListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('user_id'))
            try:
                sample_collector_list = SampleCollector.objects.filter(
                    lab_id=lab.id)

                serializer_class = SampleCollectorSerializer(
                    sample_collector_list, many=True)

                for i in range(0, len(sample_collector_list)):
                    serializer_class.data[i]['lab_name'] = sample_collector_list[i].lab_id.name

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except SampleCollector.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})


# # API for sample collector
# class QualityCertificateView(APIView):
#     permission_classes = (IsAuthenticated,)

#     # Get request to get data of the lab
#     def get(self, request, *args, **kwargs):
#         try:
#             quality_certificate = QualityCertificate.objects.get(
#                 id=kwargs.get('id'))
#             serializer_class = QualityCertificateSerializer(
#                 quality_certificate, many=False)
#             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

#         except QualityCertificate.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No record exist."})

#     def delete(self, request, *args, **kwargs):
#             certificate_id = kwargs.get('id')
#             try:
#                 certificate = QualityCertificate.objects.get(id=certificate_id)
#                 lab = certificate.lab_id  # Assuming lab is a ForeignKey in QualityCertificate

#                 # Store the previous lab rating
#                 previous_lab_rating = lab.rating

#                 certificate.delete()
#                 remaining_certificates = QualityCertificate.objects.filter(
#                 lab_id=lab,
#                 certificate_type=certificate.certificate_type
#                  )
#                 print ("remaining certificates:", remaining_certificates)
#                 if not remaining_certificates.exists():
#                 # If no certificates of this type exist, subtract 0.375 from the lab rating
#                     lab.rating = lab.rating - 0.125
#                     new_lab_rating = lab.rating
#                     lab.save()
#                 else:
#                      new_lab_rating = lab.rating

#                 return Response({
#                     "status": status.HTTP_200_OK,
#                     "message": "Deleted successfully",
#                     "previous_rating": previous_lab_rating,
#                     "new_rating": new_lab_rating
#                 })

#             except QualityCertificate.DoesNotExist:
#                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})
                
#         # Put request to update data of the sample collactor
#     def put(self, request, *args, **kwargs):
#         try:
#             # Here what we are getting as id is the id of offered test record to be updated
#             quality_certificate = QualityCertificate.objects.get(
#                 id=kwargs.get('id'))

#             serializer = QualityCertificateSerializer(
#                 quality_certificate, data=request.data, partial=False)

#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Quality certificate updated successfully."})
#             else:
#                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

#         except QualityCertificate.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

#     # Post request to store data of the sample collector
#     def post(self, request, *args, **kwargs):
#         try:
#             lab = Lab.objects.get(account_id=kwargs.get('id'))

#             request.data._mutable = True  # Make data mutable first
#             request.data['lab_id'] = lab.id
#             request.data._mutable = False  # Immute after making changes

#             serializer_class = QualityCertificateSerializer(data=request.data)

#             certificate_type = request.data['certificate_type']  # Adjust with your actual field for certificate_type
#             existing_certificate = QualityCertificate.objects.filter(
#                 lab_id=lab.id,
#                 certificate_type=certificate_type
#             ).exists()

#             # Always add the certificate
#             if serializer_class.is_valid():
#                 serializer_class.save()

#                 if not existing_certificate:
#                     current_lab_rating = lab.rating
#                     print ("current rating:", current_lab_rating)

#                     Certificate_rating = current_lab_rating + 0.125  # Update the rating with 0.125 if certificate is added
#                     lab.rating = Certificate_rating
#                     lab.save()

#                     # Print the lab rating for verification
#                     print("Lab's final rating after certificate added:", Certificate_rating)
                
#                 return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Certificate added successfully."})
#             else:
#                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer_class.errors})

#         except Lab.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab exists."})

# # API for quality certificate list
# class QualityCertificateListView(APIView):
#     permission_classes = (AllowAny,)

#     # Get request to get data of the Tests to get all of the test list
#     def get(self, request, *args, **kwargs):
#         try:
#             collection_point = Lab.objects.get(account_id=kwargs.get('user_id'))
#             if collection_point.main_lab_quality:
#                 main_lab = Lab.objects.get(account_id=collection_point.main_lab_account_id)
#                 quality_certificate_list = QualityCertificate.objects.filter(lab_id=main_lab.id)
#             else:
#                 quality_certificate_list = QualityCertificate.objects.filter(lab_id=collection_point.id)

#             serializer_class = QualityCertificateSerializer(quality_certificate_list, many=True)
#             for i in range(len(quality_certificate_list)):
#                 serializer_class.data[i]['lab_name'] = quality_certificate_list[i].lab_id.name
#                 serializer_class.data[i]['expiry_date'] = quality_certificate_list[i].expiry_date
#                 print("expiry date", quality_certificate_list[i].expiry_date)

#             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Quality Certificte added successfully."})
#         except Lab.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})


# API for sample collector
class PathologistView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the lab
    def get(self, request, *args, **kwargs):
        try:
            pathologist = Pathologist.objects.get(id=kwargs.get('id'))
            serializer_class = PathologistSerializer(
                pathologist, many=False)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except Pathologist.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such sample collector exist."})

    # Delete request to delete data of the sample collactor
    def delete(self, request, *args, **kwargs):
            try:
                pathologist_id = kwargs.get('id')
                lab = Lab.objects.get(pathologist__id=pathologist_id)

                Pathologist.objects.get(id=pathologist_id).delete()

                # Calculate the total remaining pathologists for the lab
                total_pathologists = Pathologist.objects.filter(lab_id=lab.id).count()

                # Update lab rating logic
                current_lab_rating = lab.rating
                if total_pathologists >= 5:
                    lab.rating = current_lab_rating  # Leave rating unchanged
                elif total_pathologists < 5:
                    lab.rating = current_lab_rating - 0.2  # Subtract 0.2 from the current rating
                lab.save()

                return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

            except Pathologist.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})
            except Lab.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab exists."})
    # Put request to update data of the sample collactor
    def put(self, request, *args, **kwargs):
        try:
            # Here what we are getting as id is the id of offered test record to be updated
            pathologist = Pathologist.objects.get(id=kwargs.get('id'))

            serializer = PathologistSerializer(
                pathologist, data=request.data, partial=False)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Sample collector updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Pathologist.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

    # Post request to store data of the sample collector
    def post(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))

            request.data._mutable = True  # Make data mutable first
            request.data['lab_id'] = lab.id
            request.data._mutable = False  # Immute after making changes

            serializer_class = PathologistSerializer(data=request.data)

            if serializer_class.is_valid():
                serializer_class.save()
                request.data._mutable = True
                lab.pathologist = 1
                lab.save()
                # request.data._mutable = False

                # total_pathologists = lab.pathologists

                request.data._mutable = False
                total_pathologists = Pathologist.objects.filter(lab_id=lab.id).count()


                current_lab_rating = lab.rating
                print("lab pathologists:", total_pathologists)

                # Update lab rating logic
                if total_pathologists == 5:
                    lab.rating = current_lab_rating + 1
                elif total_pathologists < 5:
                    lab.rating = current_lab_rating + 0.2
                lab.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "pathologist Collector added successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer_class.errors})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab exists."})

# API for sample test list
class PathologistListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('user_id'))
            try:
                pathologist_list = Pathologist.objects.filter(
                    lab_id=lab.id)

                serializer_class = PathologistSerializer(
                    pathologist_list, many=True)
                
                for i in range(0, len(pathologist_list)):
                    serializer_class.data[i]['lab_name'] = pathologist_list[i].lab_id.name

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except Pathologist.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})


class TestAppointmentsCollectionPointView(APIView):
    permission_classes = (AllowAny, )
            # Post request to store data of the offered test
    def post(self, request, *args, **kwargs):
        try:
            # Here what we are getting as id from header is the user account id
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            # print("lab id", lab)
            # Search test record through test id in Test table if doesn't exist throw exception
            request.data._mutable = True
            if request.data['main_lab_appointments']:
                print("getting frontend lab appointment type", request.data['main_lab_appointments'])
                # ActivityLog.objects.create(
                #     user_id= request.user.id,
                #     actions= "Synchronize"
                # )
                # main_lab_id=lab.main_lab_account_id.lab.id
                # lab2=Lab.objects.filter(id=main_lab_id)
                lab2=Lab.objects.filter(id=lab.id).update(main_lab_appointments=request.data['main_lab_appointments'])
                print("hellooo update in lab field or not",lab2)
            return Response({"status": status.HTTP_200_OK, "message": "Lab updated successfully."})
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})
        
        
class QualityCertificateCollectionPointView(APIView):
    permission_classes = (AllowAny, )
            # Post request to store data of the offered test
    def post(self, request, *args, **kwargs):
        try:
            # Here what we are getting as id from header is the user account id
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            # print("lab id", lab)
            # Search test record through test id in Test table if doesn't exist throw exception
            request.data._mutable = True
            if request.data['main_lab_quality']== "Yes":
                print("lab main quality", request.data['main_lab_quality'])
                ActivityLog.objects.create(
                    user_id= request.user.id,
                    actions= "Synchronize"
                )
                # main_lab_id=lab.main_lab_account_id.lab.id
                # lab2=Lab.objects.filter(id=main_lab_id)
                lab2=Lab.objects.filter(id=lab.id).update(main_lab_quality=True)
                print("using quality update main lab quality",lab2)
            return Response({"status": status.HTTP_200_OK, "message": "Lab updated successfully."})
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

# --------------------- Test Appointment List APIs ---------------------
class TestAppointmentCompletedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list

class TestAppointmentInProcessListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list

# API of for getting the List of Invoices of all patients of that lab
class InvoiceView(APIView):
    permission_classes = (AllowAny,)


# API for feedback of patient


class FeedbackListView(APIView):
    permission_classes = (AllowAny,)


class discountOfferedTestListView(APIView):
    permission_classes = (AllowAny,)

    # def get(self, request, *args, **kwargs):
    #     try:
    #         lab = Lab.objects.get(id=kwargs.get('id'))

    #         try:
    #             offered_test_list = OfferedTest.objects.filter(lab_id=lab.id)
    #             date_today= datetime.datetime.now().date()

    #             for i in offered_test_list:
    #                 print (i.end_date)
    #                 if i.end_date==date_today:
    #                     i.discount=0
    #             serializer_class = OfferedTestSerializer(
    #                 offered_test_list, many=True)

    #             for i in range(0, len(offered_test_list)):
    #                 serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
    #                 # serializer_class.data[i]['unit_name'] = offered_test_list[i].unit_id.name
    #             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
    #         except OfferedTest.DoesNotExist:
    #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        # except Lab.DoesNotExist:
        #     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(id=kwargs.get('id'))
            try:
                offered_test_list = OfferedTest.objects.filter(lab_id=lab.id)
                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)

                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    # serializer_class.data[i]['unit_name'] = offered_test_list[i].unit_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})


    def put(self, request, *args, **kwargs):
        try:
            discount_test = OfferedTest.objects.get(id=kwargs.get('id'))
            serializer = OfferedTestSerializer(discount_test, data=request.data, partial=True)

            if serializer.is_valid():
                old_discount_by_lab = {field: getattr(discount_test, field) for field in serializer.fields}
                serializer.save()
                new_discount_by_lab = {field: getattr(discount_test, field) for field in serializer.fields}

                # Update ActivityLog for the discount field
                if old_discount_by_lab.get("discount") != new_discount_by_lab.get("discount"):
                    ActivityLog.objects.create(
                        offered_test_id=discount_test,
                        field_name="discount_by_lab",
                        old_discount_by_lab=old_discount_by_lab.get("discount"),
                        new_discount_by_lab=new_discount_by_lab.get("discount"),
                        start_date_by_lab=request.data['start_date'],
                        end_date_by_lab=request.data['end_date'],
                        user_id=request.user.id,
                        actions="Updated"
                    )

                print(serializer.data)
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Information updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})
# This code checks if the "discount" field has been changed and, if so, updates the ActivityLog accordingly. The rest of the logic remains the same as your existing put method.


class discountAllOfferedTestView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        lab = Lab.objects.get(account_id=kwargs.get('id'))

        try:
            # Use filter instead of get
            discount_tests = OfferedTest.objects.filter(lab_id=lab.id)

            if not discount_tests.exists():
                raise OfferedTest.DoesNotExist

            # Assuming you want to update all matching records
            for discount_test in discount_tests:
                old_discount_by_lab = discount_test.discount

                # Update OfferedTest fields
                discount_test.discount = request.data['discount']
                discount_test.start_date = request.data['start_date']
                discount_test.end_date = request.data['end_date']
                discount_test.save()

            # Create one ActivityLog record for the entire update
            ActivityLog.objects.create(
                # lab_id=lab,
                field_name="Discount_For_All_Tests",
                old_discount_by_lab=old_discount_by_lab,
                new_discount_by_lab=request.data['discount'],
                start_date_by_lab=request.data['start_date'],
                end_date_by_lab=request.data['end_date'],
                user_id=request.user.id,
                actions="Updated"
            )

            return Response({"status": status.HTTP_200_OK, "message": "All Test Discounts updated successfully."})
        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

# API for adding donor in payment and creating account statement
class LabPaymentView(APIView):
    permission_classes = (AllowAny,)

    # Post request for donor in payment
    def post(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))

            # Set some values for Lab Payment in API itself
            request.data._mutable = True
            request.data['lab_id'] = lab.id
            request.data['invoice_id'] = shortuuid.ShortUUID(
                alphabet="0123456789").random(length=5)

            # Set paid at time as now when the payment method is Card
            if request.data['payment_method'] == "Card":
                request.data['payment_status'] == "Paid"
                request.data['paid_at'] = datetime.datetime.now()
                

            request.data._mutable = False

            lab_payment_serializer = LabPaymentSerializer(
                data=request.data)

            if lab_payment_serializer.is_valid():
                lab_payment_serializer.save()

                # Lab payment is successfully created so we need to create lab account statement
                request.data._mutable = True

                request.data['lab_id'] = lab.id
                request.data['lab_payment_id'] = str(
                    lab_payment_serializer.data['id'])
                request.data['transaction_type'] = "In"
                request.data['generated_at'] = datetime.datetime.now()

                # Set transaction completed in case of Card
                if request.data['payment_method'] == "Card":
                    request.data['is_transaction_completed'] = 1

                request.data._mutable = False

                lab_statement_serializer = AccountStatementSerializer(
                    data=request.data)

                if lab_statement_serializer.is_valid():
                    lab_statement_serializer.save()
                    return Response({"status": status.HTTP_200_OK, "payment_data": lab_payment_serializer.data, "lab_statement_serializer": lab_statement_serializer.data, "message": "Lab payment added successfully and account statement created."})

                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": lab_statement_serializer.errors})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No record exists."})

# Advertisement Request from Lab to Marketer Admin

class LabAdvertisementListView(APIView):
    permission_classes = (AllowAny,)


# Get the Invoice of the Advertisement of lab 
class LabAdvertisementInvoiceView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the lab

class OfferedTestCollectionPointView(APIView):
    permission_classes = (AllowAny, )
            # Post request to store data of the offered test
    # def post(self, request, *args, **kwargs):
    #     try:
    #         # Here what we are getting as id from header is the user account id
    #         lab = Lab.objects.get(account_id=kwargs.get('id'))
    #         # Search test record through test id in Test table if doesn't exist throw exception
    #         request.data._mutable = True
    #         if request.data['main_lab_tests']== "Yes":
    #             ActivityLog.objects.create(
    #                 user_id= request.user.id,
    #                 actions= "Synchronize"
    #             )
    #             main_lab_id=lab.main_lab_account_id.lab.id
    #             # lab2=Lab.objects.filter(id=main_lab_id)
    #             Lab.objects.filter(id=lab.id).update(main_lab_tests=True)
    #             # print("hellooo",main_lab_id)
    #             try:
    #                 offeredtest = OfferedTest.objects.filter(
    #                 lab_id=main_lab_id)
    #                 for i in offeredtest:
    #                     try:
    #                         request.data['test_id'] = i.test_id.id
    #                         request.data['lab_id']= lab.id
    #                         request.data['end_date']= i.end_date
    #                         request.data['end_date_by_labhazir']= i.end_date_by_labhazir
    #                         request.data['test_details']= i.test_details
    #                         request.data['test_type']= i.test_type
    #                         request.data['duration_required']= i.duration_required
    #                         request.data['duration_type']= i.duration_type
    #                         request.data['price']= i.price
    #                         request.data['shared_percentage']= i.shared_percentage
    #                         print("percentage is", request.data['shared_percentage'])
    #                         request.data['sample_type']= i.sample_type
    #                         request.data['is_eqa_participation']= i.is_eqa_participation
    #                         request.data['is_home_sampling_available']= i.is_home_sampling_available
    #                         request.data['is_test_performed']= i.is_test_performed
    #                         if i.shared_percentage > 0:
    #                             i.status = 'Approved'
    #                             i.save()
    #                             print("status update or no", i.status)
    #                         else:
    #                             request.data['status'] = i.status
    #                     except Test.DoesNotExist:
    #                         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such Test exist in our database."})
    #                     serializer_class = OfferedTestSerializer(
    #                                     data=request.data)
    #                     # print(serializer_class)
    #                     if serializer_class.is_valid():
    #                         serializer_class.save()
    #                 request.data._mutable = False
    #                 return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
    #             except:            
    #                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No tests are added by main lab"})
    #     except Lab.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})
        
# class OfferedTestCollectionPointView(APIView):
#     permission_classes = (AllowAny, )

#     # Post request to store data of the offered test
#     def post(self, request, *args, **kwargs):
#         try:
#             # Here what we are getting as id from header is the user account id
#             lab = Lab.objects.get(account_id=kwargs.get('id'))
#             # Search test record through test id in Test table if doesn't exist throw exception
#             request.data._mutable = True
#             if request.data['main_lab_tests']== "Yes":
#                 main_lab_id=lab.main_lab_account_id.id
#                 print(main_lab_id)
#                 offeredtest = OfferedTest.objects.filter(
#                 lab_id=main_lab_id)
#                 print("gyyuu",offeredtest) 
#                 for i in offeredtest:
#                     try:
#                         request.data['test_id'] = i.test_id.id
#                         request.data['lab_id']= lab.id
#                         request.data['end_date']= i.end_date
#                         request.data['end_date_by_labhazir']= i.end_date_by_labhazir
#                         request.data['test_details']= i.test_details
#                         request.data['test_type']= i.test_type
#                         request.data['duration_required']= i.duration_required
#                         request.data['duration_type']= i.duration_type
#                         request.data['price']= i.price
#                         request.data['sample_type']= i.sample_type
#                         request.data['is_eqa_participation']= i.is_eqa_participation
#                         request.data['is_home_sampling_available']= i.is_home_sampling_available
#                         request.data['is_test_performed']= i.is_test_performed
#                         request.data['description_in_english']= i.description_in_english
#                         request.data['description_in_urdu']= i.description_in_urdu
                       
                
#                     except Test.DoesNotExist:
#                         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such Test exist in our database."})
#                     serializer_class = OfferedTestSerializer(
#                                     data=request.data)
#                     print(serializer_class)
#                     if serializer_class.is_valid():
#                         serializer_class.save()
#                 request.data._mutable = False
#                 return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
#             else:
#                 return Response({"status": status.HTTP_200_OK, "message": "Hellooooo" })

#         except Lab.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

class ActivityLogView(APIView):
    permission_classes = (AllowAny, )

    # Get request to get data of the offered test
    def get(self, request, *args, **kwargs):
        try:
            lab=Lab.objects.get(account_id=kwargs.get('id'))
            print(lab.main_lab_account_id)
            if lab.type=="Collection Point":
                activity_log = ActivityLog.objects.filter(Q(user_id=kwargs.get('id')) | Q(user_id=lab.main_lab_account_id))
                serializer_class =  ActivityLogSerializer(activity_log, many=True)
            else:
                # activity_log = ActivityLog.objects.filter(user_id=kwargs.get('id'))
                # serializer_class =  ActivityLogSerializer(activity_log, many=True)
                branches = Lab.objects.filter(main_lab_account_id=kwargs.get('id'))
                print(branches)
                branch_ids = [branch.account_id for branch in branches]
                activity_log = ActivityLog.objects.filter(Q(user_id__in=branch_ids) | Q(user_id=kwargs.get('id')))
                serializer_class =  ActivityLogSerializer(activity_log, many=True)
            for i in range(0, len(activity_log)):
                serializer_class.data[i]['lab_name'] = activity_log[i].user.username
                if (activity_log[i].offered_test_id!= None):
                    serializer_class.data[i]['test_name'] = activity_log[i].offered_test_id.test_id.name            
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except ActivityLog.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No activity log exists for this lab."})



class LabNamesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            labs = Lab.objects.all()
            print(labs)
            serializer_class = LabInformationSerializer(
                labs, many=True)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})
        # try:
        #     profile_list = Test.objects.filter(type="Test")
        #     print(profile_list)
        #     serializer_class = MedicalTestSerializer(
        #         profile_list, many=True)
        #     return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        # except Test.DoesNotExist:
        #     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
# API for storing information of a payment
class CorporatListForLabView(APIView):
    permission_classes = (AllowAny,)
 
    
class ReffrellFeeCorporationsListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            labcorporate = LabCorporate.objects.filter(status="Accept")

            serializer_class = LabCorporateSerializer(labcorporate, many=True)
            for i in range(0, len(labcorporate)):
                serializer_class.data[i]['corporate_name'] = labcorporate[i].corporate_id.name
                serializer_class.data[i]['lab_name'] = labcorporate[i].lab_id.name
                serializer_class.data[i]['city'] = labcorporate[i].corporate_id.city
                serializer_class.data[i]['phone'] = labcorporate[i].corporate_id.phone
                serializer_class.data[i]['address'] = labcorporate[i].corporate_id.address
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Lab record doesn't exist."})
        

# class ManufacturalList(APIView):
#     permission_classes = (AllowAny,)

#     def get(self, request, *args, **kwargs):
#         try:
#             database = Manufactural.objects.all()

#             serializer = ManufacturalSerializer(database, many=True)
        
#             return Response({"status": status.HTTP_200_OK, "data": serializer.data})
#         except Manufactural.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! record doesn't exist."})
        
#     def post(self, request, *args, **kwargs):
#         serializer = ManufacturalSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"status": status.HTTP_201_CREATED, "data": serializer.data})
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForChartCalculationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        analyte_id = request.data.get('analyte_id')
        print("analyte id is", analyte_id)
        if analyte_id:
            # Retrieve TestAppointment instances where analyte_ids contains the analyte_id
            analyte_result = Result.objects.filter(analyte_id=analyte_id)
            print("appointmnets", analyte_result)

            # Check status of each TestAppointment instance
            for analyte in analyte_result:
                print("Lab ID:", analyte.lab_id, "- Result:", analyte.result, analyte.analyte)

            # Define all possible statuses
            possible_result = ["10", "20", "30", "40"]
            
            # Initialize data with all possible statuses set to zero
            data_dict = {result: 0 for result in possible_result}
            print("data result", data_dict)
            # Count appointments for each result
            for result_count in analyte_result.values_list('result', flat=True):
                if result_count in data_dict:
                    data_dict[result_count] += 1

            # Prepare the response data
            categories = list(data_dict.keys())
            data = list(data_dict.values())
            
            response_data = {
                'categories': categories,
                'data': data
            }

            return Response(response_data, status=status.HTTP_200_OK)