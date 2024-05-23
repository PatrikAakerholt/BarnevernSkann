import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path

# Funksjon for å laste inn konfigurasjon fra JSON-fil
def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

# Funksjon for å sende e-post med vedlegg
def send_email_with_attachments(config, file_paths):
    msg = MIMEMultipart()
    msg['From'] = config['email_from']
    msg['To'] = config['email_to']
    msg['Subject'] = config['email_subject']

    for file_path in file_paths:
        part = MIMEBase('application', "octet-stream")
        with open(file_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file_path)))
        msg.attach(part)

    with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
        server.starttls()
        server.login(config['smtp_username'], config['smtp_password'])
        server.sendmail(config['email_from'], config['email_to'], msg.as_string())

# Hent filer som er eldre enn en dag
def get_old_pdfs(folder_path):
    old_pdfs = []
    cutoff_time = datetime.now() - timedelta(days=1)
    for file in Path(folder_path).glob('*.pdf'):
        file_mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        if file_mod_time < cutoff_time:
            old_pdfs.append(str(file))
    return old_pdfs

if __name__ == "__main__":
    config_path = 'email_config.json'  # Filsti til konfigurasjonsfilen
    config = load_config(config_path)

    old_pdf_files = get_old_pdfs(config['folder_path'])
    if old_pdf_files:
        send_email_with_attachments(config, old_pdf_files)
        print(f"Sent {len(old_pdf_files)} old PDF files to {config['email_to']}")
    else:
        print("No old PDF files found.")
