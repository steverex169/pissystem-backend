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
from django.contrib.sites.shortcuts import get_current_site
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn, PartnerBetwarInfo
from organizationdata.serializers import OrganizationSerializer, ScrapdataSerializer, PartnerBetwarInfoSerializer
from account.models import UserAccount
from account.serializers import RegisterSerializer
import re
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


import re
from datetime import datetime
from django.db.models import Q


class Statements2View(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            user = UserAccount.objects.get(id=kwargs.get('id'))

            # Fetch data for both user and "XAOS"
            all_scrape = Scrapdata.objects.filter(partner_name=user.username)
            volume_data_list = ScrapBetwarVolumn.objects.filter(partner_name=user.username)
            print("Volume Data List:", volume_data_list)
            partnrinfo = PartnerBetwarInfo.objects.filter(partner_name=user.username)


            print("all_scrape:", all_scrape)
            if not all_scrape.exists():
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Data not found"})
            
            partner_info_dict = {
                partner.partner_name: partner.volume_formula
                for partner in PartnerBetwarInfo.objects.filter(partner_name__in=["BASS", "JRS", "PARIS", "BAWS", "POPE", "POPE2", "JCCCS", "MIZ", "CLASSICO", ])
            }

            multipliers = {
                "BASS": partner_info_dict.get("BASS", 0),  # Default to 0 if not found
                "JRS": partner_info_dict.get("JRS", 0),
                "PARIS": partner_info_dict.get("PARIS", 0),
                "BAWS": partner_info_dict.get("BAWS", 0),
                "POPE": partner_info_dict.get("POPE", 0),
                "POPE2": partner_info_dict.get("POPE2", 0),
                "JCCCS": partner_info_dict.get("JCCCS", 0),
                "MIZ": partner_info_dict.get("MIZ", 0),
                "CLASSICO": partner_info_dict.get("CLASSICO", 0),

            }
            print("multipliers values", multipliers)

            account_items = []
            total_volume = 0
            processed_combinations = set()
            processed_partner_profit_dates = set()

            def standardize_date(date_str):
                try:
                    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", date_str):
                        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%m/%d/%y")
                    elif re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%y")
                    else:
                        return date_str
                except Exception:
                    return date_str

            for scrape in all_scrape:
                partner_type = scrape.partner
                partner_profit_date = scrape.partner_profit
                weekly_key = standardize_date(scrape.partner_profit or "")

                print(f"Processing Partner: {partner_type} - {scrape.partner_name}, Weekly Key: {weekly_key}")

                if not re.match(r"^\d{1,2}/\d{1,2}/\d{2} - \d{1,2}/\d{1,2}/\d{2}$", weekly_key):
                    print("Invalid Weekly Key Skipped:", weekly_key)
                    continue

                calculated_volume = 0.0  

                if partner_type in ["BETWAR", "XAOS"]:  # Now XAOS is included
                    print("Checking volumes for:", scrape.partner_name)
                    
                    volume_data = volume_data_list.filter(
                        partner_name=scrape.partner_name,
                        weak_date=weekly_key
                    ).first()
                    

                    print("Selected entry format:", volume_data)

                    combination = (scrape.partner_name, weekly_key)

                    if combination not in processed_combinations and partner_profit_date not in processed_partner_profit_dates:
                        processed_combinations.add(combination)
                        processed_partner_profit_dates.add(partner_profit_date)
                        
                        # Convert raw_volume to float safely
                        raw_volume = 0.0
                        if volume_data and volume_data.volume:
                            try:
                                raw_volume = float(volume_data.volume.replace(",", ""))
                            except ValueError:
                                raw_volume = 0.0

                        # Ensure the multiplier is a float
                        multiplier = float(multipliers.get(scrape.partner_name, 0))  # Convert to float

                        if scrape.partner_name == "SNOWCLASSICO":
                            raw_volume *= 0.80  # Reduce by 20%

                        # Perform the multiplication
                        calculated_volume = raw_volume * multiplier  
                        print("Multiplier & Calculated Volume:", multiplier, calculated_volume, raw_volume)


                        total_volume += calculated_volume

                item = {
                    "volume": calculated_volume,
                    "partner": partner_type,
                    "weekly": scrape.weekly,
                    "partner_name": scrape.partner_name,
                    "website_url": scrape.website_url,
                    "username": scrape.username,
                    "password": scrape.password,
                    "figure": scrape.figure,
                    "affiliate_profit": scrape.affiliate_profit,
                    "partner_profit": scrape.partner_profit,
                    "office_profit": scrape.office_profit,
                    "total": scrape.total,
                    "user": scrape.user,
                    "id": scrape.id,

                }
                account_items.append(item)

            return Response({
                "status": status.HTTP_200_OK,
                "data": account_items,
                "totalVolume": total_volume
            })

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})
    def put(self, request, *args, **kwargs):
        try:
            organization = Scrapdata.objects.get(id=kwargs.get('id'))
            serializer = ScrapdataSerializer(organization, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})

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
                partnerdata = PartnerBetwarInfo.objects.filter(partner_name=admin.username).first()  # Get first match
                if partnerdata:
                    serialized_data[i]["partner_percentage"] = partnerdata.partner_percentage
                else:
                    serialized_data[i]["partner_percentage"] = None  # Default value if no match found
                if partnerdata:
                    serialized_data[i]["volume_formula"] = partnerdata.volume_formula
                else:
                    serialized_data[i]["volume_formula"] = None  # Default value if no match found

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
            partners = PartnerBetwarInfo.objects.filter(partner_name=staff.username)
            print("partner info", partners)

            updated_records = []

            # If no partner records exist, create a new one
            if not partners.exists():
                serializer = PartnerBetwarInfoSerializer(data={
                    **request.data,
                    "partner_name": staff.username,
                    "volume_formula": request.data.get("volume_formula"),
                    "partner_percentage": request.data.get("partner_percentage")
                })
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "status": status.HTTP_201_CREATED,
                        "data": serializer.data,
                        "message": "No matching partner data found. A new record has been created."
                    })
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})


            # Iterate through each partner record and update
            for partner in partners:
                serializer = PartnerBetwarInfoSerializer(partner, data=request.data, partial=True)
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
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Sorry! Account with this ID doesn't exist. Please create account first."
            })
        except Exception as e:
            # Handle unexpected errors
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            })

    # def put(self, request, *args, **kwargs):
    #     try:
    #         # Get the staff by ID
    #         staff = UserAccount.objects.get(id=kwargs.get('id'))
    #         print("staff info", staff, staff.username)

    #         # Fetch all Scrapdata objects for this partner
    #         partners = PartnerBetwarInfo.objects.filter(partner_name=staff.username)
    #         print("partner info", partners)

    #         # Check if any partners exist
    #         if not partners.exists():
    #             return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No matching partner data found for the staff."})

    #         # Iterate through each partner record and update
    #         updated_records = []
    #         for partner in partners:
    #             serializer = PartnerBetwarInfoSerializer(partner, data=request.data, partial=True)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 updated_records.append(serializer.data)
    #             else:
    #                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

    #         return Response({
    #             "status": status.HTTP_200_OK,
    #             "data": updated_records,
    #             "message": f"Updated {len(updated_records)} records successfully"
    #         })

    #     except UserAccount.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this ID doesn't exist. Please create account first."})
    #     except Exception as e:
    #         # Handle unexpected errors
    #         return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

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


