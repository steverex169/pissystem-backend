from datetime import datetime
import datetime
from django.forms.models import model_to_dict
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from databaseadmin.models import Cycle, Scheme
from registrationadmin.serializers import AnalyteSchemeSerializer,RoundSerializer, ActivityLogUnitsSerializer, PaymentSerializer,SelectedSchemeSerializer, StatisticsSerializer
from registrationadmin.models import   ActivityLogUnits, Round, Payment, SelectedScheme
from staff.models import Staff

from labowner.models import Lab, OfferedTest, Pathologist, Result, SampleCollector
from labowner.serializers import LabInformationSerializer,  PathologistSerializer, OfferedTestSerializer, ResultSerializer
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Q
from account.models import UserAccount
from organization.models import Organization
from django.shortcuts import get_object_or_404

from django.db import transaction

from django.db.models import Avg
import numpy as np 
import decimal
from decimal import Decimal
import math
from scipy.stats import trim_mean
import logging
logger = logging.getLogger(__name__)
import ast


class UpdateMembershipStatusView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        try:
            # Fetch the staff user based on account_id
            account_id = request.data.get('added_by')
            staff_user = Staff.objects.get(account_id=account_id)

            # Retrieve the organization associated with the staff user
            organization = staff_user.organization_id

            # Retrieve the existing status object
            membership_status = Lab.objects.get(id=kwargs.get('id'), organization_id=organization)

            serializer = LabInformationSerializer(membership_status, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer.errors})
                
        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class PaymentPostAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            account_id = request.data['added_by']
            staff_user = Staff.objects.get(account_id=account_id)
            organization = staff_user.organization_id

            try:
                participant = Lab.objects.get(id=request.data.get('participant'))
                print("labbbbbbbbbbbbb", participant)
            except Lab.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid participant name provided."})
            
            scheme_ids_str = request.data.get('scheme', '')
            scheme_ids = [int(sid) for sid in scheme_ids_str.split(',') if sid.isdigit()]
            # print("schemeeee", scheme_ids)

            with transaction.atomic():

                payment = Payment.objects.create(
                    organization_id=organization,
                    participant_id=participant,
                    price=request.data['price'],
                    scheme=scheme_ids,
                    discount=request.data['discount'],
                    photo=request.data['photo'],
                    paymentmethod=request.data['paymentmethod'],
                    paydate=request.data['paydate']
                )

                participant.payment_status = 'Paid'
                participant.save()

                selected_scheme = SelectedScheme.objects.create(
                    organization_id=organization,
                    scheme_id=scheme_ids,
                    added_at=datetime.datetime.now()

                )
                selected_scheme.participant = participant.id
                selected_scheme.save()
                # print("selected scheme", selected_scheme, selected_scheme.participant, participant.id)

                payment_serializer = PaymentSerializer(payment)
                selected_scheme_serializers = SelectedSchemeSerializer(selected_scheme)

                return Response({
                    "status": status.HTTP_201_CREATED,
                    "payment_data": payment_serializer.data,
                    "selected_schemes": selected_scheme_serializers.data,
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

class AllLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            organization = staff.organization_id
            pending_labs = Lab.objects.filter(organization_id=organization)
            
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
                round_data = {
                    "id": round_obj.id,
                    "nooflabs": round_obj.nooflabs,
                    "rounds": round_obj.rounds,
                    "cycle_no": round_obj.cycle_no,
                    "sample": round_obj.sample,
                    "issue_date": round_obj.issue_date,
                    "closing_date": round_obj.closing_date,
                    "status": round_obj.status,
                    "account_id": round_obj.account_id_id if round_obj.account_id else None,
                    "organization_id": round_obj.organization_id_id if round_obj.organization_id else None,
                    "scheme": round_obj.scheme.id if round_obj.scheme else None,
                    "participant_count": round_obj.participants.count(),
                }
                 # Count participants
                round_data['participant_count'] = round_obj.participants.count()
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
            old_values = {field: getattr(round, field) for field in ["rounds", "scheme", "cycle_no", "sample", "issue_date", "closing_date", "status"]}
            
            serializer = RoundSerializer(round, data=request.data, partial=True)

            if serializer.is_valid():
                updated_round = serializer.save()
                
                # Retrieve new values after updating
                new_values = {field: getattr(updated_round, field) for field in ["rounds", "scheme", "cycle_no", "sample", "issue_date", "closing_date", "status"]}

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
        round_id = kwargs.get('id')
        try:
            round_instance = Round.objects.get(id=round_id)
            
            # Check if the round's status is 'Open'
            if round_instance.status == 'Open':
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Cannot delete round. It is currently open."})
            
            round_instance.delete()
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

# Participants Dashboard Rounds API      
class SelectedSchemeListAPIView(APIView):
      def get(self, request, *args, **kwargs):
        try:
            account_id = kwargs.get('id')
            # Fetch the participant (Lab) based on account_id
            participant = Lab.objects.get(account_id=account_id)
            
            # Fetch all SelectedScheme instances for the given participant
            selected_schemes = SelectedScheme.objects.filter(participant=participant.id)
            
            # List to hold serialized data
            serialized_data = []
            
            for selected_scheme in selected_schemes:
                # Assuming selected_scheme.scheme_id is a string representation of a list
                scheme_ids = ast.literal_eval(selected_scheme.scheme_id)
                # Filter Cycle objects based on the scheme_ids (which correspond to Cycle ids)
                cycles = Cycle.objects.filter(id__in=scheme_ids)
                
                for cycle in cycles:
                    # Fetch Scheme object associated with the Cycle
                    scheme = cycle.scheme_name
                    
                    # Fetch related Round data for each scheme
                    rounds = Round.objects.filter(scheme=scheme)
                    
                    # Serialize round data
                    rounds_data = [
                        {
                            'rounds': round.rounds,
                            'cycle_no': round.cycle_no,
                            'sample': round.sample,
                            'issue_date': round.issue_date,
                            'closing_date': round.closing_date,
                            'status': round.status,
                        }
                        for round in rounds
                    ]
                    
                    # Serialize the scheme data along with rounds data
                    scheme_data = {
                        'id': scheme.id,
                        'name': scheme.name,
                        'status': scheme.status,
                        'price': scheme.price,
                        'rounds': rounds_data  # Include rounds data here
                    }
                    serialized_data.append(scheme_data)

            # Return the serialized data as JSON response
            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Participant not found."})

        except ValueError as ve:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(ve)})
        
        except SelectedScheme.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
        
    # def get(self, request, *args, **kwargs):
    #     try:
    #         account_id = kwargs.get('id')
    #         # print("account_idddddd", account_id)
    #         participant_id = Lab.objects.get(account_id=account_id)
            
    #         # Fetch all SelectedScheme instances for the given participant
    #         selected_schemes = SelectedScheme.objects.filter(participant=participant_id.id)
    #         print("selected_schemesssss", selected_schemes)
    #             # List to hold serialized data
    #         serialized_data = []
            
    #         for selected_scheme in selected_schemes:
    #             # Assuming selected_scheme.scheme_id is a string representation of a list
    #             # Use ast.literal_eval(selected_scheme.scheme_id) to convert the string back into a list
    #             scheme_ids = ast.literal_eval(selected_scheme.scheme_id)
                
    #             # Fetch Scheme objects corresponding to each scheme_id
    #             schemes = Scheme.objects.filter(id__in=scheme_ids)
    #             # print("Schemesssss:", schemes)
    #             # Serialize each Scheme object
    #             for scheme in schemes:
    #                 # Fetch related Round data for each scheme and include related Round data
    #                 # rounds = Round.objects.filter(scheme_id=scheme.id) OR 
    #                 rounds = Round.objects.filter(scheme=scheme)
    #                 # print("Rounds for Scheme:", scheme.id, rounds)

    #                 rounds_data = [
    #                     {
    #                         'rounds': round.rounds,
    #                         'cycle_no': round.cycle_no,
    #                         'sample': round.sample,
    #                         'issue_date': round.issue_date,
    #                         'closing_date': round.closing_date,
    #                         'status': round.status,
    #                     }
    #                     for round in rounds
    #                 ]
    #                 scheme_data = {
    #                     'id':scheme.id,
    #                     'name': scheme.name,
    #                     'status': scheme.status,
    #                     'price': scheme.price,
    #                     'rounds': rounds_data  # Include rounds data here
    #                 }
    #                 serialized_data.append(scheme_data)

    #         # Return the serialized data as JSON response
    #         return Response({"status": status.HTTP_200_OK, "data": serialized_data})

    #     except ValueError as ve:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(ve)})
        
    #     except SelectedScheme.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})



class ParticipantResultView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # filtering only unique analyte records
            participant_results = Result.objects.filter(scheme_id=kwargs.get('id'))  
            serializer = ResultSerializer(participant_results, many=True)
            return Response({"status": status.HTTP_200_OK, "data": serializer.data})
        except Result.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such Result exists."})
        
    # Delete request to delete data of the sample collactor
    def delete(self, request, *args, **kwargs):
            try:
                result_id = kwargs.get('id')

                Result.objects.get(id=result_id).delete()

                return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

            except Result.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})
            except Result.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Result exists."})
    
    def put(self, request, *args, **kwargs):
        try:
            # Here what we are getting as id is the id of offered test record to be updated
            ParticipentResult = Result.objects.get(id=kwargs.get('id'))

            serializer = ResultSerializer(
                ParticipentResult, data=request.data, partial=False)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Result updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except Result.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

    def post(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(account_id=kwargs.get('id'))
            organization = lab.organization_id

            # Prepare the data to be saved or updated
            data = {
                'scheme_id': request.data.get('scheme_id'),
                'lab_id': lab.id,
                'organization_id': organization.id if organization else None,
                'units': request.data.get('unit_name'),
                'instrument': request.data.get('instrument_name'),
                'method': request.data.get('method_name'),
                'reagents': request.data.get('reagent_name'),
                'result': request.data.get('result'),
                'analyte': request.data.get('analyte_id'),
                'rounds': request.data.get('rounds'),
            }

            # Check if the result already exists for the given lab, analyte, and round
            existing_result = Result.objects.filter(
                lab_id=lab.id,
                analyte_id=request.data.get('analyte_id'),
                rounds=request.data.get('rounds')
            ).first()

            if existing_result:
                # If it exists, update the existing record
                serializer = ResultSerializer(existing_result, data=data)
                action = "updated"
            else:
                # If it doesn't exist, create a new record
                serializer = ResultSerializer(data=data)
                action = "created"

            # Save the result and return the appropriate response
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": status.HTTP_200_OK, 
                    "data": serializer.data, 
                    "message": f"Participant result {action} successfully."
                })
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST, 
                    "message": serializer.errors
                })

        except Lab.DoesNotExist:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST, 
                "message": "No such Lab exists."
            })

        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR, 
                "message": str(e)
            })

    

