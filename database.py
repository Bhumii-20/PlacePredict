import sqlite3
import os


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_FOLDER = os.path.join(
    BASE_DIR,
    "database"
)

DB_PATH = os.path.join(
    DB_FOLDER,
    "placepredict.db"
)


# ============================================================
# CREATE TABLE
# ============================================================

def create_table():

    os.makedirs(
        DB_FOLDER,
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# SAVE STUDENT
# ============================================================

def save_student(data):

    create_table()

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (

            name,
            email,
            education_category,
            stream,
            current_year,
            cgpa,
            tenth_percentage,
            twelfth_percentage,
            backlogs,
            technical_skills,
            programming_languages,
            projects,
            internships,
            certifications,
            aptitude_score,
            communication_score,
            preferred_career,
            preferred_location,
            placement_probability,
            readiness_level

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        data["name"],

        data["email"],

        data["education_category"],

        data["stream"],

        data["current_year"],

        data["cgpa"],

        data["tenth_percentage"],

        data["twelfth_percentage"],

        data["backlogs"],

        data["technical_skills"],

        data["programming_languages"],

        data["projects"],

        data["internships"],

        data["certifications"],

        data["aptitude_score"],

        data["communication_score"],

        data["preferred_career"],

        data["preferred_location"],

        data["placement_probability"],

        data["readiness_level"]
    ))

    conn.commit()

    conn.close()

    return True