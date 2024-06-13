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

    # Post API for creating units
    def post(self, request, *args, **kwargs):
        try:
            # user_id = request.data['added_by']
            # print("id", request.data['added_by'])
            # organozation = Organization.objects.get(account_id=user_id)

            # Create a new unit
            unit = Units.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                # organization_id=organozation
            )

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                unit_id=unit,
                old_value= request.data['name'], # Here you can specify old value for post
                new_value= "",  # Assuming 'name' is the new value
                date_of_addition=timezone.now(),
                # organization_id=organozation,
                actions='Added'  # Specify action as 'Added'
            )
            # Serialize the created unit
            unit_serializer = UnitsSerializer(unit)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({"status": status.HTTP_201_CREATED,  "unit_data": unit_serializer.data, "activity_log_data": activity_log_serializer.data, "message": "Unit added successfully."})

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
                    added_by=request.user, 
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
                instrument_data = model_to_dict(instrument)
                if instrument.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=instrument.added_by_id)
                    instrument_data['added_by'] = user_account.username
                else:
                    instrument_data['added_by'] = None
                
                # Fetch name from instrumenttype table based on instrument_type
                if instrument.instrument_type_id:  # Check if instrument_type_id is not None
                    instrument_type = InstrumentType.objects.get(id=instrument.instrument_type_id)
                    instrument_data['instrument_type'] = instrument_type.name
                else:
                    instrument_data['instrument_type'] = None

                # Fetch name from manufactural table based on manufactural_type_id
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
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

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
                added_by=user_account,
                code=request.data['code'],
                status=request.data['status'],
                instrument_type=instrument_type,  # Assign the InstrumentType instance
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
                added_by=user_account,
                actions='Added',
                type="Instrumentlist"
            )

            instrument_serializer = InstrumentSerializer(instrument)

            return Response({"status": status.HTTP_201_CREATED, "instrument_data": instrument_serializer.data,
                             "message": "Instrument added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class InstrumentsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            instrument = Instrument.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(instrument, field) for field in ["name", "code", "status","instrument_type","manufactural"]}
            
            serializer = InstrumentSerializer(instrument, data=request.data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_unit, field) for field in ["name", "code", "status","instrument_type","manufactural"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    instrument_id=instrument,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    added_by=request.user,
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
                reagent_data = model_to_dict(reagent)
                if reagent.added_by_id:
                    user_account = UserAccount.objects.get(id=reagent.added_by_id)
                    reagent_data['added_by'] = user_account.username
                else:
                    reagent_data['added_by'] = None
                serialized_data.append(reagent_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Reagents.DoesNotExist:
            return Response({"status": status.  HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
  
# Reagents Post API 
class ReagentsPostAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

            # Create a new method
            reagent = Reagents.objects.create(
                code=request.data['code'],
                name=request.data['name'],
                status= request.data['status'],
                date_of_addition=timezone.now(),
                added_by=user_account
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
                added_by=user_account,
                actions='Added',
                type="Reagent"
            )

            reagent_serializer = ReagentsSerializer(reagent)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": reagent_serializer.data,
                             "message": "Unit added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})



class ReagentsPutAPIView(APIView):
    permission_classes = (AllowAny,)      
    def put(self, request, *args, **kwargs):
        try:
            reagents = Reagents.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(reagents, field) for field in ["name", "code", "status"]}
            
            serializer = ReagentsSerializer(reagents, data=request.data, partial=True)

            if serializer.is_valid():
                updated_reagents = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_reagents, field) for field in ["name", "code", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    reagent_id=reagents,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    added_by=request.user,
                    actions="Updated",
                    type="Reagent"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Reagents Information updated successfully."
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
                manufactural_data = model_to_dict(manufactural)
                 # Handle the 'added_by' field
                if manufactural.added_by_id:
                    user_account = UserAccount.objects.get(id=manufactural.added_by_id)
                    manufactural_data['added_by'] = user_account.username
                else:
                    manufactural_data['added_by'] = None
                 # Handle the 'image' field
                if manufactural.image:
                    manufactural_data['image'] = manufactural.image.url
                else:
                    manufactural_data['image'] = None
                serialized_data.append(manufactural_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Manufactural.DoesNotExist:
            return Response({"status": status.  HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
        
class ManufacturalPostAPIView(APIView):
    permission_classes = (AllowAny,)  

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)
            image = request.FILES.get('image')

            # Create a new method
            manufactural = Manufactural.objects.create(
                name=request.data['name'],
                city= request.data['city'],
                country = request.data['country'],
                telephone= request.data['telephone'],
                address = request.data['address'],
                image = image,
                date_of_addition=timezone.now(),
                added_by=user_account,
                
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
                added_by=user_account,
                actions='Added',
                type="Manufactural"
            )

            manufactural_serializer = ManufacturalSerializer(manufactural)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": manufactural_serializer.data,
                             "message": "Manufactural added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class  ManufacturalPutAPIView(APIView):
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
                    added_by=request.user,
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
                if method.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=method.added_by_id)
                    method_data['added_by'] = user_account.username
                else:
                    method_data['added_by'] = None
                serialized_data.append(method_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Method.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    # Post API for creating units
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

            # Create a new method
            method = Method.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                added_by=user_account,
                code=request.data['code'],
                status=request.data['status'],
            )

            # Concatenate all changes into a single string
            changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["name", "code", "status"]])

            # Save data in activity log as a single field
            ActivityLogUnits.objects.create(
                method_id=method,
                date_of_addition=timezone.now(),
                field_name="Changes",
                old_value=None,  # No old value during creation
                new_value=changes_string,
                added_by=user_account,
                actions='Added',
                type="Method"
            )

            method_serializer = MethodSerializer(method)

            return Response({"status": status.HTTP_201_CREATED, "unit_data": method_serializer.data,
                             "message": "Unit added successfully."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class MethodsUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            method = Method.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(method, field) for field in ["name", "code", "status"]}
            
            serializer = MethodSerializer(method, data=request.data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_unit, field) for field in ["name", "code", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    method_id=method,
                    date_of_addition=timezone.now(),
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    added_by=request.user,
                    actions="Updated",
                    type="Method"
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Method Information updated successfully."
                })
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
                instrument_type_data = model_to_dict(instrument_type)
                if instrument_type.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=instrument_type.added_by_id)
                    instrument_type_data['user_name'] = user_account.username
                else:
                    instrument_type_data['user_name'] = None
                serialized_data.append(instrument_type_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except InstrumentType.DoesNotExist:
            return Response({"status": status.  HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

            # Create a new instrument_type
            instrument_type = InstrumentType.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                added_by=user_account
            )

            # Save data in activity log
            activity_log = ActivityLogUnits.objects.create(
                instrumenttype_id=instrument_type,
                date_of_addition=timezone.now(),
                old_value=request.data['name'],
                added_by=user_account,
                actions='Added',
                type= "Instruments"
            )
            # Serialize the created instrument_type
            serializer = InstrumentTypeSerializer(instrument_type)
            activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

            return Response({"status": status.HTTP_201_CREATED,  "unit_data": serializer.data, "activity_log_data": activity_log_serializer.data, "message": "Unit added successfully."})

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
                old_values = {field: getattr(instrument_type, field) for field in serializer.fields}

                updated_instrument_type = serializer.save()
                new_values = {field: getattr(instrument_type, field) for field in serializer.fields}

                for field, value in serializer.data.items():
                    if field in ["name"] and old_values.get(field) != value:
                        ActivityLogUnits.objects.create(
                            instrumenttype_id=instrument_type,
                            field_name=field, 
                            old_value=old_values.get(field), 
                            new_value=new_values.get(field), 
                            added_by=request.user,
                            actions= "Updated",
                            type= "Instruments"
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
                analyte_data = model_to_dict(analyte)
                if analyte.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=analyte.added_by_id)
                    analyte_data['added_by'] = user_account.username
                else:
                    analyte_data['added_by'] = None
                serialized_data.append(analyte_data)
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        except Analyte.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    # Post API for creating units
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['added_by']
            user_account = UserAccount.objects.get(id=user_id)

            # Create a new Analyte
            analyte = Analyte.objects.create(
                name=request.data['name'],
                date_of_addition=timezone.now(),
                added_by=user_account,
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
                added_by=user_account,
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
                    added_by=request.user,
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
                news_data = model_to_dict(newss)

                # Handle binary data separately, e.g., picture field
                if 'picture' in news_data and news_data['picture']:
                    news_data['picture'] = newss.picture.url  # Assuming you store images as URL or file path
                else:
                    news_data['picture'] = None
                
                if newss.added_by_id:  # Check if added_by_id is not None
                    user_account = UserAccount.objects.get(id=newss.added_by_id)
                    news_data['added_by'] = user_account.username
                else:
                    news_data['added_by'] = None
                
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
                
                
                news = News.objects.create(
                    title=request.data.get('title'),
                    date_of_addition=timezone.now(),
                    added_by=user_account,
                    description=request.data.get('description'),
                    picture=request.data.get('picture'),
                )
                news_data = model_to_dict(news)
                news_data['added_by'] = user_account.username  # Replace added_by id with username

                # Handle picture field for response
                if 'picture' in news_data and news_data['picture']:
                    news_data['picture'] = news.picture.url
                else:
                    news_data['picture'] = None

                return Response({"status": status.HTTP_201_CREATED, "data": news_data})

            except UserAccount.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        return Response({"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors})