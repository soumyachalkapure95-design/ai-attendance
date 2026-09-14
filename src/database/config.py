import streamlit as st


from supabase import create_client, Client

supabase_url = st.secrets.get("SUPABASE_URL", "https://your-supabase-project.supabase.co")
supabase_key = st.secrets.get("SUPABASE_KEY", "your-supabase-anon-key")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception:
    supabase = None