from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from databaseadmin.models import City
from databaseadmin.serializers import CitySerializer
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils import timezone
from account.models import UserAccount
from organizationdata.models import Organization
from django.shortcuts import get_object_or_404
from datetime import datetime
import pandas as pd

class InstrumentTypefileView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        account_id = kwargs.get('id')
        
        # Fetch the staff user based on account_id
        try:
            staff_user = Staff.objects.get(account_id=account_id)
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Staff user not found."})

        # Retrieve the organization associated with the staff user
        organization = staff_user.organization_id

        if not organization:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Organization not found for the staff user."})

        # Case 1: Data provided in request
        if request.FILES.get('excel_file'):  # Assuming the Excel file is uploaded with key 'excel_file'
            excel_file = request.FILES['excel_file']
            excel_data = self.extract_excel_data(excel_file)
            if excel_data:
                # Filter out duplicates based on employee_code
                unique_data = self.remove_duplicate_name(excel_data)
                if not unique_data:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No unique data found after filtering duplicates."})
                
                # Attempt to save each unique entry
                saved_entries = []
                for entry in unique_data:
                    try:
                        employee = InstrumentType.objects.get(name=entry['name'])
                        # If employee with same name already exists, skip this entry
                        continue
                    except InstrumentType.DoesNotExist:
                        entry['organization_id'] = organization.id  # Append the organization ID
                        serializer = InstrumentTypeSerializer(data=entry)
                        if serializer.is_valid():
                            serializer.save()
                            saved_entries.append(serializer.data)
                        else:
                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid data provided.", "errors": serializer.errors})
                
                return Response({"status": status.HTTP_200_OK, "message": "Data extracted and saved successfully.", "saved_entries": saved_entries})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Failed to extract data from Excel file."}) 
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Excel file not provided."})

    def extract_excel_data(self, excel_file):
        try:
            # Assuming the Excel file has headers 'name'
            df = pd.read_excel(excel_file)
            # Assuming all rows contain the data of interest
            data = df[['name']]  # Extract relevant columns
            # Convert data to a list of dictionaries
            extracted_data = data.to_dict(orient='records')
            return extracted_data
        except Exception as e:
            print("Error extracting Excel data:", e)
            return None

    def remove_duplicate_name(self, excel_data):
        unique_instrumentType_name = set()
        unique_data = []
        for entry in excel_data:
            name = entry.get('name')
            if name not in unique_instrumentType_name:
                unique_instrumentType_name.add(name)
                unique_data.append(entry)
        return unique_data

class ParticipantSectorListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter sector based on the organization
            sector_list = ParticipantSector.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(sector) for sector in sector_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except ParticipantSector.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No sector records found."})

class ParticipantSectorCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if ParticipantSector.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new sector
            sector = ParticipantSector.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,
                sector_id=sector,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type="ParticipantSector"
            )

            # Serialize the created sector and activity log
            sector_serializer = ParticipantSectorSerializer(sector)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "sector_data": sector_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "ParticipantSector added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ParticipantSectorUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing sector object
            sector = ParticipantSector.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the sector
            old_values = {
                'name': sector.name,
            }
            
            # Serialize the updated data
            serializer = ParticipantSectorSerializer(sector, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the ParticipantSector table
                updated_sector = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_sector.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    sector_id=sector,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',  
                    type="ParticipantSector"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "ParticipantSector Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except ParticipantSector.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ParticipantTypeListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter type based on the organization
            type_list = ParticipantType.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(type) for type in type_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except ParticipantType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No type records found."})

class ParticipantTypeCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if ParticipantType.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new type
            type = ParticipantType.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,
                type_id=type,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type="ParticipantType"
            )

            # Serialize the created type and activity log
            type_serializer = ParticipantTypeSerializer(type)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "type_data": type_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "ParticipantType added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ParticipantTypeUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing type object
            type = ParticipantType.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the type
            old_values = {
                'name': type.name,
            }
            
            # Serialize the updated data
            serializer = ParticipantTypeSerializer(type, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the ParticipantType table
                updated_type = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_type.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    type_id=type,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='ParticipantType'
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "ParticipantType Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except ParticipantType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CityListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            user_account = UserAccount.objects.get(id=account_id)
            if user_account.account_type == 'organization':
                org = Organization.objects.get(account_id=account_id)
                organization = org.id
            else:
                # Fetch the staff user based on account_id
                staff_user = Staff.objects.get(account_id=account_id)
                # Retrieve the organization associated with the staff user
                organization = staff_user.organization_id
            
            # Filter city based on the organization
            city_list = City.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(city) for city in city_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except City.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No City records found."})

class CityCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            print("yaha kya h", request.data.get('added_by'))
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if City.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new city
            city = City.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,
                city_id=city,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='City'
            )

            # Serialize the created city and activity log
            city_serializer = CitySerializer(city)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "city_data": city_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "City added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CityUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing city object
            city = City.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the city
            old_values = {
                'name': city.name,
            }
            
            # Serialize the updated data
            serializer = CitySerializer(city, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the City table
                updated_city = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_city.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account, 
                    city_id=city,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated' ,
                    type='City'
 
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "City Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except City.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ProvinceListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
           # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter province based on the organization
            province_list = ParticipantProvince.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(province) for province in province_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except ParticipantProvince.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No City records found."})

class ProvinceCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if ParticipantProvince.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new province
            province = ParticipantProvince.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                province_id=province,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='ParticipantProvince'
            )

            # Serialize the created province and activity log
            province_serializer = ProvinceSerializer(province)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "province_data": province_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Province added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ProvinceUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing province object
            province = ParticipantProvince.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the province
            old_values = {
                'name': province.name,
            }
            
            # Serialize the updated data
            serializer = ProvinceSerializer(province, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the Province table
                updated_province = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_province.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    province_id=province,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='ParticipantProvince'
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Province Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except ParticipantProvince.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CountryListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter country based on the organization
            country_list = ParticipantCountry.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(country) for country in country_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except ParticipantCountry.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No City records found."})

class CountryCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if ParticipantCountry.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new country
            country = ParticipantCountry.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                country_id=country,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='ParticipantCountry'
            )

            # Serialize the created country and activity log
            country_serializer = CountrySerializer(country)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "country_data": country_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Country added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CountryUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing country object
            country = ParticipantCountry.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the country
            old_values = {
                'name': country.name,
            }
            
            # Serialize the updated data
            serializer = CountrySerializer(country, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the Country table
                updated_country = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_country.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    country_id=country,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated', 
                    type='ParticipantCountry' 
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Country Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except ParticipantCountry.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DistrictListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter district based on the organization
            district_list = District.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(district) for district in district_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except District.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No District records found."})

class DistrictCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if District.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new district
            district = District.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                district_id=district,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='District'

            )

            # Serialize the created district and activity log
            district_serializer = DistrictSerializer(district)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "district_data": district_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "District added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DistrictUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing district object
            district = District.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the district
            old_values = {
                'name': district.name,
            }
            
            # Serialize the updated data
            serializer = DistrictSerializer(district, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the district table
                updated_district = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_district.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    district_id=district,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='District'  
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "District Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except District.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DepartmentListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter department based on the organization
            department_list = Department.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(department) for department in department_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Department.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Department records found."})

class DepartmentCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if Department.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new department
            department = Department.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                department_id=department,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='Department'
            )

            # Serialize the created department and activity log
            department_serializer = DepartmentSerializer(department)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "department_data": department_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Department added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DepartmentUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing department object
            department = Department.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the department
            old_values = {
                'name': department.name,
            }
            
            # Serialize the updated data
            serializer = DepartmentSerializer(department, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the department table
                updated_department = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_department.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    department_id=department,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='Department'
  
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Department Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Department.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DesignationListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter designation based on the organization
            designation_list = Designation.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(designation) for designation in designation_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Designation.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Designation records found."})

class DesignationCreateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if Designation.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })
            
            # Create a new designation
            designation = Designation.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                designation_id=designation,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='Designation'
            )

            # Serialize the created designation and activity log
            designation_serializer = DesignationSerializer(designation)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "designation_data": designation_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Designation added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DesignationUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing designation object
            designation = Designation.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the designation
            old_values = {
                'name': designation.name,
            }
            
            # Serialize the updated data
            serializer = DesignationSerializer(designation, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the designation table
                updated_designation = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_designation.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    designation_id=designation,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='Designation'
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Designation Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Designation.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class UnitsListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        account_id = kwargs.get('id')
        try:

            user_account = UserAccount.objects.get(id=account_id)
            organization = None

            if user_account.account_type == 'labowner':
                participant = Lab.objects.get(account_id=account_id)
                organization = participant.organization_id
            else:
                staff_member = Staff.objects.get(account_id=account_id)
                organization = staff_member.organization_id

            if organization:
                units_list = Units.objects.filter(organization_id=organization.id)
                serialized_data = [model_to_dict(unit) for unit in units_list]
                return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Units records found."})
     
class UnitsAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            if Units.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A unit with this name already exists in the organization."
                })
            
            # Create a new unit
            unit = Units.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                unit_id=unit,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                type='Units'
            )

            # Serialize the created unit and activity log
            unit_serializer = UnitsSerializer(unit)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "unit_data": unit_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Unit added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class UnitsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing unit object
            unit = Units.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the unit
            old_values = {
                'name': unit.name,
            }
            
            # Serialize the updated data
            serializer = UnitsSerializer(unit, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the Units table
                updated_unit = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_unit.name,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    unit_id=unit,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type='Units'
  
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Unit Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class QualitativeTypeListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter qualitativetype based on the organization
            qualitativetype_list = QualitativeType.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(qualitativetype) for qualitativetype in qualitativetype_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except QualitativeType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No QualitativeType records found."})
        
class QualitativeTypePostAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Create a new qualitativetype
            qualitativetype = QualitativeType.objects.create(
                organization_id=organization,
                name=request.data['name'],
                number=request.data['number'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']},number: {request.data['number']}, "

            # Save data in activity log
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                qualitativetype_id=qualitativetype,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added',  # Specify action as 'Added'
                # type='Designation'

            )

            # Serialize the created qualitativetype and activity log
            qualitativetype_serializer = QualitativeTypeSerializer(qualitativetype)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "qualitativetype_data": qualitativetype_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "qualitativetype added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class QualitativeTypeUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing qualitativetype object
            qualitativetype = QualitativeType.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the qualitativetype
            old_values = {
                'name': qualitativetype.name,
                'number': qualitativetype.number,
            }
            
            # Serialize the updated data
            serializer = QualitativeTypeSerializer(qualitativetype, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the QualitativeType table
                updated_qualitativetype = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_qualitativetype.name,
                    'number': updated_qualitativetype.number,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])
                
                # Create a new entry in the ActivityLogUnits table
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    qualitativetype_id=qualitativetype,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "qualitativetype Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except QualitativeType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
            
class InstrumentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
             # Get the staff user's account_id
            account_id = kwargs.get('id')
            user_account = UserAccount.objects.get(id=account_id)

            if user_account.account_type == 'labowner':
                participant = Lab.objects.get(account_id=account_id)
                organization = participant.organization_id
            else:
                staff_user = Staff.objects.get(account_id=account_id)
                organization = staff_user.organization_id
                
            # Filter instruments based on the organization
            instruments_list = Instrument.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = []
            for instrument in instruments_list:
                analytes = Analyte.objects.filter(instruments=instrument)
                analytes_count = analytes.count()

                # Retrieve the instrumenttype
                instrument_type_name = None
                if instrument.instrument_type:
                    try:
                        instrument_type = InstrumentType.objects.get(id=instrument.instrument_type.id)
                        instrument_type_name = instrument_type.name  
                    except InstrumentType.DoesNotExist:
                        instrument_type_name = None

                # Retrieve the manufacturer
                manufactural_name = None
                if instrument.manufactural:
                    try:
                        manufactural = Manufactural.objects.get(id=instrument.manufactural.id)
                        manufactural_name = manufactural.name  
                    except Manufactural.DoesNotExist:
                        manufactural_name = None

                # Retrieve the country
                country_name = None
                if instrument.country:
                    try:
                        country = ParticipantCountry.objects.get(id=instrument.country.id)
                        country_name = country.name  # Assuming ParticipantCountry has a 'name' field
                    except ParticipantCountry.DoesNotExist:
                        country_name = None
                
                instrument_data = model_to_dict(instrument)
                instrument_data['analytes_count'] = analytes_count
                instrument_data['instrument_type'] = instrument_type_name
                instrument_data['manufactural'] = manufactural_name
                instrument_data['country'] = country_name

                serialized_data.append(instrument_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

# Post API for creating units
class InstrumentsPostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data['added_by']
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the instrument_type instance based on instrument_type name
            instrument_type_name = request.data.get('instrument_type')
            try:
                instrument_type = InstrumentType.objects.get(name=instrument_type_name, organization_id=organization)
            except InstrumentType.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid instrument_type name provided."})

            # Fetch the manufactural instance based on manufacturer name
            manufactural_name = request.data.get('manufactural')
            try:
                manufactural = Manufactural.objects.get(name=manufactural_name, organization_id=organization)
            except Manufactural.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural name provided."})

            # Fetch the country instance based on country name
            country_name = request.data.get('country')
            try:
                country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
            except ParticipantCountry.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})
            
            if Instrument.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Instrument with this name already exists in the organization."
                })
            
            # Create a new instrument
            instrument = Instrument.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
                code=request.data['code'],
                model=request.data['model'],
                status=request.data['status'],
                instrument_type=instrument_type,
                manufactural=manufactural,
                country=country,
            )

            # Concatenate all changes into a single string with names
            changes_string = f"name: {request.data['name']}, code: {request.data['code']}, status: {request.data['status']}, instrument_type: {instrument_type.name}, manufactural: {manufactural.name},country: {country.name}"

            # Save data in activity log as a single field
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                instrument_id=instrument,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                actions='Added',
                type="Instrumentlist"
            )

            instrument_serializer = InstrumentSerializer(instrument)

            return Response({
                "status": status.HTTP_201_CREATED,
                "instrument_data": instrument_serializer.data,
                "message": "Instrument added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid instrument_type."})

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural."})

        except ParticipantCountry.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class InstrumentsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing instrument object
            instrument = Instrument.objects.get(id=kwargs.get('id'), organization_id=organization)

            # Create a mutable copy of request.data
            data = request.data.copy()

            # Store old values before updating
            old_values = {
                'name': instrument.name,
                'code': instrument.code,
                'model': instrument.model,
                'status': instrument.status,
                'instrument_type': instrument.instrument_type.name if instrument.instrument_type else None,
                'manufactural': instrument.manufactural.name if instrument.manufactural else None,
                'country': instrument.country.name if instrument.country else None,
            }

            # Fetch the instrument_type instance based on instrument_type name
            instrument_type_name = data.get('instrument_type')
            if instrument_type_name:
                try:
                    instrument_type = InstrumentType.objects.get(name=instrument_type_name, organization_id=organization)
                    data['instrument_type'] = instrument_type.id  # Replace the instrument_type name with its pk value
                except InstrumentType.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid instrument_type name provided."})

            # Fetch the manufactural instance based on manufactural name
            manufactural_name = data.get('manufactural')
            if manufactural_name:
                try:
                    manufactural = Manufactural.objects.get(name=manufactural_name, organization_id=organization)
                    data['manufactural'] = manufactural.id  # Replace the manufactural name with its pk value
                except Manufactural.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural name provided."})

            # Fetch the country instance based on country name
            country_name = data.get('country')
            if country_name:
                try:
                    country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
                    data['country'] = country.id  # Replace the country name with its pk value
                except ParticipantCountry.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})

            # Pass the modified data dictionary to the serializer
            serializer = InstrumentSerializer(instrument, data=data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {
                    'name': updated_unit.name,
                    'code': updated_unit.code,
                    'model': updated_unit.model,
                    'status': updated_unit.status,
                    'instrument_type': updated_unit.instrument_type.name if updated_unit.instrument_type else None,
                    'manufactural': updated_unit.manufactural.name if updated_unit.manufactural else None,
                    'country': updated_unit.country.name if updated_unit.country else None,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    instrument_id=instrument,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    actions="Updated",
                    type="Instrumentlist"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Instrument Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})     

