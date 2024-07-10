from datetime import datetime
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from databaseadmin.models import Scheme
from labowner.models import Lab, OfferedTest, Pathologist, SampleCollector
from labowner.serializers import LabInformationSerializer,  PathologistSerializer, OfferedTestSerializer

from labowner.models import Lab 
from labowner.serializers import LabInformationSerializer

from registrationadmin.serializers import RoundSerializer, ActivityLogUnitsSerializer
from registrationadmin.models import  ActivityLogUnits, Round
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Q
from account.models import UserAccount
from staff.models import Staff
from helpers.mail import send_mail
from django.conf import settings


# Create your views here
# API for displaying list of pending labs
class PendingLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
        try:
            
            pending_labs = Lab.objects.filter(
                status="Pending")
            serializer_class = LabInformationSerializer(
                pending_labs, many=True)
            for i in range(0, len(pending_labs)):
                if (pending_labs[i].marketer_id != None):
                    serializer_class.data[i]['marketer_name'] = pending_labs[i].marketer_id.name
                    serializer_class.data[i]['marketer_phone'] = pending_labs[i].marketer_id.phone
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})


# API for displaying list of approved labs
class ApproveUnapproveLabView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Patch request to update data of the Lab for approval
    def put(self, request, *args, **kwargs):
        try:
            staff = Staff.objects.get(account_id=kwargs.get('id'))
            try:
                lab = Lab.objects.get(id=request.data['lab_id'])

                request.data._mutable = True

                # If shared percentage (referee fee percentage) value is coming to API
                # It means it is approved operation otherwise it is assumed to be unapproved operation
                if request.data['is_approved'] == 'true':
                    request.data['status'] = 'Approved'
                else:
                    request.data['status'] = 'Unapproved'

                request.data['done_by'] = staff.id
                request.data['done_at'] = datetime.now()
                request.data._mutable = False

                serializer = LabInformationSerializer(
                    lab, data=request.data, partial=True)

                if serializer.is_valid():
                    serializer.save()

                    if request.data['is_approved'] == 'true':
                        subject, from_email, to = 'Approval Notification', settings.EMAIL_HOST_USER, lab.email

                        data = {
                            'lab_name': lab.name,
                            'email': lab.email,
                            'login_link': settings.LINK_OF_REACT_APP + "/login"
                        }

                        send_mail(subject, "approval-mail.html",
                                  from_email, to, data)
                        audit_data = {}
                        audit_data['lab_id'] = str(
                            serializer.data['id'])
                        audit_data['generated_at'] = str(
                            serializer.data['done_at'])
                    else:
                        subject, from_email, to = 'Non-Approval Notification', settings.EMAIL_HOST_USER, lab.email

                        data = {
                            'lab_name': lab.name,
                            'contact_email': "complaints@labhazir.com",
                            'contact_number': "+923018540968"
                        }

                        send_mail(subject, "nonapproval-mail.html",
                                  from_email, to, data)

                    return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Lab has been approved successfully."})
                else:
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

            except Lab.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No lab exist with this id."})

        except Staff.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No staff exist with this id."})


# API for displaying list of approved labs
class ApprovedLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
        try:
            approved_labs = Lab.objects.filter(
                status="Approved")
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

# API for displaying list of approved labs
class UnapprovedLabsView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
        try:
            unapproved_labs = Lab.objects.filter(Q(status="Unapproved") or Q(is_active="No"))
            serializer_class = LabInformationSerializer(
                unapproved_labs, many=True)
            for i in range(len(unapproved_labs)):
                serializer_class.data[i]['lab_phone'] = unapproved_labs[i].landline

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})


# API for displaying list of approved b2b clients
class ApproveUnapproveB2BClientView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

# API for displaying list of pending donors
class PendingDonorsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the test whose id is being passed
 
# API for displaying list of approved donors
class ApprovedDonorsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the test whose id is being passed

# API for displaying list of unapproved donors
class UnapprovedDonorsView(APIView):
    permission_classes = (AllowAny,)

# API for displaying list of approved donors
class ApproveUnapproveDonorView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    # Patch request to update data of the Lab for approval

class ReferrelLabTestListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            offered_test_list = OfferedTest.objects.filter(status="Pending")

            serializer_class = OfferedTestSerializer(
                offered_test_list, many=True)

            for i in range(0, len(offered_test_list)):
                serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

