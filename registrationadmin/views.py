from datetime import datetime
from django.forms.models import model_to_dict
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from databaseadmin.models import Scheme
from labowner.models import Lab, OfferedTest, Pathologist, SampleCollector
from labowner.serializers import LabInformationSerializer,  PathologistSerializer, OfferedTestSerializer
from registrationadmin.serializers import RoundSerializer, ActivityLogUnitsSerializer, PaymentSerializer,SelectedSchemeSerializer
from registrationadmin.models import  ActivityLogUnits, Round, Payment, SelectedScheme
from staff.models import Staff
from labowner.models import Lab 

from registrationadmin.serializers import RoundSerializer, ActivityLogUnitsSerializer
from registrationadmin.models import  ActivityLogUnits, Round
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Q
from account.models import UserAccount
from organization.models import Organization
import datetime
from django.shortcuts import get_object_or_404
from databaseadmin.models import Scheme 
from django.db import transaction


class PaymentPostAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data['added_by']
            staff_user = Staff.objects.get(account_id=account_id)
            
            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Fetch the participant instance based on participant name
            participant_name = request.data.get('participant')
            try:
                participant = Lab.objects.get(name=participant_name, organization_id=organization)
            except Lab.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid participant name provided."})

            # Create a new Payment instance
            with transaction.atomic():
                payment = Payment.objects.create(
                    organization_id=organization,
                    participant_id=participant,
                    price=request.data['price'],
                    discount=request.data['discount'],
                    photo=request.data['photo'],
                    paymentmethod=request.data['paymentmethod'],
                    paydate=request.data['paydate']
                )

                # Update the payment status to 'Paid'
                participant.payment_status = 'Paid'
                participant.save()

                # Create SelectedScheme instance
                selectedscheme = SelectedScheme.objects.create(
                    organization_id=organization,
                    lab_id=participant,
                    added_at=datetime.datetime.now()
                )

                # Ensure 'scheme' is parsed as a list of integers
                scheme = request.data.get('scheme', [])
                if isinstance(scheme, str):
                    scheme = list(map(int, scheme.split(',')))

                # Set schemes for Payment and SelectedScheme
                payment.scheme.set(scheme)
                selectedscheme.scheme_id.set(scheme)
            # Ensure 'scheme' is parsed as a list of integers
            scheme = request.data.get('scheme', [])
            print("scheme",scheme)
            if isinstance(scheme, str):
                scheme = list(map(int, scheme.split(',')))
            
            payment.scheme.set(scheme)  # Assuming scheme are passed as a list of IDs
            payment.save()

                # Serialize the payment instance
                payment_serializer = PaymentSerializer(payment)
                selectedscheme_serializer = SelectedSchemeSerializer(selectedscheme)

                return Response({
                    "status": status.HTTP_201_CREATED,
                    "payment_data": payment_serializer.data,
                    "selected_scheme": selectedscheme_serializer.data,
                    "message": "Payment added successfully."
                })

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

# API for displaying list of pending labs

class PendingLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            organization = staff.organization_id
            pending_labs = Lab.objects.filter(organization_id=organization, status="Pending")
            
            serializer = LabInformationSerializer(pending_labs, many=True)
            data = serializer.data

            for i, lab in enumerate(pending_labs):
                if lab.marketer_id is not None:
                    data[i]['marketer_name'] = lab.marketer_id.name
                    data[i]['marketer_phone'] = lab.marketer_id.phone

            return Response({"status": status.HTTP_200_OK, "data": data})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Staff not found."})
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})

class ApproveUnapproveLabView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    def put(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            try:
                lab = Lab.objects.get(id=request.data['lab_id'])

                request.data._mutable = True

                if request.data['is_approved'] == 'true':
                    request.data['status'] = 'Approved'
                else:
                    request.data['status'] = 'Unapproved'

                request.data['done_by'] = staff.id
                request.data['done_at'] = datetime.datetime.now()
                request.data._mutable = False

                serializer = LabInformationSerializer(
                    lab, data=request.data, partial=True)

                if serializer.is_valid():
                    serializer.save()

                    return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Lab has been approved successfully."})
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})

            except Lab.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No lab exists with this id."})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No staff exists with this id."})

class UnapprovedLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            organization = staff.organization_id
            
            unapproved_labs = Lab.objects.filter(Q(organization_id=organization, status="Unapproved") or Q(is_active="No"))
            serializer_class = LabInformationSerializer(
                unapproved_labs, many=True)
            for i in range(len(unapproved_labs)):
                serializer_class.data[i]['lab_phone'] = unapproved_labs[i].landline

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})

# API for displaying list of approved labs
class ApprovedLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            organization = staff.organization_id
           
            

            approved_labs = Lab.objects.filter(
               organization_id=organization, status="Approved")
            serializer_class = LabInformationSerializer(
                approved_labs, many=True)

            for i in range(0, len(approved_labs)):
                serializer_class.data[i]['lab_address'] = approved_labs[i].address
                serializer_class.data[i]['lab_email'] = approved_labs[i].email
                serializer_class.data[i]['lab_city'] = approved_labs[i].city
                serializer_class.data[i]['lab_phone'] = approved_labs[i].landline
                
                serializer_class.data[i]['lab_name'] = approved_labs[i].name
               


            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})


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
                 # Convert participants field to a list of participant IDs
                round_data['participants'] = list(round_obj.participants.values_list('id', flat=True))
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
                # participants=request.data['participants'],
                issue_date=request.data['issue_date'],
                closing_date=request.data['closing_date'],
                # notes=request.data['notes'],
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

class RoundUpdateAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            round = Round.objects.get(id=kwargs.get('id'))

            # Store old values before updating
            old_values = {field: getattr(round, field) for field in ["rounds", "scheme", "cycle_no", "sample", "participants", "issue_date", "closing_date", "status"]}
            
            serializer = RoundSerializer(round, data=request.data, partial=True)

            if serializer.is_valid():
                updated_unit = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_unit, field) for field in ["rounds", "scheme", "cycle_no", "sample", "participants", "issue_date", "closing_date", "status"]}

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


# Round Add Participants
class RoundsLabsAPIView(APIView):
    permission_classes = (AllowAny,)  # Adjust permission classes as needed

    def get(self, request, id, *args, **kwargs):
        try:
            round = Round.objects.get(id=id)
            participants = round.participants.all()  # Fetch all participants associated with the round
            participant_ids = [participant.id for participant in participants]
            
            # Serialize data
            serialized_data = {
                #"round": RoundSerializer(round).data,
                "participants": participant_ids  # Send list of lab IDs
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Round not found."})
        
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})

class RoundAddLabsAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, id, *args, **kwargs):
        try:
            round = Round.objects.get(id=id)
            
            # Ensure 'participants' is parsed as a list of integers
            participants = request.data.get('participants', [])
            if isinstance(participants, str):
                participants = participants.split(',')
            if not isinstance(participants, list):
                raise ValueError("participants must be a list of integers.")

            # Convert all elements to integers and handle possible conversion errors
            participants = [int(r) for r in participants if r.strip().isdigit()]
            
            round.participants.set(participants)  # Assuming participants are passed as a list of IDs
            round.save()

            return Response({"status": status.HTTP_200_OK, "message": "participants added to round successfully."})
        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Round not found."})
        except ValueError as ve:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(ve)})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})



class RoundUpdateLabsAPIView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id, *args, **kwargs):
        try:
            round = Round.objects.get(id=id)
            participants = request.data.get('participants', [])
            if isinstance(participants, str):
                participants = list(map(int, participants.split(',')))
            
            round.participants.set(participants)  # Assuming participants are passed as a list of IDs
            round.save()
            serialized_data = RoundSerializer(round).data
            return Response({"status": status.HTTP_200_OK, "analyte_data": serialized_data, "message": "Labs updated for Round successfully."})
        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Round does not exist."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
