# import os

# DATA_FOLDER = "data"

# def check_files():
#     print("\nChecking if CSV files exist...")
#     files = os.listdir(DATA_FOLDER)

#     if not files:
#         print("❌ No CSV files found. Exiting.")
#         return False
    
#     print(f"✅ Found {len(files)} files: {', '.join(files)}")
#     return True

# def upload_to_db():
#     print("\nUploading to database...")
#     # Your database logic here (e.g., using SQLAlchemy or psycopg2)
#     print("✅ Data successfully uploaded to database.")

# if __name__ == "__main__":
#     if check_files():
#         upload_to_db()
#     else:
#         print("❌ Skipping database upload.")




import os
import shutil
import datetime

DATA_FOLDER = "data"
BACKUP_FOLDER = "backup"

def create_backup():
    """Move existing CSV files to a timestamped backup folder."""
    files = os.listdir(DATA_FOLDER)
    
    if not files:
        print("✅ No previous data found. Proceeding with new automation.")
        return

    # Create backup folder with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(BACKUP_FOLDER, timestamp)

    os.makedirs(backup_path, exist_ok=True)

    # Move files to backup folder
    for file in files:
        src = os.path.join(DATA_FOLDER, file)
        dest = os.path.join(backup_path, file)
        shutil.move(src, dest)
    
    print(f"🔄 Moved {len(files)} files to backup: {backup_path}")

def check_files():
    """Check if new CSV files exist in the data folder."""
    print("\nChecking if CSV files exist...")
    files = os.listdir(DATA_FOLDER)

    if not files:
        print("❌ No new CSV files found. Exiting.")
        return False
    
    print(f"✅ Found {len(files)} new files: {', '.join(files)}")
    return True

def upload_to_db():
    """Simulated database upload."""
    print("\nUploading to database...")
    # Your database logic here
    print("✅ Data successfully uploaded to database.")

if __name__ == "__main__":
    create_backup()  # Backup old files before automation starts
    if check_files():
        upload_to_db()
    else:
        print("❌ Skipping database upload.")