# class PartnersList(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             unique_users = Scrapdata.objects.values("partner_name").distinct()
#             partner_name = [user["partner_name"] for user in unique_users]
#             return Response(
#                 {"status": status.HTTP_200_OK, "data": partner_name},
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             return Response(
#                 {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )     

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
from django.contrib.sites.shortcuts import get_current_site
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn, PartnerBetwarInfo
from organizationdata.serializers import OrganizationSerializer, ScrapdataSerializer, PartnerBetwarInfoSerializer
from account.models import UserAccount
from account.serializers import RegisterSerializer
import re
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


import re
from datetime import datetime
from django.db.models import Q


class Statements2View(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            user = UserAccount.objects.get(id=kwargs.get('id'))

            # Fetch data for both user and "XAOS"
            all_scrape = Scrapdata.objects.filter(partner_name=user.username)
            volume_data_list = ScrapBetwarVolumn.objects.filter(partner_name=user.username)
            print("Volume Data List:", volume_data_list)
            partnrinfo = PartnerBetwarInfo.objects.filter(partner_name=user.username)


            print("all_scrape:", all_scrape)
            if not all_scrape.exists():
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Data not found"})
            
            partner_info_dict = {
                partner.partner_name: partner.volume_formula
                for partner in PartnerBetwarInfo.objects.filter(partner_name__in=["BASS", "JRS", "PARIS", "BAWS", "POPE", "POPE2", "JCCCS", "MIZ", "CLASSICO", ])
            }

            multipliers = {
                "BASS": partner_info_dict.get("BASS", 0),  # Default to 0 if not found
                "JRS": partner_info_dict.get("JRS", 0),
                "PARIS": partner_info_dict.get("PARIS", 0),
                "BAWS": partner_info_dict.get("BAWS", 0),
                "POPE": partner_info_dict.get("POPE", 0),
                "POPE2": partner_info_dict.get("POPE2", 0),
                "JCCCS": partner_info_dict.get("JCCCS", 0),
                "MIZ": partner_info_dict.get("MIZ", 0),
                "CLASSICO": partner_info_dict.get("CLASSICO", 0),

            }
            print("multipliers values", multipliers)

            account_items = []
            total_volume = 0
            processed_combinations = set()
            processed_partner_profit_dates = set()

            def standardize_date(date_str):
                try:
                    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", date_str):
                        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%m/%d/%y")
                    elif re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%y")
                    else:
                        return date_str
                except Exception:
                    return date_str

            for scrape in all_scrape:
                partner_type = scrape.partner
                partner_profit_date = scrape.partner_profit
                weekly_key = standardize_date(scrape.partner_profit or "")

                print(f"Processing Partner: {partner_type} - {scrape.partner_name}, Weekly Key: {weekly_key}")

                if not re.match(r"^\d{1,2}/\d{1,2}/\d{2} - \d{1,2}/\d{1,2}/\d{2}$", weekly_key):
                    print("Invalid Weekly Key Skipped:", weekly_key)
                    continue

                calculated_volume = 0.0  

                if partner_type in ["BETWAR", "XAOS"]:  # Now XAOS is included
                    print("Checking volumes for:", scrape.partner_name)
                    
                    volume_data = volume_data_list.filter(
                        partner_name=scrape.partner_name,
                        weak_date=weekly_key
                    ).first()
                    

                    print("Selected entry format:", volume_data)

                    combination = (scrape.partner_name, weekly_key)

                    if combination not in processed_combinations and partner_profit_date not in processed_partner_profit_dates:
                        processed_combinations.add(combination)
                        processed_partner_profit_dates.add(partner_profit_date)
                        
                        # Convert raw_volume to float safely
                        raw_volume = 0.0
                        if volume_data and volume_data.volume:
                            try:
                                raw_volume = float(volume_data.volume.replace(",", ""))
                            except ValueError:
                                raw_volume = 0.0

                        # Ensure the multiplier is a float
                        multiplier = float(multipliers.get(scrape.partner_name, 0))  # Convert to float

                        if scrape.partner_name == "SNOWCLASSICO":
                            raw_volume *= 0.80  # Reduce by 20%

                        # Perform the multiplication
                        calculated_volume = raw_volume * multiplier  
                        print("Multiplier & Calculated Volume:", multiplier, calculated_volume, raw_volume)


                        total_volume += calculated_volume

                item = {
                    "volume": calculated_volume,
                    "partner": partner_type,
                    "weekly": scrape.weekly,
                    "partner_name": scrape.partner_name,
                    "website_url": scrape.website_url,
                    "username": scrape.username,
                    "password": scrape.password,
                    "figure": scrape.figure,
                    "affiliate_profit": scrape.affiliate_profit,
                    "partner_profit": scrape.partner_profit,
                    "office_profit": scrape.office_profit,
                    "total": scrape.total,
                    "user": scrape.user,
                    "id": scrape.id,

                }
                account_items.append(item)

            return Response({
                "status": status.HTTP_200_OK,
                "data": account_items,
                "totalVolume": total_volume
            })

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})
    def put(self, request, *args, **kwargs):
        try:
            organization = Scrapdata.objects.get(id=kwargs.get('id'))
            serializer = ScrapdataSerializer(organization, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Organization.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this id doesn't exist. Please create account first."})

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
                partnerdata = PartnerBetwarInfo.objects.filter(partner_name=admin.username).first()  # Get first match
                if partnerdata:
                    serialized_data[i]["partner_percentage"] = partnerdata.partner_percentage
                else:
                    serialized_data[i]["partner_percentage"] = None  # Default value if no match found
                if partnerdata:
                    serialized_data[i]["volume_formula"] = partnerdata.volume_formula
                else:
                    serialized_data[i]["volume_formula"] = None  # Default value if no match found

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
            partners = PartnerBetwarInfo.objects.filter(partner_name=staff.username)
            print("partner info", partners)

            updated_records = []

            # If no partner records exist, create a new one
            if not partners.exists():
                serializer = PartnerBetwarInfoSerializer(data={
                    **request.data,
                    "partner_name": staff.username,
                    "volume_formula": request.data.get("volume_formula"),
                    "partner_percentage": request.data.get("partner_percentage")
                })
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "status": status.HTTP_201_CREATED,
                        "data": serializer.data,
                        "message": "No matching partner data found. A new record has been created."
                    })
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})


            # Iterate through each partner record and update
            for partner in partners:
                serializer = PartnerBetwarInfoSerializer(partner, data=request.data, partial=True)
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
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Sorry! Account with this ID doesn't exist. Please create account first."
            })
        except Exception as e:
            # Handle unexpected errors
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            })

    # def put(self, request, *args, **kwargs):
    #     try:
    #         # Get the staff by ID
    #         staff = UserAccount.objects.get(id=kwargs.get('id'))
    #         print("staff info", staff, staff.username)

    #         # Fetch all Scrapdata objects for this partner
    #         partners = PartnerBetwarInfo.objects.filter(partner_name=staff.username)
    #         print("partner info", partners)

    #         # Check if any partners exist
    #         if not partners.exists():
    #             return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No matching partner data found for the staff."})

    #         # Iterate through each partner record and update
    #         updated_records = []
    #         for partner in partners:
    #             serializer = PartnerBetwarInfoSerializer(partner, data=request.data, partial=True)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 updated_records.append(serializer.data)
    #             else:
    #                 return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

    #         return Response({
    #             "status": status.HTTP_200_OK,
    #             "data": updated_records,
    #             "message": f"Updated {len(updated_records)} records successfully"
    #         })

    #     except UserAccount.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! Account with this ID doesn't exist. Please create account first."})
    #     except Exception as e:
    #         # Handle unexpected errors
    #         return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

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


