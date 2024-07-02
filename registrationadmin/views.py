from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from registrationadmin.models import  ActivityLogUnits, Round
from staff.models import Staff
from registrationadmin.serializers import RoundSerializer, ActivityLogUnitsSerializer
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
from django.shortcuts import get_object_or_404
from databaseadmin.models import Scheme 

class ActivityLogRegistrationadmin(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            id_value = kwargs.get('id')

            # Try to get the data from Units
            try:
                round = Round.objects.get(id=id_value)
                activity_log = ActivityLogUnits.objects.filter(round_id=round.id)
            except Round.DoesNotExist:
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


class RoundAPIView(APIView):
    permission_classes = (AllowAny,)  # AllowAny temporarily for demonstration

    def get(self, request, *args, **kwargs):
        try:
            # Get the staff user's account_id
            account_id = kwargs.get('id')
            
            # Fetch the staff user based on account_id
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Filter rounds based on the organization
            round_list = Round.objects.filter(organization_id=organization)
            
            # Serialize rounds data including scheme name
            serialized_data = []
            for round_obj in round_list:
                round_data = model_to_dict(round_obj)
                scheme = round_obj.scheme
                if scheme:
                    round_data['scheme_name'] = scheme.name
                else:
                    round_data['scheme_name'] = None  # Handle case where scheme is None
                serialized_data.append(round_data)

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Round records found."})

class RoundPostAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)

            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the Scheme object based on the provided ID
            scheme_id = request.data.get('scheme')  # Assuming 'scheme' is sent in the request data
            scheme = get_object_or_404(Scheme, pk=scheme_id)

            # Create a new Round instance with the fetched Scheme object
            round = Round.objects.create(
                organization_id=organization,
                rounds=request.data['rounds'],
                scheme=scheme,  # Assign the fetched Scheme object
                cycle_no=request.data['cycle_no'],
                sample=request.data['sample'],
                participants=request.data['participants'],
                issue_date=request.data['issue_date'],
                closing_date=request.data['closing_date'],
                notes=request.data['notes'],
                status=request.data['status'],
            )

            # Handle activity log and serializers as per your application logic
            round_serializer = RoundSerializer(round)
            return Response({
                "status": status.HTTP_201_CREATED,
                "unit_data": round_serializer.data,
                # "activity_log_data": activity_log_serializer.data,
                "message": "Round added successfully."
            })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

# class RoundPostAPIView(APIView):
#     permission_classes = (AllowAny,)  # Temporary permission setting for demonstration

#     def post(self, request, *args, **kwargs):
#         try:
#             # Fetch the staff user based on account_id
#             account_id = request.data.get('added_by')  # Use 'added_by' from request data
#             staff_user = Staff.objects.get(account_id=account_id)

#             # Retrieve the organization associated with the staff user
#             organization = staff_user.organization_id

#             # Create a new round
#             round = Round.objects.create(
#                 organization_id=organization,
#                 rounds=request.data['rounds'], 
#                 scheme=request.data['scheme'],
#                 cycle_no=request.data['cycle_no'],
#                 sample=request.data['sample'],
#                 issue_date=request.data['issue_date'],
#                 closing_date=request.data['closing_date'],
#                 notes=request.data['notes'],
#                 status=request.data['status'],
#             )

#             # Concatenate all changes into a single string
#             changes_string = ", ".join([f"{field}: {request.data[field]}" for field in ["rounds", "scheme", "cycle_no", "sample", "issue_date", "closing_date", "notes", "status"]])

#             # Save data in activity log as a single field
#             activity_log = ActivityLogUnits.objects.create(
#                 round_id=round,
#                 old_value="", 
#                 new_value=changes_string, 
#                 issue_date=request.data['issue_date'],
#                 closing_date=request.data['closing_date'],
#                 field_name="Changes",
#                 actions='Added'
#             )

#             round_serializer = RoundSerializer(round)
#             activity_log_serializer = ActivityLogUnitsSerializer(activity_log)

#             return Response({
#                 "status": status.HTTP_201_CREATED,
#                 "unit_data": round_serializer.data,
#                 "activity_log_data": activity_log_serializer.data,
#                 "message": "Round added successfully."
#             })

#         except Staff.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

#         except Exception as e:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class RoundUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            round = Round.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(round, field) for field in ["rounds", "scheme", "cycle_no", "sample", "participants", "issue_date", "closing_date", "notes", "status"]}
            
            serializer = RoundSerializer(round, data=request.data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_unit, field) for field in ["rounds", "scheme", "cycle_no", "sample", "participants", "issue_date", "closing_date", "notes", "status"]}

                # Find the fields that have changed
                changed_fields = {field: new_values[field] for field in new_values if new_values[field] != old_values[field]}

                # Concatenate all changes into a single string
                changes_string = ", ".join([f"{field}: {changed_fields[field]}" for field in changed_fields])

                # Save data in activity log as a single field
                ActivityLogUnits.objects.create(
                    round_id=round,
                    issue_date=request.data['issue_date'],
                    closing_date=request.data['closing_date'],
                    field_name="Changes",
                    old_value= ", ".join([f"{field}: {old_values[field]}" for field in changed_fields]),
                    new_value=changes_string,
                    added_by=request.user,
                    actions="Updated",
                    type="Round",
                )

                return Response({
                    "status": status.HTTP_200_OK,
                    "data": serializer.data,
                    "message": "Round Information updated successfully."
                })
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class RoundDeleteAPIView(APIView):
    permission_classes = (AllowAny,)

    def delete(self, request, *args, **kwargs):
        try:
            Round.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})


