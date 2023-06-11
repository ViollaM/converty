import smtplib
import os
from email.mime.text import MIMEText

def smpt_connect(smtp_config):
    """Makes connection to smtp server

    :param smtp_config: smtp connection config
    """
    try:
        smtp_server = smtplib.SMTP(smtp_config["Host"], smtp_config["Port"])
        smtp_server.ehlo()
        smtp_server.starttls()
        login = smtp_config["Login"]
        file = open(smtp_config["PasswordReadFrom"], mode='r')
        password = file.read()
        file.close()
        try:
            smtp_server.login(login, password)
            return smtp_server
        except Exception as _ex:
            print(f'SMTP login failed: {_ex}', flush=True)
    except Exception as _ex:
        print(f'Connection to the SMTP Server failed: {_ex}', flush=True)
    return None

def send_email(server, sender, address, message):
    msg = MIMEText(message)
    msg["Subject"] = "Your files"
    server.sendmail(sender, address, msg.as_string())