class ActivityLogDatabaseadmin(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            id_value = kwargs.get('id')
            type_value = request.GET.get('type')
            print("id in the request", id_value, type_value)

            # Try to get the data from Units
            if request.GET.get('type') == "Units":
                try:
                    unit = Units.objects.get(id=id_value)
                    print("unit print", unit.id)
                    activity_log = ActivityLogUnits.objects.filter(unit_id=unit.id, type=type_value)
                    print("in the log table", activity_log)
                except Units.DoesNotExist:
                # If Units does not exist, try InstrumentType
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})

            elif request.GET.get('type') == "Instruments":

                try:
                    instrument_type = InstrumentType.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(instrumenttype_id=instrument_type.id, type=type_value)
                except InstrumentType.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Analyte":

                try:
                    print("id_valuetype_value....................", id_value,type_value )
                    analyte = Analyte.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(analyte_id=analyte.id, type=type_value)
                except Analyte.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Reagent":

                # If InstrumentType also does not exist, try Reagents
                try:
                    reagent = Reagents.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(reagent_id=reagent.id, type=type_value)
                except Reagents.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Scheme":

                try:
                    scheme = Scheme.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(scheme_id=scheme.id, type=type_value)
                except Scheme.DoesNotExist: 
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Method":
                try:
                    method = Method.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(method_id=method.id, type=type_value)
                except Method.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Manufactural":
                try:
                    manufactural = Manufactural.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(manufactural_id=manufactural.id, type=type_value)
                except Manufactural.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Cycle":
                try:
                    cycle = Cycle.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(cycle_id=cycle.id, type=type_value)
                except Cycle.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No data found."})
            elif request.GET.get('type') == "Instrumentlist":

                try:
                    instrument = Instrument.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(instrument_id=instrument.id, type=type_value)
                except Instrument.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "Instrumentlist":

                try:
                    instrument = Instrument.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(instrument_id=instrument.id, type=type_value)
                except Instrument.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "City":

                try:
                    city = City.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(city_id=city.id, type=type_value)
                except City.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "ParticipantCountry":

                try:
                    country = ParticipantCountry.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(country_id=country.id, type=type_value)
                except ParticipantCountry.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "ParticipantProvince":

                try:
                    country = ParticipantProvince.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(province_id=country.id, type=type_value)
                except ParticipantProvince.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "District":

                try:
                    country = District.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(district_id=country.id, type=type_value)
                except District.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 

            elif request.GET.get('type') == "Department":

                try:
                    country = Department.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(department_id=country.id, type=type_value)
                except Department.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
            elif request.GET.get('type') == "Designation":

                try:
                    country = Designation.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(designation_id=country.id, type=type_value)
                except Designation.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."})
            elif request.GET.get('type') == "ParticipantType":

                try:
                    country = ParticipantType.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(type_id=country.id, type=type_value)
                except ParticipantType.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."})
            elif request.GET.get('type') == "ParticipantSector":

                try:
                    country = ParticipantSector.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(sector_id=country.id, type=type_value)
                except ParticipantSector.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."})
            if activity_log is None:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid type provided."})

            serializer = ActivityLogUnitsSerializer(activity_log, many=True)
            if activity_log.exists():
                data = []
                for log_entry in serializer.data:
                    print("added by", log_entry['added_by'])
                    user_id = log_entry['added_by']
                    username = UserAccount.objects.get(id=user_id).username
                    log_entry['added_by'] = username
                    data.append(log_entry)
                return Response({"status": status.HTTP_200_OK, "data": data})
            else:
                return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No Unit History found."})

        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

class AnalyteAddReagents(APIView):
    permission_classes = (AllowAny,) 

    def post(self, request, *args, **kwargs):
       
        try:
            analyte_id = request.data.get('analyte_id')
            reagents = request.data.getlist('reagent')  # Use getlist to retrieve multiple values
            print("fjdkgdjkgh", reagents)
            analyte = Analyte.objects.get(id=analyte_id)

            # Save reagents to analyte
            for reagent_id in reagents:
                reagent = Reagents.objects.get(id=reagent_id)
                analyte.reagents.add(reagent)

            return Response({"message": "Reagents added to analyte successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Reagents get API 
class ReagentsListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            user_account = UserAccount.objects.get(id=account_id)

            if user_account.account_type == 'labowner':
                participant = Lab.objects.get(account_id=account_id)
                organization = participant.organization_id
            else:
                staff_user = Staff.objects.get(account_id=account_id)
                organization = staff_user.organization_id
                
            # Filter reagents based on the organization
            reagents_list = Reagents.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = []
            for reagent in reagents_list:
                analytes_count = reagent.analyte_set.count()  # Count analytes associated with the reagent
                reagent_data = model_to_dict(reagent)
                reagent_data['analytes_count'] = analytes_count

                # Fetch name from Manufactural table based on manufactural_id
                if reagent.manufactural_id:  # Check if manufactural_id is not None
                    manufactural = Manufactural.objects.get(id=reagent.manufactural_id)
                    reagent_data['manufactural'] = manufactural.name
                else:
                    reagent_data['manufactural'] = None

                # Fetch name from country table based on manufactural_id
                if reagent.country_id:  # Check if country_id is not None
                    country = ParticipantCountry.objects.get(id=reagent.country_id)
                    reagent_data['country'] = country.name
                else:
                    reagent_data['country'] = None

                serialized_data.append(reagent_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

# Reagents Post API 
class ReagentsPostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration
    
    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the manufactural instance based on manufacturer name
            manufactural_name = request.data.get('manufactural')
            try:
                manufactural = Manufactural.objects.get(name=manufactural_name, organization_id=organization)
            except Manufactural.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural name provided."})

            # Fetch the country instance based on country name
            country_name = request.data.get('country')
            try:
                country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
            except ParticipantCountry.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})

            if Reagents.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Reagents with this name already exists in the organization."
                })
            # Create a new reagent
            reagent = Reagents.objects.create(
                organization_id=organization,
                code=request.data['code'],
                name=request.data['name'],
                status=request.data['status'],
                date_of_addition=timezone.now(),
                manufactural=manufactural,
                country=country,
            )

            # Concatenate all changes into a single string with names
            changes_string = f"name: {request.data['name']}, code: {request.data['code']}, status: {request.data['status']},  manufactural: {manufactural.name},country: {country.name}"

            # Save data in activity log as a single field
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            activity_log=ActivityLogUnits.objects.create(
                added_by= user_account,                
                organization_id=organization,
                reagent_id=reagent,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,
                new_value=changes_string,
                actions='Added',
                type="Reagent"
            )

            reagent_serializer = ReagentsSerializer(reagent)

            return Response({
                "status": status.HTTP_201_CREATED,
                "unit_data": reagent_serializer.data,
                "message": "Reagent added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural."})

        except ParticipantCountry.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid Country."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})



class ReagentsPutAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing reagent object
            reagent = Reagents.objects.get(id=kwargs.get('id'), organization_id=organization)
            
            # Create a mutable copy of request.data
            data = request.data.copy()

            # Store old values before updating
            old_values = {
                'name': reagent.name,
                'code': reagent.code,
                'status': reagent.status,
                'manufactural': reagent.manufactural.name if reagent.manufactural else None,
                'country': reagent.country.name if reagent.country else None,
            }

            # Fetch the manufactural instance based on manufactural name
            manufactural_name = data.get('manufactural')
            if manufactural_name:
                try:
                    manufactural = Manufactural.objects.get(name=manufactural_name, organization_id=organization)
                    data['manufactural'] = manufactural.id  # Replace the manufactural name with its pk value
                except Manufactural.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid manufactural name provided."})

            # Fetch the country instance based on country name
            country_name = data.get('country')
            if country_name:
                try:
                    country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
                    data['country'] = country.id  # Replace the country name with its pk value
                except ParticipantCountry.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})

            serializer = ReagentsSerializer(reagent, data=data, partial=True)

            if serializer.is_valid():
                updated_reagent = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_reagent.name,
                    'code': updated_reagent.code,
                    'status': updated_reagent.status,
                    'manufactural': updated_reagent.manufactural.name if updated_reagent.manufactural else None,
                    'country': updated_reagent.country.name if updated_reagent.country else None,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                user_account = UserAccount.objects.get(id=account_id)

                # Save data in activity log as a single field
                activity_log=ActivityLogUnits.objects.create(
                    added_by= user_account,                    
                    reagent_id=reagent,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    actions="Updated",
                    type="Reagent"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Reagent Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class ManufacturalListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter manufacturals based on the organization
            manufactural_list = Manufactural.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = []
            for manufactural in manufactural_list:
                instruments = Instrument.objects.filter(manufactural=manufactural)
                instrument_count = instruments.count()
                
                # Retrieve the country
                country_name = None
                if manufactural.country is not None:
                    try:
                        country = ParticipantCountry.objects.get(id=manufactural.country.id)
                        country_name = country.name  # Assuming ParticipantCountry has a 'name' field
                    except ParticipantCountry.DoesNotExist:
                        country_name = None

                reagents = Reagents.objects.filter(manufactural=manufactural)
                reagents_count = reagents.count()

                manufactural_data = model_to_dict(manufactural)
                manufactural_data['instrument_count'] = instrument_count
                manufactural_data['reagents_count'] = reagents_count
                manufactural_data['country'] = country_name
                
                serialized_data.append(manufactural_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        
class ManufacturalPostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the country instance based on country name
            country_name = request.data.get('country')
            try:
                country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
            except ParticipantCountry.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})

            if Manufactural.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Manufactural with this name already exists in the organization."
                })
            # Create a new manufactural
            manufactural = Manufactural.objects.create(
                organization_id=organization,
                name=request.data['name'],
                website=request.data['website'],
                country=country,
                date_of_addition=timezone.now(),
            )
            # Concatenate all changes into a single string with names
            changes_string = f"name: {request.data['name']}, website: {request.data['website']}, country: {country.name}"
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                added_by= user_account,
                organization_id=organization,
                manufactural_id=manufactural,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                actions='Added',
                type="Manufactural"
            )

            manufactural_serializer = ManufacturalSerializer(manufactural)

            return Response({
                "status": status.HTTP_201_CREATED,
                "unit_data": manufactural_serializer.data,
                "message": "Manufactural added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class ManufacturalPutAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Create a mutable copy of request.data
            data = request.data.copy()
            
            # Fetch the staff user based on account_id
            account_id = data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing manufactural object
            manufactural = Manufactural.objects.get(id=kwargs.get('id'), organization_id=organization)

            # Store old values before updating
            old_values = {
                'name': manufactural.name,
                'website': manufactural.website,
                'country': manufactural.country.name if manufactural.country else None,
            }

            # Fetch the country instance based on country name
            country_name = data.get('country')
            if country_name:
                try:
                    country = ParticipantCountry.objects.get(name=country_name, organization_id=organization)
                    data['country'] = country.id  # Replace the country name with its pk value
                except ParticipantCountry.DoesNotExist:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid country name provided."})

            serializer = ManufacturalSerializer(manufactural, data=data, partial=True)

            if serializer.is_valid():
                updated_manufactural = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_manufactural.name,
                    'website': updated_manufactural.website,
                    'country': updated_manufactural.country.name if updated_manufactural.country else None,
                }

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    manufactural_id=manufactural,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    actions="Updated",
                    type="Manufactural"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Manufactural Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class MethodsAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
             # Get the staff user's account_id
            account_id = kwargs.get('id')
            user_account = UserAccount.objects.get(id=account_id)

            if user_account.account_type == 'labowner':
                participant = Lab.objects.get(account_id=account_id)
                organization = participant.organization_id
            else:
                staff_user = Staff.objects.get(account_id=account_id)
                organization = staff_user.organization_id
                
            # Filter methods based on the organization
            methods_list = Method.objects.filter(organization_id=organization)

            # Serialize data
            serialized_data = []
            for method in methods_list:
                analytes_count = method.analyte_set.count()  # Count analytes associated with the method
                method_data = model_to_dict(method)
                method_data['analytes_count'] = analytes_count
                serialized_data.append(method_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

class MethodsPostAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            if Method.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Method with this name already exists in the organization."
                })
            # Create a new method
            method = Method.objects.create(
                organization_id=organization,
                code=request.data['code'],
                name=request.data['name'],
                status=request.data['status'],
                date_of_addition=timezone.now(),
            )
            user_account = UserAccount.objects.get(id=account_id)
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])

            # Save data in activity log as a single field
            activity_log = ActivityLogUnits.objects.create(
                added_by= user_account,
                organization_id=organization,                
                method_id=method,
                old_value=None,
                new_value=changes_string,
                date_of_addition=timezone.now(),
                actions='Added',
                type="Method"
            )

            method_serializer= MethodSerializer(method) 
            return Response({
                "status": status.HTTP_201_CREATED,
                "method_data": method_serializer.data,
                "activity_log_data": ActivityLogUnitsSerializer(activity_log).data,
                "message": "Method added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class MethodsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)

            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Retrieve the existing method object
            method = Method.objects.get(id=kwargs.get('id'), organization_id=organization)

            # Store old values before updating
            old_values = {field: getattr(method, field) for field in ["name", "code", "status"]}

            serializer = MethodSerializer(method, data=request.data, partial=True)

            if serializer.is_valid():
                updated_method = serializer.save()

                # Retrieve new values after updating
                new_values = {field: getattr(updated_method, field) for field in ["name", "code", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    method_id=method,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    actions="Updated",
                    type="Method"
                )

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Method information updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('id')
            if not user_id:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "User ID not provided."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch user_type based on user_id
            user_type = UserAccount.objects.get(id=user_id)
            
            if user_type.account_type == 'labowner':
                try:
                    participant = Lab.objects.get(account_id=user_id)
                    organization = participant.organization_id
                    schemelist = Scheme.objects.filter(organization_id=organization.id)
                except Lab.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Lab not found."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    staff_member = Staff.objects.get(account_id=user_id)
                    organization = staff_member.organization_id
                    schemelist = Scheme.objects.filter(organization_id=organization.id)
                except Staff.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Staff member not found."
                    }, status=status.HTTP_404_NOT_FOUND)
              
                serialized_data = []
                for scheme in schemelist:
                    # Ensure the scheme is saved to get an ID before accessing the analytes field
                    if scheme.pk is None:
                        scheme.save()
                    # analytes_count = scheme.analytes.count()
                    # Handle analytes as a CharField
                    analytes_list = scheme.analytes.split(',') if scheme.analytes else []
                    analytes_count = len(analytes_list)
                    # Serialize scheme data
                    scheme_data = model_to_dict(scheme, exclude=['analytes'])  # Exclude non-serializable fields

                    # Convert analytes to a list of dictionaries (if analyte IDs or names are stored)
                    analytes = [{"id": analyte_id} for analyte_id in analytes_list]  
                    scheme_data['analytes'] = analytes
                    scheme_data['noofanalytes'] = analytes_count

                    # Update status based on number of analytes
                    
                    # if analytes_count != 0 and scheme.status != 'Active':
                    #     scheme= Scheme.objects.filter(id=scheme.id).update(status="Active")
                    #     print("scheme", scheme)
                    # elif analytes_count == 0 and scheme.status != 'Inactive':
                    #     scheme=Scheme.objects.filter(id=scheme.id).update(status="Inactive")

                    if scheme.added_by:  # Check if added_by_id is not None
                        print("added", scheme.added_by)
                        # user_account = UserAccount.objects.get(id=scheme.added_by.id)
                        scheme_data['added_by'] = scheme.added_by.username
                    else:
                        scheme_data['added_by'] = None
                    
                    serialized_data.append(scheme_data)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serialized_data
            }, status=status.HTTP_200_OK)
        
        except Organization.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Organization not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SchemePostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)

            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the UserAccount object for the added_by field
            user_account = UserAccount.objects.get(id=account_id)
            user_name = user_account.username
            print("status in request", request.data['status'])

            if Scheme.objects.filter(organization_id=organization, name=request.data['name']).exists():
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "A Scheme with this name already exists in the organization."
                })

            # Create a new Scheme
            scheme = Scheme.objects.create(
                organization_id=organization,
                name=request.data['name'],
                price=request.data['price'],
                date_of_addition=timezone.now(),
                added_by=user_account,  # Use the UserAccount object
                status=request.data['status'],
            )
            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "price"]])
            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                scheme_id=scheme,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                added_by=user_account,  # Use the UserAccount object
                actions='Added',
                type="Scheme"
            )

            scheme_serializer = SchemeSerializer(scheme)
            return Response({"status": status.HTTP_201_CREATED, "unit_data": scheme_serializer.data,
                             "message": "Scheme added successfully."})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Staff user not found."})
        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "User account not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            scheme = Scheme.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(scheme, field) for field in ["name", "price"]}
            
            serializer = SchemeSerializer(scheme, data=request.data, partial=True)

            if serializer.is_valid():
                updated_analyte = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_analyte, field) for field in ["name", "price"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    scheme_id=scheme,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    # added_by=request.user,
                    actions="Updated",
                    type="Scheme"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Scheme Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class SchemeDeleteAPIView(APIView):
   

    def delete(self, request, *args, **kwargs):
        try:
            Scheme.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})     

class CycleAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            print("id in front end", kwargs.get('id'))
            account_id = kwargs.get('id')
            user_account = UserAccount.objects.get(id=account_id)

            if user_account.account_type == 'labowner':
                participant = Lab.objects.get(account_id=account_id)
                organization = participant.organization_id
            else:
                staff_user = Staff.objects.get(account_id=account_id)
                organization = staff_user.organization_id

            # Filter cycles based on the organization
            cycle_list = Cycle.objects.filter(organization_id=organization)

            serialized_data = []
            for cycle in cycle_list:
                # Initialize cycle_data dictionary
                cycle_data = model_to_dict(cycle)

                # Retrieve the scheme associated with the cycle
                scheme = cycle.scheme_name
                
                if scheme:
                    # analytes_count = scheme.analytes.count()
                    analytes_list = scheme.analytes.split(',') if scheme.analytes else []
                    analytes_count = len(analytes_list)
                    
                    # Serialize scheme data excluding analytes
                    scheme_data = model_to_dict(scheme, exclude=['analytes']) 

                    # Convert analytes to a list of dictionaries (assuming analyte IDs are stored as the string values)
                    # Here, we're assuming only analyte IDs are stored. You may customize the dictionary fields as needed.
                    analytes = [{"id": analyte_id.strip()} for analyte_id in analytes_list]  # Stripping spaces for safety
                    scheme_data['analytes'] = analytes  # Include the analytes in the response
                    scheme_data['noofanalytes'] = analytes_count  # Include the number of analytes 
                    
                    # # Convert analytes to a list of dictionaries
                    # analytes = list(scheme.analytes.values('id', 'name', 'code', 'status'))  
                    # scheme_data['analytes'] = analytes
                    # scheme_data['noofanalytes'] = analytes_count

                    cycle_data['scheme_name'] = scheme.name
                    cycle_data['price'] = scheme.price
                    cycle_data['scheme_id'] = scheme.id
                    print("scheme id",  cycle_data['scheme_id'])
                    cycle_data['noofanalytes'] = analytes_count  # Ensure noofanalytes is added to cycle_data
                else:
                    cycle_data['scheme_name'] = None
                    cycle_data['scheme_id'] = None  # Handle case where scheme is None
                    cycle_data['noofanalytes'] = 0  # or None, depending on your preference

                serialized_data.append(cycle_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No cycle records found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})            
            
class CyclePostAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            account_id = request.data['added_by']
 
            staff_user = Staff.objects.get(account_id=account_id)

            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            scheme_id = request.data.get('scheme_name')  # Assuming 'scheme' is sent in the request data
            scheme = get_object_or_404(Scheme, pk=scheme_id)
            scheme_id = request.data.get('scheme_name')  # Assuming 'scheme' is sent in the request data
            scheme = get_object_or_404(Scheme, pk=scheme_id)

            # Parse start_date and end_date from request data
            start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()  # Convert string to date
            end_date = datetime.strptime(request.data['end_date'], '%Y-%m-%d').date()  # Convert string to date

            print("start and end date ", start_date, end_date)

            # Calculate the difference in months
            total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

            # Convert the total months into years and months
            years_duration = total_months // 12
            months_duration = total_months % 12

            # Determine the message based on the calculated duration
            if years_duration > 0 and months_duration > 0:
                duration_message = f"{years_duration} year(s) and {months_duration} month(s)"
            elif years_duration > 0:
                duration_message = f"{years_duration} year(s)"
            else:
                duration_message = f"{months_duration} month(s)"

            print("calculation with start and end date", duration_message)


            # Create a new Analyte
            cycle = Cycle.objects.create(
                organization_id= organization,
                scheme_name=scheme,
                cycle_no=request.data['cycle_no'],
                cycle=duration_message,
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
                rounds=request.data['rounds'],
                # status=request.data['status'],
                # status=request.data['status'],
                # added_by=user_account,
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["scheme_name", "cycle_no", "rounds", "cycle"]])
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["scheme_name", "cycle_no", "rounds", "cycle"]])

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                cycle_id=cycle,
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                # added_by=user_account,
                actions='Added',
                type="Cycle"
            )

            cycle_serializer = CycleSerializer(cycle)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": cycle_serializer.data,
                             "message": "Cycle added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CycleUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            cycle = Cycle.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status", "start_date", "end_date"]}
            # old_values = {field: getattr(cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status", "start_date", "end_date"]}
            
            serializer = CycleSerializer(cycle, data=request.data, partial=True)

            if serializer.is_valid():
                updated_cycle = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    cycle_id=cycle,
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    # added_by=request.user,
                    actions="Updated",
                    type="Cycle"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Cycle Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})


        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CycleDeleteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        cycle_id = kwargs.get('id')
        try:
            cycle = Cycle.objects.get(id=cycle_id)
            
            # Check if the cycle is used in any round
            if Round.objects.filter(cycle_no=cycle.cycle_no).exists():
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Cannot delete cycle. It has been utilized in round."})
            
            cycle.delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})

class InstrumentTypeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # Get the account_id from kwargs
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter instrument types based on the organization
            instrument_type_list = InstrumentType.objects.filter(organization_id=organization)
            
            # Serialize data and include instrument counts
            serialized_data = []
            for instrument_type in instrument_type_list:
                instruments = Instrument.objects.filter(instrument_type=instrument_type)
                instrument_count = instruments.count()
                instrument_type_data = model_to_dict(instrument_type)
                instrument_type_data['instrument_count'] = instrument_count
                serialized_data.append(instrument_type_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class InstrumentTypeCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            print("account id received here is", account_id)
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Create a new instrument_type
            instrument_type = InstrumentType.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )

            # Fetch the UserAccount instance
            user_account = UserAccount.objects.get(id=account_id)

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                organization_id=organization,
                added_by=user_account,
                instrumenttype_id=instrument_type,
                date_of_addition=timezone.now(),
                field_name="name",
                old_value=None,
                new_value=request.data['name'],
                actions='Added',
                type="Instruments"
            )

            # Serialize the created instrument_type
            serializer = InstrumentTypeSerializer(instrument_type)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "unit_data": serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Instrument type added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid user account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class UpdateInstrumentTypeView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing instrument_type object
            instrument_type = InstrumentType.objects.get(id=kwargs.get('id'), organization_id=organization)
            
            # Get the old value before updating the instrument_type
            old_value = instrument_type.name
            user_account = UserAccount.objects.get(id=account_id)
            # Serialize the updated data
            serializer = InstrumentTypeSerializer(instrument_type, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the InstrumentType table
                updated_instrument_type = serializer.save()
                
                # Save data in activity log
                ActivityLogUnits.objects.create(
                    organization_id=organization,
                    added_by=user_account,
                    instrumenttype_id=instrument_type,
                    date_of_addition=timezone.now(),
                    field_name="name",
                    old_value=old_value,
                    new_value=serializer.validated_data['name'],
                    actions='Updated',
                    type="Instruments"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Instrument Type Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

#Analyte adding reagents
class AnalytesReagentsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            reagents = analyte.reagents.all()  # Fetch all reagents associated with the analyte
            reagent_ids = [reagent.id for reagent in reagents]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "reagents": reagent_ids  # Send list of reagent IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#Equipments in manufacturer
class InstrumentsInManufacturerAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            manufactural = Manufactural.objects.get(id=id)
            instruments = Instrument.objects.filter(manufactural=manufactural)
            
            # Serialize data including instrument count
            serialized_data = InstrumentSerializer(instruments, many=True).data
            
            # Calculate instrument count
            instrument_count = instruments.count()
            
            # Prepare response data
            response_data = {
                "status": status.HTTP_200_OK,
                "data": serialized_data,
            }
            
            return Response(response_data)
        
        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Manufacturer not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#reagents in manufacturer
class ReagentsInManufacturerAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            manufactural = Manufactural.objects.get(id=id)
            reagents = Reagents.objects.filter(manufactural=manufactural)
            
            # Serialize data including instrument count
            serialized_data = InstrumentSerializer(reagents, many=True).data
            
            # Calculate instrument count
            reagents_count = reagents.count()
            
            # Prepare response data
            response_data = {
                "status": status.HTTP_200_OK,
                "data": serialized_data,
            }
            
            return Response(response_data)
        
        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Manufacturer not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#Equipments in Type
class InstrumentAndInstrumentTypeAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            instrument_type = InstrumentType.objects.get(id=id)
            instruments = Instrument.objects.filter(instrument_type=instrument_type)
            
            # Serialize data including instrument count
            serialized_data = InstrumentSerializer(instruments, many=True).data
            
            # Calculate instrument count
            instrument_count = instruments.count()
            
            # Prepare response data
            response_data = {
                "status": status.HTTP_200_OK,
                "data": serialized_data,
            }
            
            return Response(response_data)
        
        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "InstrumentType not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteAddReagentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            
            # Ensure 'reagents' is parsed as a list of integers
            reagents = request.data.get('reagents', [])
            if isinstance(reagents, str):
                reagents = list(map(int, reagents.split(',')))
            
            analyte.reagents.set(reagents)  # Assuming reagents are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Reagents added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class AnalyteUpdateReagentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            reagents = request.data.get('reagents', [])
            if isinstance(reagents, str):
                reagents = list(map(int, reagents.split(',')))
            
            analyte.reagents.set(reagents)  # Assuming reagents are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Reagents updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

# Scheme add Analytes
class SchemeAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            scheme = Scheme.objects.get(id=id)
            
            # Get the analytes field, default to an empty string if None
            analytes_str = scheme.analytes or ""  # This assumes 'analytes' is a char field

            # Split the comma-separated string into a list of strings, then convert to integers
            analytes = [int(analyte_id) for analyte_id in analytes_str.split(',') if analyte_id.strip()]
            
            # Serialize data
            serialized_data = {
                "analytes": analytes  # Send list of analyte IDs as integers
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Scheme not found."})
        
        except ValueError:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Error parsing analytes."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeAddAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, id, *args, **kwargs):
        print("sdhs id", id, kwargs.get('id'))

        try:
            analyte = Scheme.objects.get(id=id)
            print("amnalut", analyte) 
            # Ensure 'instruments' is parsed as a list of integers
            analytes_ids_str = request.data.get('analytes', '')
            analytes_ids= [int(sid) for sid in analytes_ids_str.split(',') if sid.isdigit()]
            # print("analytes", analytes_ids),
            analyte.analytes = analytes_ids,
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Equipments added to analyte successfully."})
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeUpdateAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Scheme object by ID
            scheme = Scheme.objects.get(id=id)

            # Get 'analytes' from the request data
            analytes_data = request.data.get('analytes', '')
            # Handle if the frontend sends a comma-separated string
            if isinstance(analytes_data, str):
                # Split the string into a list of integers (IDs)
                analytes_ids = [int(aid) for aid in analytes_data.split(',') if aid.isdigit()]
            # Handle if the frontend sends an array of IDs
            elif isinstance(analytes_data, list):
                # Ensure all elements in the list are integers
                analytes_ids = [int(aid) for aid in analytes_data if isinstance(aid, int)]
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST, 
                    "message": "Invalid format for analytes data."
                })

            # Store the list of IDs as a comma-separated string in the 'analytes' CharField
            scheme.analytes = ','.join(map(str, analytes_ids))
            # Save the updated scheme object
            scheme.save()

            # Optionally serialize the updated scheme
            serialized_data = SchemeSerializer(scheme).data

            return Response({
                "status": status.HTTP_200_OK, 
                "analyte_data": serialized_data, 
                "message": "Analytes updated successfully."
            })

        except Scheme.DoesNotExist:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST, 
                "message": "Scheme does not exist."
            })
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST, 
                "message": str(e)
            })

# Analytes Assocaited With Cycle
class AnalytesByCycleAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permissions as needed

    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Cycle object based on id
            scheme = Scheme.objects.get(id=id)
            
            # Retrieve all analytes associated with the cycle
            analytes = Analyte.objects.filter(scheme=scheme)
            
            # Serialize the queryset of analytes
            serializer = AnalyteSerializer(analytes, many=True)
            
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Scheme object does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})


class AnalytesListAPIView(APIView):
      def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('id')
            # Fetch user_type based on user_id
            try:
                user_type = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "User account not found."
                }, status=status.HTTP_400_BAD_REQUEST)
            # print("vvvvvvvvvvv", user_id, user_type)
            if user_type.account_type == 'labowner':
                try:
                    participant = Lab.objects.get(account_id=user_id)
                    organization = participant.organization_id
                    analyte_list = Analyte.objects.filter(organization_id=organization)
                except Lab.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Lab not found."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                    staff_user = Staff.objects.get(account_id=user_id)
                    organization = staff_user.organization_id
                    analyte_list = Analyte.objects.filter(organization_id=organization)

            serialized_data = AnalyteSerializer(analyte_list, many=True).data
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Analyte records found."})


class AnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')  # Use 'added_by' from request data
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Create a new Analyte
            analyte = Analyte.objects.create(
                organization_id=organization,
                name=request.data['name'],
                code=request.data['code'],
                status=request.data['status'],
                date_of_addition=timezone.now(),
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])
            user_account=UserAccount.objects.get(id=account_id)
            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                added_by=user_account,
                analyte_id=analyte,
                old_value=None,
                new_value=changes_string,
                date_of_addition=timezone.now(),
                actions='Added',
                type="Analyte"
            )

            # Serialize the created analyte and activity log
            analyte_serializer = AnalyteSerializer(analyte)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({
                "status": status.HTTP_201_CREATED,
                "analyte_data": analyte_serializer.data,
                "activity_log_data": activity_log_serializer.data,
                "message": "Analyte added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteUpdateAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def put(self, request, *args, **kwargs):
        try:
            analyte_id = kwargs.get('id')
            if not analyte_id:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte ID is required."})

            account_id = request.data.get('added_by')
            if not account_id:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Added by field is required."})

            staff_user = Staff.objects.get(account_id=account_id)
            analyte = Analyte.objects.get(id=analyte_id)

            old_values = {
                'name': analyte.name,
                'code': analyte.code,
                'status': analyte.status,
            }

            serializer = AnalyteSerializer(analyte, data=request.data, partial=True)

            if serializer.is_valid():
                updated_analyte = serializer.save()

                new_values = {
                    'name': updated_analyte.name,
                    'code': updated_analyte.code,
                    'status': updated_analyte.status,
                }

                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                activity_log = ActivityLogUnits.objects.create(
                    analyte_id=analyte,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    date_of_addition=timezone.now(),
                    actions='Updated',
                    type="Analyte"

                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Analyte information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        

class NewsListView(APIView):
    permission_classes = (AllowAny,)
    # API FOR STAFF + Participant dashboard**************
    def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('id')
            if not user_id:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "User ID not provided."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch user_type based on user_id
            try:
                user_type = UserAccount.objects.get(id=user_id)
                
            except UserAccount.DoesNotExist:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "User account not found."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            newss = None 
            if user_type.account_type == 'labowner':
                try:
                    participant = Lab.objects.get(account_id=user_id)
                    organization = participant.organization_id
                    if organization is None:
                        raise Organization.DoesNotExist
                    newss = News.objects.filter(organization_id=organization.id)
                except Lab.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Lab not found."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    staff_member = Staff.objects.get(account_id=user_id)
                    organization = staff_member.organization_id
                    # staff_member = Staff.objects.get(account_id=user_id)
                    # organization = staff_member.organization_id
                    if organization is None:
                        raise Organization.DoesNotExist
                    newss = News.objects.filter(organization_id=organization.id)
                    
                except Staff.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Staff member not found."
                    }, status=status.HTTP_404_NOT_FOUND)

            if newss is not None and newss.exists():
                serializer = NewsSerializer(newss, many=True)
                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "No news found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        except Organization.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Organization not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# API FOR STAFF dashboard**************
    # def get(self, request, *args, **kwargs):
    #     try:
    #         # Get the staff user's account_id from query params
    #         account_id = kwargs.get('id')
    #         # print("idddddddddd",account_id)
    #         # Fetch the staff user based on account_id
    #         staff_user = Staff.objects.get(account_id=account_id)
            
    #         # Retrieve the organization associated with the staff user
    #         organization = staff_user.organization_id
            
    #         # Filter news based on the organization
    #         news_list = News.objects.filter(organization_id=organization)
            
    #         # Serialize data
    #         serialized_data = NewsSerializer(news_list, many=True).data
            
    #         return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
    #     except Staff.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
    #     except News.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No News records found."})

    #  API for Staff and PArticipant Dashboard ***********************  
    
#******** fOR only pARTICIPANT dashboard
# class NewsListViewParticipant(APIView):
#     permission_classes = (AllowAny,)  
#     def get(self, request, *args, **kwargs):
#         try:
#             # Get the staff user's account_id from query params
#             account_id = kwargs.get('id')
#             # print("idddddddddd",account_id)
#             # Fetch the staff user based on account_id
#             participant = Lab.objects.get(account_id=account_id)
            
#             # Retrieve the organization associated with the staff user
#             organization = participant.organization_id
            
#             # Filter news based on the organization
#             news_list = News.objects.filter(organization_id=organization)
            
#             # Serialize data
#             serialized_data = NewsSerializer(news_list, many=True).data
            
#             return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
#         except Lab.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
#         except News.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No News records found."})  
        
class NewsAddAPIView(APIView):
    permission_classes = (AllowAny,)    
    def post(self, request, *args, **kwargs):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Fetch the staff user based on account_id
                account_id1 = request.data.get('added_by')  # Use 'added_by' from request data
                print("idddddddddddddddddddd",account_id1)
                staff_user = Staff.objects.get(account_id=account_id1)
            # Retrieve the organization associated with the staff user
                organization = staff_user.organization_id
                # print("orgID/Name", organization)
                user_account = UserAccount.objects.get(id=account_id1)
                date_of_addition = timezone.now()
                # news = serializer.save(added_by=user_account)
                news = serializer.save(
                    added_by=user_account,
                    organization_id=organization,
                    date_of_addition=date_of_addition
                )
                # Serialize the organization object or get its specific attributes
                # organization_data = {
                #     'id': organization.id,
                #     'name': organization.name,
                #     # Add other fields as needed
                # }
                
                news_data = {
                    # 'organization_id': organization_data,
                    # 'added_by':account_id1,
                    # 'id': news.id,
                    'title': news.title,
                    'date_of_addition': date_of_addition,
                    'description': news.description,
                    'picture': news.picture.url if news.picture else None,
                    # Add other fields as needed
                }
                print("username",user_account)
                print("org",organization)
                return Response({"status": status.HTTP_201_CREATED, "data": news_data})

            except UserAccount.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        return Response({"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors})

# Sample
class SampleListView(APIView):   
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter samples based on the organization
            sample_list = Sample.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = []
            for sample in sample_list:
                sample_data = {
                    'id': sample.id,
                    'samplename': sample.samplename,
                    'sampleno': sample.sampleno,
                    'detail': sample.detail,
                    'notes': sample.notes,
                    'scheme_id': sample.scheme_id.id if sample.scheme_id else None,
                    'status': sample.status,
                }
                
                # Fetch name from Scheme table based on scheme_id
                if sample.scheme_id:
                    scheme = Scheme.objects.get(id=sample.scheme_id.id)
                    sample_data['scheme'] = scheme.name
                    
                    # Count the analytes from the scheme's analytes field (comma-separated IDs)
                    analytes_ids = scheme.analytes.split(',')  # Convert comma-separated string to list
                    analytes_count = len([analyte for analyte in analytes_ids if analyte])  # Filter out empty values
                    sample_data['noofanalytes'] = analytes_count
                else:
                    sample_data['scheme'] = None
                    sample_data['noofanalytes'] = 0
                
                # Convert analytes to a list of dictionaries
                analytes = list(sample.analytes.values('id', 'name', 'code', 'status'))
                sample_data['analytes'] = analytes
                sample_data['noofanalytes'] = analytes_count
    
                # Fetch cycle_no from Cycle model based on scheme_id
                if sample.scheme_id:
                    cycle = Cycle.objects.filter(scheme_name_id=sample.scheme_id.id).first()
                    sample_data['cycle_no'] = cycle.cycle_no if cycle else None
                else:
                    sample_data['cycle_no'] = None

                serialized_data.append(sample_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Sample records found."})

class SamplePostView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            # print("Accounttttttttttttt", account_id)
            staff_user = Staff.objects.get(account_id=account_id)
            organization = staff_user.organization_id
            id = request.data.get('scheme')
            Cycle_id = Cycle.objects.get(id=id)
            print("cycle in sample", Cycle_id.scheme_name)
            # Assuming Sample model has account_id field as ForeignKey to UserAccount
            # Fetch the UserAccount instance based on account_id
           
            user_account = get_object_or_404(UserAccount, id=account_id)
            sample = Sample.objects.create(
                organization_id = organization,
                samplename=request.data['samplename'],
                sampleno=request.data['sampleno'],
                scheme_id=Cycle_id.scheme_name,
                Cycle_id=Cycle_id,
                detail=request.data['detail'],
                notes=request.data['notes'],
                # status=request.data['status'],
                added_by=user_account,
                date_of_addition=timezone.now(),
            )

            sample_serializer = SampleSerializer(sample)
            return Response({
                "status": status.HTTP_201_CREATED,
                "data": sample_serializer.data
            })
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Staff user does not exist."})
        
        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User account does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SampleListUpdateAPIView(APIView):
    def put(self, request, id, *args, **kwargs):
        try:
            sample = Sample.objects.get(id=id)
            serializer = SampleSerializer(sample, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Updated Successfully"})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sample with this ID doesn't exist."})

class SampleListDeleteAPIView(APIView):    
    def delete(self, request, *args, **kwargs):
        try:
            Sample.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."}) 

# Sample Analytes
class SampleAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            sample = Sample.objects.get(id=id)
            analytes = sample.analytes.all()  # Fetch all reagents associated with the analyte
            analyte_ids = [analyte.id for analyte in analytes]
            
            # Serialize data
            serialized_data = {
                #"scheme": SchemeSerializer(scheme).data,
                "analytes": analyte_ids  # Send list of reagent IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sample not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SampleAddAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, id, *args, **kwargs):
        print("sdhs id", id, kwargs.get('id'))

        try:
            analyte = Sample.objects.get(id=id)
            print("amnalut", analyte) 
            # Ensure 'instruments' is parsed as a list of integers
            analytes = request.data.get('analytes', [])
            print("analytes2", analytes)
            if isinstance(analytes, str):
                analytes = list(map(int, analytes.split(',')))
            
            analyte.analytes.set(analytes)  # Assuming instruments are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Equipments added to analyte successfully."})
        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SampleUpdateAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
       
        try:
            sample = Sample.objects.get(id=id)
            analytes = request.data.get('analytes', [])
            if isinstance(analytes, str):
                analytes = list(map(int, analytes.split(',')))
            
            sample.analytes.set(analytes)  # Assuming reagents are passed as a list of IDs
            sample.save()
            serialized_data = SampleSerializer(sample).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Reagents updated for Analyte successfully."})
        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sample does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


#Analyte adding equipments
class AnalytesEquipmentsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            instruments = analyte.instruments.all()  # Fetch all instruments associated with the analyte
            instrument_ids = [instrument.id for instrument in instruments]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "equipments": instrument_ids  # Send list of instrument IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteAddEquipmentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            
            # Ensure 'instruments' is parsed as a list of integers
            instruments = request.data.get('equipments', [])
            if isinstance(instruments, str):
                instruments = list(map(int, instruments.split(',')))
            
            analyte.instruments.set(instruments)  # Assuming instruments are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Equipments added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class AnalyteUpdateEquipmentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            instruments = request.data.get('equipments', [])
            if isinstance(instruments, str):
                instruments = list(map(int, instruments.split(',')))
            
            analyte.instruments.set(instruments)  # Assuming instruments are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Equipments updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#Analyte adding methods
class AnalytesMethodsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            methods = analyte.methods.all()  # Fetch all methods associated with the analyte
            method_ids = [method.id for method in methods]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "methods": method_ids  # Send list of methods IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteAddMethodsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            
            # Ensure 'methods' is parsed as a list of integers
            methods = request.data.get('methods', [])
            if isinstance(methods, str):
                methods = list(map(int, methods.split(',')))
            
            analyte.methods.set(methods)  # Assuming methods are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Methods added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class AnalyteUpdateMethodsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            methods = request.data.get('methods', [])
            if isinstance(methods, str):
                methods = list(map(int, methods.split(',')))
            
            analyte.methods.set(methods)  # Assuming methods are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Methods updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#Analytes assocaited with method~
class AnalytesByMethodAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permissions as needed

    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Method object based on id
            method = Method.objects.get(id=id)
            
            # Retrieve all analytes associated with the method
            analytes = Analyte.objects.filter(methods=method)
            
            # Serialize the queryset of analytes
            serializer = AnalyteSerializer(analytes, many=True)
            
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        
        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Method object does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

#Analytes assocaited with instrument~
class AnalytesByInstrumentAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permissions as needed

    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Instrument object based on id
            instrument = Instrument.objects.get(id=id)
            
            # Retrieve all analytes associated with the method
            analytes = Analyte.objects.filter(instruments=instrument)
            
            # Serialize the queryset of analytes
            serializer = AnalyteSerializer(analytes, many=True)
            
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        
        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Instrument object does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

#Analytes assocaited with reagent
class AnalytesByReagentAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permissions as needed

    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Method object based on id
            reagent = Reagents.objects.get(id=id)
            
            # Retrieve all analytes associated with the reagent
            analytes = Analyte.objects.filter(reagents=reagent)
            
            # Serialize the queryset of analytes
            serializer = AnalyteSerializer(analytes, many=True)
            
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        
        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Reagents object does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

#Analytes assocaited with unit~
class AnalytesByUnitAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permissions as needed

    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the Units object based on id
            unit = Units.objects.get(id=id)
            
            # Retrieve all analytes associated with the unit
            analytes = Analyte.objects.filter(units=unit)
            
            # Serialize the queryset of analytes
            serializer = AnalyteSerializer(analytes, many=True)
            
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        
        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Units object does not exist."})
        
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)})

#Analyte adding qualitativeunits
class AnalytesQualitativeUnitsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            qualitativetype = analyte.qualitativetype.all()  # Fetch all qualitativetype associated with the analyte
            qualitativetype_ids = [qualitativetype.id for qualitativetype in qualitativetype]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "qualitativetype": qualitativetype_ids  # Send list of qualitativetype IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteAddQualitativeUnitsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            
            # Ensure 'qualitativetype' is parsed as a list of integers
            qualitativetype = request.data.get('qualitativetype', [])
            if isinstance(qualitativetype, str):
                qualitativetype = list(map(int, qualitativetype.split(',')))
            
            analyte.qualitativetype.set(qualitativetype)  # Assuming qualitativetype are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "qualitativetype added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class AnalyteUpdateQualitativeUnitsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            qualitativetype = request.data.get('qualitativetype', [])
            if isinstance(qualitativetype, str):
                qualitativetype = list(map(int, qualitativetype.split(',')))
            
            analyte.qualitativetype.set(qualitativetype)  # Assuming qualitativetype are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "qualitativetype updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

#Analyte adding units
class AnalytesUnitsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            units = analyte.units.all()  # Fetch all units associated with the analyte
            unit_ids = [unit.id for unit in units]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "units": unit_ids,  # Send list of units IDs
                "master_unit": analyte.master_unit.id if analyte.master_unit else None,
                "conversion_formula": analyte.conversion_formula if analyte.conversion_formula else None
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteAddUnitsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            
            # Ensure 'units' and 'masterUnit' are parsed correctly
            units = request.data.get('units', [])
            if isinstance(units, str):
                units = list(map(int, units.split(',')))

            master_unit_id = request.data.get('masterUnit', None)

            if master_unit_id:
                master_unit = Units.objects.get(id=master_unit_id)
                analyte.master_unit = master_unit
                analyte.conversion_formula = request.data.get('conversion_formula')

            analyte.units.set(units)  # Assuming units are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Units added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Master unit not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class AnalyteUpdateUnitsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=id)
            units = request.data.get('units', [])
            if isinstance(units, str):
                units = list(map(int, units.split(',')))

            master_unit_id = request.data.get('masterUnit', None)

            if master_unit_id:
                master_unit = Units.objects.get(id=master_unit_id)
                analyte.master_unit = master_unit
                analyte.conversion_formula = request.data.get('conversion_formula')

            analyte.units.set(units)  # Assuming units are passed as a list of IDs
            analyte.save()

            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Units updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Master unit not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class DeleteInstrumentTypeView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            instrument_type = InstrumentType.objects.get(id=kwargs.get('id'))
            instrument_type.delete()  # Deletes the InstrumentType object from the database
            return Response({"status": status.HTTP_200_OK, "message": "InstrumentType deleted successfully."})

        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such InstrumentType to delete."})

class DeleteMethodView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            method = Method.objects.get(id=kwargs.get('id'))
            method.delete()  # Deletes the Method object from the database
            return Response({"status": status.HTTP_200_OK, "message": "Method deleted successfully."})

        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Method to delete."})

class DeleteReagentView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            reagent = Reagents.objects.get(id=kwargs.get('id'))
            reagent.delete()  # Deletes the Reagents object from the database
            return Response({"status": status.HTTP_200_OK, "message": "Reagent deleted successfully."})

        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Method to delete."})

class DeleteAnalyteView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=kwargs.get('id'))
            analyte.delete()  # Deletes the Analyte object from the database
            return Response({"status": status.HTTP_200_OK, "message": "Analyte deleted successfully."})

        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Analyte to delete."})

