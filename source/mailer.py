import smtplib
import mimetypes
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase


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


def send_email(smtp, sender: str, address: str, filename: str):
    """Sends email with processed file to address

    :param smtp: smtp connection
    :param sender: from address
    :param address: to address
    :param filename: path to output file
    """
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = address
    msg["Subject"] = "Processed files from Converty Bot"
    path_to_file = filename.split("/")
    ftype, encoding = mimetypes.guess_type(filename)
    file_type, subtype = ftype.split("/")
    with open(f'{filename}', mode="rb") as f:
        match file_type:
            case "text":
                file = MIMEText(f.read())
            case "image":
                file = MIMEImage(f.read(), subtype)
            case "audio":
                file = MIMEAudio(f.read(), subtype)
            case "application":
                file = MIMEApplication(f.read(), subtype)
            case _:
                file = MIMEBase(file_type, subtype)
                file.set_payload(f.read())
                encoders.encode_base64(file)
    file.add_header('content-disposition', 'attachment', filename=path_to_file[-1])
    msg.attach(file)
    smtp.sendmail(sender, address, msg.as_string())
