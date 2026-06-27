import sqlite3
import streamlit as st

# --- PAGE SETUP & LOVABLE DESIGN ENGINE ---
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
    
    # 1. Create the base table if it doesn't exist at all
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            class TEXT,
            track TEXT,
            house TEXT,
            status TEXT
        )
    """)
    
    # 2. Migration: Safely add new columns if an old DB table exists without them
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN track TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN house TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # 3. Seed default data if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO students (id, name, class, track, house, status) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("STU001", "Kwame Mensah", "Form 3", "General Science", "Kennedy House", "Paid"),
            ("STU002", "Ama Serwaa", "Form 2", "Business", "Aggregation House", "Pending")
        ])
    conn.commit()
    conn.close()
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO students (id, name, class, track, house, status) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("STU001", "Kwame Mensah", "Form 3", "General Science", "Kennedy House", "Paid"),
            ("STU002", "Ama Serwaa", "Form 2", "Business", "Aggregation House", "Pending")
        ])
    conn.commit()
    conn.close()

init_db()

def get_student_by_name(full_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, track, house, status FROM students WHERE LOWER(name) = LOWER(?)", (full_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "name": result[1], "class": result[2], "track": result[3], "house": result[4], "status": result[5]}
    return None

def get_all_students():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, track, house, status FROM students ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"name": row[1], "class": row[2], "track": row[3], "house": row[4], "status": row[5]} for row in rows}

def add_student(id, name, cls, track, house, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (id, name, class, track, house, status) VALUES (?, ?, ?, ?, ?, ?)", (id, name, cls, track, house, status))
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


# --- SESSION MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

ADMIN_PASSCODE = "secure123"

# --- CSS CARD CUSTOM STYLING ---
st.markdown("""
    <style>
    /* White Navbar header strip matching image */
    .top-header {
        background-color: #ffffff;
        padding: 14px 45px;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -4rem -4rem 2rem -4rem;
    }
    .header-left-box {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .school-title-text {
        font-size: 18px !important;
        font-weight: 700;
        color: #1E293B;
        margin: 0;
        line-height: 1.2;
    }
    .portal-tagline {
        font-size: 11px !important;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    
    /* Metrics numbers adjustments */
    div[data-testid="stMetricValue"] {
        font-size: 30px !important;
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

# --- INJECT TOP NAVBAR HEADER ---
st.markdown("""
<div class="top-header">
    <div class="header-left-box">
        <span style="font-size: 26px;">🏫</span>
        <div>
            <div class="school-title-text">Adventist SHS</div>
            <div class="portal-tagline">Prefect Portal</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Right-aligned floating sign-out control button layer
nav_space1, nav_space2 = st.columns([5.2, 0.8])
with nav_space2:
    if st.session_state.current_page != "Welcome" and st.button("🚪 Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.show_add_form = False
        st.session_state.current_page = "Welcome"
        st.rerun()


# --- PUBLIC LANDING PAGE ROUTE ---
if st.session_state.current_page == "Welcome":
    st.title("Welcome to the PTA Portal")
    st.markdown("### Secure Payment Tracking & Status Verification")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎓 Student Dashboard View", use_container_width=True):
            st.session_state.current_page = "Student Dashboard"
            st.rerun()
    with c2:
        if st.button("⚙️ Admin Dashboard View", use_container_width=True):
            st.session_state.current_page = "Admin Dashboard"
            st.rerun()


# --- STUDENT VERIFICATION VIEW ---
elif st.session_state.current_page == "Student Dashboard":
    st.markdown("### 🎓 Student Directory Search")
    search_name = st.text_input("Enter Student Full Name:", placeholder="e.g., Kwame Mensah").strip()
    
    if search_name:
        student = get_student_by_name(search_name)
        if student:
            st.success(f"Record matched: **{student['name']}**")
            if student['status'] == "Paid":
                st.info("🟢 **Payment Dues Status:** Verified Fully Paid")
            else:
                st.warning("🟡 **Payment Dues Status:** Pending / Unpaid Balance")
            st.markdown(f"""
            * **Student ID:** {student['id']}
            * **Form Group:** {student['class']}
            * **Academic Track:** {student['track']}
            * **House:** {student['house']}
            """)
        else:
            st.error("No record found matching that name setup.")


# --- DYNAMIC ADMIN DASHBOARD PANEL PANEL ---
elif st.session_state.current_page == "Admin Dashboard":
    if not st.session_state.logged_in:
        st.subheader("🔒 Administrative Gateway Verification")
        with st.form("login_container_form"):
            passcode_attempt = st.text_input("Enter Passcode Key:", type="password")
            if st.form_submit_button("Verify Access Keys"):
                if passcode_attempt == ADMIN_PASSCODE:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials entered.")
    else:
        # Layout Header contexts matching image precisely
        st.markdown("<p style='color:#3B82F6; font-weight:700; font-size:12px; margin:0; text-transform:uppercase;'>ADMIN</p>", unsafe_allow_html=True)
        
        t_col, b_col = st.columns([3.5, 2.5])
        with t_col:
            st.markdown("<h1 style='margin-top:0; font-weight:800; font-size:38px; color:#0F172A;'>Dashboard</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748B; margin-top:-10px; font-size:14px;'>Overview of the student directory.</p>", unsafe_allow_html=True)
            
        with b_col:
            st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
            act_1, act_2, act_3 = st.columns([1, 1.2, 1.8])
            with act_2:
                if st.button("🛡️ Admins", use_container_width=True):
                    st.toast("System status clearance verified.")
            with act_3:
                if st.button("➕ Manage students", type="primary", use_container_width=True):
                    st.session_state.show_add_form = not st.session_state.show_add_form
                    st.rerun()

        all_students = get_all_students()
        
        # Pull layout analytic tracking states
        total_st = len(all_students)
        total_houses = len(set(info['house'] for info in all_students.values())) if total_st > 0 else 0
        total_tracks = len(set(info['track'] for info in all_students.values())) if total_st > 0 else 0
        total_paid_30d = total_st

        # Metrics cards block row grid
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="👥 Students", value=total_st)
            st.markdown("</div>", unsafe_allow_html=True)
        with m2:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="🏠 Houses", value=total_houses)
            st.markdown("</div>", unsafe_allow_html=True)
        with m3:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="🔖 Tracks / Positions", value=total_tracks)
            st.markdown("</div>", unsafe_allow_html=True)
        with m4:
            st.markdown("<div style='background:#ffffff; padding:20px; border:1px solid #E2E8F0; border-radius:12px;'>", unsafe_allow_html=True)
            st.metric(label="📅 Added (30D)", value=total_paid_30d)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Dropdown sub-panel form for record creation
        if st.session_state.show_add_form:
            st.markdown("<div style='background:#F8FAFC; padding:25px; border-radius:12px; border:1px dashed #CBD5E1;'>", unsafe_allow_html=True)
            st.subheader("Write New Student Profile")
            with st.form("input_form_panel", clear_on_submit=True):
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    i_id = st.text_input("Unique Student ID:").strip().upper()
                    i_name = st.text_input("Full Name:")
                    i_class = st.selectbox("Form level:", ["Form 1", "Form 2", "Form 3"])
                with f_c2:
                    i_track = st.selectbox("Academic Track:", ["General Science", "General Arts", "Business", "Home Economics"])
                    i_house = st.text_input("Dormitory House Name:")
                    i_status = st.selectbox("Payment State:", ["Paid", "Pending"])
                    
                if st.form_submit_button("Commit Changes To Database", use_container_width=True):
                    if not i_id or not i_name or not i_house:
                        st.error("Fields cannot be left blank.")
                    else:
                        if add_student(i_id, i_name, i_class, i_track, i_house, i_status):
                            st.success(f"Successfully recorded data profile for {i_name}.")
                            st.session_state.show_add_form = False
                            st.rerun()
                        else:
                            st.error("Unique key registration collision: This ID already exists.")
            st.markdown("</div><br>", unsafe_allow_html=True)

        # Split Card container block display area
        left_panel, right_panel = st.columns([1.2, 2.0])
        
        with left_panel:
            st.markdown("<div style='background:#ffffff; padding:24px; border:1px solid #E2E8F0; border-radius:12px; min-height:320px;'>", unsafe_allow_html=True)
            st.markdown("<div style='display:flex; justify-content:space-between;'><b style='font-size:16px; color:#0F172A;'>By house</b><span style='color:#64748B; font-size:12px;'>Total</span></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:12px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
            if not all_students:
                st.markdown("<p style='color:#64748B; font-size:14px;'>No data yet.</p>", unsafe_allow_html=True)
            else:
                house_metrics = {}
                for item in all_students.values():
                    house_metrics[item['house']] = house_metrics.get(item['house'], 0) + 1
                for house, total in house_metrics.items():
                    st.markdown(f"🏠 **{house}:** {total} student(s)")
            st.markdown("</div>", unsafe_allow_html=True)

        with right_panel:
            st.markdown("<div style='background:#ffffff; padding:24px; border:1px solid #E2E8F0; border-radius:12px; min-height:320px;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size:16px; color:#0F172A;'>Recently added</b>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:12px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
            if not all_students:
                st.markdown("<div style='text-align:center; padding:40px 0; color:#64748B;'>No students yet.</div>", unsafe_allow_html=True)
                if st.button("➕ Add the first one", type="primary"):
                    st.session_state.show_add_form = True
                    st.rerun()
            else:
                for current_id, info in all_students.items():
                    r1, r2, r3, r4 = st.columns([1.5, 3.5, 2.5, 1.5])
                    r1.text(current_id)
                    r2.markdown(f"**{info['name']}** \n`{info['class']} - {info['house']}`")
                    
                    status_choices = ["Paid", "Pending"]
                    idx = status_choices.index(info['status'])
                    updated_st = r3.selectbox("Status Update", status_choices, index=idx, key=f"tbl_st_{current_id}", label_visibility="collapsed")
                    if updated_st != info['status']:
                        update_student_status(current_id, updated_st)
                        st.rerun()
                        
                    if r4.button("🗑️", key=f"tbl_del_{current_id}", help="Delete Entry"):
                        delete_student(current_id)
                        st.rerun()
                    st.markdown("<div style='border-bottom:1px solid #F1F5F9; margin:6px 0;'></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
