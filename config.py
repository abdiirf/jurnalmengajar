from pymongo import MongoClient

# Fungsi untuk mendapatkan koneksi database
def get_database_connection(db_url):
    client = MongoClient(db_url)
    db = client["jurnalmengajar"] # Nama Database
    guru_collection = db["guru"]  # Collection periode
    return client, db, guru_collection
# Secret key untuk signing JWT
SECRET_KEY = "thisisverysecretsuperadminpassword"
