import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(
    page_title="Adventist SHS PTA Portal",
    page_icon="🎓",
    layout="wide"
)

# ---------------- STYLING ---------------- #
st.markdown("""
<style>

.main {
    background-color: #f4f7fc;
}

.header {
    background: white;
    padding:20px;
    border-bottom:3px solid #0B3D91;
    border-radius:10px;
}

.title {
    font-size:40px;
    font-weight:800;
    color:#0B3D91;
}

.subtitle {
    color:gray;
    margin-top:-10px;
}

.card {
    background:white;
    padding:25px;
    border-radius:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    text-align:center;
}

.metric-card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
}

.paid {
    color:green;
    font-weight:bold;
}

.pending {
    color:orange;
    font-weight:bold;
}

.student-panel {
    background:white;
    padding:30px;
    border-radius:20px;
    box-shadow:0px 3px 15px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("pta_records.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id TEXT PRIMARY KEY,
    name TEXT,
    class TEXT,
    track TEXT,
    house TEXT,
    status TEXT
)
""")

conn.commit()

# ---------------- HEADER ---------------- #

st.markdown("""
<div class="header">
    <div class="title">🎓 Adventist SHS</div>
    <div class="subtitle">PTA Payment Portal</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- HOME CARDS ---------------- #

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h2>🎓 Student Dashboard</h2>
        <p>Check your PTA payment status.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h2>⚙️ Admin Dashboard</h2>
        <p>Manage student records.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------- STUDENT SEARCH ---------------- #

st.markdown("""
<div class="student-panel">
<h2>Student Dashboard</h2>
</div>
""", unsafe_allow_html=True)

search = st.text_input(
    "Enter Full Name",
    placeholder="e.g. Ama Serwaa"
)

if st.button("🔍 Search Status", use_container_width=True):

    cursor.execute(
        "SELECT * FROM students WHERE LOWER(name)=LOWER(?)",
        (search,)
    )

    student = cursor.fetchone()

    if student:

        st.success("Student Found")

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Student ID:**", student[0])
            st.write("**Class:**", student[2])
            st.write("**House:**", student[4])

        with c2:
            st.write("**Track:**", student[3])

            if student[5] == "Paid":
                st.markdown(
                    '<p class="paid">🟢 PAID</p>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<p class="pending">🟠 PENDING</p>',
                    unsafe_allow_html=True
                )

    else:
        st.error("No student record found.")

st.divider()

# ---------------- ADMIN DASHBOARD ---------------- #

st.header("⚙️ Admin Dashboard")

cursor.execute("SELECT COUNT(*) FROM students")
total_students = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM students WHERE status='Paid'"
)
paid = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM students WHERE status='Pending'"
)
pending = cursor.fetchone()[0]

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Students", total_students)

with m2:
    st.metric("Paid", paid)

with m3:
    st.metric("Pending", pending)

st.write("")

# ---------------- ADD STUDENT ---------------- #

with st.expander("➕ Add Student"):

    sid = st.text_input("Student ID")
    name = st.text_input("Name")

    c1, c2 = st.columns(2)

    with c1:
        cls = st.selectbox(
            "Class",
            ["Form 1", "Form 2", "Form 3"]
        )

        track = st.selectbox(
            "Track",
            [
                "General Science",
                "Business",
                "General Arts",
                "Home Economics"
            ]
        )

    with c2:
        house = st.text_input("House")

        status = st.selectbox(
            "Status",
            ["Paid", "Pending"]
        )

    if st.button("Save Student"):

        try:
            cursor.execute("""
            INSERT INTO students
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sid,
                name,
                cls,
                track,
                house,
                status
            ))

            conn.commit()

            st.success("Student added successfully.")

        except:
            st.error("Student ID already exists.")

# ---------------- STUDENT TABLE ---------------- #

st.subheader("Student Records")

cursor.execute("SELECT * FROM students")
records = cursor.fetchall()

for row in records:

    c1, c2, c3, c4 = st.columns([2,3,2,2])

    c1.write(row[0])
    c2.write(row[1])

    if row[5] == "Paid":
        c3.success("Paid")
    else:
        c3.warning("Pending")

    if c4.button("Delete", key=row[0]):
        cursor.execute(
            "DELETE FROM students WHERE id=?",
            (row[0],)
        )
        conn.commit()
        st.rerun()

conn.close()
