from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from databaseadmin.models import News,Instrument, Units, ActivityLogUnits,Reagents , Manufactural, Method,InstrumentType, Analyte
from databaseadmin.serializers import NewsSerializer,InstrumentSerializer, MethodSerializer,AnalyteSerializer, InstrumentTypeSerializer, UnitsSerializer, ActivityLogUnitsSerializer, ReagentsSerializer, ManufacturalSerializer
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
import datetime
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
                formula=request.data['formula'],
                date_of_addition=timezone.now(),
            )
            changes_string = f"name: {request.data['name']}{request.data['formula']}, "

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
                'formula': unit.formula,
            }
            
            # Serialize the updated data
            serializer = UnitsSerializer(unit, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the Units table
                updated_unit = serializer.save()

                # Retrieve new values after updating
                new_values = {
                    'name': updated_unit.name,
                    'formula': updated_unit.formula,
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
                                manufactural = Manufactural.objects.get(id=id_value)
                                activity_log = ActivityLogUnits.objects.filter(manufactural_id=manufactural.id)
                            except Manufactural.DoesNotExist:
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

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "city", "country", "telephone", "address"]])

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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
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
                "units": unit_ids  # Send list of units IDs
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
            
            # Ensure 'units' is parsed as a list of integers
            units = request.data.get('units', [])
            if isinstance(units, str):
                units = list(map(int, units.split(',')))
            
            analyte.units.set(units)  # Assuming units are passed as a list of IDs
            analyte.save()

            return Response({"status": status.HTTP_200_OK, "message": "Units added to analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte not found."})
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
            
            analyte.units.set(units)  # Assuming units are passed as a list of IDs
            analyte.save()
            serialized_data = AnalyteSerializer(analyte).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Units updated for Analyte successfully."})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Analyte does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        
class NewsListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            news = News.objects.all()
            serialized_data = []
            for newss in news:
                news_data = {
                    'id': newss.id,
                    'title': newss.title,
                    'date_of_addition': newss.date_of_addition,
                    'description': newss.description,
                    'picture': newss.picture.url if newss.picture else None,
                    # Add other fields as needed
                }
                serialized_data.append(news_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except News.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    def post(self, request, *args, **kwargs):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Fetch the staff user based on account_id
                account_id1 = request.data.get('added_by')  # Use 'added_by' from request data
                # print("idddddddd",account_id1)
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
                    'id': news.id,
                    'title': news.title,
                    'date_of_addition': date_of_addition,
                    'description': news.description,
                    'picture': news.picture.url if news.picture else None,
                    # Add other fields as needed
                }
                # print("username",user_account)
                return Response({"status": status.HTTP_201_CREATED, "data": news_data})

            except UserAccount.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        return Response({"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors})