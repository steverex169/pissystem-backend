from datetime import datetime
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from labowner.models import Lab, OfferedTest, Pathologist, SampleCollector
from labowner.serializers import LabInformationSerializer,  PathologistSerializer, OfferedTestSerializer

from labowner.models import Lab 
from labowner.serializers import LabInformationSerializer

from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Q
from account.models import UserAccount

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


# API for displaying list of approved labs
# class ApprovedLabsView(APIView):
#     permission_classes = (IsAuthenticated,)

#     # Get request to get data of the cart
#     def get(self, request, *args, **kwargs):
#         try:
#             approved_labs = Lab.objects.filter(
#                 status="Approved")
#             offertest = OfferedTest.objects.filter(
#                         lab_id=approved_labs).annotate(
#                 num_offered_tests=Count('test_id'),
#             )
#             serializer_class = LabInformationSerializer(
#                 approved_labs, many=True)

#             for i in range(0, len(approved_labs)):
#                 serializer_class.data[i]['lab_address'] = approved_labs[i].address
#                 serializer_class.data[i]['lab_email'] = approved_labs[i].email
#                 serializer_class.data[i]['lab_city'] = approved_labs[i].city
#                 serializer_class.data[i]['lab_phone'] = approved_labs[i].landline
#                 serializer_class.data[i]['offered_tests'] = offertest[i].num_offered_tests
#                 serializer_class.data[i]['lab_name'] = approved_labs[i].name
#                 print("offeref test have or not", offertest[i].num_offered_tests)
#                 serializer_class.data[i]['pathologists'] = approved_labs[i].pathologists
#                 serializer_class.data[i]['sample_collectors'] = approved_labs[i].sample_collectors
#                 serializer_class.data[i]['quality_certificates'] = approved_labs[i].quality_certificates


#             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

#         except Lab.DoesNotExist:
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No pending labs exist."})
class ApprovedLabsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            approved_labs = Lab.objects.filter(status="Approved", is_active="Yes")
            offertest = OfferedTest.objects.filter(lab_id__in=approved_labs).values('lab_id').annotate(num_offered_tests=Count('test_id', distinct=True))
            pathologist = Pathologist.objects.filter(lab_id__in=approved_labs).values('lab_id').annotate(num_pathologist=Count('id', distinct=True))
            scolletor = SampleCollector.objects.filter(lab_id__in=approved_labs).values('lab_id').annotate(num_scollector=Count('id', distinct=True))
            # qualityc = QualityCertificate.objects.filter(lab_id__in=approved_labs).values('lab_id').annotate(num_qualityc=Count('id', distinct=True))
            print("offertest", offertest)

            serializer_class = LabInformationSerializer(approved_labs, many=True)

            for i in range(len(approved_labs)):
                lab_id = approved_labs[i].id

                matching_offertest = next((item for item in offertest if item['lab_id'] == lab_id), None)
                # matching_qualityc = next((item for item in qualityc if item['lab_id'] == lab_id), None)
                matching_scolletor = next((item for item in scolletor if item['lab_id'] == lab_id), None)
                matching_pathologist = next((item for item in pathologist if item['lab_id'] == lab_id), None)

                serializer_class.data[i]['offered_tests'] = matching_offertest['num_offered_tests'] if matching_offertest else 0
                # serializer_class.data[i]['quality_certificates'] = matching_qualityc['num_qualityc'] if matching_qualityc else 0
                serializer_class.data[i]['sample_collectors'] = matching_scolletor['num_scollector'] if matching_scolletor else 0
                serializer_class.data[i]['pathologists'] = matching_pathologist['num_pathologist'] if matching_pathologist else 0

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
