import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def _create_cached_supabase_client(url: str, key: str):
    return create_client(url, key)

def get_supabase_client():
    url = ""
    key = ""
    
    # Check Streamlit secrets
    try:
        if "SUPABASE_URL" in st.secrets:
            url = str(st.secrets["SUPABASE_URL"]).strip()
    except Exception:
        pass
        
    if not url:
        url = os.environ.get("SUPABASE_URL", "").strip()

    try:
        if "SUPABASE_KEY" in st.secrets:
            key = str(st.secrets["SUPABASE_KEY"]).strip()
    except Exception:
        pass
        
    if not key:
        key = os.environ.get("SUPABASE_KEY", "").strip()

    # Validation
    missing = []
    if not url or "your-supabase" in url:
        missing.append("SUPABASE_URL")
    if not key or "your-supabase" in key:
        missing.append("SUPABASE_KEY")

    if missing:
        return None, f"Secrets not found or using placeholders ({', '.join(missing)}). Please check Streamlit Cloud App Settings -> Secrets."

    try:
        client = _create_cached_supabase_client(url, key)
        return client, None
    except Exception as e:
        return None, f"Failed to initialize Supabase client: {e}"

# Backward compatibility proxy
class SupabaseProxy:
    def __getattr__(self, name):
        client, err = get_supabase_client()
        if not client:
            raise RuntimeError(err or "Supabase client not available")
        return getattr(client, name)

supabase = SupabaseProxy()