import requests
import datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.conf import settings
from helpers.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from accountstatement.serializers import DonorAccountStatementSerializer
from territories.models import Territories
from account.models import UserAccount

from django.db.models import Q
from accountstatement.models import AccountStatement, B2BAccountStatement
from accountstatement.serializers import AccountStatementSerializer, B2BAccountStatementSerializer

from organization.models import Organization
from labowner.models import Lab, SampleCollector

from staff.models import Staff
from staff.serializers import StaffSerializer
from django.db.models import F



# Create your views here.
class RegisterStaffView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    def post(self, request, *args, **kwargs):
        # Error handling to check if the id being passed account exists
        try:
            print("hellooo")
            account = UserAccount.objects.get(id=kwargs.get('id'))
            print("ac",account)
            print("id:",kwargs.get('id'))
            email_exists = UserAccount.objects.filter(email=request.data['email']).exists()
            print(email_exists, request.data['email'])

        # If the email exists then check the account type
            if email_exists:
                # account = UserAccount.objects.get(email=request.data['email'])
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your Email already exist. Please use new Email."})

            else:
                if account.username != 'admin':
                
                    staff_account = Staff.objects.filter(
                        account_id=account.id).count()
              


                    # Check if this account id is asssociated with any of the user and if so return error message
                    if  staff_account == 0 :
                        request.data._mutable = True
                        request.data['account_id'] = account.id
                        print("id2",kwargs.get('account_id'))
                        request.data['user_name'] = account.username
                        print(request.data['user_name'])
                        request.data['staff_type'] = account.account_type
                        request.data['registered_at'] = datetime.datetime.now()
                        request.data._mutable = False

                        staff_serializer = StaffSerializer(
                            data=request.data)

                        if staff_serializer.is_valid():
                            staff_serializer.save()
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
                            return Response({"status": status.HTTP_200_OK, "data": staff_serializer.data, "message": "Staff registered successfully."})
                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": staff_serializer.errors})

                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id already exists."})

                else:
                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Admin can't have other accounts."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such user account exist."})

    def put(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(id=kwargs.get('id'))

            serializer = StaffSerializer(
                staff, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})

    # Delete request to delete one cart item
    def delete(self, request, *args, **kwargs):
        # Here what we are passing as id from url is the cart item id
        try:
            # Get the item which is not checkedout yet through id to delete
            staff = Staff.objects.get(id=kwargs.get('id'))
            UserAccount.objects.get(id=staff.account_id.id).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Staff deleted successfully."})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such staff to delete."})


# API for showing and changing information of any staff
class StaffProfileView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Get request to get data of the staff
    def get(self, request, *args, **kwargs):
        staff_detail = {}
        try:
            staff = Staff.objects.get(account_id=kwargs.get('account_id'))
            serializer_class = StaffSerializer(staff, many=False)
            
    

            staff_detail.update(serializer_class.data)
            staff_detail['completed_audits'] = completed_audits
            staff_detail['inprocess_audits'] = inprocess_audits  
            return Response({"status": status.HTTP_200_OK, "data": staff_detail})
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! record doesn't exist."})
    # Patch request to update data of the staff information
    def put(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('account_id'))

            serializer = StaffSerializer(
                staff, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})


# API for displaying csr list

# CSR belong to Central office
class CSRCentralListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            csr_list = Staff.objects.filter(staff_type="CSR", territory_office="Central Office")
            serializer_class = StaffSerializer(
                csr_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No csr staff exist."})

# CSR belong to South office
class CSRSouthListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            csr_list = Staff.objects.filter(staff_type="CSR", territory_office="South Office")
            serializer_class = StaffSerializer(
                csr_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No csr staff exist."})

# CSR belong to North office
class CSRNorthListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            csr_list = Staff.objects.filter(staff_type="CSR", territory_office="North Office")
            serializer_class = StaffSerializer(
                csr_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No csr staff exist."})

class CSRListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get("id")
            organization = Organization.objects.get(account_id=id)
            organization_id = organization.id
            csr_list = Staff.objects.filter(organization_id=organization_id, staff_type="CSR")
            serializer_class = StaffSerializer(
                csr_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No csr staff exist."})


class FinanceOfficerListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            organization = Organization.objects.get(account_id=id)
            organization_id = organization.id
            finance_officer_list = Staff.objects.filter(organization_id=organization_id,
                staff_type="registration-admin")
            serializer_class = StaffSerializer(
                finance_officer_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No auditor staff exist."})


# API for displaying database admin list
class AuditorListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # Extract id from the URL
            id = kwargs.get('id')
            # Retrieve organization ID associated with the id
            organization = Organization.objects.get(account_id=id)
            organization_id = organization.id
            
            # Filter staff based on organization_id
            auditor_list = Staff.objects.filter(organization_id=organization_id, staff_type="database-admin")
            
            serializer_class = StaffSerializer(auditor_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Organization not found."})
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Database Admin staff exist for this organization."})

# API for displaying database admin list
class OrganizationListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            organization_list = Staff.objects.filter(staff_type="organization")
            serializer_class = StaffSerializer(
                organization_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No Organization data  exist."})

# API for displaying Central auditor list
class AuditorCentralListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            auditor_list = Staff.objects.filter(staff_type="auditor", territory_office="Central Office")
            serializer_class = StaffSerializer(
                auditor_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No Central Office auditor staff exist."})

# API for displaying South Office auditor list
class AuditorSouthListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            auditor_list = Staff.objects.filter(staff_type="auditor", territory_office="South Office")
            serializer_class = StaffSerializer(
                auditor_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No South Office auditor staff exist."})

# API for displaying North auditor list
class AuditorNorthListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to display list of pending audits
    def get(self, request, *args, **kwargs):
        try:
            auditor_list = Staff.objects.filter(staff_type="auditor", territory_office="North Office")
            serializer_class = StaffSerializer(
                auditor_list, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No north Office auditor staff exist."})



# API for displaying finance officer list

# API for storing information of a payment
class CSRAppointmentListView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

  # Put request to update data of sample collector status

class CommentsListView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)
    # Post request to store data of the sample collector


class CSRAdminAppointmentListView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)


 # Put request to update data of sample collector status



