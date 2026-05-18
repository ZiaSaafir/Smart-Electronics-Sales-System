import os
import datetime
import subprocess
import smtplib
import zipfile
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

def create_backup():
    """Create database backup"""
    db_name = 'farman_pos_db'
    db_user = 'root'
    db_password = '12345'  # CHANGE THIS TO YOUR MYSQL PASSWORD
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/backup_{timestamp}.sql'
    zip_file = f'backups/backup_{timestamp}.zip'
    
    os.makedirs('backups', exist_ok=True)
    
    # Create backup
    cmd = f'mysqldump -u {db_user} -p{db_password} {db_name} > {backup_file}'
    subprocess.run(cmd, shell=True, check=True)
    
    # Compress
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(backup_file, os.path.basename(backup_file))
    
    os.remove(backup_file)
    return zip_file

def send_email_backup(zip_file):
    """Send backup via email"""
    
    # Email settings (use Gmail)
    sender_email = "ziagit11@gmail.com"  # Your email
    sender_password = "your-app-password"  # Gmail App Password (see instructions below)
    receiver_email = "ziagit11@gmail.com"  # Where to send backup
    
    # Create email
    subject = f"POS Backup - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    body = "Attached is your POS database backup."
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach file
    with open(zip_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(zip_file)}')
        msg.attach(part)
    
    # Send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")
        return False

def cleanup_old_backups(days=30):
    """Delete backups older than 30 days"""
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        now = time.time()
        for file in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file)
            if os.path.getctime(file_path) < now - days * 86400:
                os.remove(file_path)
                print(f"Deleted old: {file}")

if __name__ == "__main__":
    print("Creating backup...")
    zip_file = create_backup()
    print(f"Backup created: {zip_file}")
    
    print("Sending email...")
    send_email_backup(zip_file)
    
    cleanup_old_backups()
    print("Done!")
