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
from organizationdata.models import Organization, Scrapdata
from organizationdata.serializers import OrganizationSerializer, ScrapdataSerializer
from account.models import UserAccount
from account.serializers import RegisterSerializer
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




class Statements2View(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try: 
            user = UserAccount.objects.get(id=kwargs.get('id'))
            print("user id is", user)

            try:
                scrape_data = Scrapdata.objects.filter(partner_name=user.username)
                print(scrape_data)
                
                account_items = []
                for cart_item in scrape_data:
                        partner = cart_item.partner
                        partner_name = cart_item.partner_name
                        website_url = cart_item.website_url
                        username = cart_item.username
                        password = cart_item.password
                        figure = cart_item.figure
                        affiliate_profit = cart_item.affiliate_profit
                        partner_profit = cart_item.partner_profit
                        office_profit = cart_item.office_profit
                        total = cart_item.total
                        weekly = cart_item.weekly
                        user = cart_item.user


                        account_items.append({"user": user, "partner": partner, "weekly": weekly, "partner_name": partner_name, "website_url": website_url, "username": username, "password": password, "figure":figure, "affiliate_profit": affiliate_profit, "partner_profit": partner_profit, "office_profit": office_profit,"total":total,})
                return Response({"status": status.HTTP_200_OK,  "data": account_items })
            except Scrapdata.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})


class AccountsListsView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        try:
            # Get all users (not used)
            all_users = UserAccount.objects.all()
            print(all_users)

            # Get all database admins
            database_admins = UserAccount.objects.filter(account_type="database-admin")
            print(database_admins)

            # Initialize an empty list for serialized data
            serializer = RegisterSerializer(database_admins, many=True)
            serialized_data = serializer.data  # Convert it into mutable list

            # Iterate over each admin and find partner data
            for i, admin in enumerate(database_admins):
                partnerdata = Scrapdata.objects.filter(partner_name=admin.username).first()  # Get first match
                if partnerdata:
                    serialized_data[i]["partner_percentage"] = partnerdata.partner_percentage
                else:
                    serialized_data[i]["partner_percentage"] = None  # Default value if no match found

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Exception as e:
            return Response(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # GET request to retrieve user accounts with account_type="database-admin"
    # def get(self, request, *args, **kwargs):
    #     try:
    #         all_users = UserAccount.objects.all()
    #         print(all_users)

    #         database_admins = UserAccount.objects.filter(account_type="database-admin")
    #         print(database_admins)

    #         database_admins = UserAccount.objects.filter(account_type="database-admin")
    #         print(database_admins)

    #         # partnerdata = Scrapdata.objects.filter(UserAccount=database_admins.UserAccount)
    #         # print("partnerdata username", partnerdata)

    #         serializer = RegisterSerializer(database_admins, many=True)
    #         return Response(
    #             {"status": status.HTTP_200_OK, "data": serializer.data},
    #             status=status.HTTP_200_OK
    #         )
    #     except Exception as e:
    #         return Response(
    #             {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def get(self, request, *args, **kwargs):
    #     try:
    #         all_users = UserAccount.objects.all()
    #         print(all_users)

    #         database_admins = UserAccount.objects.filter(account_type="database-admin")
    #         print(database_admins)

    #         # Retrieve partner data related to database admins
    #         partnerdata = Scrapdata.objects.filter(partner_name=database_admins)
    #         print("Partner Data:", partnerdata)

    #         # Serialize the database admins and their related partner data
    #         admins_serializer = RegisterSerializer(database_admins, many=True)
    #         print("admins serializer", admins_serializer)
    #         partners_serializer = ScrapdataSerializer(partnerdata, many=True)

    #         return Response(
    #             {
    #                 "status": status.HTTP_200_OK,
    #                 "database_admins": admins_serializer.data,
    #                 "partner_data": partners_serializer.data,
    #             },
    #             status=status.HTTP_200_OK,
    #         )

    #     except Exception as e:
    #         return Response(
    #             {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
                
    #         )
    def put(self, request, *args, **kwargs):
        try:
            # Get the staff by ID
            staff = UserAccount.objects.get(id=kwargs.get('id'))
            print("staff info", staff, staff.username)

            # Fetch all Scrapdata objects for this partner
            partners = Scrapdata.objects.filter(partner_name=staff.username)
            print("partner info", partners)

            # Check if any partners exist
            if not partners.exists():
                return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No matching partner data found for the staff."})

            # Iterate through each partner record and update
            updated_records = []
            for partner in partners:
                serializer = ScrapdataSerializer(partner, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_records.append(serializer.data)
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

            return Response({
                "status": status.HTTP_200_OK,
                "data": updated_records,
                "message": f"Updated {len(updated_records)} records successfully"
            })

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this ID doesn't exist. Please create account first."})
        except Exception as e:
            # Handle unexpected errors
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

    # def put(self, request, *args, **kwargs):
    #     try:
    #         staff = UserAccount.objects.get(id=kwargs.get('id'))
    #         print("staff info", staff, staff.username)

    #         partners = Scrapdata.objects.filter(partner_name = staff.username)
    #         print("partner info", partners)

    #         serializer = ScrapdataSerializer(
    #             partners, data=request.data, partial=True)

    #         if serializer.is_valid():
    #             serializer.save()

    #             return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
    #         else:
    #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

    #     except UserAccount.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})

    # Delete request to delete one cart item
    def delete(self, request, *args, **kwargs):
        # Here what we are passing as id from url is the cart item id
        try:
            # Get the item which is not checkedout yet through id to delete
            staff = UserAccount.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Partner deleted successfully."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Partner to delete."})
   
