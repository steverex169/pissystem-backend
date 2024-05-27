from django.db import models

# Create your models here.
DISTRICTS = (('Abbottabad', 'Abbottabad'),('Attock', 'Attock'),('Awaran', 'Awaran'),
  ('Badin', 'Badin'),('Bahawalnagar', 'Bahawalnagar'),('Bahawalpur', 'Bahawalpur'),('Bajur', 'Bajur'),
  ('Bannu', 'Bannu'),('Barkhan', 'Barkhan'),('Batagram', 'Batagram'),('Bhakkar', 'Bhakkar'),
  ('Bunair', 'Bunair'),('Chagai', 'Chagai'),('Chakwal', 'Chakwal'),('Chaman', 'Chaman'),
  ('Charsada', 'Charsada'),('Chiniot', 'Chiniot'),('Chitral', 'Chitral'),('Dadu', 'Dadu'),
  ('Dera Bugti', 'Dera Bugti'),('Dera Ghazi Khan', 'Dera Ghazi Khan'),('Dera Ismail Khan', 'Dera Ismail Khan'),
   ('Duki', 'Duki'),('Faisalabad', 'Faisalabad'),('Ghotki', 'Ghotki'),
  ('Gujar Khan', 'Gujar Khan'),
  ('Jhang', 'Jhang'),('Jhal Magsi', 'Jhal Magsi'),('Jamshoro', 'Jamshoro'),('Jaffarabad', 'Jaffarabad'),('Jacobabad', 'Jacobabad'),
  ('Islamabad', 'Islamabad'),('Hyderabad', 'Hyderabad'),('Hub', 'Hub'),('Harnai', 'Harnai'),('Haripur', 'Haripur'),
    ('Hangu', 'Hangu'),('Hafizabad', 'Hafizabad'),('Gwadar', 'Gwadar'),('Gujrat', 'Gujrat'),('Gujranwala', 'Gujranwala'),
    ('Kurram', 'Kurram'),
    ('Kolai Palas', 'Kolai Palas'),
    ('Korangi', 'Korangi'),
    ('Kohlu', 'Kohlu'),
    ('Kohistan', 'Kohistan'),
    ('Kohat', 'Kohat'),
    ('Khyber', 'Khyber'),
    ('Khuzdar', 'Khuzdar'),
    ('Khushab', 'Khushab'),
    ('Kharan', 'Kharan'),
    ('Khanewal', 'Khanewal'),
    ('Khairpur', 'Khairpur'),
    ('Kech/Turbat', 'Kech/Turbat'),
    ('Kasur', 'Kasur'),
    ('Kashmore', 'Kashmore'),
    ('Karak', 'Karak'),
    ('Karachi', 'Karachi'),
    ('Kalat', 'Kalat'),
    ('Kachhi/Bolan', 'Kachhi/Bolan'),
    ('Jhelum', 'Jhelum'),
    ('Rawalpindi', 'Rawalpindi'),
    ('Rajanpur', 'Rajanpur'),('Rahim Yar Khan', 'Rahim Yar Khan'),('Quetta', 'Quetta'),('Qilla Saifullah', 'Qilla Saifullah'), ('Qilla Abdullah', 'Qilla Abdullah'),
    ('Pishin', 'Pishin'),('Peshawar', 'Peshawar'),('Panjgoor', 'Panjgoor'),('Pakpattan', 'Pakpattan'),('Orakzai', 'Orakzai'),('Okara', 'Okara'),('Nushki', 'Nushki'),('Nowshero Feroze', 'Nowshero Feroze'),('Nowshera', 'Nowshera'),('Nasirabad/Tamboo', 'Nasirabad/Tamboo'),('Narowal', 'Narowal'),('Nankana Sahib', 'Nankana Sahib'),
    ('Muzaffargarh', 'Muzaffargarh'),('Musa Khel', 'Musa Khel'),('Multan', 'Multan'),('Mohmand', 'Mohmand'),('Mirpur Khas', 'Mirpur Khas'),('Mianwali', 'Mianwali'),('Matiari', 'Matiari'),('Mastung', 'Mastung'),('Mardan', 'Mardan'),
    ('Mansehra', 'Mansehra'),('Malir', 'Malir'),('Mandi Bahauddin', 'Mandi Bahauddin'),('Malakand', 'Malakand'),('Lower Dir', 'Lower Dir'),('Loralai', 'Loralai'),('Lodhran', 'Lodhran'),('Layyah', 'Layyah'),('Lasbela', 'Lasbela'),('Larkana', 'Larkana'),('Lakki Marwat', 'Lakki Marwat'),('Lahore', 'Lahore'),
    ('Swat', 'Swat'),('Nawabshah', 'Nawabshah'),
    ('Swabi', 'Swabi'),
    ('Sukkur', 'Sukkur'),
    ('Sujawal', 'Sujawal'),
    ('Sohbatpur', 'Sohbatpur'),('Sibbi', 'Sibbi'),
    ('Sialkot', 'Sialkot'),('Shikarpur', 'Shikarpur'),('Sherani', 'Sherani'),('Sheikhupura', 'Sheikhupura'),('Shangla', 'Shangla'),('Shaheed Sikandar Abad', 'Shaheed Sikandar Abad'),('Shaheed Banazir Abad', 'Shaheed Banazir Abad'),('Shahdadkot', 'Shahdadkot'),('Sargodha', 'Sargodha'),('Sanghar', 'Sanghar'),('Sahiwal', 'Sahiwal'),
    ('Tando Allah Yar', 'Tando Allah Yar'),
    ('Tando Muhammad Khan', 'Tando Muhammad Khan'),('Tank', 'Tank'),('Tharparkar', 'Tharparkar'),
    ('Toba Tek Singh', 'Toba Tek Singh'),('Tor Garh', 'Tor Garh'),('Umer Kot', 'Umer Kot'),
    ('Upper Dir', 'Upper Dir'),('Vehari', 'Vehari'),('Washuk', 'Washuk'),
    ('Waziristan', 'Waziristan'),('Zhob', 'Zhob'),('Ziarat', 'Ziarat'),
    ('Muzaffarabad', 'Muzaffarabad'), ('Kotli', 'Kotli'), ('Lakki Marwat', 'Lakki Marwat'), ('Skardu', 'Skardu'), ('Taunsa', 'Taunsa')
)
OFFICE = (
    ('Central Office', 'Central Office'),
    ('North Office', 'North Office'),
    ('South Office', 'South Office'),

)
PROVINCE= (
    ('Punjab', 'Punjab'),
    ('Sindh', 'Sindh'),
    ('Khyber Pakhtunkhuwa', 'Khyber Pakhtunkhuwa'),
    ('Balochistan', 'Balochistan'),
    ('Azad Kashmir', 'Azad Kashmir'),
    ('Gilgit Baltistan', 'Gilgit Baltistan'),

)

class Territories(models.Model):
    province = models.CharField(max_length=255, null=True,
                            blank=False,choices=PROVINCE, default='Punjab')
    city = models.CharField(max_length=255, null=True,
                            blank=False, unique=True)
    district = models.CharField(max_length=255, choices= DISTRICTS,
                             default= 'Rawalpindi')
    office = models.CharField(

        max_length=50, choices=OFFICE, default='Central Office')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Territories'
