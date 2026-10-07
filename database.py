import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def _is_postgres():
    return bool(DATABASE_URL)


def _connect():
    """Use Render/PostgreSQL in the cloud and SQLite locally."""
    if _is_postgres():
        import psycopg2
        return psycopg2.connect(DATABASE_URL), True

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_folder = os.path.join(base_dir, "database")
    os.makedirs(db_folder, exist_ok=True)
    db_path = os.path.join(db_folder, "placepredict.db")
    return sqlite3.connect(db_path), False


def create_table():
    conn, postgres = _connect()
    cursor = conn.cursor()

    if postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                education_category TEXT,
                stream TEXT,
                current_year TEXT,
                cgpa DOUBLE PRECISION,
                tenth_percentage DOUBLE PRECISION,
                twelfth_percentage DOUBLE PRECISION,
                backlogs INTEGER,
                technical_skills TEXT,
                programming_languages TEXT,
                projects INTEGER,
                internships INTEGER,
                certifications INTEGER,
                aptitude_score DOUBLE PRECISION,
                communication_score DOUBLE PRECISION,
                preferred_career TEXT,
                preferred_location TEXT,
                placement_probability DOUBLE PRECISION,
                readiness_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                education_category TEXT,
                stream TEXT,
                current_year TEXT,
                cgpa REAL,
                tenth_percentage REAL,
                twelfth_percentage REAL,
                backlogs INTEGER,
                technical_skills TEXT,
                programming_languages TEXT,
                projects INTEGER,
                internships INTEGER,
                certifications INTEGER,
                aptitude_score REAL,
                communication_score REAL,
                preferred_career TEXT,
                preferred_location TEXT,
                placement_probability REAL,
                readiness_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    conn.close()


def save_student(data):
    create_table()
    conn, postgres = _connect()
    cursor = conn.cursor()
    placeholder = "%s" if postgres else "?"
    placeholders = ", ".join([placeholder] * 20)

    cursor.execute(f"""
        INSERT INTO students (
            name, email, education_category, stream, current_year,
            cgpa, tenth_percentage, twelfth_percentage, backlogs,
            technical_skills, programming_languages, projects, internships,
            certifications, aptitude_score, communication_score,
            preferred_career, preferred_location, placement_probability,
            readiness_level
        ) VALUES ({placeholders})
    """, (
        data["name"], data["email"], data["education_category"],
        data["stream"], data["current_year"], data["cgpa"],
        data["tenth_percentage"], data["twelfth_percentage"],
        data["backlogs"], data["technical_skills"],
        data["programming_languages"], data["projects"],
        data["internships"], data["certifications"],
        data["aptitude_score"], data["communication_score"],
        data["preferred_career"], data["preferred_location"],
        data["placement_probability"], data["readiness_level"]
    ))

    conn.commit()
    conn.close()
    return True
