# from datetime import timedelta
import datetime
import requests
import base64
import gzip

from financeofficer.models import ActivityLogFinance, PaymentIn, PaymentOut, BankTransferDetail, InvoiceAdjustment
from financeofficer.serializers import  ActivityLogFinanceSerializer, InvoiceAdjustmentSerializer, PaymentInSerializer, PaymentOutSerializer, BankTransferDetailSerializer


import shortuuid
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework import status
from account.models import UserAccount
from accountstatement.models import  AccountStatement,  BankAccountStatement
from accountstatement.serializers import  BankAccountStatementSerializer, AccountStatementSerializer


from labowner.models import Lab, LabCorporate
from labowner.serializers import LabInformationSerializer, LabCorporateSerializer

from staff.models import Staff

from django.db.models import Window, Sum, F
from django.db.models import Count, Q
from django.core.exceptions import MultipleObjectsReturned



class DonorListView(APIView):
    permission_classes = (AllowAny,)

        

# API for adding donor in payment and creating account statement
class PaymentInView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            donor_finance = PaymentIn.objects.filter()
            serializer_class = PaymentInSerializer(
                donor_finance, many=True)
            # for i in range(0, len(donor_finance)):
            #     serializer_class.data[i]['lab_name'] = donor_finance[i].lab_id.name
                # serializer_class.data[i]['patient_account_id'] = donor_finance[i].patient_id.account_id.id

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except PaymentIn.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})


    # Post request for donor in payment
 # Put request to update data of the sample collactor


        
    def delete(self, request, *args, **kwargs):
        try:
            PaymentIn.objects.get(id=kwargs.get('id')).delete()
            return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

        except PaymentIn.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})

class IsmaListView(APIView):
    permission_classes= (AllowAny, )
    def get(self, request, *args, **kwargs):
        try:
            isma = UserAccount.objects.get(id= kwargs.get('id'))
            try:
                ismalist= PaymentIn.objects.filter(payment_status= "Created")
                serializer_class = PaymentInSerializer(ismalist, many= True)
                for i in range(0, len(ismalist)):
                    if(ismalist[i].lab_id != None ):
                        serializer_class[i]['lab_name']= ismalist[i].lab_id.name

                return Response({"status":status.HTTP_200_OK, "data":serializer_class.data})  
            except PaymentIn.DoesNotExist:
                return Response({"srtatus": status.HTTP_400_BAD_REQUEST, "message": "no record found"})
        except UserAccount.DoesNotExist:
           return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Np such account exist"})        
class PaymentInCreatedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_in_created_list = PaymentIn.objects.filter(
                    payment_status="Created")
   
                # payment_in_created_list = PaymentIn.objects.all()
                serializer_class = PaymentInSerializer(
                    payment_in_created_list, many=True)

                for i in range(0, len(payment_in_created_list)):
                    if (payment_in_created_list[i].advertisement_id != None): 
                        serializer_class.data[i]['advertisement_title'] = payment_in_created_list[i].advertisement_id.title
                    if (payment_in_created_list[i].donor_id != None): 
                        serializer_class.data[i]['donor_name'] = payment_in_created_list[i].donor_id.name
                    if (payment_in_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_in_created_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentIn.DoesNotExist:

                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})

class PaymentInDepositedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_in_created_list = PaymentIn.objects.filter(
                    payment_status="Pending Clearance")
                serializer_class = PaymentInSerializer(
                    payment_in_created_list, many=True)

                for i in range(0, len(payment_in_created_list)):
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['account_no'] = payment_in_created_list[i].bankaccount_id.account_no
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['bank_name'] = payment_in_created_list[i].bankaccount_id.bank_id.name
                        print("account no have", payment_in_created_list[i].bankaccount_id.bank_id.name)
                    if (payment_in_created_list[i].advertisement_id != None): 
                        serializer_class.data[i]['advertisement_title'] = payment_in_created_list[i].advertisement_id.title
                    if (payment_in_created_list[i].donor_id != None): 
                        serializer_class.data[i]['donor_name'] = payment_in_created_list[i].donor_id.name
                    if (payment_in_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_in_created_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentIn.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})

class PaymentInClearedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_in_created_list = PaymentIn.objects.filter(
                    payment_status="Cleared")
                serializer_class = PaymentInSerializer(
                    payment_in_created_list, many=True)
                for i in range(0, len(payment_in_created_list)):
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['account_no'] = payment_in_created_list[i].bankaccount_id.account_no
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['bank_name'] = payment_in_created_list[i].bankaccount_id.bank_id.name
                    if (payment_in_created_list[i].advertisement_id != None): 
                        serializer_class.data[i]['advertisement_title'] = payment_in_created_list[i].advertisement_id.title
                    if (payment_in_created_list[i].donor_id != None): 
                        serializer_class.data[i]['donor_name'] = payment_in_created_list[i].donor_id.name
                    if (payment_in_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_in_created_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except PaymentIn.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})

class PaymentInBouncedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_in_created_list = PaymentIn.objects.filter(
                    payment_status="Bounced")
                serializer_class = PaymentInSerializer(
                    payment_in_created_list, many=True)
                for i in range(0, len(payment_in_created_list)):
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['account_no'] = payment_in_created_list[i].bankaccount_id.account_no
                    if (payment_in_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['bank_name'] = payment_in_created_list[i].bankaccount_id.bank_id.name
                    if (payment_in_created_list[i].advertisement_id != None): 
                        serializer_class.data[i]['advertisement_title'] = payment_in_created_list[i].advertisement_id.title
                    if (payment_in_created_list[i].donor_id != None): 
                        serializer_class.data[i]['donor_name'] = payment_in_created_list[i].donor_id.name
                    if (payment_in_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_in_created_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentIn.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})

class PaymentOutView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            donor_finance = PaymentOut.objects.all()

            serializer_class = PaymentOutSerializer(
                donor_finance, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except PaymentOut.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
    # Post request for donor in payment

    #Put request to update data of the sample collactor

class PaymentOutPendingListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_out_created_list = PaymentOut.objects.filter(
                    status="Pending Clearance")
                # payment_out_created_list = PaymentOut.objects.all()
                serializer_class = PaymentOutSerializer(
                    payment_out_created_list, many=True)
                
                for i in range(0, len(payment_out_created_list)):
                    if (payment_out_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['account_no'] = payment_out_created_list[i].bankaccount_id.account_no
                        print("account no have", payment_out_created_list[i].bankaccount_id.account_no)

                        serializer_class.data[i]['bank_name'] = payment_out_created_list[i].bankaccount_id.bank_id.name
                    if (payment_out_created_list[i].b2b_id != None): 
                        serializer_class.data[i]['business_name'] = payment_out_created_list[i].b2b_id.business_name
                    if (payment_out_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_out_created_list[i].lab_id.name
                    
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentOut.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})


class PaymentOutCreatedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_out_created_list = PaymentOut.objects.filter(
                    status="Created")
                # payment_out_created_list = PaymentOut.objects.all()
                serializer_class = PaymentOutSerializer(
                    payment_out_created_list, many=True)

                for i in range(0, len(payment_out_created_list)):
                    if (payment_out_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['bank_account_no'] = payment_out_created_list[i].bankaccount_id.account_no
                        print("account no have", payment_out_created_list[i].bankaccount_id.account_no)

                        serializer_class.data[i]['bank_name'] = payment_out_created_list[i].bankaccount_id.bank_id.name
                    if (payment_out_created_list[i].b2b_id != None): 
                        serializer_class.data[i]['business_name'] = payment_out_created_list[i].b2b_id.business_name
                    if (payment_out_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_out_created_list[i].lab_id.name

                    
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentOut.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})


class PaymentOutBouncedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_out_created_list = PaymentOut.objects.filter(
                    status="Bounced")
                # payment_out_created_list = PaymentOut.objects.all()
                serializer_class = PaymentOutSerializer(
                    payment_out_created_list, many=True)

                for i in range(0, len(payment_out_created_list)):
                    serializer_class.data[i]['account_no'] = payment_out_created_list[i].bankaccount_id.account_no
                    serializer_class.data[i]['bank_name'] = payment_out_created_list[i].bankaccount_id.bank_id.name
                    if (payment_out_created_list[i].b2b_id != None): 
                        serializer_class.data[i]['business_name'] = payment_out_created_list[i].b2b_id.business_name
                    if (payment_out_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_out_created_list[i].lab_id.name
                    
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
            except PaymentOut.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})

class PaymentOutnClearedListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            finance_officer = UserAccount.objects.get(id=kwargs.get('id'))
            try:
                payment_out_created_list = PaymentOut.objects.filter(
                    status="Cleared")
                serializer_class = PaymentOutSerializer(
                    payment_out_created_list, many=True)
                for i in range(0, len(payment_out_created_list)):
                    if (payment_out_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['account_no'] = payment_out_created_list[i].bankaccount_id.account_no
                        print("account no have", payment_out_created_list[i].bankaccount_id.account_no)
                    if (payment_out_created_list[i].bankaccount_id != None): 
                        serializer_class.data[i]['bank_name'] = payment_out_created_list[i].bankaccount_id.bank_id.name
                        print("account no have", payment_out_created_list[i].bankaccount_id.bank_id.name)
                    # if (payment_out_created_list[i].advertisement_id != None): 
                    #     serializer_class.data[i]['advertisement_title'] = payment_out_created_list[i].advertisement_id.title
                    if (payment_out_created_list[i].b2b_id != None): 
                        serializer_class.data[i]['business_name'] = payment_out_created_list[i].b2b_id.business_name
                    if (payment_out_created_list[i].lab_id != None): 
                        serializer_class.data[i]['lab_name'] = payment_out_created_list[i].lab_id.name
                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except PaymentIn.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

        except UserAccount.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such Finance Officer account exists."})
        
# API for offered test list
class LabMOFListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            labs = Lab.objects.filter(is_blocked="No",
                status="Approved")
            serializer_class = LabInformationSerializer(
                labs, many=True)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except Lab.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such lab account exists."})

class AllLabListForCorporateView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            labcorporate = LabCorporate.objects.filter(status="Accept", remaining_amount__gt=0)
            print(labcorporate)
            serializer_class = LabCorporateSerializer(
                labcorporate, many=True)

            for i in range(0, len(labcorporate)):
                serializer_class.data[i]['name'] = labcorporate[i].lab_id.name
                serializer_class.data[i]['corporate_name'] = labcorporate[i].corporate_id.name
                serializer_class.data[i]['office'] = labcorporate[i].lab_id.office
                serializer_class.data[i]['type'] = labcorporate[i].lab_id.type
                serializer_class.data[i]['city'] = labcorporate[i].lab_id.city
                serializer_class.data[i]['lab_phone'] = labcorporate[i].lab_id.phone
                serializer_class.data[i]['lab_email'] = labcorporate[i].lab_id.email

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except LabCorporate.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})



# 
class InvoiceAdjustmentView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            donor_finance = InvoiceAdjustment.objects.all()

            serializer_class = InvoiceAdjustmentSerializer(
                donor_finance, many=True)

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except InvoiceAdjustment.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
    # Post request for donor in payment

class BankTransferDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            bank_transfer = BankTransferDetail.objects.all()

            serializer_class = BankTransferDetailSerializer(
                bank_transfer, many=True)
            
            for i in range(0, len(bank_transfer)):
                if (bank_transfer[i].bankaccount_id != None): 
                    serializer_class.data[i]['account_no'] = bank_transfer[i].bankaccount_id.account_no
                    serializer_class.data[i]['bank_name'] = bank_transfer[i].bankaccount_id.bank_id.name
                if (bank_transfer[i].from_bankaccount_id != None): 
                    serializer_class.data[i]['from_account_no'] = bank_transfer[i].from_bankaccount_id.account_no
                    serializer_class.data[i]['from_bank_name'] = bank_transfer[i].from_bankaccount_id.bank_id.name
                # if (bank_transfer[i].lab_id != None): 
                #     serializer_class.data[i]['lab_name'] = bank_transfer[i].lab_id.name

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except BankTransferDetail.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
    # Post request for donor in payment

