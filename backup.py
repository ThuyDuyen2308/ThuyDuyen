import os
import shutil
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy thông tin mail từ environment
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

# Đường dẫn thư mục chứa database và thư mục backup
SOURCE_FOLDER = "./"  # thư mục hiện tại
BACKUP_FOLDER = "./backup"

# Hàm gửi email
def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["To"] = EMAIL_RECEIVER
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Hàm backup database
def backup_database():
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        files_backed_up = []
        for filename in os.listdir(SOURCE_FOLDER):
            if filename.endswith(".sql") or filename.endswith(".sqlite3"):
                src_path = os.path.join(SOURCE_FOLDER, filename)
                dest_path = os.path.join(BACKUP_FOLDER, filename)
                shutil.copy2(src_path, dest_path)
                files_backed_up.append(filename)

        if files_backed_up:
            subject = "Backup Successful"
            body = f"The following files were backed up successfully:\n" + "\n".join(files_backed_up)
        else:
            subject = "Backup Completed - No Files Found"
            body = "No .sql or .sqlite3 files found for backup."

        send_email(subject, body)
    except Exception as e:
        subject = "Backup Failed"
        body = f"An error occurred during backup:\n{e}"
        send_email(subject, body)

# Lên lịch backup lúc 00:00 AM mỗi ngày
schedule.every().day.at("00:00").do(backup_database)

print("Backup service started... Waiting for schedule...")

while True:
    schedule.run_pending()
    time.sleep(60)  # kiểm tra mỗi phút
