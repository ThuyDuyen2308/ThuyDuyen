import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

email_sender = os.getenv('email_sender')
email_password = os.getenv('email_password')
email_receiver = os.getenv('email_receiver')

source_folder = "./"
backup_folder = 'backup/'

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Kết nối đến máy chủ SMTP và gửi email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email_sender, email_password)
        text = msg.as_string()
        server.sendmail(email_sender, email_receiver, text)
        server.quit()

        print(f"Email đang được gởi đến{email_receiver}")

    except Exception as e:
        print(f"Gửi mail thất bại: {e}")

def backup_database():
    try:
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        files_backed_up = []
        for filename in os.listdir(source_folder):
            if filename.endswith(".sql") or filename.endswith(".sqlite3"):
                src_path = os.path.join(source_folder, filename)
                now = datetime.now().strftime("%Y-%m-%d_%H-%M")
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

schedule.every().day.at("00:00").do(backup_database)

print("Đang backup... Đợi đến giờ sao lưu: ")


while True:
    schedule.run_pending()
    time.sleep(60)  
