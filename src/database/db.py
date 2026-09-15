import streamlit as st
import bcrypt
from src.database.config import get_supabase_client

def get_db():
    client, err = get_supabase_client()
    if err:
        st.error(f"⚠️ {err}")
        return None
    return client

def notify_supabase_error(e: Exception = None):
    client, err = get_supabase_client()
    if err:
        st.error(f"⚠️ {err}")
    elif e:
        st.error(f"⚠️ Supabase Query Error: {e}")
    else:
        st.error("⚠️ Unable to connect to Supabase database. Please check your credentials.")

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exists(username):
    db = get_db()
    if not db:
        return False
    try:
        response = db.table("teachers").select("username").eq("username", username).execute()
        return len(response.data) > 0 if response and response.data else False
    except Exception as e:
        notify_supabase_error(e)
        return False

def create_teacher(username, password, name):
    db = get_db()
    if not db:
        return None
    try:
        data = { "username" : username, "password": hash_pass(password), "name": name}
        response = db.table("teachers").insert(data).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def teacher_login(username, password):
    db = get_db()
    if not db:
        return None
    try:
        response = db.table("teachers").select("*").eq("username", username).execute()
        if response and response.data:
            teacher = response.data[0]
            if check_pass(password, teacher['password']):
                return teacher
        return None
    except Exception as e:
        notify_supabase_error(e)
        return None

def get_all_students():
    db = get_db()
    if not db:
        return []
    try:
        response = db.table('students').select("*").execute()
        return response.data if response and response.data else []
    except Exception as e:
        notify_supabase_error(e)
        return []

def create_student(new_name, face_embedding=None, voice_embedding=None):
    db = get_db()
    if not db:
        return None
    try:
        data = {'name': new_name, 'face_embedding': face_embedding, "voice_embedding": voice_embedding}
        response = db.table('students').insert(data).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def create_subject(subject_code, name, section, teacher_id):
    db = get_db()
    if not db:
        return None
    try:
        data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
        response = db.table("subjects").insert(data).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def get_teacher_subjects(teacher_id):
    db = get_db()
    if not db:
        return []
    try:
        response = db.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
        subjects = response.data if response and response.data else []

        for sub in subjects:
            sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
            attendance = sub.get('attendance_logs', [])
            unique_sessions = len(set(log['timestamp'] for log in attendance))
            sub['total_classes'] = unique_sessions

            sub.pop('subject_student', None)
            sub.pop('attendance_logs', None)

        return subjects
    except Exception as e:
        notify_supabase_error(e)
        return []

def enroll_student_to_subject(student_id, subject_id):
    db = get_db()
    if not db:
        return None
    try:
        data = {'student_id': student_id, "subject_id": subject_id}
        response = db.table('subject_students').insert(data).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def unenroll_student_to_subject(student_id, subject_id):
    db = get_db()
    if not db:
        return None
    try:
        response = db.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def get_student_subjects(student_id):
    db = get_db()
    if not db:
        return []
    try:
        response = db.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
        return response.data if response and response.data else []
    except Exception as e:
        notify_supabase_error(e)
        return []

def get_student_attendance(student_id):
    db = get_db()
    if not db:
        return []
    try:
        response = db.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
        return response.data if response and response.data else []
    except Exception as e:
        notify_supabase_error(e)
        return []

def create_attendance(logs):
    db = get_db()
    if not db:
        return None
    try:
        response = db.table('attendance_logs').insert(logs).execute()
        return response.data
    except Exception as e:
        notify_supabase_error(e)
        return None

def get_attendance_for_teacher(teacher_id):
    db = get_db()
    if not db:
        return []
    try:
        response = db.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
        return response.data if response and response.data else []
    except Exception as e:
        notify_supabase_error(e)
        return []
