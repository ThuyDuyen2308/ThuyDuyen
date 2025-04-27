import os
import shutil
import smtplib
import schedule
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
email_sender = os.getenv('email_sender')
email_password = os.getenv('email_password')
email_receiver = os.getenv('email_receiver')

source_folder = "./"
backup_folder = "./backup"

def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = email_sender
        message["To"] = email_receiver
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, message.as_string())
        print("Đã gửi email thông báo thành công.")
    except Exception as e:
        print(f"Gửi email thất bại: {e}")

def backup_database():
    try:
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        files_backed_up = []
        for filename in os.listdir(source_folder):
            if filename.endswith(".sql") or filename.endswith(".sqlite3"):
                src_path = os.path.join(source_folder, filename)
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                new_filename = f"{now}_{filename}"
                dest_path = os.path.join(backup_folder, new_filename)
                shutil.copy2(src_path, dest_path)
                files_backed_up.append(new_filename)

        if files_backed_up:
            subject = "Backup thành công"
            body = "Các file sau đã được backup thành công:\n" + "\n".join(files_backed_up)
        else:
            subject = "Backup hoàn tất - Không có file cần backup"
            body = "Không tìm thấy file .sql hoặc .sqlite3 nào để backup."

        send_email(subject, body)
    except Exception as e:
        subject = "Backup thất bại"
        body = f"Đã xảy ra lỗi trong quá trình backup:\n{e}"
        send_email(subject, body)


schedule.every().day.at("13:30").do(backup_database)

print("Chương trình backup đã khởi động... Đang chờ đến giờ backup...")

while True:
    schedule.run_pending()
    time.sleep(60)
