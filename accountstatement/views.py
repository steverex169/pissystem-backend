from curses import window
import datetime
import json
from multiprocessing import context
from telnetlib import DO
import requests
import calendar
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework import status
from accountstatement.models import AccountStatement,  B2BAccountStatement, BankAccountStatement, DonorAccountStatement, CorporateLabStatement
from accountstatement.serializers import AccountStatementSerializer, CorporateLabStatementSerializer, B2BAccountStatementSerializer, BankAccountStatementSerializer, DonorAccountStatementSerializer
from account.models import UserAccount
from financeofficer.models import PaymentIn
from financeofficer.serializers import PaymentInSerializer
from labowner.models import Lab, LabCorporate
from django.db.models import Count, Q
from django.db.models import Window, Sum, F, RowRange
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.utils import timezone
# from weasyprint import HTML
from helpers.mail import mail_send
from django.utils import timezone

class AccountStatementsPdfView(APIView):
    def get(self, request):
        # Get the account statements data for the current month
        pk_tz = pytz.timezone('Asia/Karachi')
        today = timezone.now().astimezone(pk_tz)
        print("today",today)
        start_date = timezone.datetime(today.year, today.month, 1)
        print("start_date",start_date)
        end_date = timezone.datetime(today.year, today.month, 1) + timezone.timedelta(days=30)
        print("end_date",end_date)
        labs=Lab.objects.all()
        print(labs)
        for lab in labs:
            statements = AccountStatement.objects.filter(lab_id=lab.id, generated_at__gte=start_date, generated_at__lt=end_date)
            print(statements)
            print(lab.current_amount)
            # Render the account statements as HTML using a Django template
            context = {'statements': statements, 'current_amount': lab.current_amount, 'month': calendar.month_name[today.month], 'year': today.year}
            html_content = render_to_string('account_statements.html', context)

            # Generate the PDF using WeasyPrint
            # pdf_file = HTML(string=html_content).write_pdf()
            subject, from_email, to = 'Account Statement', settings.EMAIL_HOST_USER, lab.email
            # Send the PDF file as an attachment in an email to the user
            data = {
                        'lab_name': lab.name,
                        'month': calendar.month_name[today.month],
                    }
            # mail_send(subject, 'account-statement-mail.html', from_email, to, data, pdf_file)

        # Return a response indicating that the PDF was generated and sent
        return Response({"status": status.HTTP_200_OK, "message": "Account statements PDF generated and sent" })
    
# Create your views here.
# API for sample test list
class AccountStatementsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list


class DonorAccountStatementsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the cart
    # def get(self, request, *args, **kwargs):
    #     try:
    #         donor = Donor.objects.get(account_id=kwargs.get('id'))
    #         try:
    #             donor_statement_list = DonorAccountStatement.objects.filter(
    #                 donor_id=donor.id)
    #             serializer_class = DonorAccountStatementSerializer(
    #                 donor_statement_list, many=True)

    #             for i in range(0, len(donor_statement_list)):
    #                 serializer_class.data[i]['payment_in_id'] = donor_statement_list[i].donor_id
    #                 # serializer_class.data[i]['test_appointment_id'] = donor_statement_list[i].test_appointment_id

    #                 # Checking for payment details of a particular appointment
    #                 # try:
    #                 #     paymentin = PaymentIn.objects.get(
    #                 #         donor_id=donor_statement_list[i].id)
    #                 #     serializer_class.data[i]['dues'] = paymentin.amount
    #                 #     serializer_class.data[i]['payment_method'] = paymentin.payment_method
    #                 #     serializer_class.data[i]['payment_status'] = paymentin.status
    #                 # except PaymentIn.DoesNotExist:
    #                 #     pass
    #             return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

    #         except DonorAccountStatement.DoesNotExist:
    #             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})

    #     except Donor.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No such donor account exists."})

class B2BAccountStatementsView(APIView):
    permission_classes = (AllowAny,)

class CorporateLabAccountStatementsView(APIView):
    permission_classes = (AllowAny,)

class LabAccountStatementListsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
            try:
                donor_statement_list = AccountStatement.objects.all()
                serializer_class = AccountStatementSerializer(
                    donor_statement_list, many=True)

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except AccountStatement.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
class DonorAccountStatementListsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
            try:
                donor_statement_list = DonorAccountStatement.objects.all()
                serializer_class = DonorAccountStatementSerializer(
                    donor_statement_list, many=True)

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except DonorAccountStatement.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
class CorporateLabAccountStatementsListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            donor_statement_list = CorporateLabStatement.objects.all()
            serializer_class = CorporateLabStatementSerializer(
                donor_statement_list, many=True)
            
            for i in range(0, len(donor_statement_list)):
                serializer_class.data[i]['lab_name'] = donor_statement_list[i].lab_id.name
                serializer_class.data[i]['lab_phone'] = donor_statement_list[i].lab_id.landline
                serializer_class.data[i]['lab_city'] = donor_statement_list[i].lab_id.city
                serializer_class.data[i]['lab_address'] = donor_statement_list[i].lab_id.address
                serializer_class.data[i]['corporate_name'] = donor_statement_list[i].corporate_id.name
                serializer_class.data[i]['patient_name'] = donor_statement_list[i].test_appointment_id.patient_name
                serializer_class.data[i]['is_home_sampling_availed'] = donor_statement_list[i].test_appointment_id.is_home_sampling_availed
                serializer_class.data[i]['booked_at'] = donor_statement_list[i].test_appointment_id.booked_at
                serializer_class.data[i]['appointment_status'] = donor_statement_list[i].test_appointment_id.status

            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

        except B2BAccountStatement.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
class B2bAccountStatementListsView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the cart
    def get(self, request, *args, **kwargs):
            try:
                donor_statement_list = B2BAccountStatement.objects.all()
                serializer_class = B2BAccountStatementSerializer(
                    donor_statement_list, many=True)

                return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})

            except B2BAccountStatement.DoesNotExist:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No Record Exist."})
