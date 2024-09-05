from django.contrib import admin
from labowner.models import  Lab,  ActivityLog, LabPayment, Pathologist, OfferedTest, SampleCollector, Staff, Result


# Change settings for showing in Admin
class LabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'is_blocked',)
    search_fields = ('name', 'email', 'phone',
                     'landline', 'address', 'city', )
class Media:
    js = ("https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
            "js/scripts.js",)


class PathologistAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'name', 'email', 'phone', 'landline', 'designation',
                    'is_available_for_consultation', 'is_available_on_whatsapp', 'is_associated_with_pap')
    search_fields = ('id', 'name', 'email', 'phone', 'landline', 'designation',
                     'is_available_for_consultation', 'is_available_on_whatsapp', 'is_associated_with_pap')


class SampleCollectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'name', 'gender', 'cnic', 'phone')
    search_fields = ('id', 'name', 'cnic', 'gender', 'phone')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'analyte', 'units',  'method', 'reagents', 'result',)
    search_fields = ('id', 'lab_id', 'analyte', 'units',  'method', 'reagents', 'result',)

class OfferedTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id','test_type','duration_required', 'duration_type', 'shared_percentage',
                    'sample_type', 'price', 'is_eqa_participation', 'is_home_sampling_available', 'main_lab_tests', 'is_active','status')
    search_fields =  ('id', 'duration_required', 'test_id__name','test_type','duration_type', 'shared_percentage',
                     'price', 'is_eqa_participation','is_home_sampling_available', 'status')


# class QualityCertificateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'offered_test', 'field_name', 'old_value', 'new_value', 'user', 'created_at')
#     search_fields = ('id', 'offered_test', 'field_name', 'old_value', 'new_value', 'user', 'created_at')


class LabPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'invoice_id', 'payment_method', 'address_type', 'address', 'amount', 'paid_at',
                    'cheque_no', 'cheque_image', 'deposited_at', 'deposit_slip', 'is_cleared', 'cleared_at', 'is_settled')
    search_fields = ('id', 'invoice_id', 'payment_method', 'address_type', 'address', 'amount', 'paid_at', 'cheque_no',
                     'cheque_image', 'deposited_at',  'deposit_slip', 'is_cleared', 'cleared_at', 'is_settled')
    
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'scheme_id', 'lab_id', 'analyte', 'units', 'instrument', 'method',
                    'reagents', 'result', 'result_status', 'updated_at')
    search_fields = ('id', ' organization_id', 'scheme_id', 'lab_id', 'analyte', 'units', 'instrument', 'method',
                    'reagents', 'result', 'result_status') 
# class QualityCertificateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'lab_id', 'name', 'type', 'certificate', 'sub_certificate_type')
#     search_fields = ('id', 'name', 'type', 'certificate', 'sub_certificate_type')

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'offered_test_id', 'field_name', 'old_value', 'new_value', 'actions', 'user', 'created_at','old_discount_by_lab',
    'new_discount_by_lab','start_date_by_lab','end_date_by_lab','old_discount_by_labhazir','new_discount_by_labhazir','start_date_by_labhazir',
    'end_date_by_labhazir')
    search_fields = ('id', 'offered_test_id', 'field_name', 'old_value', 'new_value', 'actions', 'user', 'created_at','old_discount_by_lab',
    'new_discount_by_lab','start_date_by_lab','end_date_by_lab','old_discount_by_labhazir','new_discount_by_labhazir','start_date_by_labhazir',
    'end_date_by_labhazir')



# Register your models here

admin.site.register(Lab, LabAdmin)
# admin.site.register(Result, ResultAdmin)
admin.site.register(Pathologist, PathologistAdmin)
admin.site.register(SampleCollector, SampleCollectorAdmin)
admin.site.register(OfferedTest, OfferedTestAdmin)
# admin.site.register(QualityCertificate, QualityCertificateAdmin)
admin.site.register(LabPayment, LabPaymentAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(Result, ResultAdmin)
