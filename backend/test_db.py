import os
from supabase import create_client, Client

url: str = "https://kdxtytslsxchjjcckgco.supabase.co"
key: str = "sb_publishable_0C2D22ybemtor6zOtTlz6w_5kKcd00N"
supabase: Client = create_client(url, key)

try:
    # Just try querying a common table name or 'parameters' table to see what happens
    response = supabase.table('parameters').select('*').execute()
    print("Table 'parameters' exists and has data:")
    print(response.data)
except Exception as e:
    print(f"Error querying 'parameters': {e}")
    
try:
    # Let's try grabbing some records from any table, or maybe we just catch exception to see if the table exists
    response = supabase.table('parameter_docs').select('*').execute()
    print("Table 'parameter_docs' info:")
    print(response.data[:2])
except Exception as e:
    print(f"Error querying 'parameter_docs': {e}")

try:
    response = supabase.table('docs').select('*').execute()
    print("Table 'docs' info:")
    print(response.data[:2])
except Exception as e:
    print(f"Error querying 'docs': {e}")
