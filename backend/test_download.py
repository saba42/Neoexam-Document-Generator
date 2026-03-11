import os
import sys
from dotenv import load_dotenv

load_dotenv()
from storage.supabase_loader import download_documentation

print("Starting download...")
try:
    path = download_documentation()
    print("Downloaded to:", path)
except Exception as e:
    print("Error:", e)
