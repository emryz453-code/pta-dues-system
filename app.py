import sqlite3
import streamlit as st

# Set up page configurations with school name
st.set_page_config(page_title="Adventist Senior High - PTA Portal", page_icon="💳", layout="centered")

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
    # Insert default data if table is completely empty
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

# Initialize database
init_db()

# Helper database functions
def get_student(student_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, class, status FROM students WHERE id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "class": result[1], "status": result[2]}
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


# Set your secure admin passcode here
ADMIN_PASSCODE = "secure123"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation Menu")
user_role = st.sidebar.radio("Select Portal:", ["Student Dashboard", "Admin Dashboard"])

# --- STUDENT DASHBOARD ---
if user_role == "Student Dashboard":
    st.title("🎓 Adventist Senior High")
    st.subheader("PTA Dues Verification Portal")
    st.write("Enter your unique Student ID below to verify your payment status.")
    
    search_id = st.text_input("Enter Student ID:", placeholder="e.g., STU001").strip().upper()
    
    if search_id:
        student = get_student(search_id)
        if student:
            st.success(f"Record found for **{student['name']}**")
            
            # Display colored status blocks
            if student['status'] == "Paid":
                st.info("🟢 **Payment Status:** Fully Paid")
            else:
                st.warning("🟡 **Payment Status:** Pending / Unpaid")
                
            # Clean summary display
            st.markdown(f"""
            * **Student ID:** {search_id}
            * **Class:** {student['class']}
            """)
        else:
            st.error("No record found for this Student ID. Please double-check or visit the administration office.")

# --- ADMIN DASHBOARD ---
elif user_role == "Admin Dashboard":
    st.title("⚙️ Adventist Senior High Portal")
    st.subheader("PTA Administration Management")
    
    # Secure Lock check
    entered_passcode = st.text_input("Enter Admin Passcode to login:", type="password")
    
    if entered_passcode == ADMIN_PASSCODE:
        st.success("Access Granted.")
        
        # Form to add a new student
        st.subheader("➕ Add New Student Record")
        with st.form("add_student_form", clear_on_submit=True):
            stu_id = st.text_input("Unique Student ID:").strip().upper()
            stu_name = st.text_input("Student Full Name:")
            stu_class = st.text_input("Class / Form:")
            stu_status = st.selectbox("Payment Status:", ["Paid", "Pending"])
            
            submit_button = st.form_submit_button("Save Student Record")
            
            if submit_button:
                if not stu_id or not stu_name or not stu_class:
                    st.error("All fields are required to register a student.")
                else:
                    success = add_student(stu_id, stu_name, stu_class, stu_status)
                    if success:
                        st.success(f"Successfully added {stu_name} to the system!")
                        st.rerun()
                    else:
                        st.error(f"Error: A student with ID {stu_id} already exists.")

        st.markdown("---")
        
        # Displaying and Managing current data
        st.subheader("📋 Registered Students & Payment Records")
        all_students = get_all_students()
        
        if not all_students:
            st.write("No students registered yet.")
        else:
            # Table Header layout
            col1, col2, col3, col4 = st.columns([1.5, 2.5, 2, 1.5])
            col1.markdown("**ID**")
            col2.markdown("**Name**")
            col3.markdown("**Status**")
            col4.markdown("**Action**")
            
            # Generate individual row control for management
            for current_id, info in all_students.items():
                c1, c2, c3, c4 = st.columns([1.5, 2.5, 2, 1.5])
                c1.text(current_id)
                c2.text(info['name'])
                
                # Interactive status dropdown to update status live
                status_list = ["Paid", "Pending"]
                current_idx = status_list.index(info['status'])
                new_status = c3.selectbox(
                    "Update Status", status_list, index=current_idx, key=f"status_{current_id}", label_visibility="collapsed"
                )
                
                if new_status != info['status']:
                    update_student_status(current_id, new_status)
                    st.rerun()
                
                # Quick Delete button
                if c4.button("🗑️ Delete", key=f"del_{current_id}"):
                    delete_student(current_id)
                    st.rerun()
                    
    elif entered_passcode != "":
        st.error("Incorrect passcode. Access denied.")
