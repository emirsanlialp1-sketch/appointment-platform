import streamlit as st
import pandas as pd
import os
from database import (
    init_db, check_login, get_instructors, get_candidates, 
    book_appointment, get_candidate_appointments, get_instructor_appointments,
    get_all_appointments, update_rating, delete_appointment,
    send_announcement, get_announcements, get_connection,
    add_video, get_instructor_videos, delete_video, get_all_videos,
    send_chat_message, get_chat_messages, book_bulk_appointments,
    update_appointment_details
)
from datetime import datetime

# Setup upload directory
UPLOAD_DIR = "uploads/videos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Page config
st.set_page_config(page_title="Randevu Sistemi", page_icon="📅", layout="wide")

# Initialize database
init_db()

# Noir Executive & White-Gold Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Reset & Dark Mode Base */
    html, body {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #020617; /* Deepest Navy/Black */
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 41, 59, 0.5) 0, transparent 50%), 
            radial-gradient(at 50% 0%, rgba(15, 23, 42, 0.5) 0, transparent 50%);
    }

    /* Sidebar - Solid Black Noir */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid rgba(252, 246, 186, 0.2);
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Cinzel', serif;
        color: #fcf6ba !important;
        font-size: 0.9rem;
        letter-spacing: 3px;
        text-align: center;
        padding-top: 20px;
        border-bottom: 1px solid rgba(252, 246, 186, 0.1);
        margin-bottom: 30px;
    }
    
    /* The Polished White-Gold Button (User's Favorite) */
    .stButton>button {
        background: linear-gradient(135deg, #fcf6ba 0%, #bf953f 100%);
        color: #000000 !important;
        border-radius: 2px;
        font-weight: 800;
        letter-spacing: 1.5px;
        border: none;
        height: 3.5rem;
        box-shadow: 0 4px 20px rgba(191, 149, 63, 0.2);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ffffff 0%, #fcf6ba 100%);
        box-shadow: 0 0 30px rgba(252, 246, 186, 0.4);
        transform: translateY(-2px);
    }
    
    /* Noir Cards - Dark Slate Grey */
    .card {
        background-color: #0f172a; /* Dark Grey/Navy */
        padding: 35px;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 2px solid #bf953f;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        margin-bottom: 30px;
    }
    .card h4 {
        font-family: 'Cinzel', serif;
        color: #fcf6ba;
        font-weight: 600;
        font-size: 1.25rem;
        letter-spacing: 1.5px;
        margin-bottom: 20px;
        text-transform: uppercase;
    }
    .card p {
        color: #94a3b8; /* Muted slate for text */
        font-size: 1rem;
        line-height: 1.6;
    }
    .card b {
        color: #fcf6ba;
        font-weight: 600;
    }
    
    /* Announcement - High Contrast Noir */
    .announcement {
        background-color: #1e293b;
        color: #f1f5f9;
        padding: 25px;
        border-right: 4px solid #fcf6ba;
        border-radius: 4px;
        margin-bottom: 25px;
    }
    .announcement b {
        color: #fcf6ba;
        font-family: 'Cinzel', serif;
        font-size: 1.1rem;
    }
    
    /* Input Fields - Darkened Integrated Style */
    .stTextInput input, .stSelectbox select, .stDateInput input {
        background-color: #020617 !important;
        border: 1px solid #334155 !important;
        color: #f1f5f9 !important;
        border-radius: 4px !important;
    }
    .stTextInput label, .stSelectbox label {
        color: #fcf6ba !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px;
    }

    /* Hide the auto-generated anchor links from Streamlit headers */
    .element-container:has(h1) a, .element-container:has(h2) a, 
    .element-container:has(h3) a, .element-container:has(h4) a {
        display: none !important;
    }

    /* Pro Sharp Dark & Gold */
    .stApp {
        background-color: #020617;
    }
    
    .login-container {
        max-width: 340px; /* Reduced from 440px for a more compact look */
        margin: 120px auto;
        background-color: #0f172a; /* Solid Slate */
        padding: 40px; /* Slightly reduced padding */
        border: 1px solid #334155;
        border-top: 3px solid #bf953f; /* Crisp Gold Top */
        border-radius: 4px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-header h1 {
        font-family: 'Cinzel', serif;
        color: #fcf6ba;
        font-size: 2.2rem;
        letter-spacing: 3px;
        margin: 0;
        padding: 0;
        text-shadow: none;
    }
    
    .login-header p {
        color: #64748b;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
    }

    /* Input Styling */
    .stTextInput label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# --- Login Page ---
if not st.session_state.logged_in:
    # Use even narrower columns for strict width control: [2, 1, 2] 
    # The middle column will now be 1/5th of the screen width.
    cols = st.columns([2, 1.2, 2])
    with cols[1]:
        st.markdown(f"""
            <div class="login-container">
                <div class="login-header">
                    <h1>SİSTEM</h1>
                    <p>Randevu Kontrol Paneli</p>
                </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("KULLANICI ADI")
        password = st.text_input("ŞİFRE", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SİSTEME GİRİŞ YAP"):
            user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = {
                    'id': user[0],
                    'username': user[1],
                    'name': user[2],
                    'role': user[3]
                }
                st.success("DOĞRULANDI")
                st.rerun()
            else:
                st.error("Kimlik bilgileri hatalı.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#334155; font-size:0.7rem; margin-top:20px; letter-spacing:2px;'>EST. 2026 CORPORATE PORTAL</p>", unsafe_allow_html=True)
else:
    # --- Main App ---
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Hoş Geldiniz, {user['name']}")
        st.markdown(f"**Rol:** {user['role']}")
        st.divider()
        
        menu = []
        if user['role'] == "Aday":
            menu = ["Ders Randevusu Al", "Randevularım", "Eğitim Videoları", "Sohbet Paneli", "Duyurular"]
        elif user['role'] == "Eğitmen":
            menu = ["Ders Programım", "Eğitim Videoları", "Sohbet Paneli", "Duyuru Gönder", "Duyurular"]
        elif user['role'] == "Admin":
            menu = ["Tüm Dersler", "Ders Ekle", "Sohbet Paneli", "Duyuru Gönder", "Eğitmen Puanları"]
            
        choice = st.radio("Menü", menu)
        
        st.divider()
        if st.button("Güvenli Çıkış"):
            logout()

    # --- Dashboard Pages ---
    
    # ADAY PAGES
    if user['role'] == "Aday":
        if choice == "Ders Randevusu Al":
            st.header("5 Derslik Paket Randevusu")
            
            # Check current appointments count
            current_apps = get_candidate_appointments(user['id'])
            lessons_taken = len(current_apps)
            remaining_rights = max(0, 5 - lessons_taken)
            
            # Display Status
            st.markdown(f"""
                <div style='background:rgba(191,149,63,0.1); padding:20px; border-radius:8px; border-left:5px solid #bf953f; margin-bottom:25px;'>
                    <h4 style='color:#fcf6ba; margin:0;'>Ders Hakkı Bilgisi</h4>
                    <p style='font-size:1.2rem; margin:10px 0;'>Toplam Hak: <b>5 Ders</b> | Kalan Hak: <b style='color:#fcf6ba'>{remaining_rights} Ders</b></p>
                    <small style='color:#94a3b8'>* Randevu aldığınızda seçtiğiniz saat 5 hafta boyunca sizin için rezerve edilir.</small>
                </div>
            """, unsafe_allow_html=True)
            
            if remaining_rights >= 5:
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    instructors = get_instructors()
                    inst_list = {f"{i[1]} {i[2]}": i[0] for i in instructors}
                    
                    selected_inst_name = st.selectbox("Eğitmen Seçin", list(inst_list.keys()))
                    selected_inst_id = inst_list[selected_inst_name]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        date = st.date_input("Başlangıç Tarihi", min_value=datetime.today())
                    with col2:
                        time_options = [f"{h:02d}:00" for h in range(8, 19)]
                        selected_time = st.selectbox("Ders Saati", time_options)
                    
                    vehicle = st.text_input("Araç Bilgisi", "B Sınıfı")
                    
                    st.warning(f"⚠️ Bilgi: {date} tarihinden itibaren her hafta aynı saatte 5 dersiniz tanımlanacaktır.")
                    
                    if st.button("Hakkımı Kullan ve 5 Randevu Oluştur"):
                        success, conflict_date = book_bulk_appointments(user['id'], selected_inst_id, str(date), selected_time, vehicle)
                        if success:
                            st.success(f"Tebrikler! {selected_inst_name} ile 5 haftalık ders programınız başarıyla oluşturuldu.")
                            st.rerun()
                        else:
                            st.error(f"Maalesef seçilen saat {conflict_date} tarihinde dolu. Lütfen başka bir saat veya eğitmen seçin.")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Tüm ders haklarınızı kullandınız veya mevcut aktif bir programınız var. Yeni bir paket almak için mevcut derslerin bitmesini beklemeniz veya admin ile görüşmeniz gerekmektedir.")

        elif choice == "Randevularım":
            st.header("Sistemdeki Derslerim")
            
            # Information notice about the 5-lesson bundle
            st.markdown(f"""
                <div style='background:rgba(252, 246, 186, 0.05); padding:15px; border-radius:4px; border-left:3px solid #bf953f; margin-bottom:20px;'>
                    <p style='color:#fcf6ba; margin:0; font-size:1rem;'>
                        ℹ️ <b>Bilgilendirme:</b> Eğitim sürecinizin verimliliği için seçtiğiniz 5 dersin tamamı; 
                        aynı gün, aynı saat ve aynı eğitmenle olacak şekilde planlanmıştır. 
                        Aşağıda bu plana ait ders detaylarını görebilirsiniz.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            apps = get_candidate_appointments(user['id'])
            if apps:
                for app in apps:
                    with st.container():
                        st.markdown(f"""
                        <div class='card'>
                            <h4>Eğitmen: {app[1]} {app[2]}</h4>
                            <p><b>Telefon:</b> {app[3]}</p>
                            <p><b>Tarih/Saat:</b> {app[4]} - {app[5]}</p>
                            <p><b>Araç:</b> {app[6]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Rating
                        current_rating = app[7] if app[7] and app[7] > 0 else 5
                        new_rating = st.slider(f"Eğitmen Puanı (Ders: {app[4]})", 1, 5, int(current_rating), key=f"rate_{app[0]}")
                        if st.button("Puanı Kaydet", key=f"btn_{app[0]}"):
                            update_rating(app[0], new_rating)
                            st.success("Puanınız kaydedildi (Sadece admin görebilir).")
            else:
                st.info("Henüz bir randevunuz bulunmamaktadır.")

        elif choice == "Duyurular":
            st.header("Duyuru Merkezi")
            anns = get_announcements(user['id'])
            for ann in anns:
                st.markdown(f"""
                <div class='announcement'>
                    <b>{ann[0]}</b> - <small>{ann[2]} ({ann[3]})</small><br>
                    {ann[1]}
                </div>
                """, unsafe_allow_html=True)

        elif choice == "Eğitim Videoları":
            st.header("Eğitim Videoları")
            vids = get_all_videos()
            if vids:
                for vid in vids:
                    # vid structure: [id, title, url, instructor_name, instructor_id]
                    with st.container():
                        st.markdown(f"""
                        <div class='card'>
                            <h4>{vid[1]}</h4>
                            <p><b>Yükleyen Eğitmen:</b> {vid[3]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.video(vid[2])
                        
                        # Messaging Feature
                        with st.expander(f"Eğitmen {vid[3]} Hocaya Mesaj Gönder"):
                            msg_title = st.text_input("Mesaj Başlığı", value=f"{vid[1]} Hakkında Soru", key=f"title_{vid[0]}")
                            msg_content = st.text_area("Mesajınız", key=f"msg_{vid[0]}")
                            if st.button("Mesajı Gönder", key=f"btn_send_{vid[0]}"):
                                if msg_content:
                                    send_announcement(user['id'], vid[4], msg_title, msg_content)
                                    st.success(f"Mesajınız {vid[3]} hocamıza başarıyla iletildi.")
                                else:
                                    st.warning("Lütfen mesaj içeriğini doldurun.")
            else:
                st.info("Henüz yüklenmiş eğitim videosu bulunmamaktadır.")

    # EĞİTMEN PAGES
    elif user['role'] == "Eğitmen":
        if choice == "Ders Programım":
            st.header("Ders Programı")
            apps = get_instructor_appointments(user['id'])
            if apps:
                df = pd.DataFrame(apps, columns=["ID", "Ad", "Soyad", "Telefon", "Tarih", "Saat", "Araç"])
                st.table(df[["Ad", "Soyad", "Telefon", "Tarih", "Saat", "Araç"]])
            else:
                st.info("Programınızda henüz ders bulunmamaktadır.")

        elif choice == "Duyuru Gönder":
            st.header("Duyuru Oluştur")
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                type_sel = st.radio("Duyuru Tipi", ["Genel (Tüm Adaylar)", "Şahsi (Özel)"])
                
                target_user = None
                if type_sel == "Şahsi (Özel)":
                    candidates = get_candidates()
                    cand_list = {f"{c[1]} {c[2]}": c[0] for c in candidates}
                    sel_cand = st.selectbox("Aday Seç", list(cand_list.keys()))
                    target_user = cand_list[sel_cand]
                
                title = st.text_input("Başlık")
                msg = st.text_area("Mesaj")
                
                if st.button("Duyuruyu Yayınla"):
                    send_announcement(user['id'], target_user, title, msg)
                    st.success("Duyuru başarıyla gönderildi.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        elif choice == "Duyurular":
            st.header("📢 Gelen Duyurular")
            anns = get_announcements(user['id'])
            for ann in anns:
                st.markdown(f"""
                <div class='announcement'>
                    <b>{ann[0]}</b> - <small>{ann[2]} ({ann[3]})</small><br>
                    {ann[1]}
                </div>
                """, unsafe_allow_html=True)

        elif choice == "Eğitim Videoları":
            st.header("Eğitim Videoları Yönetimi")
            
            # Add New Video
            with st.expander("Yeni Video Dünyası", expanded=True):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                v_title = st.text_input("Video Başlığı")
                
                upload_type = st.radio("Yükleme Tipi", ["Video Linki (YouTube/Vimeo)", "Video Dosyası (MP4)"])
                
                final_url = ""
                if upload_type == "Video Linki (YouTube/Vimeo)":
                    final_url = st.text_input("Video URL")
                else:
                    uploaded_file = st.file_uploader("Ekran Kaydı veya Video Dosyası Seçin", type=["mp4", "mov", "avi", "webm", "mkv"])
                    if uploaded_file:
                        # Ensure filename is safe and unique
                        safe_filename = f"{user['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        file_path = os.path.join(UPLOAD_DIR, safe_filename)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        final_url = file_path
                
                if st.button("Sisteme Kaydet"):
                    if v_title and final_url:
                        add_video(user['id'], v_title, final_url)
                        st.success("Video başarıyla eklendi.")
                        st.rerun()
                    else:
                        st.warning("Lütfen başlık ve video bilgisini eksiksiz girin.")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # List My Videos
            st.subheader("Yayındaki Videolarım")
            my_vids = get_instructor_videos(user['id'])
            if my_vids:
                for vid in my_vids:
                    with st.container():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"#### {vid[1]}")
                        st.video(vid[2])
                        if st.button("Videoyu Kaldır", key=f"del_vid_{vid[0]}"):
                            # If it's a local file, delete it from disk too
                            if os.path.exists(vid[2]) and "uploads" in vid[2]:
                                os.remove(vid[2])
                            delete_video(vid[0])
                            st.success("Video sistemden kaldırıldı.")
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Henüz video yüklemediniz.")

    elif user['role'] == "Admin":
        if choice == "Tüm Dersler":
            st.header("Randevu Yönetimi")
            apps = get_all_appointments()
            if apps:
                df = pd.DataFrame(apps, columns=["ID", "Aday", "Eğitmen", "Tarih", "Saat", "Araç", "Puan"])
                display_df = df.copy()
                display_df['Puan'] = display_df['Puan'].apply(lambda x: x if x > 0 else "Henüz Puanlanmadı")
                st.dataframe(display_df, use_container_width=True)
                
                st.divider()
                st.subheader("🛠️ İşlem Merkezi")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.container(border=True):
                        st.markdown("<p style='color:#bf953f; font-weight:bold; font-size:1.1rem;'>Randevu İptal Paneli</p>", unsafe_allow_html=True)
                        del_id = st.number_input("İptal Edilecek ID", min_value=1, step=1, key="del_input")
                        if st.button("Seçili Randevuyu KALICI OLARAK SİL"):
                            delete_appointment(del_id)
                            st.success(f"ID: {del_id} başarıyla silindi.")
                            st.rerun()
                
                with col2:
                    with st.container(border=True):
                        st.markdown("<p style='color:#bf953f; font-weight:bold; font-size:1.1rem;'>Randevu Güncelleme Paneli</p>", unsafe_allow_html=True)
                        edit_id = st.number_input("Güncellenecek ID", min_value=1, step=1, key="edit_input")
                        
                        # Form for editing
                        with st.expander(f"Seçili ID ({edit_id}) Detaylarını Düzenle"):
                            cands = get_candidates()
                            cand_list = {f"{c[1]} {c[2]}": c[0] for c in cands}
                            insts = get_instructors()
                            inst_list = {f"{i[1]} {i[2]}": i[0] for i in insts}
                            
                            new_cand = st.selectbox("Aday Seç", list(cand_list.keys()), key="edit_cand")
                            new_inst = st.selectbox("Eğitmen Seç", list(inst_list.keys()), key="edit_inst")
                            new_date = st.date_input("Yeni Tarih Seç", key="edit_date")
                            
                            time_options = [f"{h:02d}:00" for h in range(8, 19)]
                            new_time = st.selectbox("Yeni Saat Seç", time_options, key="edit_time")
                            new_veh = st.text_input("Araç Bilgisini Güncelle", value="B Sınıfı", key="edit_veh")
                            
                            if st.button("Değişiklikleri Onayla ve Kaydet"):
                                update_appointment_details(
                                    edit_id, 
                                    cand_list[new_cand], 
                                    inst_list[new_inst], 
                                    str(new_date), 
                                    new_time, 
                                    new_veh
                                )
                                st.success("Randevu başarıyla güncellendi.")
                                st.rerun()
            else:
                st.info("Sistemde henüz ders kaydı yok.")

        elif choice == "Ders Ekle":
            st.header("Randevu Kaydı Oluştur")
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                cands = get_candidates()
                cand_list = {f"{c[1]} {c[2]}": c[0] for c in cands}
                insts = get_instructors()
                inst_list = {f"{i[1]} {i[2]}": i[0] for i in insts}
                
                c1, c2 = st.columns(2)
                with c1:
                    sel_cand = st.selectbox("Aday", list(cand_list.keys()))
                    date = st.date_input("Tarih")
                with c2:
                    sel_inst = st.selectbox("Eğitmen", list(inst_list.keys()))
                    # Time options
                    time_options = [f"{h:02d}:00" for h in range(8, 19)]
                    selected_time = st.selectbox("Saat", time_options)
                
                veh = st.text_input("Araç")
                
                if st.button("Ders Kaydet"):
                    if book_appointment(cand_list[sel_cand], inst_list[sel_inst], str(date), selected_time, veh):
                        st.success("Ders başarıyla eklendi.")
                    else:
                        st.error("Bu saatte eğitmen dolu.")
                st.markdown("</div>", unsafe_allow_html=True)

        elif choice == "Duyuru Gönder":
            st.header("Sistem Duyurusu")
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                target = st.radio("Hedef", ["Herkes", "Eğitmenler", "Adaylar", "Şahsi"])
                
                target_user = None
                if target == "Şahsi":
                    all_users = []
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("SELECT id, full_name, role FROM users")
                    all_users = c.fetchall()
                    conn.close()
                    user_map = {f"{u[1]} ({u[2]})": u[0] for u in all_users}
                    sel = st.selectbox("Kullanıcı Seç", list(user_map.keys()))
                    target_user = user_map[sel]
                
                title = st.text_input("Başlık")
                msg = st.text_area("Mesaj")
                
                if st.button("Duyuruyu Gönder"):
                    send_announcement(user['id'], target_user, title, msg)
                    st.success("Duyuru gönderildi.")
                st.markdown("</div>", unsafe_allow_html=True)

        elif choice == "Eğitmen Puanları":
            st.header("Eğitmen Performans Raporu")
            apps = get_all_appointments()
            if apps:
                df = pd.DataFrame(apps, columns=["ID", "Aday", "Eğitmen", "Tarih", "Saat", "Araç", "Puan"])
                # Sadece 1-5 arası olan gerçek puanları istatistiğe dahil et
                rated_apps = df[df['Puan'] >= 1]
                if not rated_apps.empty:
                    stats = rated_apps.groupby('Eğitmen')['Puan'].mean().reset_index()
                    st.bar_chart(stats.set_index('Eğitmen'))
                    st.table(stats)
                else:
                    st.info("Henüz 1-5 arası puanlanmış ders bulunmamaktadır.")
            else:
                st.info("Sistemde ders kaydı yok.")
            
    # COMMON CHAT PANEL (For all relevant roles)
    if "Sohbet Paneli" in choice:
        st.header("Sohbet Merkezi")
        
        # Channel logic based on role
        if user['role'] == "Aday":
            tabs = ["Eğitmenlerle Sohbet"]
        else:
            tabs = ["Ders & Aday Sohbeti", "Eğitmenler Odası (Özel)"]
            
        active_tab = st.tabs(tabs)
        
        # Tab 1: Public Chat (Students & Instructors)
        with active_tab[0]:
            st.subheader("💡 Dersler ve Sorular")
            msgs = get_chat_messages('public')
            
            chat_container = st.container(height=400)
            with chat_container:
                for m in msgs:
                    role_color = "#bf953f" if m[2] != "Aday" else "#94a3b8"
                    st.markdown(f"""
                        <div style='margin-bottom:10px; padding:10px; background:rgba(255,255,255,0.03); border-left:3px solid {role_color}'>
                            <small style='color:{role_color}'>{m[1]} ({m[2]}) - {m[3]}</small><br>
                            <span style='color:#f1f5f9'>{m[0]}</span>
                        </div>
                    """, unsafe_allow_html=True)
            
            with st.form("public_chat_form", clear_on_submit=True):
                client_msg = st.text_input("Mesajınız", placeholder="Sorunuzu veya mesajınızı buraya yazın...")
                if st.form_submit_button("Gönder"):
                    if client_msg:
                        send_chat_message(user['id'], client_msg, 'public')
                        st.rerun()

        # Tab 2: Private Chat (Instructors Only) - Hidden from candidates
        if user['role'] != "Aday":
            with active_tab[1]:
                st.subheader("🔒 Eğitmen Özel Alanı")
                msgs = get_chat_messages('private')
                
                chat_container_priv = st.container(height=400)
                with chat_container_priv:
                    for m in msgs:
                        st.markdown(f"""
                            <div style='margin-bottom:10px; padding:10px; background:rgba(191,149,63,0.05); border-left:3px solid #fcf6ba'>
                                <small style='color:#fcf6ba'>{m[1]} - {m[3]}</small><br>
                                <span style='color:#f1f5f9'>{m[0]}</span>
                            </div>
                        """, unsafe_allow_html=True)
                
                with st.form("private_chat_form", clear_on_submit=True):
                    priv_msg = st.text_input("Mesajınız", placeholder="Hocalar arası gizli mesaj...")
                    if st.form_submit_button("Özel Mesaj Gönder"):
                        if priv_msg:
                            send_chat_message(user['id'], priv_msg, 'private')
                            st.rerun()
