import sqlite3
import streamlit as st

# Set up clean page configurations
st.set_page_config(page_title="Adventist Senior High - PTA Portal", page_icon="💳", layout="wide")

# --- DATABASE SETUP ---
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


ADMIN_PASSCODE = "secure123"

# Initialize logged_in state if it doesn't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🏫 Portal Menu")
user_role = st.sidebar.radio("Select View:", ["Student Dashboard", "Admin Dashboard"])

# If the user switches back to the Student view, reset admin login status for safety
if user_role == "Student Dashboard":
    st.session_state.logged_in = False

# --- STUDENT DASHBOARD ---
if user_role == "Student Dashboard":
    st.title("🎓 Adventist Senior High")
    st.subheader("PTA Dues Verification Portal")
    st.write("Enter your Full Name below to verify your payment status.")
    
    search_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Kwame Mensah").strip()
    
    if search_name:
        student = get_student_by_name(search_name)
        if student:
            st.success(f"Record found for **{student['name']}**")
            if student['status'] == "Paid":
                st.info("🟢 **Payment Status:** Fully Paid")
            else:
                st.warning("🟡 **Payment Status:** Pending / Unpaid")
                
            st.markdown(f"""
            * **Student ID:** {student['id']}
            * **Class:** {student['class']}
            """)
        else:
            st.error("No record found matching this name. Please check your spelling or contact administration.")

# --- MODERN ADMIN DASHBOARD ---
elif user_role == "Admin Dashboard":
    # Screen 1: Login Screen (Only shows if NOT logged in)
    if not st.session_state.logged_in:
        st.title("⚙️ PTA Administration Gateway")
        st.markdown("##### Adventist Senior High Management Portal")
        
        with st.form("login_form"):
            entered_passcode = st.text_input("Enter Admin Passcode to login:", type="password")
            login_submitted = st.form_submit_button("Access Dashboard")
            
            if login_submitted:
                if entered_passcode == ADMIN_PASSCODE:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Incorrect passcode. Access denied.")

    # Screen 2: The Actual Dashboard (Only shows AFTER successful login)
    else:
        # Header area with a logout button
        h_col1, h_col2 = st.columns([5, 1])
        with h_col1:
            st.title("⚙️ PTA Administration Hub")
            st.markdown("##### Welcome Back, Administrator")
        with h_col2:
            st.markdown(" ")
            if st.button("🔒 Log Out"):
                st.session_state.logged_in = False
                st.rerun()
                
        all_students = get_all_students()
        
        # --- APP METRICS BLOCK ---
        total_count = len(all_students)
        paid_count = sum(1 for info in all_students.values() if info['status'] == "Paid")
        pending_count = total_count - paid_count
        
        st.markdown("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Registered", total_count)
        m_col2.metric("Fully Paid", paid_count, delta=f"{paid_count/max(total_count,1)*100:.1f}% Total")
        m_col3.metric("Pending Balance", pending_count)
        st.markdown("---")
        
        # --- TABBED LAYOUT ---
        tab1, tab2 = st.tabs(["📋 Student Records", "➕ Register New Student"])
        
        with tab1:
            st.subheader("Active Student Directory")
            if not all_students:
                st.info("No students registered yet.")
            else:
                col1, col2, col3, col4 = st.columns([1.5, 3.0, 2.0, 1.5])
                col1.markdown("**ID**")
                col2.markdown("**Full Name**")
                col3.markdown("**Dues Status**")
                col4.markdown("**Actions**")
                st.markdown(" ")
                
                for current_id, info in all_students.items():
                    c1, c2, c3, c4 = st.columns([1.5, 3.0, 2.0, 1.5])
                    c1.text(current_id)
                    c2.text(info['name'])
                    
                    status_list = ["Paid", "Pending"]
                    current_idx = status_list.index(info['status'])
                    new_status = c3.selectbox(
                        "Update Status", status_list, index=current_idx, key=f"status_{current_id}", label_visibility="collapsed"
                    )
                    
                    if new_status != info['status']:
                        update_student_status(current_id, new_status)
                        st.rerun()
                    
                    if c4.button("🗑️ Remove", key=f"del_{current_id}"):
                        delete_student(current_id)
                        st.rerun()
                        
        with tab2:
            st.subheader("Add Student Information")
            with st.form("add_student_form", clear_on_submit=True):
                stu_id = st.text_input("Unique Student ID:").strip().upper()
                stu_name = st.text_input("Student Full Name:")
                stu_class = st.text_input("Class / Form:")
                stu_status = st.selectbox("Current Status:", ["Paid", "Pending"])
                
                submit_button = st.form_submit_button("Save Student to Database")
                
                if submit_button:
                    if not stu_id or not stu_name or not stu_class:
                        st.error("All input fields are required.")
                    else:
                        success = add_student(stu_id, stu_name, stu_class, stu_status)
                        if success:
                            st.success(f"Successfully added {stu_name}!")
                            st.rerun()
                        else:
                            st.error(f"Error: A student with ID {stu_id} already exists.")
