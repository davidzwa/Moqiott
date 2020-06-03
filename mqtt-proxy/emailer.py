import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_secrets import *

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP(host, port) as server:
    server.starttls(context=context)
    # server.helo()  # Can be omitted
    server.login(email_address, password)
    # TODO: Send email here

    msg = MIMEMultipart()
    msg.add_header('From', email_address)
    msg.add_header("To", to_addresses)
    msg.add_header("Subject", "Test")
    text = '''
    Hello Sven,

    This is David's Raspberry Pi sending you a message using Mijndomein and admin@ds4.nl as email address.
    What does this mean? The ds4 site can actually send emails to groups or mail lists.
    Now the question is: <b>how do we receive email on the ds4 server</b>.

    This mail was sent to:
    {}

    Cheers!
    David's Raspberry Pi 3
    '''.format(to_addresses)
    msg.attach(MIMEText(text, 'plain'))

    try:
        print(text)
        # senderrs = server.sendmail(email_address, to_addresses,
        #    msg.as_string())
        # print(senderrs)
    except Exception as e:
        print(e)
    # server.quit()
