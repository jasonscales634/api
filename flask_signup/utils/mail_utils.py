import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = 'smtp.zoho.com'
SMTP_PORT = 465
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


def send_confirmation_email(email, token):
    confirmation_link = f"https://affise.adcpa.live/confirm/{token}"
    subject = "Email Confirmation"

    # Plain text version
    text = f"Hello!\nTo activate your account, click the link below:\n{confirmation_link}"

    # HTML version with clickable link
    html = f"""\
    <html>
      <body>
        <p>Hello!<br>
           To activate your account, click the link below:<br><br>
           <a href="{confirmation_link}" target="_blank" style="font-size:16px;">Activate your account</a>
           <br><br>
           If the link above doesn't work, copy and paste this into your browser:<br>
           {confirmation_link}
        </p>
      </body>
    </html>
    """

    # Combine both plain and HTML
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_EMAIL
    message["To"] = email

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, message.as_string())
