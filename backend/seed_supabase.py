import pandas as pd
from supabase import create_client, Client

url = "https://kdxtytslsxchjjcckgco.supabase.co"
key = "sb_publishable_0C2D22ybemtor6zOtTlz6w_5kKcd00N"
supabase: Client = create_client(url, key)

df = pd.read_csv("data/sample_parameters.csv")

for _, row in df.iterrows():
    data = {
        "parameter_key": str(row.get("parameter_key", "")).strip(),
        "display_name": str(row.get("display_name", "")).strip(),
        "definition": str(row.get("definition", "")).strip(),
        "how_it_works": str(row.get("how_it_works", "")).strip(),
        "faq": str(row.get("faq", "")).strip()
    }
    
    try:
        response = supabase.table("parameters").insert(data).execute()
        print(f"Inserted: {data['display_name']}")
    except Exception as e:
        print(f"Error inserting {data['display_name']}: {e}")

print("Seeding complete!")
