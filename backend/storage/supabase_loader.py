import os
import tempfile
from dotenv import load_dotenv
from supabase import create_client, Client

from backend.utils.paths import get_base_dir
load_dotenv(os.path.join(get_base_dir(), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
DOCS_BUCKET = os.getenv("DOCS_BUCKET", "parameter-docs").strip()
DOCS_FILENAME = os.getenv("DOCS_FILENAME", "Source_Data.docx").strip()
DOCS_URL = os.getenv("DOCS_URL")

from backend.utils.paths import get_cache_path
CACHE_PATH = get_cache_path("source_doc_cache.docx")
CACHE_DIR = os.path.dirname(CACHE_PATH)

def get_source_document_path():
    """
    Returns local path to source document.
    
    Priority:
    1. Try Supabase → save cache → return path
    2. If Supabase fails → use cache → return path  
    3. If no cache → raise clear error
    """
    from backend.utils.paths import get_base_dir
    load_dotenv(os.path.join(get_base_dir(), ".env"))
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
    DOCS_BUCKET = os.getenv("DOCS_BUCKET", "parameter-docs").strip()
    DOCS_FILENAME = os.getenv("DOCS_FILENAME", "Paramter Document.docx").strip()

    # Try Supabase first
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            # We use the official Supabase pyclient but also can just use HTTP if client fails
            # Since the user requested using the 'supabase' library, we'll try that
            import urllib.parse
            import requests
            import warnings
            from urllib3.exceptions import InsecureRequestWarning
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            
            encoded_filename = urllib.parse.quote(DOCS_FILENAME)
            url_target = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{DOCS_BUCKET}/{encoded_filename}"
            headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
            
            r = requests.get(url_target, headers=headers, timeout=10, verify=False)
            if r.status_code == 200:
                os.makedirs(CACHE_DIR, exist_ok=True)
                with open(CACHE_PATH, "wb") as f:
                    f.write(r.content)
                print("✅ Source document fetched from Supabase and cached.")
                return CACHE_PATH
            else:
                print(f"⚠️ Supabase fetch failed (HTTP {r.status_code})")
    except Exception as e:
        print(f"⚠️  Supabase fetch failed: {e}")
        print("Falling back to local cache...")
    
    # Try local cache
    if os.path.exists(CACHE_PATH):
        print("✅ Using cached source document.")
        return CACHE_PATH
    
    # Nothing available
    raise FileNotFoundError(
        "Source document not available.\n"
        "Please check your internet connection "
        "or Supabase configuration in .env file."
    )
