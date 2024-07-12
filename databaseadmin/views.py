from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from databaseadmin.models import ParticipantProvince,ParticipantCountry, ParticipantType,ParticipantSector,Department,Designation,District,City,News,Instrument, Units, ActivityLogUnits,Reagents , Manufactural, Method,InstrumentType, Analyte

from databaseadmin.serializers import CountrySerializer,NewsSerializer,InstrumentSerializer, MethodSerializer,AnalyteSerializer, InstrumentTypeSerializer, UnitsSerializer, ActivityLogUnitsSerializer, ReagentsSerializer, ManufacturalSerializer, Scheme, Cycle,Sample,ParticipantTypeSerializer, ParticipantSectorSerializer,DepartmentSerializer,DesignationSerializer,DistrictSerializer,CitySerializer,SchemeSerializer, CycleSerializer,  SampleSerializer, ProvinceSerializer

from labowner.models import Lab
from staff.models import Staff

from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils import timezone
from account.models import UserAccount
from organization.models import Organization
from django.shortcuts import get_object_or_404
import datetime

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
            
            # Create a new sector
            sector = ParticipantSector.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                sector_id=sector,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    sector_id=sector,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new type
            type = ParticipantType.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                type_id=type,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    type_id=type,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Create a new city
            city = City.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                city_id=city,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    city_id=city,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new province
            province = ParticipantProvince.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                province_id=province,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    province_id=province,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new country
            country = ParticipantCountry.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                country_id=country,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    country_id=country,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new district
            district = District.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                district_id=district,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    district_id=district,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new department
            department = Department.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                department_id=department,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    department_id=department,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
            # Create a new designation
            designation = Designation.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                designation_id=designation,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    designation_id=designation,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter units based on the organization
            units_list = Units.objects.filter(organization_id=organization)
            
            # Serialize data
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
            
            # Create a new unit
            unit = Units.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}, "

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                unit_id=unit,
                old_value="", 
                new_value=changes_string, 
                date_of_addition=timezone.now(),
                actions='Added'  # Specify action as 'Added'
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
                ActivityLogUnits.objects.create(
                    unit_id=unit,
                    old_value=", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string, 
                    date_of_addition=timezone.now(),
                    actions='Updated'  
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
            
class InstrumentsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
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
            ActivityLogUnits.objects.create(
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
                ActivityLogUnits.objects.create(
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

            # Try to get the data from Units
            try:
                unit = Units.objects.get(id=id_value)
                activity_log = ActivityLogUnits.objects.filter(unit_id=unit.id)
            except Units.DoesNotExist:
                # If Units does not exist, try InstrumentType
                try:
                    instrument_type = InstrumentType.objects.get(id=id_value)
                    activity_log = ActivityLogUnits.objects.filter(instrumenttype_id=instrument_type.id)
                except InstrumentType.DoesNotExist:
                    # If InstrumentType also does not exist, try Reagents
                    try:
                        reagent = Reagents.objects.get(id=id_value)
                        activity_log = ActivityLogUnits.objects.filter(reagent_id=reagent.id)
                    except Reagents.DoesNotExist:
                        # If InstrumentType also does not exist, try Reagents
                        try:
                            method = Method.objects.get(id=id_value)
                            activity_log = ActivityLogUnits.objects.filter(method_id=method.id)
                        except Method.DoesNotExist:
                            try:
                                scheme = Scheme.objects.get(id=id_value)
                                activity_log = ActivityLogUnits.objects.filter(scheme_id=scheme.id)
                            except Scheme.DoesNotExist:
                                try:
                                    manufactural = Manufactural.objects.get(id=id_value)
                                    activity_log = ActivityLogUnits.objects.filter(manufactural_id=manufactural.id)
                                except Manufactural.DoesNotExist:
                                    try:
                                        sample = Sample.objects.get(id=id_value)
                                        activity_log = ActivityLogUnits.objects.filter(sample_id=sample.id)
                                    except Sample.DoesNotExist:
                                        try:
                                            instrument = Instrument.objects.get(id=id_value)
                                            activity_log = ActivityLogUnits.objects.filter(instrument_id=instrument.id)
                                        except Instrument.DoesNotExist:
                                            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No record exists."}) 
          

            serializer = ActivityLogUnitsSerializer(activity_log, many=True)
            if activity_log.exists():
                data = []
                for log_entry in serializer.data:
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
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
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
            ActivityLogUnits.objects.create(
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
                ActivityLogUnits.objects.create(
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
            print("AAAAAAAAA", account_id)
            
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

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
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

            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)

            # Retrieve the organization associated with the staff user
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

            # Create a new method
            method = Method.objects.create(
                organization_id=organization,
                code=request.data['code'],
                name=request.data['name'],
                status=request.data['status'],
                date_of_addition=timezone.now(),
            )

            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])

            # Save data in activity log as a single field
            activity_log = ActivityLogUnits.objects.create(
                method_id=method,
                old_value=None,
                new_value=changes_string,
                date_of_addition=timezone.now(),
                actions='Added',
                type="Method"
            )

            method_serializer = MethodSerializer(method)

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

                analytes_count = scheme.analytes.count()
                
                # Serialize scheme data
                scheme_data = model_to_dict(scheme, exclude=['analytes'])  # Exclude non-serializable fields
                
                # Convert analytes to a list of dictionaries
                analytes = list(scheme.analytes.values('id', 'name', 'code', 'status'))  
                scheme_data['analytes'] = analytes
                scheme_data['noofanalytes'] = analytes_count

                # Update status based on number of analytes
                if analytes_count > 0 and scheme.status != 'Active':
                    scheme.status = 'Active'
                    scheme.save()
                elif analytes_count == 0 and scheme.status != 'Inactive':
                    scheme.status = 'Inactive'
                    scheme.save()

                if scheme.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=scheme.added_by_id)
                    scheme_data['added_by'] = user_account.username
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
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "price", "status"]])

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                scheme=scheme,
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
            old_values = {field: getattr(scheme, field) for field in ["name", "price", "status"]}
            
            serializer = SchemeSerializer(scheme, data=request.data, partial=True)

            if serializer.is_valid():
                updated_analyte = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_analyte, field) for field in ["name", "price", "status"]}

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
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')

            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
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
                    analytes_count = scheme.analytes.count()
                    
                    # Serialize scheme data excluding analytes
                    scheme_data = model_to_dict(scheme, exclude=['analytes'])  
                    
                    # Convert analytes to a list of dictionaries
                    analytes = list(scheme.analytes.values('id', 'name', 'code', 'status'))  
                    scheme_data['analytes'] = analytes
                    scheme_data['noofanalytes'] = analytes_count

                    cycle_data['scheme_name'] = scheme.name
                    cycle_data['price'] = scheme.price
                    cycle_data['scheme_id'] = scheme.id
                else:
                    cycle_data['scheme_name'] = None
                    cycle_data['scheme_id'] = None  # Handle case where scheme is None

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

            # Create a new Analyte
            cycle = Cycle.objects.create(
                organization_id= organization,
                scheme_name=scheme,
                cycle_no=request.data['cycle_no'],
                cycle=request.data['cycle'],
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
            old_values = {field: getattr(cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status"]}
            old_values = {field: getattr(cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status"]}
            
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
        try:
            Cycle.objects.get(id=kwargs.get('id')).delete()
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
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Create a new instrument_type
            instrument_type = InstrumentType.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
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
            
            # Serialize the updated data
            serializer = InstrumentTypeSerializer(instrument_type, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the InstrumentType table
                updated_instrument_type = serializer.save()
                
                # Save data in activity log
                ActivityLogUnits.objects.create(
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

#analytes
        
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

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                analyte_id=analyte,
                old_value=None,
                new_value=changes_string,
                date_of_addition=timezone.now(),
                actions='Added'
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
                    actions='Updated'
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


# Scheme add Analytes
class SchemeAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            scheme = Scheme.objects.get(id=id)
            analytes = scheme.analytes.all()  # Fetch all reagents associated with the analyte
            analyte_ids = [analyte.id for analyte in analytes]
            
            # Serialize data
            serialized_data = {
                #"scheme": SchemeSerializer(scheme).data,
                "analytes": analyte_ids  # Send list of reagent IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Scheme not found."})
        
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
            analytes = request.data.get('analytes', [])
            print("analytes2", analytes)
            if isinstance(analytes, str):
                analytes = list(map(int, analytes.split(',')))
            
            analyte.analytes.set(analytes)  # Assuming instruments are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Equipments added to analyte successfully."})
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

    # def post(self, request, id, *args, **kwargs):
       
    #     try:
    #         scheme = Scheme.objects.get(id=id)
    #         print("id", scheme)
    #         # Ensure 'analytes' is parsed as a list of integers
    #         analytes = request.data.get('analytes', [])
    #         if isinstance(analytes, str):
    #             analytes = analytes.split(',')
    #         if not isinstance(analytes, list):
    #             raise ValueError("analytes must be a list of integers.")

    #         # Convert all elements to integers and handle possible conversion errors
    #         analytes = [int(r) for r in analytes if r.strip().isdigit()]

    #         scheme.analytes.set(analytes)  # Assuming analytes are passed as a list of IDs
    #         scheme.save()

    #         return Response({"status": status.HTTP_200_OK, "message": "analytes added to scheme successfully."})
    #     except Scheme.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Scheme not found."})
    #     except ValueError as ve:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(ve)})
    #     except Exception as e:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeUpdateAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
       
        try:
            scheme = Scheme.objects.get(id=id)
            analytes = request.data.get('analytes', [])
            if isinstance(analytes, str):
                analytes = list(map(int, analytes.split(',')))
            
            scheme.analytes.set(analytes)  # Assuming reagents are passed as a list of IDs
            scheme.save()
            serialized_data = SchemeSerializer(scheme).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Reagents updated for Analyte successfully."})
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Scheme does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        
class AnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter analytes based on the organization
            analyte_list = Analyte.objects.filter(organization_id=organization)
            
            # Serialize data
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

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                analyte_id=analyte,
                old_value=None,
                new_value=changes_string,
                date_of_addition=timezone.now(),
                actions='Added'
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
                    actions='Updated'
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

class SampleListView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            sample = Staff.objects.get(account_id=kwargs.get('id'))

            organization = sample.organization_id
            sample_list = Sample.objects.filter(organization_id=organization)
            serialized_data = [model_to_dict(sample) for sample in sample_list]
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Staff record not found."})

        except Sample.DoesNotExist:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No Sample found with that ID."})

class SamplePostView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            organization = staff_user.organization_id

            # Assuming Sample model has account_id field as ForeignKey to UserAccount
            # Fetch the UserAccount instance based on account_id
           

            sample = Sample.objects.create(
                organization_id=organization,
           
                sampleno=request.data['sampleno'],
                details=request.data['details'],
                notes=request.data['notes'],
                scheme=request.data['scheme'],
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
                "master_unit": analyte.master_unit.id if analyte.master_unit else None
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
