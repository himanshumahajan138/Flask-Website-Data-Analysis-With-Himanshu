import smtplib,ssl
from email.message import EmailMessage
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def is_valid(email_addr="xyz@xyz.com"):
    response = requests.get(f"{os.environ.get('ABSTRACT_API')}+{email_addr}")
    if response.status_code == 200:
        x= response.content.decode()
        y = x.split(",")[-1].split(":")[-1].split("}}")[0].split("\"")[1]
        z = x.split(",")[2:3][0].split(":")[1].split("\"")[1]
        li = [y,z]
        if li[0] == 'TRUE' and li[1] == 'DELIVERABLE':
            return True
        else: return False
    else: return False

def send_email(name="xyz",email="xyz@gmail.com",subject="xyz",message="xyz",other=False,reciever='phenominal138@outlook.com',count=0):
    try:
        email_sender = 'data.analysis.138@gmail.com'
        email_password = os.environ.get("EMAIL_PASSWORD")
        email_receiver = reciever
        msg = f"From : {email}\nName : {name}\nSubject : {subject}\nMessage : {message}\n"
        if other:
            email_receiver = email
            subject = "Thank you for reaching out to Data Analysis  With Himanshu"
            msg = f"Dear {name},\n\n"
            with open(r"static\forms\email.txt","r") as file:
                for line in file.readlines():
                    msg+=line
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(msg)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, em.as_string())
        if count==0:
            send_email(name=name,email=email,subject=subject,message=message,count=1)
        return True
    except Exception as e:
        return e

