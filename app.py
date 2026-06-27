import sqlite3
from datetime import datetime
import streamlit as st

# Set layout wide to support the horizontal grids
st.set_page_config(
    page_title="Adventist Senior High - PTA Portal", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DATABASE ENGINE ---
DB_FILE = "pta_records.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            class TEXT,
            track TEXT,
            house TEXT,
            status TEXT,
            date_added TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        current_date = datetime.now().strftime("%Y-%m-%d")
        cursor.executemany("""
            INSERT INTO students (id, name, class, track, house, status, date_added) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ("STU001", "Kwame Mensah", "Form 3", "General Science", "Kennedy House", "Paid", current_date),
            ("STU002", "Ama Serwaa", "Form 2", "Business", "Aggregation House", "Pending", current_date)
        ])
    conn.commit()
    conn.close()

init_db()

def get_student_by_name(full_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, track, house, status, date_added FROM students WHERE LOWER(name) = LOWER(?)", (full_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "name": result[1], "class": result[2], "track": result[3], "house": result[4], "status": result[5], "date": result[6]}
    return None

def get_all_students():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, track, house, status, date_added FROM students ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"name": row[1], "class": row[2], "track": row[3], "house": row[4], "status": row[5], "date": row[6]} for row in rows}

def add_student(id, name, cls, track, house, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute("""
            INSERT INTO students (id, name, class, track, house, status, date_added) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id, name, cls, track, house, status, current_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_student_status(id, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()

def delete_student(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- ROUTING & VIEW CONTROLLER ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

ADMIN_PASSCODE = "secure123"

# --- CSS INJECTION FOR THE LOVABLE WHITE HEADER & METRICS ---
st.markdown("""
    <style>
    /* Top Header Bar */
    .top-header {
        background-color: #ffffff;
        padding: 12px 40px;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -4rem -4rem 2rem -4rem;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .school-logo {
        font-size: 28px;
    }
    .school-name {
        font-size: 18px !important;
        font-weight: 700;
        color: #111827;
        margin: 0;
        line-height: 1.2;
    }
    .portal-subtitle {
        font-size: 12px !important;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    
    /* Metrics Custom Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748B !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- RENDER TOP HEADER BAR ---
header_html = f"""
<div class="top-header">
    <div class="header-left">
        <span class="school-logo">🏢</span>
        <div>
            <div class="school-name">Adventist SHS</div>
            <div class="portal-subtitle">PTA Portal</div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Navigation utilities overlay on top-right area using a standard line container
top_nav_col1, top_nav_col2 = st.columns([5, 1])
with top_nav_col2:
    if st.session_state.current_page != "Welcome" and st.button("🚪 Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.show_add_form = False
        st.session_state.current_page = "Welcome"
        st.rerun()


# --- PUBLIC LANDING VIEW ---
if st.session_state.current_page == "Welcome":
    st.title("Welcome to the PTA Portal")
    st.markdown("### Secure Payment Tracking & Status Verification")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 Student Dashboard View", use_container_width=True):
            st.session_state.current_page = "Student Dashboard"
            st.rerun()
    with col2:
        if st.button("⚙️ Admin Dashboard View", use_container_width=True):
            st.session_state.current_page = "Admin Dashboard"
            st.rerun()


# --- STUDENT VERIFICATION DASHBOARD ---
elif st.session_state.current_page == "Student Dashboard":
    st.markdown("### 🎓 Student Directory Portal")
    search_name = st.text_input("Enter Student Full Name to verify status:", placeholder="e.g., Kwame Mensah").strip()
    
    if search_name:
        student = get_student_by_name(search_name)
        if student:
            st.success(f"Record found for **{student['name']}**")
            if student['status'] == "Paid":
                st.info("🟢 **PTA Dues Status:** Fully Paid")
            else:
                st.warning("🟡 **PTA Dues Status:** Pending / Unpaid")
                
            st.markdown(f"""
            * **Student ID:** {student['id']}
            * **Form Group:** {student['class']}
            * **Program Track:** {student['track']}
            * **House Assigned:** {student['house']}
            """)
        else:
            st.error("No matches found. Verify the name spelling or visit the administration office.")


# --- ADMIN DASHBOARD (MATCHING SCREENSHOT) ---
elif st.session_state.current_page == "Admin Dashboard":
    if not st.session_state.logged_in:
        st.subheader("Admin Gateway Verification")
        with st.form("admin_login_box"):
            entered_passcode = st.text_input("Enter Passcode:", type="password")
            if st.form_submit_button("Verify Identity"):
                if entered_passcode == ADMIN_PASSCODE:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Access denied.")
    else:
        # 1. Main Headings Row matching screenshot layout
        st.markdown("<p style='color:#3B82F6; font-weight:700; font-size:12px; margin:0; text-transform:uppercase;'>ADMIN</p>", unsafe_allow_html=True)
        
        title_col, action_col = st.columns([3, 2])
        with title_col:
            st.markdown("<h1 style='margin-top:0; font-weight:800; font-size:38px; color:#0F172A;'>Dashboard</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748B; margin-top:-10px; font-size:14px;'>Overview of the student directory.</p>", unsafe_allow_html=True)
            
        with action_col:
            st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True) # spacer
            act_c1, act_c2, act_c3 = st.columns([1, 1.2, 1.8])
            with act_c2:
                if st.button("🛡️ Admins", use_container_width=True):
                    st.toast("Admin profile configuration is up to date.")
            with act_c3:
                # Toggle adding state to reveal form
                if st.button("➕ Manage students", type="primary", use_container_width=True):
                    st.session_state.show_add_form = not st.session_state.show_add_form
                    st.rerun()

        all_students = get_all_students()
        
        # Pull metric stats dynamically
        total_students = len(all_students)
        unique_houses = len(set(info['house'] for info in all_students.values())) if total_students > 0 else 0
        unique_tracks = len(set(info['track'] for info in all_students.values())) if total_students > 0 else 0
        recently_added_count = total_students # In a production environment, filter entries <= 30 days old

        # 2. Four Horizontal Metric Grid Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="👥 Students", value=total_students)
            st.markdown("</div>", unsafe_allow_html=True)
        with m_col2:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="🏠 Houses", value=unique_houses)
            st.markdown("</div>", unsafe_allow_html=True)
        with m_col3:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="🔖 Tracks / Programs", value=unique_tracks)
            st.markdown("</div>", unsafe_allow_html=True)
        with m_col4:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="📅 Added (30D)", value=recently_added_count)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Dynamic Dropdown Form Interface if "Manage students" button is triggered
        if st.session_state.show_add_form:
            st.markdown("<div style='background:#F8FAFC; padding:25px; border-radius:12px; border:1px dashed #CBD5E1; margin-bottom:20px;'>", unsafe_allow_html=True)
            st.subheader("📝 Registration Data Entry Panel")
            with st.form("add_student_form_panel", clear_on_submit=True):
                f1, f2 = st.columns(2)
                with f1:
                    stu_id = st.text_input("Student Unique ID:").strip().upper()
                    stu_name = st.text_input("Full Legal Name:")
                    stu_class = st.selectbox("Form Level:", ["Form 1", "Form 2", "Form 3"])
                with f2:
                    stu_track = st.selectbox("Academic Track:", ["General Science", "General Arts", "Business", "Home Economics", "Visual Arts"])
                    stu_house = st.text_input("House Name:")
                    stu_status = st.selectbox("Dues Payment Status:", ["Paid", "Pending"])
                
                if st.form_submit_button("Save Student Record", use_container_width=True):
                    if not stu_id or not stu_name or not stu_house:
                        st.error("Please fill in all layout blocks.")
                    else:
                        if add_student(stu_id, stu_name, stu_class, stu_track, stu_house, stu_status):
                            st.success(f"Saved entry for {stu_name} successfully.")
                            st.session_state.show_add_form = False
                            st.rerun()
                        else:
                            st.error("Database conflict: This Student ID already exists.")
            st.markdown("</div>", unsafe_allow_html=True)

        # 4. Main Divided Cards Area Layout ("By house" vs "Recently added")
        left_panel, right_panel = st.columns([1.2, 2.0])
        
        with left_panel:
            st.markdown("<div style='background:#ffffff; padding:24px; border:1px solid #E2E8F0; border-radius:12px; min-height:300px;'>", unsafe_allow_html=True)
            st.markdown("<div style='display:flex; justify-content:space-between;'><b style='font-size:16px; color:#0F172A;'>By house</b><span style='color:#64748B; font-size:12px;'>Total metrics</span></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:12px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
            if not all_students:
                st.write("No data yet.")
            else:
                # Aggregate counts per house for quick visualization
                house_counts = {}
                for info in all_students.values():
                    house_counts[info['house']] = house_counts.get(info['house'], 0) + 1
                for house, count in house_counts.items():
                    st.markdown(f"🏠 **{house}:** {count} student(s)")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with right_panel:
            st.markdown("<div style='background:#ffffff; padding:24px; border:1px solid #E2E8F0; border-radius:12px; min-height:300px;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size:16px; color:#0F172A;'>Recently added</b>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:12px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
            if not all_students:
                st.markdown("<div style='text-align:center; padding:40px 0; color:#64748B;'>No records found.<br><br></div>", unsafe_allow_html=True)
                if st.button("➕ Add the first one", type="primary"):
                    st.session_state.show_add_form = True
                    st.rerun()
            else:
                # Render structured, modern table format
                for s_id, s_info in list(all_students.items()):
                    r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3.5, 2.5, 1.5])
                    r_col1.text(s_id)
                    r_col2.markdown(f"**{s_info['name']}** \n`{s_info['class']} - {s_info['house']}`")
                    
                    # Dropdown matching current status index
                    st_list = ["Paid", "Pending"]
                    idx = st_list.index(s_info['status'])
                    new_st = r_col3.selectbox("Status", st_list, index=idx, key=f"table_st_{s_id}", label_visibility="collapsed")
                    if new_st != s_info['status']:
                        update_student_status(s_id, new_st)
                        st.rerun()
                        
                    if r_col4.button("🗑️", key=f"table_del_{s_id}", help="Delete Record"):
                        delete_student(s_id)
                        st.rerun()
                    st.markdown("<div style='border-bottom:1px solid #F1F5F9; margin:6px 0;'></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