# class PartnersList(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             unique_users = Scrapdata.objects.values("partner_name").distinct()
#             partner_name = [user["partner_name"] for user in unique_users]
#             return Response(
#                 {"status": status.HTTP_200_OK, "data": partner_name},
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             return Response(
#                 {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )     

import re

class PartnersList(APIView):
    def get(self, request, *args, **kwargs):
        try:
            all_scrape = Scrapdata.objects.all()

            if not all_scrape.exists():
                return Response(
                    {"status": status.HTTP_400_BAD_REQUEST, "message": "Data not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch all unique partner names
            partner_names = all_scrape.values_list("partner_name", flat=True).distinct()

            # Fetch volume data related to these partners
            volume_data_list = ScrapBetwarVolumn.objects.filter(partner_name__in=partner_names)

            # Fetch partner info and create a dictionary of multipliers
            partner_info_dict = {
                partner.partner_name: float(partner.volume_formula or 0)  # Default to 0 if None
                for partner in PartnerBetwarInfo.objects.filter(partner_name__in=partner_names)
            }

            # Initialize required variables
            account_items = []
            total_volume = 0
            first_time_tracker = {}  # Track first occurrence of (partner_name, weekly_key)

            def standardize_date_range(date_range):
                """Convert date ranges into MM/DD/YY - MM/DD/YY format"""
                try:
                    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4}) - (\d{1,2})/(\d{1,2})/(\d{2,4})", date_range)

                    if match:
                        m1, d1, y1, m2, d2, y2 = match.groups()
                        y1 = y1[-2:]  # Convert YYYY to YY
                        y2 = y2[-2:]  # Convert YYYY to YY
                        return f"{int(m1):02d}/{int(d1):02d}/{y1} - {int(m2):02d}/{int(d2):02d}/{y2}"
                    return date_range
                except Exception:
                    return date_range

            first_time_tracker = set()  # Set to track first occurrences of partner_name

            for scrape in all_scrape:
                partner_type = scrape.partner
                weekly_key = standardize_date_range(scrape.partner_profit or "")

                if not re.match(r"^\d{2}/\d{2}/\d{2} - \d{2}/\d{2}/\d{2}$", weekly_key):
                    continue

                calculated_volume = 0.0
                partner_name = scrape.partner_name  # Only tracking partner_name

                if partner_type in ["BETWAR", "XAOS"]:
                    volume_data = volume_data_list.filter(
                        partner_name=scrape.partner_name,
                        weak_date=weekly_key
                    ).first()  # Get the first matching entry
                    
                    print("yaha kya a raha h dekhty hai", volume_data)

                    combination = (scrape.partner_name, weekly_key)  # Track each partner_name + weak_date

                    if combination not in first_time_tracker:  # First occurrence of (partner_name, weak_date)
                        first_time_tracker.add(combination)  # Add this combination to the tracker

                        raw_volume = 0.0
                        if volume_data and volume_data.volume:
                            try:
                                raw_volume = float(volume_data.volume.replace(",", ""))
                            except ValueError:
                                raw_volume = 0.0

                        multiplier = partner_info_dict.get(scrape.partner_name, 0.0)

                        if scrape.partner_name == "SNOWCLASSICO":
                            raw_volume *= 0.80  # Reduce by 20%

                        calculated_volume = raw_volume * multiplier
                        total_volume += calculated_volume  # Only add real volume once

                        print("volume a raha hai yaha nahi", total_volume, calculated_volume)


                item = {
                    "volume": calculated_volume,  # First occurrence → real volume, others → 0
                    "partner": partner_type,
                    "weekly": scrape.weekly,
                    "partner_name": scrape.partner_name,
                    "website_url": scrape.website_url,
                    "username": scrape.username,
                    "password": scrape.password,
                    "figure": scrape.figure,
                    "affiliate_profit": scrape.affiliate_profit,
                    "partner_profit": weekly_key,
                    "office_profit": scrape.office_profit,
                    "total": scrape.total,
                    "user": scrape.user,
                    "id": scrape.id,
                }
                account_items.append(item)

            return Response({
                "status": status.HTTP_200_OK,
                "data": account_items,
                "totalVolume": total_volume
            })


        except Exception as e:
            return Response(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