# Analytes related to single scheme        
class AnalyteSpecificScheme(APIView):
    def get(self, request, *args, **kwargs):
        try:
            scheme_id = kwargs.get('id')
            # Fetch the Scheme object
            scheme = Scheme.objects.get(id=scheme_id)
            print("schemeeeeeeeeeeeeee", scheme, scheme_id)
            
            # Get all analytes associated with this scheme
            analytes = scheme.analytes.all()
            print("analytesss", analytes)
            
            # Serialize the analytes data
            analyte_serializer = AnalyteSchemeSerializer(analytes, many=True)

            # Fetch the Round entries associated with this scheme and having status 'Ready'
            rounds = Round.objects.filter(scheme=scheme)

            # Serialize the round data
            round_serializer = RoundSerializer(rounds, many=True)

           # Fetch all Result entries associated with this scheme
            results = Result.objects.filter(scheme_id=scheme_id)
            result_serializer = ResultSerializer(results, many=True)

            # Create a list to store participant IDs
            participant_ids = []

            # Iterate through each Result to fetch the corresponding lab's account_id
            for result in results:
                lab = result.lab_id  # Fetch the related Lab 
                participant_id = lab.account_id_id # Get the account_id from the Lab object
                participant_ids.append(participant_id)  # Add to the list

            # Include the scheme name, round data, and participant IDs in the response
            response_data = {
                'scheme_name': scheme.name,
                'analytes': analyte_serializer.data,
                'rounds': round_serializer.data,
                'participant_ids': participant_ids  # Include all participant IDs
            }


            return Response({'status': status.HTTP_200_OK, 'data': response_data}, status=status.HTTP_200_OK)
        
        except Scheme.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Scheme not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# API for calculating number of labs who has submitted the results against specific analyte 
