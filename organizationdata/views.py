from django.shortcuts import render
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
from organizationdata.models import Organization
from organizationdata.serializers import OrganizationSerializer
from account.models import UserAccount
from staff.models import Staff
from django.forms.models import model_to_dict

# Create your views here.
class RegisterOrganizationView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    def post(self, request, *args, **kwargs):
        # Error handling to check if the id being passed account exists
        try:
            account = UserAccount.objects.get(id=kwargs.get('id'))
            email_exists = UserAccount.objects.filter(email=request.data['email']).exists()
            print(email_exists, request.data['email'])

        # If the email exists then check the account type
            if email_exists:
                # account = UserAccount.objects.get(email=request.data['email'])
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Your Email already exist. Please use new Email."})

            else:
                if account.username != 'admin':
                
                    organization_account = Organization.objects.filter(
                        account_id=account.id).count()

                    # Check if this account id is asssociated with any of the user and if so return error message
                    if  organization_account == 0 :
                        request.data._mutable = True
                        request.data['account_id'] = account.id
                        print("id2",kwargs.get('account_id'))
                        request.data['user_name'] = account.username
                        print(request.data['user_name'])
                        request.data['staff_type'] = account.account_type
                        request.data['registered_at'] = datetime.datetime.now()
                        request.data._mutable = False
                        organization_serializer = OrganizationSerializer(
                            data=request.data)
                        if organization_serializer.is_valid():
                            organization_serializer.save()
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
                            return Response({"status": status.HTTP_200_OK, "data": organization_serializer.data, "message": "Organization registered successfully."})
                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": organization_serializer.errors})
                    else:
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id already exists."})
                else:
                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Admin can't have other accounts."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such user account exist."})

    def put(self, request, *args, **kwargs):
        try:
            organization = Organization.objects.get(id=kwargs.get('id'))

            serializer = OrganizationSerializer(
               organization, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})

    # Delete request to delete one cart item
    def delete(self, request, *args, **kwargs):
        # Here what we are passing as id from url is the cart item id
        try:
            # Get the item which is not checkedout yet through id to delete
            organization = Organization.objects.get(id=kwargs.get('id'))
            UserAccount.objects.get(id=organization.account_id.id).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Organization data  deleted successfully."})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Organization to delete."})
class OrganizationListView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            organization_list = Organization.objects.all()
            serialized_data = []
            
            for organization in organization_list:
                # Convert model instance to a dictionary
                organization_data = model_to_dict(organization)
                
                # Check if the organization has a photo and it's accessible
                if organization.photo:
                    # Safely try to access the URL of the image
                    try:
                        organization_data['photo'] = organization.photo.url
                    except ValueError:
                        organization_data['photo'] = None  # Handle cases where photo URL is invalid
                if organization.payment_proof:
                    # Safely try to access the URL of the image
                    try:
                        organization_data['payment_proof'] = organization.payment_proof.url
                    except ValueError:
                        organization_data['payment_proof'] = None  # Handle cases where payment_proof URL is invalid
                
                serialized_data.append(organization_data)
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Exception as e:
            return Response(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}
            )

class OrganizationListUpdateAPIView(APIView):
    def put(self, request, *args, **kwargs):
        try:
            organization = Organization.objects.get(id=kwargs.get('id'))
            serializer = OrganizationSerializer(organization, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})
    # Delete request to delete one cart item
class OrganizationListDeleteAPIView(APIView):    
    def delete(self, request, *args, **kwargs):
        # Here what we are passing as id from url is the cart item id
        try:
            # Get the item which is not checkedout yet through id to delete
            organization = Organization.objects.get(id=kwargs.get('id'))
            UserAccount.objects.get(id=organization.account_id.id).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Organization data  deleted successfully."})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Organization to delete."})
