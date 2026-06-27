import sqlite3
import streamlit as st

# --- PAGE SETUP & THEME INITIALIZATION ---
st.set_page_config(
    page_title="Adventist Senior High - PTA Portal", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
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
            status TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO students (id, name, class, status) VALUES (?, ?, ?, ?)
        """, [
            ("STU001", "Kwame Mensah", "Form 3A", "Paid"),
            ("STU002", "Ama Serwaa", "Form 2B", "Pending")
        ])
    conn.commit()
    conn.close()

init_db()

def get_student_by_name(full_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, status FROM students WHERE LOWER(name) = LOWER(?)", (full_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "name": result[1], "class": result[2], "status": result[3]}
    return None

def get_all_students():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, class, status FROM students")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"name": row[1], "class": row[2], "status": row[3]} for row in rows}

def add_student(id, name, cls, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (id, name, class, status) VALUES (?, ?, ?, ?)", (id, name, cls, status))
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

ADMIN_PASSCODE = "secure123"

# --- GLOBAL CUSTOM NAVBAR COMPONENT ---
st.markdown("""
    <style>
    .navbar {
        background-color: skyblue;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow:0 0 6px 0 black;
    }
    .navbar-title {
        color: white !important;
        font-size: 24px !important;
        font-weight: bold;
        margin: 0;
    }
    </style>
    <div class="navbar">
        <div class="navbar-title"> Adventist Senior High School</div>
    </div>
""", unsafe_allow_html=True)


# --- ROUTING LOGIC BASED ON USER NAVIGATION ---

# --- VIEW 1: WELCOME/LANDING PAGE ---
if st.session_state.current_page == "Welcome":
    st.title("Welcome to the PTA Portal")
    st.markdown("### Secure Payment Tracking & Status Verification")
    st.write("Welcome to the official Adventist Senior High PTA portal. This platform allows parents and students to securely check dues balances, while providing administrative functions to authorized staff members.")
    
    st.markdown("---")
    st.write("To get started, access our dedicated portal endpoints directly using the control router below:")
    
    if st.button("Access Portal Selection Screen", use_container_width=True):
        st.session_state.current_page = "Portal Selection"
        st.rerun()


# --- VIEW 2: PORTAL SELECTION INTERFACE ---
elif st.session_state.current_page == "Portal Selection":
    st.subheader("Select Your Destination Portal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 🎓 Student Directory Portal")
        st.write("Verify status live on the network using formal registration credentials.")
        if st.button("Enter Student View", use_container_width=True):
            st.session_state.current_page = "Student Dashboard"
            st.rerun()
            
    with col2:
        st.warning("### ⚙️ Administrative Hub")
        st.write("Secure database controller operations. Requires validation passcode.")
        if st.button("Enter Admin View", use_container_width=True):
            st.session_state.current_page = "Admin Dashboard"
            st.rerun()
            
    st.markdown("---")
    if st.button(" Return to Home Landing Page"):
        st.session_state.current_page = "Welcome"
        st.rerun()


# --- VIEW 3: STUDENT DASHBOARD ---
elif st.session_state.current_page == "Student Dashboard":
    st.title(" Student Verification Dashboard")
    st.write("Enter your Full Name below to check live financial status accounts.")
    
    search_name = st.text_input("Enter Student Full Name:", placeholder="e.g., Kwame Mensah").strip()
    
    if search_name:
        student = get_student_by_name(search_name)
        if student:
            st.success(f"Record matched for system entity: **{student['name']}**")
            if student['status'] == "Paid":
                st.info("🟢 **Payment Ledger Status:** Verified Fully Paid")
            else:
                st.warning("🟡 **Payment Ledger Status:** Account Pending / Balance Unpaid")
                
            st.markdown(f"""
            * **Assigned Unique ID:** {student['id']}
            * **Current Registered Form:** {student['class']}
            """)
        else:
            st.error("No valid system record matches that name configuration. Check spellings or consult administration fields.")
            
    st.markdown("---")
    if st.button(" Switch to Admin View"):
        st.session_state.current_page = "Admin Dashboard"
        st.rerun()
    if st.button(" Back to Selection Screen"):
        st.session_state.current_page = "Portal Selection"
        st.rerun()


# --- VIEW 4: ADMIN DASHBOARD ---
elif st.session_state.current_page == "Admin Dashboard":
    if not st.session_state.logged_in:
        st.title("🔒 Security Access Required")
        st.write("Enter system authorization key to clear network interface access routines.")
        
        with st.form("admin_login_container"):
            entered_passcode = st.text_input("Security Access Passcode:", type="password")
            login_trigger = st.form_submit_button("Verify Passcode Credentials")
            
            if login_trigger:
                if entered_passcode == ADMIN_PASSCODE:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid passcode token entry sequence. Authentication rejected.")
                    
        st.markdown("---")
        if st.button("↩️ Abort & Back to Portal Selection"):
            st.session_state.current_page = "Portal Selection"
            st.rerun()

    else:
        # Dashboard Header Section
        h_col1, h_col2 = st.columns([5, 1])
        with h_col1:
            st.title("⚙️ Core Administration Database Workspace")
            st.markdown("##### Identity Context: Active Root Administrator")
        with h_col2:
            st.markdown(" ")
            if st.button("🔒 Revoke Session (Logout)", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = "Portal Selection"
                st.rerun()
                
        all_students = get_all_students()
        
        # Real-time Visual App Analytics Metrics
        total_count = len(all_students)
        paid_count = sum(1 for info in all_students.values() if info['status'] == "Paid")
        pending_count = total_count - paid_count
        
        st.markdown("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Database Indexes", total_count)
        m_col2.metric("Settled ledgers", paid_count, delta=f"{paid_count/max(total_count,1)*100:.1f}% Total Allocation")
        m_col3.metric("Outstanding Accounts", pending_count)
        st.markdown("---")
        
        # Tabbed Control Structures
        tab1, tab2 = st.tabs(["📋 View Directory Records", "➕ Write New Database Entries"])
        
        with tab1:
            st.subheader("System Data Storage Registry")
            if not all_students:
                st.info("Empty database instances returned.")
            else:
                col1, col2, col3, col4 = st.columns([1.5, 3.0, 2.0, 1.5])
                col1.markdown("**System ID**")
                col2.markdown("**User Entity Name**")
                col3.markdown("**Dues Class State**")
                col4.markdown("**Execution Array**")
                st.markdown(" ")
                
                for current_id, info in all_students.items():
                    c1, c2, c3, c4 = st.columns([1.5, 3.0, 2.0, 1.5])
                    c1.text(current_id)
                    c2.text(info['name'])
                    
                    status_list = ["Paid", "Pending"]
                    current_idx = status_list.index(info['status'])
                    new_status = c3.selectbox(
                        "Modify State", status_list, index=current_idx, key=f"status_{current_id}", label_visibility="collapsed"
                    )
                    
                    if new_status != info['status']:
                        update_student_status(current_id, new_status)
                        st.rerun()
                    
                    if c4.button("🗑️ Drop Row", key=f"del_{current_id}", use_container_width=True):
                        delete_student(current_id)
                        st.rerun()
                        
        with tab2:
            st.subheader("Write Fresh Structural Student Block")
            with st.form("add_student_form", clear_on_submit=True):
                stu_id = st.text_input("New Registration Key (Unique ID):").strip().upper()
                stu_name = st.text_input("Full Legal Name Entry:")
                stu_class = st.text_input("Assigned Class Module / Form:")
                stu_status = st.selectbox("Initial Financial State:", ["Paid", "Pending"])
                
                submit_button = st.form_submit_button("Commit Entry To SQLite Disk Data Store")
                
                if submit_button:
                    if not stu_id or not stu_name or not stu_class:
                        st.error("Structural integrity violation: Null field instances detected.")
                    else:
                        success = add_student(stu_id, stu_name, stu_class, stu_status)
                        if success:
                            st.success(f"Write validation success: Created entry tracking record for {stu_name}!")
                            st.rerun()
                        else:
                            st.error(f"Write violation conflict: Registration key primary index value '{stu_id}' already assigned.")
