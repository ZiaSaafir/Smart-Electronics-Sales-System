import os
import datetime
import subprocess
import zipfile
import time
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GDriveBackup:
    def __init__(self):
        self.creds = None
        self.service = None
        self.backup_folder_id = None
        
    def authenticate(self):
        """Authenticate with Google Drive"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
        print("✅ Authenticated with Google Drive")
        return True
    
    def get_or_create_backup_folder(self):
        """Get or create backup folder in Google Drive"""
        results = self.service.files().list(
            q="name='Farman_POS_Backups' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            self.backup_folder_id = items[0]['id']
            print(f"✅ Found existing backup folder")
        else:
            file_metadata = {
                'name': 'Farman_POS_Backups',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            self.backup_folder_id = file.get('id')
            print(f"✅ Created new backup folder")
        
        return self.backup_folder_id
    
    def backup_database(self):
        """Create MySQL database backup"""
        db_name = 'farman_pos_db'
        db_user = 'root'
        db_password = '12345'  # CHANGE THIS TO YOUR MYSQL PASSWORD
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/farman_backup_{timestamp}.sql'
        zip_file = f'backups/farman_backup_{timestamp}.zip'
        
        os.makedirs('backups', exist_ok=True)
        
        cmd = f'mysqldump -u {db_user} -p{db_password} {db_name} > {backup_file}'
        subprocess.run(cmd, shell=True, check=True)
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_file, os.path.basename(backup_file))
        
        os.remove(backup_file)
        print(f"✅ Backup created: {zip_file}")
        return zip_file
    
    def upload_to_drive(self, file_path):
        """Upload backup to Google Drive"""
        file_name = os.path.basename(file_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [self.backup_folder_id]
        }
        
        media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Uploaded to Google Drive: {file_name}")
        return True
    
    def cleanup_old_backups(self, days=30):
        """Delete backups older than 30 days"""
        backup_dir = 'backups'
        if os.path.exists(backup_dir):
            now = time.time()
            for file in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, file)
                if os.path.getctime(file_path) < now - days * 86400:
                    os.remove(file_path)
                    print(f"🗑️ Deleted old backup: {file}")
    
    def run(self):
        print("=" * 50)
        print("Starting Google Drive Backup...")
        print("=" * 50)
        
        print("1. Authenticating...")
        self.authenticate()
        
        print("2. Setting up folder...")
        self.get_or_create_backup_folder()
        
        print("3. Creating backup...")
        backup_file = self.backup_database()
        
        print("4. Uploading to Drive...")
        self.upload_to_drive(backup_file)
        
        print("5. Cleaning old backups...")
        self.cleanup_old_backups()
        
        print("=" * 50)
        print("✅ Backup Complete!")
        print("=" * 50)

if __name__ == "__main__":
    backup = GDriveBackup()
    backup.run()
