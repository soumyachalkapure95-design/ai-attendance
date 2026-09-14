import os
import streamlit as st
from supabase import create_client, Client

def get_secret(key: str, default: str = "") -> str:
    # 1. Try streamlit secrets
    try:
        if key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val)
    except Exception:
        pass
    # 2. Try environment variables
    return os.environ.get(key, default)

supabase_url = get_secret("SUPABASE_URL", "")
supabase_key = get_secret("SUPABASE_KEY", "")

supabase: Client = None

if supabase_url and supabase_key and "your-supabase" not in supabase_url:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Supabase Client Error: {e}")
        supabase = None