# Generated by Django 3.2 on 2024-07-10 11:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labowner', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransferDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_type', models.CharField(choices=[('Deposit', 'Deposit'), ('Interbank Transfer', 'Interbank Transfer'), ('Withdraw', 'Withdraw')], default='Deposit', max_length=50)),
                ('mode', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('Online', 'Online')], max_length=50, null=True)),
                ('deposit_type', models.CharField(blank=True, choices=[('Loan Return', 'Loan Return'), ('Asset Sale', 'Asset Sale'), ('Insurance Claim', 'Insurance Claim'), ('Investments', 'Investments'), ('Others', 'Others')], max_length=50, null=True)),
                ('withdraw_type', models.CharField(blank=True, choices=[('Loan', 'Loan'), ('Tax', 'Tax'), ('Legal and Professional Expenses', 'Legal and Professional Expenses'), ('Investments', 'Investments'), ('Utilities', 'Utilities'), ('Salary and Wages', 'Salary and Wages'), ('Rent', 'Rent'), ('Marketing', 'Marketing'), ('Insurance and Securities', 'Insurance and Securities'), ('Employee Expense', 'Employee Expense'), ('Donation and Charity', 'Donation and Charity'), ('Delivery Expense', 'Delivery Expense'), ('Telecommunication', 'Telecommunication'), ('Travel and Tours', 'Travel and Tours'), ('Others', 'Others')], max_length=50, null=True)),
                ('amount', models.PositiveBigIntegerField(null=True)),
                ('deposit_copy', models.FileField(blank=True, null=True, upload_to='deposit_copy', verbose_name='Deposit copy')),
                ('payment_copy', models.FileField(blank=True, null=True, upload_to='payment_copy', verbose_name='Payment copy')),
                ('cheque_no', models.CharField(blank=True, max_length=255, null=True)),
                ('clearence_datetime', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Clearence At')),
                ('deposit_datetime', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Deposit At')),
                ('payment_datetime', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Payment At')),
                ('status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Deposited', 'Deposited'), ('Cleared', 'Cleared'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved'), ('Pending Clearance', 'Pending Clearance'), ('Bounced', 'Bounced')], default='Created', max_length=50)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Bank Transfer Detail',
            },
        ),
        migrations.CreateModel(
            name='InvoiceAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_appointment_id', models.CharField(max_length=255, null=True)),
                ('tax', models.PositiveBigIntegerField(null=True)),
                ('total_adjustment', models.PositiveBigIntegerField(default=0, null=True)),
                ('invoive_datetime', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Invoice Generated At')),
                ('status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Deposited', 'Deposited'), ('Cleared', 'Cleared'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved'), ('Pending Clearance', 'Pending Clearance'), ('Bounced', 'Bounced')], default='Created', max_length=50)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Invoice Adjustment At')),
                ('price_discount', models.PositiveBigIntegerField(default=0, null=True)),
                ('others', models.PositiveBigIntegerField(default=0, null=True)),
            ],
            options={
                'verbose_name': 'Invoice Adjustment Form',
            },
        ),
        migrations.CreateModel(
            name='PaymentOut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_for', models.CharField(choices=[('Lab', 'Lab'), ('Marketer', 'Marketer'), ('Corporate Lab', 'Corporate Lab')], default='Lab', max_length=50)),
                ('transection_type', models.CharField(choices=[('Donation', 'Donation'), ('Other', 'Other')], default='Other', max_length=50)),
                ('test_appointment_id', models.CharField(max_length=255, null=True)),
                ('invoice_id', models.CharField(max_length=5, null=True, unique=True)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('Card', 'Card')], default='Cheque', max_length=50)),
                ('amount', models.IntegerField(null=True)),
                ('payment_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('cheque_no', models.CharField(blank=True, max_length=255, null=True)),
                ('deposit_copy', models.FileField(blank=True, null=True, upload_to='deposit_copy', verbose_name='Deposit copy')),
                ('is_cleared', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=50, null=True)),
                ('cleared_at', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Cleared At')),
                ('status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Deposited', 'Deposited'), ('Cleared', 'Cleared'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved'), ('Pending Clearance', 'Pending Clearance'), ('Bounced', 'Bounced')], default='Created', max_length=50)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('tax', models.PositiveBigIntegerField(blank=True, null=True)),
                ('lab_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab')),
            ],
            options={
                'verbose_name': 'Payment Out',
            },
        ),
        migrations.CreateModel(
            name='PaymentIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_for', models.CharField(choices=[('Lab', 'Lab'), ('Marketer', 'Marketer'), ('Corporate Lab', 'Corporate Lab')], default='Lab', max_length=50)),
                ('test_appointment_id', models.CharField(max_length=255, null=True)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('Card', 'Card')], default='Cheque', max_length=50)),
                ('amount', models.PositiveBigIntegerField(null=True)),
                ('tax', models.PositiveBigIntegerField(blank=True, null=True)),
                ('cheque_no', models.CharField(blank=True, max_length=255, null=True)),
                ('paid_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('refered_no', models.CharField(blank=True, max_length=255, null=True)),
                ('cheque_image', models.ImageField(blank=True, null=True, upload_to='cheque', verbose_name='Cheque Image')),
                ('deposited_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('deposit_slip', models.FileField(blank=True, null=True, upload_to='deposit_slip', verbose_name='Deposit Slip')),
                ('recieved_by', models.CharField(blank=True, max_length=255, null=True)),
                ('handover_to', models.CharField(blank=True, max_length=255, null=True)),
                ('verified_by', models.CharField(max_length=255, null=True)),
                ('is_approved', models.BooleanField(blank=True, default=0, null=True)),
                ('is_cleared', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=50, null=True)),
                ('cleared_at', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Cleared At')),
                ('payment_status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Deposited', 'Deposited'), ('Cleared', 'Cleared'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved'), ('Pending Clearance', 'Pending Clearance'), ('Bounced', 'Bounced')], default='Created', max_length=50)),
                ('lab_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab')),
            ],
            options={
                'verbose_name': 'Payment In',
            },
        ),
        migrations.CreateModel(
            name='ActivityLogFinance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255, null=True)),
                ('old_value', models.TextField(null=True)),
                ('new_value', models.TextField(null=True)),
                ('actions', models.CharField(choices=[('Updated', 'Updated'), ('Added', 'Added'), ('Deleted', 'Deleted')], default='Updated', max_length=50, verbose_name='Which action is performed?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('Payment In', 'Payment In'), ('Payment Out', 'Payment Out'), ('Invoice Adjustment', 'Invoice Adjustment')], default='Payment In', max_length=50, verbose_name='Form type?')),
                ('payment_for', models.CharField(choices=[('Lab', 'Lab'), ('Marketer', 'Marketer'), ('Deposit', 'Deposit'), ('Interbank Transfer', 'Interbank Transfer'), ('Withdraw', 'Withdraw'), ('Invoice Adjustment', 'Invoice Adjustment')], default='Lab', max_length=50, verbose_name='Payment for?')),
                ('btd_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeofficer.banktransferdetail', verbose_name='BTD id')),
                ('invoice_adjustment_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeofficer.invoiceadjustment', verbose_name='Invoice Adjustment id')),
                ('payment_in_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeofficer.paymentin', verbose_name='Payment in id')),
                ('payment_out_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeofficer.paymentout', verbose_name='Payment out id')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Finance officer')),
            ],
            options={
                'verbose_name': 'Activity Log Finance',
            },
        ),
    ]
