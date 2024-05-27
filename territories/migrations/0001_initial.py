# Generated by Django 3.2 on 2023-10-09 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Territories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(choices=[('Punjab', 'Punjab'), ('Sindh', 'Sindh'), ('Khyber Pakhtunkhuwa', 'Khyber Pakhtunkhuwa'), ('Balochistan', 'Balochistan'), ('Azad Kashmir', 'Azad Kashmir'), ('Gilgit Baltistan', 'Gilgit Baltistan')], default='Punjab', max_length=255, null=True)),
                ('city', models.CharField(max_length=255, null=True, unique=True)),
                ('district', models.CharField(choices=[('Abbottabad', 'Abbottabad'), ('Attock', 'Attock'), ('Awaran', 'Awaran'), ('Badin', 'Badin'), ('Bahawalnagar', 'Bahawalnagar'), ('Bahawalpur', 'Bahawalpur'), ('Bajur', 'Bajur'), ('Bannu', 'Bannu'), ('Barkhan', 'Barkhan'), ('Batagram', 'Batagram'), ('Bhakkar', 'Bhakkar'), ('Bunair', 'Bunair'), ('Chagai', 'Chagai'), ('Chakwal', 'Chakwal'), ('Chaman', 'Chaman'), ('Charsada', 'Charsada'), ('Chiniot', 'Chiniot'), ('Chitral', 'Chitral'), ('Dadu', 'Dadu'), ('Dera Bugti', 'Dera Bugti'), ('Dera Ghazi Khan', 'Dera Ghazi Khan'), ('Dera Ismail Khan', 'Dera Ismail Khan'), ('Duki', 'Duki'), ('Faisalabad', 'Faisalabad'), ('Ghotki', 'Ghotki'), ('Gujar Khan', 'Gujar Khan'), ('Jhang', 'Jhang'), ('Jhal Magsi', 'Jhal Magsi'), ('Jamshoro', 'Jamshoro'), ('Jaffarabad', 'Jaffarabad'), ('Jacobabad', 'Jacobabad'), ('Islamabad', 'Islamabad'), ('Hyderabad', 'Hyderabad'), ('Hub', 'Hub'), ('Harnai', 'Harnai'), ('Haripur', 'Haripur'), ('Hangu', 'Hangu'), ('Hafizabad', 'Hafizabad'), ('Gwadar', 'Gwadar'), ('Gujrat', 'Gujrat'), ('Gujranwala', 'Gujranwala'), ('Kurram', 'Kurram'), ('Kolai Palas', 'Kolai Palas'), ('Korangi', 'Korangi'), ('Kohlu', 'Kohlu'), ('Kohistan', 'Kohistan'), ('Kohat', 'Kohat'), ('Khyber', 'Khyber'), ('Khuzdar', 'Khuzdar'), ('Khushab', 'Khushab'), ('Kharan', 'Kharan'), ('Khanewal', 'Khanewal'), ('Khairpur', 'Khairpur'), ('Kech/Turbat', 'Kech/Turbat'), ('Kasur', 'Kasur'), ('Kashmore', 'Kashmore'), ('Karak', 'Karak'), ('Karachi', 'Karachi'), ('Kalat', 'Kalat'), ('Kachhi/Bolan', 'Kachhi/Bolan'), ('Jhelum', 'Jhelum'), ('Rawalpindi', 'Rawalpindi'), ('Rajanpur', 'Rajanpur'), ('Rahim Yar Khan', 'Rahim Yar Khan'), ('Quetta', 'Quetta'), ('Qilla Saifullah', 'Qilla Saifullah'), ('Qilla Abdullah', 'Qilla Abdullah'), ('Pishin', 'Pishin'), ('Peshawar', 'Peshawar'), ('Panjgoor', 'Panjgoor'), ('Pakpattan', 'Pakpattan'), ('Orakzai', 'Orakzai'), ('Okara', 'Okara'), ('Nushki', 'Nushki'), ('Nowshero Feroze', 'Nowshero Feroze'), ('Nowshera', 'Nowshera'), ('Nasirabad/Tamboo', 'Nasirabad/Tamboo'), ('Narowal', 'Narowal'), ('Nankana Sahib', 'Nankana Sahib'), ('Muzaffargarh', 'Muzaffargarh'), ('Musa Khel', 'Musa Khel'), ('Multan', 'Multan'), ('Mohmand', 'Mohmand'), ('Mirpur Khas', 'Mirpur Khas'), ('Mianwali', 'Mianwali'), ('Matiari', 'Matiari'), ('Mastung', 'Mastung'), ('Mardan', 'Mardan'), ('Mansehra', 'Mansehra'), ('Malir', 'Malir'), ('Mandi Bahauddin', 'Mandi Bahauddin'), ('Malakand', 'Malakand'), ('Lower Dir', 'Lower Dir'), ('Loralai', 'Loralai'), ('Lodhran', 'Lodhran'), ('Layyah', 'Layyah'), ('Lasbela', 'Lasbela'), ('Larkana', 'Larkana'), ('Lakki Marwat', 'Lakki Marwat'), ('Lahore', 'Lahore'), ('Swat', 'Swat'), ('Nawabshah', 'Nawabshah'), ('Swabi', 'Swabi'), ('Sukkur', 'Sukkur'), ('Sujawal', 'Sujawal'), ('Sohbatpur', 'Sohbatpur'), ('Sibbi', 'Sibbi'), ('Sialkot', 'Sialkot'), ('Shikarpur', 'Shikarpur'), ('Sherani', 'Sherani'), ('Sheikhupura', 'Sheikhupura'), ('Shangla', 'Shangla'), ('Shaheed Sikandar Abad', 'Shaheed Sikandar Abad'), ('Shaheed Banazir Abad', 'Shaheed Banazir Abad'), ('Shahdadkot', 'Shahdadkot'), ('Sargodha', 'Sargodha'), ('Sanghar', 'Sanghar'), ('Sahiwal', 'Sahiwal'), ('Tando Allah Yar', 'Tando Allah Yar'), ('Tando Muhammad Khan', 'Tando Muhammad Khan'), ('Tank', 'Tank'), ('Tharparkar', 'Tharparkar'), ('Toba Tek Singh', 'Toba Tek Singh'), ('Tor Garh', 'Tor Garh'), ('Umer Kot', 'Umer Kot'), ('Upper Dir', 'Upper Dir'), ('Vehari', 'Vehari'), ('Washuk', 'Washuk'), ('Waziristan', 'Waziristan'), ('Zhob', 'Zhob'), ('Ziarat', 'Ziarat'), ('Muzaffarabad', 'Muzaffarabad'), ('Kotli', 'Kotli'), ('Lakki Marwat', 'Lakki Marwat'), ('Skardu', 'Skardu'), ('Taunsa', 'Taunsa')], default='Rawalpindi', max_length=255)),
                ('office', models.CharField(choices=[('Central Office', 'Central Office'), ('North Office', 'North Office'), ('South Office', 'South Office')], default='Central Office', max_length=50)),
            ],
            options={
                'verbose_name': 'Territories',
            },
        ),
    ]
