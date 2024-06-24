from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from databaseadmin.models import News,Instrument, Units, ActivityLogUnits,Reagents , Manufactural, Method,InstrumentType, Analyte
from databaseadmin.serializers import NewsSerializer,InstrumentSerializer, MethodSerializer,AnalyteSerializer, InstrumentTypeSerializer, UnitsSerializer, ActivityLogUnitsSerializer, ReagentsSerializer, ManufacturalSerializer
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
            units_list = Units.objects.all()
            serialized_data = []
            for unit in units_list:
                unit_data = model_to_dict(unit)
                if unit.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=unit.added_by_id)
                    unit_data['added_by'] = user_account.username
                else:
                    unit_data['added_by'] = None
                serialized_data.append(unit_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Units.DoesNotExist:
            return Response({"status": status.  HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
        
class UnitsAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def post(self, request, *args, **kwargs):
        try:
            # Create a new unit
            unit = Units.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
            )

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                unit_id=unit,
                old_value=request.data['name'],  # Old value before post
                new_value="",  # Assuming 'name' is the new value
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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class UnitsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)      
    
    def put(self, request, *args, **kwargs):
        try:
            # Retrieve the existing unit object
            unit = Units.objects.get(id=kwargs.get('id'))
            
            # Get the old value before updating the unit
            old_value = unit.name
            
            # Serialize the updated data
            serializer = UnitsSerializer(unit, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data to the Units table
                updated_unit = serializer.save()
                
                # Create a new entry in the ActivityLogUnits table
                ActivityLogUnits.objects.create(
                    unit_id=unit,
                    old_value=old_value,
                    new_value=updated_unit.name, 
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

        except Units.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class InstrumentsAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            instruments_list = Instrument.objects.all()
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

        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    # Post API for creating units
    def post(self, request, *args, **kwargs):
        try:
            # Fetch the InstrumentType instance
            instrument_type_id = request.data['instrument_type']
            instrument_type = InstrumentType.objects.get(id=instrument_type_id)

            # Fetch the manufactural instance
            manufactural_id = request.data['manufactural']
            manufactural = Manufactural.objects.get(id=manufactural_id)

            # Create a new instrument
            instrument = Instrument.objects.create(
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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class InstrumentsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            instrument = Instrument.objects.get(id=kwargs.get('id'))

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

        except Instrument.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})


            
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
# Reagents get API 
class ReagentsListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            reagents_list = Reagents.objects.all()
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
        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
  
# Reagents Post API 
class ReagentsPostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration
    
    def post(self, request, *args, **kwargs):
        try:
            # user_id = request.data['added_by']
            # user_account = UserAccount.objects.get(id=user_id)

            # Create a new reagent
            reagent = Reagents.objects.create(
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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class ReagentsPutAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            reagent = Reagents.objects.get(id=kwargs.get('id'))

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

        except Reagents.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class ManufacturalListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            manufactural_list = Manufactural.objects.all()
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

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
        
class ManufacturalPostAPIView(APIView):
    permission_classes = (AllowAny,)  

    def post(self, request, *args, **kwargs):
        try:

            # Create a new manufactural
            manufactural = Manufactural.objects.create(
                name=request.data['name'],
                city=request.data['city'],
                country=request.data['country'],
                telephone=request.data['telephone'],
                address=request.data['address'],
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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class ManufacturalPutAPIView(APIView):
    permission_classes = (AllowAny,)      

    def put(self, request, *args, **kwargs):
        try:
            manufactural = Manufactural.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(manufactural, field) for field in ["name", "city", "country", "telephone", "address"]}
            
            serializer = ManufacturalSerializer(manufactural, data=request.data, partial=True)

            if serializer.is_valid():
                updated_manufactural = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_manufactural, field) for field in ["name", "city", "country", "telephone", "address"]}

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

        except Manufactural.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})



class MethodsAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            methods_list = Method.objects.all()
            serialized_data = []
            for method in methods_list:
                method_data = model_to_dict(method)
                serialized_data.append(method_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    def post(self, request, *args, **kwargs):
        serializer = MethodSerializer(data=request.data)
        if serializer.is_valid():
            try:
                method = serializer.save(date_of_addition=timezone.now())

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    method_id=method,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value=None,  # No old value during creation
                    new_value=changes_string,
                    actions='Added',
                    type="Method"
                )

                method_data = model_to_dict(method)
                return Response({"status": status.HTTP_201_CREATED, "data": method_data, "message": "Method added successfully."})

            except Exception as e:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

        return Response({"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors})

class MethodsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            method = Method.objects.get(id=kwargs.get('id'))

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

        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class InstrumentTypeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            instrument_type_list = InstrumentType.objects.all()
            serialized_data = []
            for instrument_type in instrument_type_list:
                instrument_type_data = {
                    'id': instrument_type.id,
                    'name': instrument_type.name,
                    'date_of_addition': instrument_type.date_of_addition,
                    'user_name': None,  # No need to include 'added_by' information
                }
                serialized_data.append(instrument_type_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    def post(self, request, *args, **kwargs):
        try:
            # Create a new instrument_type
            instrument_type = InstrumentType.objects.create(
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

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class UpdateInstrumentTypeView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Retrieve the existing instrument_type object
            instrument_type = InstrumentType.objects.get(id=kwargs.get('id'))
            
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

        except InstrumentType.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})
        
class AnalyteAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            analyte_list = Analyte.objects.all()
            serialized_data = []
            for analyte in analyte_list:
                analyte_data = {
                    'id': analyte.id,
                    'name': analyte.name,
                    'code': analyte.code,
                    'status': analyte.status,
                    # Add other fields as needed
                }
                serialized_data.append(analyte_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    # Post API for creating analytes
    def post(self, request, *args, **kwargs):
        try:
            # user_id = request.data['added_by']
            # user_account = UserAccount.objects.get(id=user_id)

            # Create a new Analyte
            analyte = Analyte.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                # added_by=user_account,
                code=request.data['code'],
                status=request.data['status'],
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                analyte_id=analyte,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                # added_by=user_account,
                actions='Added',
                type="Analyte"
            )

            analyte_serializer = AnalyteSerializer(analyte)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": analyte_serializer.data,
                             "message": "Analyte added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class AnalyteUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            analyte = Analyte.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(analyte, field) for field in ["name", "code", "status"]}
            
            serializer = AnalyteSerializer(analyte, data=request.data, partial=True)

            if serializer.is_valid():
                updated_analyte = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_analyte, field) for field in ["name", "code", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    analyte_id=analyte,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    # added_by=request.user,
                    actions="Updated",
                    type="Analyte"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Analyte Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

   
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
                user_id = request.data.get('added_by')
                user_account = UserAccount.objects.get(id=user_id)
                
                news = serializer.save(added_by=user_account)

                news_data = {
                    'id': news.id,
                    'title': news.title,
                    'date_of_addition': news.date_of_addition,
                    'description': news.description,
                    'picture': news.picture.url if news.picture else None,
                    # Add other fields as needed
                }

                return Response({"status": status.HTTP_201_CREATED, "data": news_data})

            except UserAccount.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        return Response({"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors})