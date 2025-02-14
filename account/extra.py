import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv

SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 587  
EMAIL_ADDRESS = "ali@ghostwager.com"
EMAIL_PASSWORD = "147258369Sub"

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def read_email_list(file_path):
    email_list = []
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email_list.append(row)
    return email_list

def generate_email_body():
    with open("/home/saher/Desktop/steamers.html", "r", encoding="utf-8") as html_file:
        return html_file.read()

if __name__ == "__main__":
    email_list = read_email_list("/home/saher/Desktop/Detail.csv")  

    for recipient in email_list:
        first_name = recipient['FirstName']
        to_email = recipient['Email']
        subject = 'Personalized Email from Python'
        body = generate_email_body() 
        
        body = body.replace("{FirstName}", first_name)
        
        send_email(to_email, subject, body)

