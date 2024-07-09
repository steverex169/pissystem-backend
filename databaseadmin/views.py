from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from databaseadmin.models import ParticipantType,ParticipantSector,Department,Designation,District,City,News,Instrument, Units, ActivityLogUnits,Reagents , Manufactural, Method,InstrumentType, Analyte

from databaseadmin.serializers import NewsSerializer,InstrumentSerializer, MethodSerializer,AnalyteSerializer, InstrumentTypeSerializer, UnitsSerializer, ActivityLogUnitsSerializer, ReagentsSerializer, ManufacturalSerializer, Scheme, Cycle,Sample,ParticipantTypeSerializer, ParticipantSectorSerializer,DepartmentSerializer,DesignationSerializer,DistrictSerializer,CitySerializer,SchemeSerializer, CycleSerializer,  SampleSerializer

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
                instrument_data = {
                    'id': instrument.id,
                    'name': instrument.name,
                    'code': instrument.code,
                    'status': instrument.status,
                }

                # Fetch name from InstrumentType table based on instrument_type
                if instrument.instrument_type_id:  # Check if instrument_type_id is not None
                    instrument_type = InstrumentType.objects.get(id=instrument.instrument_type_id)
                    instrument_data['instrument_type'] = instrument_type.name
                else:
                    instrument_data['instrument_type'] = None

                # Fetch name from Manufactural table based on manufactural_id
                if instrument.manufactural_id:  # Check if manufactural_id is not None
                    manufactural = Manufactural.objects.get(id=instrument.manufactural_id)
                    instrument_data['manufactural'] = manufactural.name
                else:
                    instrument_data['manufactural'] = None

                serialized_data.append(instrument_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

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

            # Fetch the InstrumentType instance
            instrument_type_id = request.data['instrument_type']
            instrument_type = InstrumentType.objects.get(id=instrument_type_id, organization_id=organization)

            # Fetch the manufactural instance
            manufactural_id = request.data['manufactural']
            manufactural = Manufactural.objects.get(id=manufactural_id, organization_id=organization)

            # Create a new instrument
            instrument = Instrument.objects.create(
                organization_id=organization,
                name=request.data['name'],
                date_of_addition=timezone.now(),
                code=request.data['code'],
                status=request.data['status'],
                instrument_type=instrument_type,
                manufactural=manufactural,
            )

            # Concatenate all changes into a single string with names
            changes_string = f"name: {request.data['name']}, code: {request.data['code']}, status: {request.data['status']}, instrument_type: {instrument_type.name}, manufactural: {manufactural.name}"

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

            # Store old values before updating
            old_values = {
                'name': instrument.name,
                'code': instrument.code,
                'status': instrument.status,
                'instrument_type': instrument.instrument_type.name if instrument.instrument_type else None,
                'manufactural': instrument.manufactural.name if instrument.manufactural else None,
            }
            
            serializer = InstrumentSerializer(instrument, data=request.data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {
                    'name': updated_unit.name,
                    'code': updated_unit.code,
                    'status': updated_unit.status,
                    'instrument_type': updated_unit.instrument_type.name if updated_unit.instrument_type else None,
                    'manufactural': updated_unit.manufactural.name if updated_unit.manufactural else None,
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
                reagent_data = {
                    'id': reagent.id,
                    'code': reagent.code,
                    'name': reagent.name,
                    'status': reagent.status,
                    # Add other fields as needed
                }
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
            
            # Create a new reagent
            reagent = Reagents.objects.create(
                organization_id=organization,
                code=request.data['code'],
                name=request.data['name'],
                status=request.data['status'],
                date_of_addition=timezone.now(),
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])
            user_account = UserAccount.objects.get(id=account_id)
            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
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

            # Store old values before updating
            old_values = {field: getattr(reagent, field) for field in ["name", "code", "status"]}

            serializer = ReagentsSerializer(reagent, data=request.data, partial=True)

            if serializer.is_valid():
                updated_reagent = serializer.save()

                # Retrieve new values after updating
                new_values = {field: getattr(updated_reagent, field) for field in ["name", "code", "status"]}

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
                manufactural_data = {
                    'id': manufactural.id,
                    'name': manufactural.name,
                    'city': manufactural.city,
                    'country': manufactural.country,
                    'telephone': manufactural.telephone,
                    'address': manufactural.address,
                }
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

            # Create a new manufactural
            manufactural = Manufactural.objects.create(
                organization_id=organization,
                name=request.data['name'],
                city=request.data['city'],
                country=request.data['country'],
                # telephone=request.data['telephone'],
                # address=request.data['address'],
                date_of_addition=timezone.now(),
            )
            user_account = UserAccount.objects.get(id=account_id)
            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "city", "country", "telephone", "address"]])

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

