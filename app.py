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
