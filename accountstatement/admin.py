from django.contrib import admin

from accountstatement.models import  AccountStatement,  BankAccountStatement


# Register your models here.
class AccountStatementAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'lab_payment_id', 'payment_in_id','statement', 'sample_collector_amount', 'status', 'lab_share', 'received_payment_lab', 'received_payment_labHazir', 'dues_before_discount', 'order_id', 'ordered_at', 'dues', 'payment_method',
                    'paid_at', 'labhazir_share', 'payable', 'Receivable',
                    'lab_total_discount_percentage', 'discounted_by_lab', 'sample_collector_amount', 'discounted_by_labhazir', 'referral_remaining_fee_margin', 'total_dues_before_discount',
                    'lab_remaining_fee_margin', 'is_settled', 'transaction_type', 'is_transaction_completed', 'generated_at')

    search_fields = ('id', 'order_id', 'ordered_at', 'payment_in_id','status', 'statement', 'lab_share', 'received_payment_lab', 'paid_at', 'labhazir_share',  'total_dues_before_discount', 'received_payment_labHazir', 'dues_before_discount', 'payable', 'Receivable', 'dues', 'payment_method',
                     'lab_total_discount_percentage', 'discounted_by_lab', 'discounted_by_labhazir',
                     'referral_remaining_fee_margin', 'is_settled', 'lab_remaining_fee_margin', 'transaction_type', 'is_transaction_completed', 'generated_at')





class BankAccountStatementAdmin(admin.ModelAdmin):
    list_display = ('id', 'b2b_id', 'lab_id', 'status', 'Credit', 'Debit')
    search_fields = ('id', 'b2b_id', 'lab_id', 'Credit', 'Debit',)
    

 
admin.site.register(AccountStatement, AccountStatementAdmin)


admin.site.register(BankAccountStatement, BankAccountStatementAdmin)



