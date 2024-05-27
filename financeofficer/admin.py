from django.contrib import admin

# Register your models here.

from financeofficer.models import PaymentIn, PaymentOut, BankTransferDetail, ActivityLogFinance, InvoiceAdjustment


# Register your models here.
# class DonorAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'phone', 'email', 'type', 'cnic', 'company_name',
#                     'is_income_tax_payable', 'is_blocked', )
#     search_fields = ('id', 'name', 'phone', 'email', 'type', 'cnic',
#                      'company_name', 'is_income_tax_payable', 'is_blocked')


class PaymentInAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'payment_method', 'handover_to', 'recieved_by', 'refered_no', 'amount', 'paid_at', 
                    'cheque_no', 'cheque_image', 'deposited_at', 'deposit_slip', 'payment_status', 'verified_by', 'is_approved', 'is_cleared', 'cleared_at')
    search_fields = ('id', 'payment_method', 'recieved_by', 'handover_to', 'amount', 'paid_at', 'is_approved', 'payment_status', 'refered_no','cheque_no',
                     'cheque_image', 'created_by', 'deposited_at', 'deposit_slip', 'verified_by', 'is_cleared', 'cleared_at'  )


class PaymentOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'invoice_id', 'payment_method', 'amount', 'payment_at', 
                    'cheque_no', 'deposit_copy', 'is_cleared', 'cleared_at','status', 'comments')
    search_fields = ('id', 'invoice_id', 'payment_method', 'amount', 'payment_at', 
                    'cheque_no', 'created_by', 'deposit_copy', 'is_cleared', 'cleared_at','status', 'comments')

class BankTransferDetailAdmin(admin.ModelAdmin):
    list_display = ('id','transfer_type', 'amount', 'deposit_copy', 'clearence_datetime', 'payment_datetime','status', 'comments')
    search_fields = ('id','transfer_type', 'amount', 'deposit_copy', 'clearence_datetime', 'payment_datetime','status', 'comments')

class InvoiceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('id','test_appointment_id', 'tax','total_adjustment', 'invoive_datetime', 'status', 'comments','created_at', 'comments')
    search_fields = ('id','test_appointment_id', 'tax','total_adjustment', 'invoive_datetime', 'status', 'comments','created_at', 'comments')

class ActivityLogFinanceAdmin(admin.ModelAdmin):
    list_display = ('id','payment_in_id', 'payment_out_id','btd_id','field_name', 'old_value', 'new_value', 'actions','user_id', 'created_at', 'type', 'payment_for')
    search_fields = ('id','payment_in_id', 'payment_out_id','btd_id','field_name', 'old_value', 'new_value', 'actions','user_id', 'created_at', 'type', 'payment_for')

admin.site.register(PaymentIn, PaymentInAdmin)
admin.site.register(PaymentOut, PaymentOutAdmin)
admin.site.register(BankTransferDetail, BankTransferDetailAdmin)
admin.site.register(InvoiceAdjustment, InvoiceAdjustmentAdmin)
admin.site.register(ActivityLogFinance, ActivityLogFinanceAdmin)