class ApproveReferrelLabTestListView(APIView):

    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def post(self, request, *args, **kwargs):
        try:
            offered_test_list = OfferedTest.objects.filter(test_id__name__icontains=request.data['test_name'], status="Approved")
            serialized_data = []

            for offered_test in offered_test_list:
                serialized_data.append({
                    'test_id': offered_test.test_id.id,
                    'test_name': offered_test.test_id.name,
                    'lab_name': offered_test.lab_id.name,
                    'price': offered_test.price,
                    'test_categories': offered_test.test_id.test_categories,
                    'lab_city': offered_test.lab_id.city,
                    'is_eqa_participation': offered_test.is_eqa_participation,
                    'is_home_sampling_available': offered_test.is_home_sampling_available,
                    'is_test_performed': offered_test.is_test_performed,
                    'shared_percentage': offered_test.shared_percentage,
                })

            return Response({"status": status.HTTP_200_OK, "data": serialized_data})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

        # page = int(request.data.get('page', 1))
        # print("data per page", page)
        # try:
        #     offered_test_list = OfferedTest.objects.filter(status="Approved")

        #     # Apply pagination to the queryset
        #     start_index = (page - 1) * self.PAGE_SIZE
        #     end_index = start_index + self.PAGE_SIZE
        #     paginated_offered_tests = offered_test_list[start_index:end_index]
        #     serializer_class = OfferedTestSerializer(
        #         paginated_offered_tests, many=True)

        #     response_data = []
        #     for i, data in enumerate(serializer_class.data):
        #         data['test_name'] = paginated_offered_tests[i].test_id.name
        #         data['lab_name'] = paginated_offered_tests[i].lab_id.name
        #         data['description_in_english'] = offered_test_list[i].test_id.description_in_english
        #         data['description_in_urdu'] = offered_test_list[i].test_id.description_in_urdu
        #         data['rating'] = offered_test_list[i].lab_id.rating
        #         data['all_end_date_by_labhazir'] = offered_test_list[i].test_id.end_date
        #         data['all_discount_by_labhazir'] = offered_test_list[i].test_id.discount
        #         data['lab_account_id'] = offered_test_list[i].lab_id.account_id.id
        #         data['lab_logo'] = str(offered_test_list[i].lab_id.logo)
        #         response_data.append(data)

        #     return JsonResponse({
        #         "status": status.HTTP_200_OK,
        #         "data": response_data,
        #         "has_next": len(offered_test_list) > end_index
        #     })

        # except OfferedTest.DoesNotExist:
        #     return JsonResponse({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

class UpdateReferrelLabTestListView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):

        try:
            test = OfferedTest.objects.get(id=kwargs.get('id'))
            serializer = OfferedTestSerializer(
                test, data=request.data, partial=True)

            request.data._mutable = True

            if request.data['shared_percentage'] == "":
                request.data['status'] = 'Pending'
            else:
                request.data['status'] = 'Approved'

            request.data._mutable = False

            if serializer.is_valid():
                serializer.save()

                # Check if lab type is "Main Lab"
                if test.lab.type == 'Main Lab':
                    # Update shared_percentage and status for associated collection points
                    collection_points = Lab.objects.filter(
                        main_lab_account_id=test.lab_id.account_id.id)

                    for collection_point in collection_points:
                        print("branch_lab ", collection_point,
                              collection_point.id)
                        offered_test_branch = OfferedTest.objects.filter(
                            lab_id=collection_point.id, test_id=test.test_id).update(price=request.data['price'])
                        print("offered test baches or not ",
                              offered_test_branch)

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Information updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class LabListPendingView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):

        try:
            offered_test_list = OfferedTest.objects.filter(
                status="Pending").values_list('lab_id', flat=True).distinct()
            print("offered test:", offered_test_list)

            labs_lists = []
            for i in range(0, len(offered_test_list)):
                labs_list = Lab.objects.filter(
                    id=offered_test_list[i], type="Main Lab")
                lab_serializer = LabInformationSerializer(
                    labs_list, many=True)
                # for i in range(0, len(offered_test_list)):
                #     serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories

                # return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
                # print ("catagorines",serializer_class.data[i]['test_categories'])
                labs_lists.append({
                    "lab_list": lab_serializer.data, })
                print("lab serilizer:", lab_serializer.data)

            return Response({"status": status.HTTP_200_OK, "data": labs_lists})
            # return Response({"status": status.HTTP_200_OK, "data":lab_serializer.data})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

class LabListApprovedView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):

        try:
            offered_test_list = OfferedTest.objects.filter(
                status="Approved").values_list('lab_id', flat=True).distinct()
            print("offered test:", offered_test_list)

            labs_lists = []
            for i in range(0, len(offered_test_list)):
                labs_list = Lab.objects.filter(
                    id=offered_test_list[i], type="Main Lab")
                lab_serializer = LabInformationSerializer(
                    labs_list, many=True)

                print(labs_list)
                labs_lists.append({
                    "lab_list": lab_serializer.data, })
                print("lab serilizer:", lab_serializer.data)

            return Response({"status": status.HTTP_200_OK, "data": labs_lists})
            # return Response({"status": status.HTTP_200_OK, "data":lab_serializer.data})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

class SharePercentageApprovedLabTestListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(id=kwargs.get('id'))
            try:

                offered_test_list = OfferedTest.objects.filter(
                    lab_id=lab.id, status="Approved")
                print("bbbb", offered_test_list)

                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)
                # if serializer_class.is_valid():
                #         serializer_class.save()
                # return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Offered Test information added successfully."})
                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                    serializer_class.data[i]['lab_city'] = offered_test_list[i].lab_id.city

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

class SharePercentagePendingLabTestListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            lab = Lab.objects.get(id=kwargs.get('id'))
            try:

                offered_test_list = OfferedTest.objects.filter(
                    lab_id=lab.id, status="Pending")
                print("bbbb", offered_test_list)

                serializer_class = OfferedTestSerializer(
                    offered_test_list, many=True)
                # if serializer_class.is_valid():
                #         serializer_class.save()
                # return Response({"status": status.HTTP_200_OK, "data": serializer_class.data, "message": "Offered Test information added successfully."})
                for i in range(0, len(offered_test_list)):
                    serializer_class.data[i]['test_categories'] = offered_test_list[i].test_id.test_categories
                    serializer_class.data[i]['test_name'] = offered_test_list[i].test_id.name
                    serializer_class.data[i]['lab_name'] = offered_test_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except OfferedTest.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

    def put(self, request, *args, **kwargs):

        try:
            test = OfferedTest.objects.get(id=kwargs.get('id'))
            serializer = OfferedTestSerializer(
                test, data=request.data, partial=True)

            request.data._mutable = True

            if request.data['shared_percentage'] == "":
                request.data['status'] = 'Pending'
            else:
                request.data['status'] = 'Approved'

            request.data._mutable = False

            if serializer.is_valid():
                serializer.save()

                # Check if lab type is "Main Lab"
                if test.lab_id.type == 'Main Lab':
                    # Update shared_percentage and status for associated collection points
                    collection_points = Lab.objects.filter(
                        main_lab_account_id=test.lab_id.account_id.id)

                    for collection_point in collection_points:
                        print("branch_lab ", collection_point,
                              collection_point.id)
                        offered_test_branch = OfferedTest.objects.filter(lab_id=collection_point.id, test_id=test.test_id).update(
                            shared_percentage=request.data['shared_percentage'], status='Approved')
                        print("offered test baches or not ",
                              offered_test_branch)

                return Response({"status": status.HTTP_200_OK, "data": serializer.data, "message": "Information updated successfully."})
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": serializer._errors})

        except OfferedTest.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such record exists."})

class SharePercentageAllPendingLabTestView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        lab_id = kwargs.get('id')

        try:
            lab = Lab.objects.get(id=lab_id)

            # Update OfferedTest objects for the lab
            OfferedTest.objects.filter(lab_id=lab_id, status="Pending").update(
                shared_percentage=request.data['shared_percentage'], 
                status="Approved"
            )

            if lab.type == 'Main Lab':
                # Update CollectionPoint objects for the lab
                OfferedTest.objects.filter(lab_id=lab_id).update(
                    shared_percentage=request.data['shared_percentage'], 
                    status="Approved"
                )

            return Response({"status": status.HTTP_200_OK, "message": "Share Percentage Added successfully."})
        
        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

# ////////////////////////
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
            user_id = kwargs.get('id')
            # Fetch user_type based on user_id
            user_type = UserAccount.objects.get(id=user_id)
            
            if user_type.account_type == 'labowner':
                try:
                    participant = Lab.objects.get(account_id=user_id)
                    organization = participant.organization_id
                    round_list = Round.objects.filter(organization_id=organization.id)
                except Lab.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Lab not found."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    staff_member = Staff.objects.get(account_id=user_id)
                    organization = staff_member.organization_id
                    round_list = Round.objects.filter(organization_id=organization.id)
                    
                except Staff.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Staff member not found."
                    }, status=status.HTTP_404_NOT_FOUND)
                
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

    # def get(self, request, *args, **kwargs):
    #     try:
    #         # Get the staff user's account_id
    #         account_id = kwargs.get('id')
            
    #         # Fetch the staff user based on account_id
    #         staff_user = Staff.objects.get(account_id=account_id)
            
    #         # Retrieve the organization associated with the staff user
    #         organization = staff_user.organization_id

    #         # Filter rounds based on the organization
    #         round_list = Round.objects.filter(organization_id=organization)
            
    #         # Serialize rounds data including scheme name
    #         serialized_data = []
    #         for round_obj in round_list:
    #             round_data = model_to_dict(round_obj)
    #             scheme = round_obj.scheme
    #             if scheme:
    #                 round_data['scheme_name'] = scheme.name
    #             else:
    #                 round_data['scheme_name'] = None  # Handle case where scheme is None
    #             serialized_data.append(round_data)

    #         return Response({"status": status.HTTP_200_OK, "data": serialized_data})
        
    #     except Staff.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid account_id."})
        
    #     except Round.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Round records found."})

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
            labs = round.labs.all()  # Fetch all labs associated with the round
            lab_ids = [lab.id for lab in labs]
            
            # Serialize data
            serialized_data = {
                #"round": RoundSerializer(round).data,
                "labs": lab_ids  # Send list of lab IDs
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
            
            # Ensure 'labs' is parsed as a list of integers
            labs = request.data.get('labs', [])
            if isinstance(labs, str):
                labs = list(map(int, labs.split(',')))
            
            round.labs.set(labs)  # Assuming labs are passed as a list of IDs
            round.save()

            return Response({"status": status.HTTP_200_OK, "message": "Labs added to round successfully."})
        except Round.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Round not found."})
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})