class DeleteInstrumentView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            instrument = Instrument.objects.get(id=kwargs.get('id'))
            instrument.delete()  # Deletes the Instrument object from the database
            return Response({"status": status.HTTP_200_OK, "message": "Instrument deleted successfully."})

        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Instrument to delete."})

class DeleteMAnufacturerView(APIView):
    permission_classes = (AllowAny,)
    
    def delete(self, request, *args, **kwargs):
        try:
            manufactural = Manufactural.objects.get(id=kwargs.get('id'))
            manufactural.delete()  # Deletes the Manufactural object from the database
            return Response({"status": status.HTTP_200_OK, "message": "Manufacturer deleted successfully."})

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Manufacturer to delete."})
class AnalytesListForSchemeAPIView(APIView):
   
    def get(self, request, *args, **kwargs):
        scheme_id = kwargs.get('id')
        try:
            scheme = Scheme.objects.get(id=scheme_id )
            # print("analytes", scheme.analytetype)
            organization_id=scheme.organization_id
            print("organization_id", organization_id.id)

            if scheme.analytetype == "Qualitative":
                analyte_list = Analyte.objects.filter(units__name="Pos/Neg/Equi", organization_id=organization_id)
                print("analyte_list in qualitative", analyte_list)
            else:
                analyte_list = Analyte.objects.filter(organization_id=organization_id).exclude(units__name="Pos/Neg/Equi")

            # analyte_ids = [analyte.id for analyte in analyte_list]


            serialized_data = AnalyteSerializer(analyte_list, many=True).data
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Analyte records found."})