class  ManufacturalPutAPIView(APIView):
    permission_classes = (AllowAny,)      

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Retrieve the existing manufactural object
            manufactural = Manufactural.objects.get(id=kwargs.get('id'), organization_id=organization)

            # Store old values before updating
            old_values = {field: getattr(manufactural, field) for field in ["name", "city", "country"]}
            
            # Convert 'undefined' values to None before passing to serializer
            data = {key: value if value != 'undefined' else None for key, value in request.data.items()}
            
            serializer = ManufacturalSerializer(manufactural, data=data, partial=True)

            if serializer.is_valid():
                updated_manufactural = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_manufactural, field) for field in ["name", "city", "country"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    manufactural_id=manufactural,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
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
                method_data = model_to_dict(method)
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
            analyte_list = Scheme.objects.all()
            serialized_data = []
            for analyte in analyte_list:
                analyte_data = model_to_dict(analyte)
                if analyte.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=analyte.added_by_id)
                    analyte_data['added_by'] = user_account.username
                else:
                    analyte_data['added_by'] = None
                serialized_data.append(analyte_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Scheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    # Post API for creating units
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

            # Create a new Analyte
            analyte = Scheme.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                added_by=user_account,
                status=request.data['status'],
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "status"]])

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                analyte_id=analyte,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                added_by=user_account,
                actions='Added',
                type="Analyte"
            )

            scheme_serializer = SchemeSerializer(analyte)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": scheme_serializer.data,
                             "message": "Scheme added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class SchemeUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            scheme = Scheme.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(scheme, field) for field in ["name", "status"]}
            
            serializer = SchemeSerializer(scheme, data=request.data, partial=True)

            if serializer.is_valid():
                updated_analyte = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_analyte, field) for field in ["name", "status"]}

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

            # Filter schemes based on the organization
            cycle_list = Cycle.objects.filter(organization_id=organization)

            serialized_data = []
            for cycle in cycle_list:
                # Retrieve analyte names associated with the scheme
                analyte_names = [analyte.name for analyte in cycle.analytes.all()]
                
                # Serialize cycle data
                cycle_data = model_to_dict(cycle)
                cycle_data['analytes'] = analyte_names  # Replace analyte IDs with names
                serialized_data.append(cycle_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No cycle records found."})

class CyclePostAPIView(APIView):
    permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

    def post(self, request, *args, **kwargs):
        try:
            account_id = request.data['added_by']
 
            staff_user = Staff.objects.get(account_id=account_id)

            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id


            # Create a new Analyte
            cycle = Cycle.objects.create(
                organization_id= organization,
                scheme_name=request.data['scheme_name'],
                cycle_no=request.data['cycle_no'],
                cycle=request.data['cycle'],
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
                rounds=request.data['rounds'],
                status=request.data['status'],
                # added_by=user_account,
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status"]])

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
            old_values = {field: getattr(cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status", "start_date", "end_date" ]}

            
            serializer = CycleSerializer(cycle, data=request.data, partial=True)

            if serializer.is_valid():
                updated_cycle = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_cycle, field) for field in ["scheme_name", "cycle_no", "rounds", "cycle", "status", "start_date", "end_date"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    cycle_id=cycle,
                    start_date=request.data['start_date'],
                    end_date=request.data['end_date'],
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
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id
            
            # Filter instrument types based on the organization
            instrument_type_list = InstrumentType.objects.filter(organization_id=organization)
            
            # Serialize data
            serialized_data = [model_to_dict(instrument_type) for instrument_type in instrument_type_list]

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

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
    #   *******************API for geeting Ananlytes on Stafff Dashboard*******************
    # def get(self, request, *args, **kwargs):
    #     try:
    #         # Get the staff user's account_id
    #         account_id = kwargs.get('id')
            
    #         # Fetch the staff user based on account_id
    #         staff_user = Staff.objects.get(account_id=account_id)
            
    #         # Retrieve the organization associated with the staff user
    #         organization = staff_user.organization_id
            
    #         # Filter analytes based on the organization
    #         analyte_list = Analyte.objects.filter(organization_id=organization)
            
    #         # Serialize data
    #         serialized_data = AnalyteSerializer(analyte_list, many=True).data
            
    #         return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        # except Staff.DoesNotExist:
        #     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        # except Analyte.DoesNotExist:
        #     return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Analyte records found."})

#  *****************API for getting Ananlytes on Stafff + Participant Dashboard********************
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


# Cycle add Analytes
class CycleAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            analyte = Cycle.objects.get(id=id)
            analytes = analyte.analytes.all()  # Fetch all reagents associated with the analyte
            reagent_ids = [analytes.id for analytes in analytes]
            
            # Serialize data
            serialized_data = {
                #"analyte": AnalyteSerializer(analyte).data,
                "analytes": reagent_ids  # Send list of reagent IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CycleAddAnalyteAPIView(APIView):
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
        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class CycleUpdateAnalyteAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            analyte = Cycle.objects.get(id=id)
            analytes = request.data.get('reagents', [])
            if isinstance(analytes, str):
                analytes = list(map(int, analytes.split(',')))
            
            analyte.analytes.set(analytes)  # Assuming reagents are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Reagents updated for Analyte successfully."})
        except Cycle.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
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