class AnalyteResultSubmit(APIView):
    def get(self, request, *args, **kwargs):
        try:
            scheme_id = kwargs.get('id')
            scheme = Scheme.objects.get(id=scheme_id)
            organization = scheme.organization_id
            analytes = scheme.analytes.all()

            analyte_results = []

            for analyte in analytes:
                results = Result.objects.filter(scheme_id=scheme_id, analyte=analyte, organization_id=organization)
                lab_count = results.values('lab_id').distinct().count()
                mean_result = results.aggregate(mean_result=Avg('result'))['mean_result']
                mean_result_rounded = round(float(mean_result), 2) if mean_result is not None else 0
                result_values = list(results.values_list('result', flat=True).exclude(result=None))

                if result_values:
                    sorted_results = sorted(result_values)
                    median_result = sorted_results[len(sorted_results) // 2]
                    mean_result_rounded_float = float(mean_result_rounded)
                    variance = sum((float(value) - mean_result_rounded_float) ** 2 for value in result_values) / len(result_values)
                    std_deviation = math.sqrt(variance)
                    cv_percentage = round((std_deviation / mean_result_rounded_float) * 100, 2)
                    uncertainty = round(std_deviation / math.sqrt(len(result_values)), 2)
                    trimmed_mean = trim_mean(result_values, 0.1)
                    robust_mean = round(trimmed_mean, 2)
                    z_scores_with_lab = [
                        {
                            'lab_id': result.lab_id.id,
                            'z_score': round((float(result.result) - mean_result_rounded_float) / std_deviation, 4)
                        }
                        for result in results
                    ]
                else:
                    median_result = 0.00
                    std_deviation = 0.00
                    cv_percentage = 0.00
                    uncertainty = 0.00
                    robust_mean = 0.00
                    z_scores_with_lab = []

                # Update or create Statistics instance
                statistics_instance = None  # Initialize before the loop
                for result in results:
                    # Update or create Statistics instance
                    statistics_instance, created = Statistics.objects.update_or_create(
                        scheme=scheme,
                        analyte=analyte,
                        participant_id=result.lab_id,  
                        organization_id=organization,    
                        defaults={
                            'lab_count': lab_count,
                            'mean_result': mean_result_rounded,
                            'median_result': median_result,
                            'std_deviation': round(std_deviation, 2),
                            'cv_percentage': cv_percentage,
                            'uncertainty': uncertainty,
                            'robust_mean': robust_mean,
                            'z_scores_with_lab': z_scores_with_lab,
                            'rounds': result.rounds,
                            'result': result.result
                        }
                    )

                analyte_results.append(statistics_instance)
            # Serialize the saved Statistics instances
            serializer = StatisticsSerializer(analyte_results, many=True)
            logger.info("Serializer data: %s", serializer.data)  # Using logger for better output handling
            return Response({'status': status.HTTP_200_OK, 'data': serializer.data}, status=status.HTTP_200_OK)

        except Scheme.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Scheme not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)