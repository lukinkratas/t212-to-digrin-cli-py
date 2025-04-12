import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup


def get_plain_text(html_text: str) -> str:
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.text


def encode_attachment(file_or_path: str | bytes, filename: str = '') -> bytes:
    if isinstance(file_or_path, str):
        with open(file_or_path, 'rb') as attachment_file:
            attachment = attachment_file.read()
        if not filename:
            filename = os.path.basename(file_or_path)

    else:
        attachment = file_or_path

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header
    if not filename:
        filename = 'attachment'
    part.add_header('Content-Disposition', f'attachment; filename={filename}')

    return part


def send_email(
    sender: str,
    password: str,
    receiver: str,
    host: str,
    port: int = 587,
    subject: str = '',
    body: str = '',
    attachment: str | bytes | None = None,
    filename: str = '',
) -> None:
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receiver

    message.attach(MIMEText(body, 'html'))
    message.attach(MIMEText(get_plain_text(body), 'plain'))

    if attachment:
        message.attach(encode_attachment(attachment, filename))

    context = ssl.create_default_context()

    server = smtplib.SMTP(host, port)
    server.ehlo()  # Can be omitted
    server.starttls(context=context)  # Secure the connection
    server.ehlo()  # Can be omitted
    server.login(sender, password)
    server.sendmail(sender, receiver, message.as_string())
    server.quit()


class TLSClient(object):
    def __init__(
        self, username: str, password: str, host: str, port: int = 587
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def send_email(
        self,
        receiver: str,
        subject: str = '',
        body: str = '',
        attachment: str | bytes | None = None,
        filename: str = '',
    ) -> None:
        return send_email(
            sender=self.username,
            password=self.password,
            receiver=receiver,
            host=self.host,
            port=self.port,
            subject=subject,
            body=body,
            attachment=attachment,
            filename=filename,
        )

def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(override=True)

    seznam_client = TLSClient(
        username=os.getenv('EMAIL'),
        password=os.getenv('PASSWORD'),
        host='smtp.seznam.cz',
    )
    
    seznam_client.send_email(
        receiver=os.getenv('EMAIL'),
        subject='Test',
        body='<html><body><p><br>This is a test message.<br></p></body></html>',
        attachment=b'xxx',
        filename='xxx.txt'
    )

if __name__ == '__main__':
    main()
