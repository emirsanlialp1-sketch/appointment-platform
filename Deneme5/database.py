import sqlite3
import hashlib

def get_connection():
    return sqlite3.connect('appointment_system.db')

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        surname TEXT,
        phone TEXT,
        role TEXT
    )''')
    
    # Appointments table
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        instructor_id INTEGER,
        date TEXT,
        time TEXT,
        vehicle TEXT,
        rating INTEGER DEFAULT 0,
        FOREIGN KEY (candidate_id) REFERENCES users(id),
        FOREIGN KEY (instructor_id) REFERENCES users(id)
    )''')
    
    # Announcements table
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER, -- NULL means general
        title TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id)
    )''')

    # Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instructor_id INTEGER,
        title TEXT,
        url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (instructor_id) REFERENCES users(id)
    )''')

    # Chat Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        message TEXT,
        channel TEXT, -- 'public' (Aday-Egitmen), 'private' (Egitmen-Egitmen)
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id)
    )''')

    # --- SEEDING LOGIC ---
    def add_user_if_not_exists(username, password, full_name, surname, phone, role):
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, full_name, surname, phone, role) VALUES (?, ?, ?, ?, ?, ?)", 
                      (username, hashed_pw, full_name, surname, phone, role))

    # Add Admin
    add_user_if_not_exists("admin", "admin123", "System Admin", "", "", "Admin")
    
    # Add Instructor
    add_user_if_not_exists("hoca1", "hoca123", "Ahmet", "Yılmaz", "05551112233", "Eğitmen")
    
    # Add Candidates
    add_user_if_not_exists("aday1", "aday123", "Mehmet", "Demir", "05449998877", "Aday")
    add_user_if_not_exists("aday2", "aday123", "Ayşe", "Kaya", "05332224455", "Aday")

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def get_instructors():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, full_name, surname, phone FROM users WHERE role = 'Eğitmen'")
    instructors = c.fetchall()
    conn.close()
    return instructors

def get_candidates():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, full_name, surname, phone FROM users WHERE role = 'Aday'")
    candidates = c.fetchall()
    conn.close()
    return candidates

def check_availability(instructor_id, date, time):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM appointments WHERE instructor_id = ? AND date = ? AND time = ?", 
              (instructor_id, date, time))
    result = c.fetchone()
    conn.close()
    return result is None

def book_appointment(candidate_id, instructor_id, date, time, vehicle):
    if not check_availability(instructor_id, date, time):
        return False
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO appointments (candidate_id, instructor_id, date, time, vehicle) VALUES (?, ?, ?, ?, ?)", 
              (candidate_id, instructor_id, date, time, vehicle))
    conn.commit()
    conn.close()
    return True

def book_bulk_appointments(candidate_id, instructor_id, start_date, time, vehicle, count=5):
    from datetime import datetime, timedelta
    
    # Check availability for all 5 dates first
    dates_to_book = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    for i in range(count):
        d_str = current_date.strftime('%Y-%m-%d')
        if not check_availability(instructor_id, d_str, time):
            return False, d_str # Return false and the conflicting date
        dates_to_book.append(d_str)
        current_date += timedelta(days=7) # Next week
        
    conn = get_connection()
    c = conn.cursor()
    for d in dates_to_book:
        c.execute("INSERT INTO appointments (candidate_id, instructor_id, date, time, vehicle) VALUES (?, ?, ?, ?, ?)", 
                  (candidate_id, instructor_id, d, time, vehicle))
    conn.commit()
    conn.close()
    return True, None

def get_candidate_appointments(candidate_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, u.full_name, u.surname, u.phone, a.date, a.time, a.vehicle, a.rating
        FROM appointments a
        JOIN users u ON a.instructor_id = u.id
        WHERE a.candidate_id = ?
    ''', (candidate_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def get_instructor_appointments(instructor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, u.full_name, u.surname, u.phone, a.date, a.time, a.vehicle
        FROM appointments a
        JOIN users u ON a.candidate_id = u.id
        WHERE a.instructor_id = ?
    ''', (instructor_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def get_all_appointments():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, c.full_name || ' ' || c.surname, i.full_name || ' ' || i.surname, a.date, a.time, a.vehicle, a.rating
        FROM appointments a
        JOIN users c ON a.candidate_id = c.id
        JOIN users i ON a.instructor_id = i.id
    ''')
    apps = c.fetchall()
    conn.close()
    return apps

def update_rating(appointment_id, rating):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE appointments SET rating = ? WHERE id = ?", (rating, appointment_id))
    conn.commit()
    conn.close()

def update_appointment_details(appointment_id, candidate_id, instructor_id, date, time, vehicle):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE appointments 
        SET candidate_id = ?, instructor_id = ?, date = ?, time = ?, vehicle = ?
        WHERE id = ?
    ''', (candidate_id, instructor_id, date, time, vehicle, appointment_id))
    conn.commit()
    conn.close()

def delete_appointment(appointment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()

def send_announcement(sender_id, receiver_id, title, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO announcements (sender_id, receiver_id, title, message) VALUES (?, ?, ?, ?)", 
              (sender_id, receiver_id, title, message))
    conn.commit()
    conn.close()

def get_announcements(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.title, a.message, u.full_name, a.timestamp
        FROM announcements a
        JOIN users u ON a.sender_id = u.id
        WHERE a.receiver_id IS NULL OR a.receiver_id = ?
        ORDER BY a.timestamp DESC
    ''', (user_id,))
    ann = c.fetchall()
    conn.close()
    return ann

def add_video(instructor_id, title, url):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO videos (instructor_id, title, url) VALUES (?, ?, ?)", 
              (instructor_id, title, url))
    conn.commit()
    conn.close()

def get_instructor_videos(instructor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, url, timestamp FROM videos WHERE instructor_id = ? ORDER BY timestamp DESC", 
              (instructor_id,))
    vids = c.fetchall()
    conn.close()
    return vids

def delete_video(video_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()

def get_all_videos():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT v.id, v.title, v.url, u.full_name || ' ' || u.surname as instructor_name, v.instructor_id
        FROM videos v
        JOIN users u ON v.instructor_id = u.id
        ORDER BY v.timestamp DESC
    ''')
    vids = c.fetchall()
    conn.close()
    return vids

def send_chat_message(sender_id, message, channel):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (sender_id, message, channel) VALUES (?, ?, ?)", 
              (sender_id, message, channel))
    conn.commit()
    conn.close()

def get_chat_messages(channel):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT m.message, u.full_name || ' ' || u.surname, u.role, m.timestamp 
        FROM chat_messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.channel = ?
        ORDER BY m.timestamp ASC
    ''', (channel,))
    msgs = c.fetchall()
    conn.close()
    return msgs
