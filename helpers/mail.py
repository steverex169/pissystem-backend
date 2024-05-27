from django.template.loader import get_template
from django.core.mail import EmailMessage
# from django.template.loader import get_template
# from django.core.mail import EmailMessage


def send_mail(subject, path_to_template, from_mail, to_mail, data):
    message = get_template(path_to_template).render(data)

    email = EmailMessage(
        subject,
        message,
        from_mail,
        [to_mail],
    )
    email.content_subtype = "html"  # Main content is now text/html
    email.send()

def mail_send(subject, path_to_template, from_mail, to_mail, data, pdf_file):
    message = get_template(path_to_template).render(data)

    email = EmailMessage(
        subject,
        message,
        from_mail,
        [to_mail],
    )

    # Attach the PDF to the email
    pdf_filename = "pdf_file"
    # pdf_content = pdf_file.getvalue()
    email.attach('account_statements.pdf', pdf_file, 'application/pdf')

    # email.attach(pdf_file, pdf_content, "application/pdf")

    email.content_subtype = "html"  # Main content is now text/html
    email.send()