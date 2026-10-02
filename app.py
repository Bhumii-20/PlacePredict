# ============================================================
# PlacePredict
# Machine Learning Based Student Placement Prediction
# and Career Guidance System
# ============================================================

import os
import base64
import inspect
import sqlite3
import hashlib
import secrets
from urllib.parse import quote_plus

import streamlit as st

from prediction import predict_placement
from company_matching import get_company_recommendations
from career_guidance import get_career_recommendation
from skill_gap import analyze_skill_gap
from database import create_table, save_student


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PlacePredict",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

create_table()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKGROUND_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "backgrounds"
)


# ============================================================
# LOGIN / USER AUTHENTICATION
# ============================================================

AUTH_DB = os.path.join(
    BASE_DIR,
    "placepredict_users.db"
)


def init_auth_database():
    """Create the local user table used by PlacePredict login."""

    connection = sqlite3.connect(AUTH_DB)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def hash_password(password):
    """Hash a password with a random salt."""

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120000
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(password, stored_hash):
    """Verify a password against its stored salted hash."""

    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120000
        )

        return secrets.compare_digest(
            actual_hash,
            expected_hash
        )

    except Exception:

        return False


def register_user(full_name, email, password):
    """Create a new user account."""

    email = email.strip().lower()
    full_name = full_name.strip()

    if not full_name or not email or not password:
        return False, "All fields are required."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    connection = sqlite3.connect(AUTH_DB)

    try:

        connection.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                full_name,
                email,
                hash_password(password)
            )
        )

        connection.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:

        return False, "An account with this email already exists."

    finally:

        connection.close()


def authenticate_user(email, password):
    """Return the user when login credentials are valid."""

    email = email.strip().lower()

    connection = sqlite3.connect(AUTH_DB)

    row = connection.execute(
        """
        SELECT id, full_name, email, password_hash
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    if not verify_password(
        password,
        row[3]
    ):
        return None

    return {
        "id": row[0],
        "full_name": row[1],
        "email": row[2]
    }


def show_login_page():
    """Display login/register screen and return True when authenticated."""

    if st.session_state.get(
        "authenticated",
        False
    ):
        return True


    st.markdown(
        """
        <style>
        .stApp {
            background: #f8fafc !important;
            color: #111827 !important;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #f8fafc !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Login / Create Account selector */
        [data-testid="stRadio"] {
            background: #ffffff !important;
            border: 1px solid #dbe3ef !important;
            border-radius: 14px !important;
            padding: 8px 10px !important;
            margin: 0 0 20px 0 !important;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06) !important;
        }

        [data-testid="stRadio"] label {
            color: #111827 !important;
            font-weight: 800 !important;
        }

        [data-testid="stRadio"] p {
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            font-weight: 700 !important;
        }

        [data-testid="stRadio"] div[role="radiogroup"] {
            gap: 8px !important;
            align-items: center !important;
        }

        [data-testid="stRadio"] div[role="radio"] {
            min-height: 42px !important;
            padding: 8px 16px !important;
            border-radius: 10px !important;
            color: #111827 !important;
        }

        [data-testid="stRadio"] div[role="radio"] p {
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
        }

        [data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
            background: #eff6ff !important;
            border: 1px solid #93c5fd !important;
        }

        [data-testid="stRadio"] div[role="radio"][aria-checked="true"] p {
            color: #1d4ed8 !important;
            -webkit-text-fill-color: #1d4ed8 !important;
            font-weight: 800 !important;
        }

        [data-testid="stRadio"] svg {
            color: #2563eb !important;
            fill: #2563eb !important;
        }

        [data-testid="stTextInput"] input {
            background: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d1d5db !important;
        }

        [data-testid="stTextInput"] label {
            color: #374151 !important;
        }

        [data-testid="stFormSubmitButton"] button {
            background: #2563eb !important;
            color: #ffffff !important;
            border: none !important;
        }
        [data-baseweb="tab-highlight"] {
            background: #2563eb !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="max-width:900px; margin:40px auto 22px auto; text-align:center;">
            <div style="font-size:58px; margin-bottom:8px;">🎓</div>
            <div style="font-size:13px; font-weight:800; letter-spacing:2px; color:#64748b; text-transform:uppercase;">Student Career Intelligence Platform</div>
            <h1 style="font-size:42px; margin:8px 0 8px 0; color:#111827; font-weight:900;">PlacePredict</h1>
            <p style="font-size:17px; color:#475569; margin-bottom:20px;">Machine Learning Based Student Placement Prediction & Career Guidance System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="max-width:900px; margin:0 auto 24px auto; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
            <div style="background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px 16px; color:#111827;">🤖 ML Prediction</div>
            <div style="background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px 16px; color:#111827;">🧠 Skill Gap Analysis</div>
            <div style="background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px 16px; color:#111827;">🎥 Skill Academy</div>
            <div style="background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px 16px; color:#111827;">🧭 Career Guidance</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1, 1.5, 1]
    )

    with center:

        selected_tab = st.radio(
            "Account",
            ["Login", "Create Account"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if selected_tab == "Login":

            st.markdown(
                "### Welcome Back"
            )

            with st.form("login_form"):

                login_email = st.text_input(
                    "Email",
                    placeholder="Enter your email"
                )

                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                login_clicked = st.form_submit_button(
                    "Login",
                    use_container_width=True
                )

            if login_clicked:

                user = authenticate_user(
                    login_email,
                    login_password
                )

                if user:

                    st.session_state.authenticated = True
                    st.session_state.logged_in_user = user
                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

        else:
            st.markdown(
                "### Create Your Student Account"
            )

            with st.form("register_form"):

                register_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name"
                )

                register_email = st.text_input(
                    "Email",
                    placeholder="Enter your email"
                )

                register_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="At least 6 characters"
                )

                register_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                register_clicked = st.form_submit_button(
                    "Create Account",
                    use_container_width=True
                )

            if register_clicked:

                if register_password != register_confirm:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    created, message = register_user(
                        register_name,
                        register_email,
                        register_password
                    )

                    if created:

                        st.success(message)
                        st.info(
                            "Your account is ready. "
                            "Open the Login tab to continue."
                        )

                    else:

                        st.error(message)

    st.stop()


init_auth_database()

show_login_page()


# ============================================================
# CAREER BACKGROUND IMAGES
# ============================================================

CAREER_BACKGROUNDS = {

    "Software Development":
        "software.jpg",

    "Data Analytics":
        "data_analytics.jpg",

    "Data Science":
        "data_science.jpg",

    "Machine Learning":
        "machine_learning.jpg",

    "Artificial Intelligence":
        "ai.jpg",

    "Web Development":
        "web_development.jpg",

    "Cyber Security":
        "cybersecurity.jpg",

    "Cloud Computing":
        "cloud.jpg",

    "Business Analytics":
        "business_analytics.jpg",

    "Finance":
        "finance.jpg",

    "Marketing":
        "marketing.jpg",

    "Human Resources":
        "hr.jpg",

    "Fashion & Design":
        "fashion.jpg",

    "Architecture":
        "architecture.jpg",

    "Graphic Design":
        "graphic_design.jpg",

    "UI/UX Design":
        "uiux.jpg",

    "Media & Journalism":
        "media.jpg",

    "Healthcare":
        "healthcare.jpg",

    "Education":
        "education.jpg",

    "Hospitality & Tourism":
        "hospitality.jpg"
}


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

DEFAULT_VALUES = {

    "student_name": "",

    "email": "",

    "education_category":
        "Engineering",

    "score_type":
        "CGPA",

    "cgpa_input": "",

    "percentage_input": "",

    "tenth_input": "",

    "twelfth_input": "",

    "stream":
        "Computer Science",

    "current_year":
        "Third Year",

    "backlogs_input": "",

    "technical_skills": "",

    "programming_languages": "",

    "projects_input": "",

    "internships_input": "",

    "certifications_input": "",

    "aptitude_input": "",

    "communication_input": "",

    "preferred_career":
        "Software Development",

    "preferred_location": ""
}


for key, value in DEFAULT_VALUES.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# APPLICATION STATE
# ============================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_skill_result" not in st.session_state:
    st.session_state.last_skill_result = None

if "assessment_count" not in st.session_state:
    st.session_state.assessment_count = 0


# ============================================================
# GET BACKGROUND IMAGE
# ============================================================

def get_background_image(career):

    filename = CAREER_BACKGROUNDS.get(
        career
    )

    if not filename:

        return None

    image_path = os.path.join(
        BACKGROUND_DIR,
        filename
    )

    if not os.path.isfile(image_path):

        return None

    return image_path


# ============================================================
# SET CAREER BACKGROUND
# ============================================================

def set_career_background(career):

    image_path = get_background_image(
        career
    )

    if image_path is None:

        return

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            image_data = image_file.read()


        encoded_image = (
            base64.b64encode(
                image_data
            ).decode()
        )


        extension = os.path.splitext(
            image_path
        )[1].lower()


        if extension == ".png":

            mime_type = "image/png"

        elif extension == ".webp":

            mime_type = "image/webp"

        elif extension == ".gif":

            mime_type = "image/gif"

        else:

            mime_type = "image/jpeg"


        st.markdown(
            f"""
            <style>

            html,
            body,
            [data-testid="stAppViewContainer"],
            [data-testid="stApp"] {{

                background:
                    transparent !important;
            }}


            [data-testid="stAppViewContainer"]::before {{

                content: "";

                position: fixed;

                top: 0;
                left: 0;

                width: 100vw;
                height: 100vh;

                background-image:

                    linear-gradient(
                        rgba(255,255,255,0.94),
                        rgba(255,255,255,0.94)
                    ),

                    url(
                        "data:{mime_type};base64,{encoded_image}"
                    );

                background-size: cover;

                background-position: center;

                background-repeat: no-repeat;

                background-attachment: fixed;

                z-index: 0;

                pointer-events: none;
            }}


            [data-testid="stAppViewContainer"] > .main {{

                position: relative;

                z-index: 1;

                background:
                    transparent !important;
            }}


            [data-testid="stMain"] {{

                position: relative;

                z-index: 1;

                background:
                    transparent !important;
            }}

            </style>
            """,
            unsafe_allow_html=True
        )

    except Exception:

        pass


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       APP
    ======================================================== */

    .stApp {

        background:
            #f8fafc !important;

        color:
            #111827 !important;
    }


    [data-testid="stAppViewContainer"] {

        background:
            transparent !important;
    }


    [data-testid="stMain"] {

        background:
            #f8fafc !important;
    }


    [data-testid="stHeader"] {

        background:
            transparent !important;
    }


    .main .block-container {

        max-width:
            1200px;

        padding-top:
            35px;

        padding-bottom:
            70px;
    }


    /* ========================================================
       TITLE
    ======================================================== */

    .main-title {

        text-align:
            center;

        font-size:
            44px;

        font-weight:
            900;

        color:
            #111827 !important;

        text-shadow:
            0 2px 5px
            rgba(255,255,255,0.95);

        margin-bottom:
            8px;
    }


    .subtitle {

        text-align:
            center;

        font-size:
            17px;

        font-weight:
            700;

        color:
            #374151 !important;

        text-shadow:
            0 2px 5px
            rgba(255,255,255,0.95);

        margin-bottom:
            35px;
    }


    /* ========================================================
       SECTION TITLES
    ======================================================== */

    .section-title {

        font-size:
            26px;

        font-weight:
            850;

        color:
            #111827 !important;

        text-shadow:
            0 2px 5px
            rgba(255,255,255,0.95);

        margin-top:
            30px;

        margin-bottom:
            20px;
    }


    /* ========================================================
       LABELS
    ======================================================== */

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {

        color:
            #111827 !important;

        font-weight:
            800 !important;
    }


    [data-testid="stMarkdownContainer"] p {

        color:
            #111827 !important;

        font-weight:
            600;
    }


    /* ========================================================
       TEXT INPUT
       DARK BOX
    ======================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="input"] > div {

        background:
            #ffffff !important;

        background-color:
            #ffffff !important;

        border:
            1.5px solid #4b5563 !important;

        border-radius:
            10px !important;

        opacity:
            1 !important;
    }


    div[data-baseweb="input"] input {

        background:
            #ffffff !important;

        background-color:
            #ffffff !important;

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;

        caret-color:
            #111827 !important;

        font-size:
            16px !important;

        font-weight:
            600 !important;

        opacity:
            1 !important;
    }


    div[data-baseweb="input"]
    input::placeholder {

        color:
            #94a3b8 !important;

        -webkit-text-fill-color:
            #94a3b8 !important;

        opacity:
            1 !important;
    }


    /* ========================================================
       TEXT AREA
       DARK BOX + WHITE TEXT
    ======================================================== */

    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="textarea"] > div > div,
    div[data-baseweb="textarea"] > div > div > div {

        background:
            #ffffff !important;

        background-color:
            #ffffff !important;

        border:
            1.5px solid #4b5563 !important;

        border-radius:
            10px !important;

        opacity:
            1 !important;
    }


    div[data-baseweb="textarea"] textarea,
    textarea {

        background:
            #ffffff !important;

        background-color:
            #ffffff !important;

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;

        caret-color:
            #111827 !important;

        font-size:
            16px !important;

        font-weight:
            600 !important;

        line-height:
            1.5 !important;

        border:
            none !important;

        outline:
            none !important;

        box-shadow:
            none !important;

        opacity:
            1 !important;
    }


    div[data-baseweb="textarea"]
    textarea::placeholder,
    textarea::placeholder {

        color:
            #94a3b8 !important;

        -webkit-text-fill-color:
            #94a3b8 !important;

        opacity:
            1 !important;
    }


    /* ========================================================
       SELECTBOX
       DARK BOX + WHITE TEXT
    ======================================================== */

    div[data-baseweb="select"] {

        background:
            #ffffff !important;

        color:
            #111827 !important;
    }


    div[data-baseweb="select"] > div {

        background:
            #ffffff !important;

        background-color:
            #ffffff !important;

        border:
            1.5px solid #4b5563 !important;

        border-radius:
            10px !important;

        color:
            #111827 !important;
    }


    div[data-baseweb="select"] * {

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;
    }


    div[data-baseweb="select"] input {

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;

        background:
            #ffffff !important;
    }


    /* ========================================================
       DROPDOWN
    ======================================================== */

    div[role="listbox"] {

        background:
            #ffffff !important;
    }


    div[role="option"] {

        background:
            #ffffff !important;

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;
    }


    div[role="option"]:hover {

        background:
            #eff6ff !important;

        color:
            #1d4ed8 !important;

        -webkit-text-fill-color:
            #1d4ed8 !important;
    }

    div[role="listbox"] * {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    div[role="option"]:hover * {
        color: #1d4ed8 !important;
        -webkit-text-fill-color: #1d4ed8 !important;
    }


    /* ========================================================
       RADIO
    ======================================================== */

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p {

        color:
            #111827 !important;

        font-weight:
            700 !important;
    }


    /* ========================================================
       FORM
    ======================================================== */

    [data-testid="stForm"] {

        background:
            rgba(255,255,255,0.08) !important;

        border:
            none !important;
    }


    /* ========================================================
       FORM SUBMIT BUTTON
    ======================================================== */

    [data-testid="stFormSubmitButton"] button {

        width:
            100% !important;

        min-height:
            58px !important;

        background:
            #6d28d9 !important;

        color:
            #ffffff !important;

        border:
            none !important;

        border-radius:
            12px !important;

        font-size:
            18px !important;

        font-weight:
            850 !important;

        box-shadow:
            0 7px 20px
            rgba(109,40,217,0.30) !important;
    }


    [data-testid="stFormSubmitButton"] button:hover {

        background:
            #5b21b6 !important;

        color:
            #ffffff !important;
    }


    [data-testid="stFormSubmitButton"] button p {

        color:
            #ffffff !important;
    }


    /* ========================================================
       METRICS
    ======================================================== */

    [data-testid="stMetric"] {

        background:
            rgba(255,255,255,0.97) !important;

        border:
            1px solid #d1d5db !important;

        border-radius:
            15px !important;

        padding:
            18px !important;

        box-shadow:
            0 5px 18px
            rgba(0,0,0,0.10) !important;
    }


    [data-testid="stMetricLabel"] {

        color:
            #374151 !important;

        font-weight:
            700 !important;
    }


    [data-testid="stMetricValue"] {

        color:
            #111827 !important;

        font-weight:
            900 !important;
    }


    /* ========================================================
       RESULT CARDS
    ======================================================== */

    .skill-card {

        background:
            rgba(255,255,255,0.96);

        border:
            1px solid #d1d5db;

        border-radius:
            12px;

        padding:
            14px 18px;

        margin:
            8px 0;

        color:
            #111827 !important;

        box-shadow:
            0 4px 14px
            rgba(0,0,0,0.08);
    }


    .skill-card strong {
        color: #111827 !important;
    }

    .company-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #111827 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }

    .company-icon {
        font-size: 23px;
        line-height: 1;
    }

    .company-name {
        color: #111827 !important;
        font-size: 17px;
        font-weight: 800;
    }


    /* ========================================================
       LOGIN / AUTHENTICATION
    ======================================================== */

    .auth-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #d1d5db;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    }


    /* ========================================================
       ALERTS
    ======================================================== */

    [data-testid="stAlert"] {

        border-radius:
            12px !important;
    }


    [data-testid="stAlert"] p {

        color:
            #111827 !important;
    }




    /* ========================================================
       PROFESSIONAL PROJECT SHELL
    ======================================================== */

    [data-testid="stSidebar"] {
        background: #f8fafc !important;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }

    [data-testid="stButton"] button {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(15,23,42,0.06) !important;
    }

    [data-testid="stButton"] button:hover {
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        border-color: #93c5fd !important;
    }

    [data-testid="stButton"] button p {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.06) !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: #eff6ff !important;
        border-color: #bfdbfe !important;
        color: #1d4ed8 !important;
    }

    .sidebar-brand {
        padding: 18px 8px 24px 8px;
        border-bottom: 1px solid rgba(255,255,255,0.12);
        margin-bottom: 18px;
    }

    .sidebar-brand-title {
        font-size: 24px;
        font-weight: 900;
    }

    .sidebar-brand-subtitle {
        font-size: 12px;
        color: #cbd5e1 !important;
        margin-top: 5px;
        line-height: 1.5;
    }

    .dashboard-hero {
        background: linear-gradient(135deg, #ffffff 0%, #eff6ff 55%, #dbeafe 100%);
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 22px;
        color: white !important;
        box-shadow: 0 14px 35px rgba(15,23,42,0.18);
    }

    .dashboard-hero h1, .dashboard-hero p { color: #111827 !important; }
    .dashboard-hero h1 { font-size: 34px; margin: 0 0 8px 0; font-weight: 900; }
    .dashboard-hero p { margin: 0; font-size: 16px; opacity: 0.9; }

    .module-card {
        background: rgba(255,255,255,0.98);
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        min-height: 145px;
        box-shadow: 0 8px 24px rgba(15,23,42,0.07);
        margin-bottom: 16px;
    }

    .module-icon { font-size: 28px; margin-bottom: 10px; }
    .module-title { font-weight: 850; font-size: 17px; color: #111827 !important; margin-bottom: 7px; }
    .module-text { color: #6b7280 !important; font-size: 13px; line-height: 1.55; }

    .stat-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        min-height: 92px;
        box-shadow: 0 7px 20px rgba(15,23,42,0.06);
    }

    .stat-label { color: #6b7280 !important; font-size: 11px; text-transform: uppercase; letter-spacing: 0.7px; font-weight: 750; }
    .stat-value { color: #111827 !important; font-size: 24px; font-weight: 900; margin-top: 4px; }

    .learning-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 7px 20px rgba(15,23,42,0.06);
    }

    .learning-title { color: #111827 !important; font-size: 18px; font-weight: 850; }
    .learning-meta { color: #6b7280 !important; font-size: 13px; margin-top: 4px; }
    .page-kicker { color: #64748b !important; font-size: 12px; text-transform: uppercase; letter-spacing: 1.4px; font-weight: 800; margin-bottom: 4px; }
    .page-heading { color: #111827 !important; font-size: 30px; font-weight: 900; margin-bottom: 8px; }
    .page-description { color: #64748b !important; margin-bottom: 22px; }
    
    /* Skill Improvement Videos - Light Theme */

    .section-title {
        color: #111827 !important;
        font-size: 22px !important;
        font-weight: 850 !important;
        margin-top: 24px !important;
        margin-bottom: 18px !important;
    }

    [data-testid="stVideo"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 16px !important;
        padding: 10px !important;
        margin-top: 10px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 7px 20px rgba(15, 23, 42, 0.06) !important;
    }

    [data-testid="stVideo"] video {
        background: #ffffff !important;
        border-radius: 12px !important;
    }

    [data-testid="stVideo"] > div {
        background: #ffffff !important;
    }

    [data-testid="stLinkButton"] a {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    [data-testid="stLinkButton"] a:hover {
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        border-color: #93c5fd !important;
    }

</style>
    
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROFESSIONAL PROJECT NAVIGATION
# ============================================================

VIDEO_RESOURCES_APP = {
    "python": {"title": "Python for Beginners", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
    "sql": {"title": "SQL Tutorial - Full Database Course", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
    "machine learning": {"title": "Machine Learning Course for Beginners", "url": "https://www.youtube.com/watch?v=NWONeJKn6kc"},
    "html": {"title": "Learn HTML & CSS - Full Course for Beginners", "url": "https://www.youtube.com/watch?v=a_iQb1lnAEQ"},
    "css": {"title": "Learn HTML & CSS - Full Course for Beginners", "url": "https://www.youtube.com/watch?v=a_iQb1lnAEQ"}
}


def get_weak_skills():
    result = st.session_state.get("last_skill_result") or {}
    priority = result.get("priority_skills", [])
    if priority:
        output = []
        for item in priority:
            name = item.get("skill", "") if isinstance(item, dict) else str(item)
            if name:
                output.append(name)
        return output
    return [str(x) for x in result.get("missing_skills", []) if x]


def get_video_resource(skill):
    text_value = str(skill).lower().strip()
    for keyword, resource in VIDEO_RESOURCES_APP.items():
        if keyword in text_value:
            return resource
    return None


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">🎓 PlacePredict</div>
            <div class="sidebar-brand-subtitle">ML-powered placement readiness & career development platform</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    user = st.session_state.get("logged_in_user") or {}
    if user:
        st.sidebar.caption(f"Signed in as {user.get('full_name', 'Student')}")
    pages = [("🏠", "Dashboard"), ("📝", "Assessment"), ("🎥", "Skill Academy"), ("🧭", "Career Roadmap"), ("👤", "My Profile")]
    for icon, page_name in pages:
        if st.sidebar.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.logged_in_user = None
        st.session_state.current_page = "Dashboard"
        st.rerun()


def render_dashboard():
    user = st.session_state.get("logged_in_user") or {}
    result = st.session_state.get("last_result")
    skill_result = st.session_state.get("last_skill_result") or {}
    name = user.get("full_name", "Student")
    st.markdown("<div class='page-kicker'>Student Career Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="dashboard-hero">
            <h1>Welcome back, {name} 👋</h1>
            <p>Turn your academic profile into a structured placement preparation plan using Machine Learning, skill-gap analysis, career guidance and learning resources.</p>
        </div>
    """, unsafe_allow_html=True)
    if result:
        probability = result.get("placement_probability", 0)
        readiness = result.get("readiness", "Not available")
        career = result.get("career", "Not selected")
        coverage = skill_result.get("skill_coverage", 0)
    else:
        probability = 0
        readiness = "Not assessed"
        career = st.session_state.get("preferred_career", "Not selected")
        coverage = 0
    cols = st.columns(4)
    metrics = [("Placement Probability", f"{probability:.1f}%"), ("Readiness", readiness), ("Skill Coverage", f"{coverage:.1f}%"), ("Career Target", career)]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>{label}</div><div class='stat-value'>{value}</div></div>", unsafe_allow_html=True)
    st.markdown("### 🚀 Project Modules")
    modules = [
        ("🤖", "ML Placement Prediction", "Predict placement readiness from academic, technical and communication features."),
        ("🧠", "AI Skill Gap Analysis", "Compare your current skills with the requirements of your target career."),
        ("🎥", "Skill Academy", "Get learning videos and resources targeted at your identified skill gaps."),
        ("🏢", "Company Matching", "Explore company and role recommendations generated from your profile."),
        ("🧭", "Career Roadmap", "Understand suitable roles, important skills and certifications for your target field."),
        ("📊", "Student Analytics", "Review placement probability, readiness and skill coverage in one dashboard.")
    ]
    cols = st.columns(3)
    for i, (icon, title, description) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"<div class='module-card'><div class='module-icon'>{icon}</div><div class='module-title'>{title}</div><div class='module-text'>{description}</div></div>", unsafe_allow_html=True)
    st.markdown("### 📌 What to do next")
    if not result:
        st.info("Start your first assessment to generate your personalized placement and career report.")
        if st.button("📝 Start Placement Assessment", use_container_width=True):
            st.session_state.current_page = "Assessment"
            st.rerun()
    else:
        weak = get_weak_skills()
        if weak:
            st.warning(f"Your latest assessment identified {len(weak)} skill(s) to improve: " + ", ".join(weak[:5]) + ("..." if len(weak) > 5 else ""))
            if st.button("🎥 Open Skill Academy", use_container_width=True):
                st.session_state.current_page = "Skill Academy"
                st.rerun()
        else:
            st.success("Your latest assessment did not identify a major skill gap.")


def render_skill_academy():
    st.markdown("<div class='page-kicker'>Personalized Learning</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-heading'>🎥 Skill Academy</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-description'>Learning resources are generated from the weak skills identified by your latest assessment.</div>", unsafe_allow_html=True)
    weak_skills = get_weak_skills()
    if not weak_skills:
        st.info("Complete a placement assessment first. Your identified skill gaps will appear here.")
        if st.button("📝 Go to Assessment", use_container_width=True):
            st.session_state.current_page = "Assessment"
            st.rerun()
        return
    coverage = int((st.session_state.get("last_skill_result") or {}).get("skill_coverage", 0))
    st.write(f"**Current career skill coverage: {coverage}%**")
    st.progress(coverage)
    for skill in weak_skills:
        resource = get_video_resource(skill)
        st.markdown(f"<div class='learning-card'><div class='learning-title'>📚 Improve: {skill}</div><div class='learning-meta'>This skill was identified as a development area in your latest assessment.</div></div>", unsafe_allow_html=True)
        if resource:
            st.video(resource["url"])
            st.caption(resource["title"])
        else:
            search_url = "https://www.youtube.com/results?search_query=" + quote_plus(f"{skill} tutorial for beginners")
            st.link_button(f"🔎 Find {skill} learning videos", search_url, use_container_width=True)
        st.divider()


def render_career_roadmap():
    latest_result = st.session_state.get("last_result") or {}
    career = latest_result.get(
        "career",
        st.session_state.get("preferred_career", "Software Development")
    )
    st.markdown("<div class='page-kicker'>Career Planning</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-heading'>🧭 {career} Roadmap</div>", unsafe_allow_html=True)
    try:
        function = get_career_recommendation
        parameters = inspect.signature(function).parameters
        kwargs = {}
        if "preferred_career" in parameters:
            kwargs["preferred_career"] = career
        elif "career" in parameters:
            kwargs["career"] = career
        elif "field" in parameters:
            kwargs["field"] = career
        guidance = function(**kwargs)
        if isinstance(guidance, dict):
            roles = guidance.get("roles") or guidance.get("recommended_roles") or []
            skills = guidance.get("required_skills") or guidance.get("skills") or []
            certifications = guidance.get("certifications") or guidance.get("recommended_certifications") or []
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 💼 Suitable Roles")
                for role in roles: st.write(f"• {role}")
            with c2:
                st.markdown("### 🛠️ Core Skills")
                for skill in skills: st.write(f"• {skill}")
            with c3:
                st.markdown("### 📜 Certifications")
                for cert in certifications: st.write(f"• {cert}")
        else:
            st.write(guidance)
    except Exception:
        st.info("Career roadmap details could not be loaded from the current career guidance module.")
    st.markdown("### 🗺️ Suggested Preparation Sequence")
    roadmap = [("01", "Build fundamentals", "Learn the core concepts required for your selected career."), ("02", "Practice skills", "Solve exercises and practical tasks to strengthen fundamentals."), ("03", "Build projects", "Create portfolio projects that demonstrate your ability to apply skills."), ("04", "Earn credentials", "Complete relevant certifications where they add value."), ("05", "Prepare for recruitment", "Practice aptitude, communication, technical interviews and resume presentation.")]
    for number, title, description in roadmap:
        st.markdown(f"**{number} · {title}**  \n{description}")
        st.divider()


def render_profile():
    user = st.session_state.get("logged_in_user") or {}
    result = st.session_state.get("last_result")

    # Use the career from the latest completed assessment.
    if result:
        current_career = result.get(
            "career",
            st.session_state.get("preferred_career", "Not selected")
        )
    else:
        current_career = st.session_state.get(
            "preferred_career", "Not selected"
        )

    # Back to Dashboard button
    if st.button("← Back to Dashboard", key="profile_back_dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    quick1, quick2, quick3 = st.columns(3)
    with quick1:
        if st.button("🏠 Dashboard", key="profile_dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    with quick2:
        if st.button("📝 New Assessment", key="profile_assessment", use_container_width=True):
            st.session_state.current_page = "Assessment"
            st.rerun()
    with quick3:
        if st.button("🧭 Career Roadmap", key="profile_roadmap", use_container_width=True):
            st.session_state.current_page = "Career Roadmap"
            st.rerun()

    st.markdown(
        "<div class='page-kicker'>Account</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='page-heading'>👤 My Profile</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Personal Information")
        st.write(f"**Name:** {user.get('full_name', 'Student')}")
        st.write(f"**Email:** {user.get('email', 'Not available')}")

    with c2:
        st.markdown("### Current Career Target")
        st.write(f"**Career:** {current_career}")
        st.write(
            f"**Location:** "
            f"{st.session_state.get('preferred_location') or 'Not specified'}"
        )

    st.markdown("### 📊 Latest Assessment")

    if result:
        a, b, c = st.columns(3)

        a.metric(
            "Placement Probability",
            f"{result.get('placement_probability', 0):.1f}%"
        )

        b.metric(
            "Readiness",
            result.get("readiness", "Not available")
        )

        c.metric(
            "Assessment Runs",
            st.session_state.get("assessment_count", 0)
        )

        st.markdown("### 🎯 Latest Assessment Career")
        st.info(
            f"Your latest assessment career target is **{current_career}**."
        )

    else:
        st.info("No assessment has been completed in this session yet.")

    
current_page = st.session_state.get("current_page", "Dashboard")

# Show sidebar on every page except My Profile
if current_page != "My Profile":
    render_sidebar()

if current_page == "Dashboard":

    render_dashboard()

    st.stop()

if current_page == "Skill Academy":

    render_skill_academy()

    st.stop()

if current_page == "Career Roadmap":

    render_career_roadmap()

    st.stop()

if current_page == "My Profile":

    render_profile()

    st.stop()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    "<div class='page-kicker'>Placement Intelligence Workspace</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="main-title">
        📝 Placement Assessment
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Machine Learning Based Student Placement Prediction
        and Career Guidance System
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CURRENT ACCOUNT
# ============================================================

# ============================================================
# LOGGED-IN USER
# ============================================================

logged_in_user = st.session_state.get(
    "logged_in_user",
    {}
)

if logged_in_user:

    st.caption(
        f"Logged in as: {logged_in_user.get('full_name', '')} "
        f"({logged_in_user.get('email', '')})"
    )


# ============================================================
# CAREER PREFERENCE FRAGMENT
#
# IMPORTANT:
# This section is separate from the student form.
#
# Changing career only reruns this fragment.
# It does NOT rerun the complete app.
#
# Therefore unfinished student form values are not lost.
# ============================================================

@st.fragment
def career_preferences():

    st.markdown(
        """
        <div class="section-title">
            🎯 Career Preferences
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.selectbox(
            "Preferred Career Field",
            list(
                CAREER_BACKGROUNDS.keys()
            ),
            key="preferred_career"
        )


    with col2:

        st.text_input(
            "Preferred Job Location",
            placeholder="Example: Pune",
            key="preferred_location"
        )


    # --------------------------------------------------------
    # Update background immediately
    # --------------------------------------------------------

    set_career_background(
        st.session_state.preferred_career
    )


career_preferences()


# ============================================================
# STUDENT INFORMATION FORM
#
# EVERYTHING BELOW IS INSIDE ONE FORM.
#
# This prevents reruns while entering student information.
# ============================================================

with st.form(
    "student_information_form",
    clear_on_submit=False,
    enter_to_submit=False
):


    # ========================================================
    # STUDENT PROFILE
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            👤 Student Profile
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.text_input(
            "Student Name",
            placeholder="Enter your full name",
            key="student_name"
        )


        st.text_input(
            "Email",
            placeholder="Enter your email",
            key="email"
        )


        st.selectbox(
            "Education Category",
            [
                "Engineering",
                "Science",
                "Commerce",
                "Arts",
                "Management",
                "Design",
                "Architecture",
                "Computer Applications",
                "Other"
            ],
            key="education_category"
        )


    with col2:

        st.radio(
            "Academic Score Type",
            [
                "CGPA",
                "Percentage"
            ],
            horizontal=True,
            key="score_type"
        )


        if st.session_state.score_type == "CGPA":

            st.text_input(
                "CGPA",
                placeholder="Example: 8.2",
                key="cgpa_input"
            )

        else:

            st.text_input(
                "Percentage",
                placeholder="Example: 82",
                key="percentage_input"
            )


        st.text_input(
            "10th Percentage",
            placeholder="Example: 85",
            key="tenth_input"
        )


    # ========================================================
    # EDUCATION DETAILS
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            🎓 Education Details
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.selectbox(
            "Stream / Course",
            [
                "Computer Science",
                "Information Technology",
                "Electronics",
                "Mechanical",
                "Civil",
                "Electrical",
                "Data Science",
                "Artificial Intelligence",
                "Commerce",
                "Business Administration",
                "Fashion Design",
                "Interior Design",
                "Architecture",
                "Graphic Design",
                "Media & Journalism",
                "Other"
            ],
            key="stream"
        )


        st.selectbox(
            "Current Year",
            [
                "First Year",
                "Second Year",
                "Third Year",
                "Fourth Year",
                "Final Year"
            ],
            key="current_year"
        )


    with col2:

        st.text_input(
            "12th Percentage",
            placeholder="Example: 90",
            key="twelfth_input"
        )


        st.text_input(
            "Number of Backlogs",
            placeholder="Example: 0",
            key="backlogs_input"
        )


    # ========================================================
    # SKILLS & EXPERIENCE
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            💻 Skills & Experience
        </div>
        """,
        unsafe_allow_html=True
    )


    st.text_area(
        "Technical Skills",
        placeholder=(
            "Example: Python, SQL, Pandas, "
            "Machine Learning"
        ),
        height=100,
        key="technical_skills"
    )


    st.text_area(
        "Programming Languages / Design Tools",
        placeholder=(
            "Example: Python, Java, C++ "
            "or Fashion CAD, Illustrator"
        ),
        height=100,
        key="programming_languages"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.text_input(
            "Number of Projects",
            placeholder="Example: 3",
            key="projects_input"
        )


    with col2:

        st.text_input(
            "Number of Internships",
            placeholder="Example: 1",
            key="internships_input"
        )


    with col3:

        st.text_input(
            "Number of Certifications",
            placeholder="Example: 4",
            key="certifications_input"
        )


    # ========================================================
    # ASSESSMENT SCORES
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            📊 Assessment Scores
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.text_input(
            "Aptitude Score",
            placeholder="Example: 75",
            key="aptitude_input"
        )


    with col2:

        st.text_input(
            "Communication Score",
            placeholder="Example: 80",
            key="communication_input"
        )


    # ========================================================
    # PREDICT BUTTON
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    predict_button = st.form_submit_button(
        "🚀 Predict My Placement",
        type="primary",
        use_container_width=True
    )


# ============================================================
# PREDICTION
# ============================================================

if predict_button:

    try:

        # ====================================================
        # BASIC VALIDATION
        # ====================================================

        if not st.session_state.student_name.strip():

            st.error(
                "Please enter the student's name."
            )

            st.stop()


        if not st.session_state.email.strip():

            st.error(
                "Please enter the student's email."
            )

            st.stop()


        # ====================================================
        # NUMERIC INPUTS
        # ====================================================

        try:

            tenth_percentage = float(
                st.session_state.tenth_input
            )

            twelfth_percentage = float(
                st.session_state.twelfth_input
            )

            backlogs = int(
                st.session_state.backlogs_input
            )

            projects = int(
                st.session_state.projects_input
            )

            internships = int(
                st.session_state.internships_input
            )

            certifications = int(
                st.session_state.certifications_input
            )

            aptitude_score = float(
                st.session_state.aptitude_input
            )

            communication_score = float(
                st.session_state.communication_input
            )

        except ValueError:

            st.error(
                "Please enter valid numbers in all "
                "academic, experience and score fields."
            )

            st.stop()


        # ====================================================
        # CGPA / PERCENTAGE
        # ====================================================

        if st.session_state.score_type == "CGPA":

            try:

                cgpa = float(
                    st.session_state.cgpa_input
                )

            except ValueError:

                st.error(
                    "Please enter a valid CGPA."
                )

                st.stop()

        else:

            try:

                percentage = float(
                    st.session_state.percentage_input
                )

                cgpa = percentage / 9.5

            except ValueError:

                st.error(
                    "Please enter a valid percentage."
                )

                st.stop()


        # ====================================================
        # RANGE CHECKS
        # ====================================================

        if not 0 <= cgpa <= 10:

            st.error(
                "CGPA must be between 0 and 10."
            )

            st.stop()


        if not 0 <= tenth_percentage <= 100:

            st.error(
                "10th percentage must be between 0 and 100."
            )

            st.stop()


        if not 0 <= twelfth_percentage <= 100:

            st.error(
                "12th percentage must be between 0 and 100."
            )

            st.stop()


        if backlogs < 0:

            st.error(
                "Backlogs cannot be negative."
            )

            st.stop()


        if projects < 0:

            st.error(
                "Projects cannot be negative."
            )

            st.stop()


        if internships < 0:

            st.error(
                "Internships cannot be negative."
            )

            st.stop()


        if certifications < 0:

            st.error(
                "Certifications cannot be negative."
            )

            st.stop()


        if not 0 <= aptitude_score <= 100:

            st.error(
                "Aptitude score must be between 0 and 100."
            )

            st.stop()


        if not 0 <= communication_score <= 100:

            st.error(
                "Communication score must be between 0 and 100."
            )

            st.stop()


        # ====================================================
        # MACHINE LEARNING PREDICTION
        # ====================================================

        with st.spinner(
            "Analyzing your profile using Machine Learning..."
        ):

            prediction, probability = predict_placement(

                cgpa=cgpa,

                tenth_percentage=tenth_percentage,

                twelfth_percentage=twelfth_percentage,

                backlogs=backlogs,

                technical_skills=
                    st.session_state.technical_skills,

                programming_languages=
                    st.session_state.programming_languages,

                projects=projects,

                internships=internships,

                certifications=certifications,

                aptitude_score=aptitude_score,

                communication_score=communication_score,

                stream=
                    st.session_state.stream,

                year=
                    st.session_state.current_year
            )


        # ====================================================
        # RESULT
        # ====================================================

        placement_probability = (
            probability * 100
        )


        if placement_probability >= 75:

            readiness = "Highly Ready"

        elif placement_probability >= 50:

            readiness = "Moderately Ready"

        else:

            readiness = "Needs Improvement"


        # Store the latest assessment for the project dashboard.
        st.session_state.last_result = {
            "placement_probability": placement_probability,
            "readiness": readiness,
            "career": st.session_state.preferred_career,
            "prediction": int(prediction)
        }

        st.session_state.assessment_count += 1


        # ====================================================
        # SAVE TO DATABASE
        # ====================================================

        student_record = {

            "name":
                st.session_state.student_name,

            "email":
                st.session_state.email,

            "education_category":
                st.session_state.education_category,

            "stream":
                st.session_state.stream,

            "current_year":
                st.session_state.current_year,

            "cgpa":
                cgpa,

            "tenth_percentage":
                tenth_percentage,

            "twelfth_percentage":
                twelfth_percentage,

            "backlogs":
                backlogs,

            "technical_skills":
                st.session_state.technical_skills,

            "programming_languages":
                st.session_state.programming_languages,

            "projects":
                projects,

            "internships":
                internships,

            "certifications":
                certifications,

            "aptitude_score":
                aptitude_score,

            "communication_score":
                communication_score,

            "preferred_career":
                st.session_state.preferred_career,

            "preferred_location":
                st.session_state.preferred_location,

            "placement_probability":
                placement_probability,

            "readiness_level":
                readiness
        }


        try:

            save_student(
                student_record
            )

            st.success(
                "✅ Student details saved successfully!"
            )

        except Exception as save_error:

            st.error(
                "Student prediction was generated, "
                "but the details could not be saved."
            )

            st.code(
                str(save_error)
            )


        # ====================================================
        # RESULT TITLE
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                📊 Placement Prediction Result
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # METRICS
        # ====================================================

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Placement Probability",
                f"{placement_probability:.1f}%"
            )


        with col2:

            st.metric(
                "Readiness Level",
                readiness
            )


        with col3:

            st.metric(
                "Career Field",
                st.session_state.preferred_career
            )


        # ====================================================
        # PLACEMENT STATUS
        # ====================================================

        if prediction == 1:

            st.success(
                "✅ The Machine Learning model predicts "
                "a positive placement outcome."
            )

        else:

            st.warning(
                "⚠️ The Machine Learning model predicts "
                "that additional preparation is recommended."
            )


        # ====================================================
        # PROFILE SUMMARY
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                👤 Profile Summary
            </div>
            """,
            unsafe_allow_html=True
        )


        col1, col2 = st.columns(2)


        with col1:

            st.write(
                f"**Student:** "
                f"{st.session_state.student_name}"
            )

            st.write(
                f"**Education:** "
                f"{st.session_state.education_category}"
            )

            st.write(
                f"**Stream:** "
                f"{st.session_state.stream}"
            )

            st.write(
                f"**Current Year:** "
                f"{st.session_state.current_year}"
            )

            st.write(
                f"**CGPA:** "
                f"{cgpa:.2f}"
            )


        with col2:

            st.write(
                f"**Projects:** "
                f"{projects}"
            )

            st.write(
                f"**Internships:** "
                f"{internships}"
            )

            st.write(
                f"**Certifications:** "
                f"{certifications}"
            )

            st.write(
                f"**Backlogs:** "
                f"{backlogs}"
            )

            st.write(
                f"**Preferred Career:** "
                f"{st.session_state.preferred_career}"
            )

            st.write(
                f"**Preferred Location:** "
                f"{st.session_state.preferred_location or 'Not specified'}"
            )


        # ====================================================
        # RECOMMENDED COMPANIES
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                🏢 Recommended Companies
            </div>
            """,
            unsafe_allow_html=True
        )


        try:

            function = (
                get_company_recommendations
            )

            parameters = inspect.signature(
                function
            ).parameters

            kwargs = {}


            if "preferred_career" in parameters:

                kwargs[
                    "preferred_career"
                ] = (
                    st.session_state.preferred_career
                )

            elif "career" in parameters:

                kwargs[
                    "career"
                ] = (
                    st.session_state.preferred_career
                )

            elif "field" in parameters:

                kwargs[
                    "field"
                ] = (
                    st.session_state.preferred_career
                )


            if "preferred_location" in parameters:

                kwargs[
                    "preferred_location"
                ] = (
                    st.session_state.preferred_location
                )

            elif "location" in parameters:

                kwargs[
                    "location"
                ] = (
                    st.session_state.preferred_location
                )

            elif "job_location" in parameters:

                kwargs[
                    "job_location"
                ] = (
                    st.session_state.preferred_location
                )


            companies = function(
                **kwargs
            )


            if companies:

                for company in companies:

                    if isinstance(
                        company,
                        dict
                    ):

                        company_name = (

                            company.get(
                                "company"
                            )

                            or company.get(
                                "name"
                            )

                            or company.get(
                                "company_name"
                            )

                            or "Recommended Company"
                        )

                    else:

                        company_name = str(
                            company
                        )


                    st.markdown(
                        f"""
                        <div class="company-card">
                            <span class="company-icon">🏢</span>
                            <span class="company-name">{company_name}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.info(
                    "No company recommendations found "
                    "for this career and location."
                )


        except Exception:

            st.info(
                "Company recommendations could not be loaded."
            )


        # ====================================================
        # CAREER GUIDANCE
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                🎯 Career Guidance
            </div>
            """,
            unsafe_allow_html=True
        )


        try:

            function = (
                get_career_recommendation
            )

            parameters = inspect.signature(
                function
            ).parameters

            kwargs = {}


            if "preferred_career" in parameters:

                kwargs[
                    "preferred_career"
                ] = (
                    st.session_state.preferred_career
                )

            elif "career" in parameters:

                kwargs[
                    "career"
                ] = (
                    st.session_state.preferred_career
                )

            elif "field" in parameters:

                kwargs[
                    "field"
                ] = (
                    st.session_state.preferred_career
                )


            guidance = function(
                **kwargs
            )


            if isinstance(
                guidance,
                dict
            ):

                roles = (

                    guidance.get(
                        "roles"
                    )

                    or guidance.get(
                        "recommended_roles"
                    )

                    or []
                )


                skills = (

                    guidance.get(
                        "required_skills"
                    )

                    or guidance.get(
                        "skills"
                    )

                    or []
                )


                certifications_list = (

                    guidance.get(
                        "certifications"
                    )

                    or guidance.get(
                        "recommended_certifications"
                    )

                    or []
                )


                if roles:

                    st.write(
                        "#### 💼 Suitable Roles"
                    )

                    for role in roles:

                        st.write(
                            f"• {role}"
                        )


                if skills:

                    st.write(
                        "#### 🛠️ Important Skills"
                    )

                    for skill in skills:

                        st.write(
                            f"• {skill}"
                        )


                if certifications_list:

                    st.write(
                        "#### 📜 Recommended Certifications"
                    )

                    for certification in (
                        certifications_list
                    ):

                        st.write(
                            f"• {certification}"
                        )


            else:

                st.write(
                    guidance
                )


        except Exception:

            st.info(
                "Career guidance could not be loaded."
            )


        # ====================================================
        # SKILL GAP ANALYSIS
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                🧠 AI Skill Gap Analysis
            </div>
            """,
            unsafe_allow_html=True
        )


        skill_result = analyze_skill_gap(

            preferred_career=
                st.session_state.preferred_career,

            technical_skills=
                st.session_state.technical_skills,

            programming_languages=
                st.session_state.programming_languages
        )

        st.session_state.last_skill_result = skill_result


        skill_coverage = skill_result[
            "skill_coverage"
        ]


        st.write(
            f"**Career Skill Coverage: "
            f"{skill_coverage:.1f}%**"
        )


        st.progress(
            int(skill_coverage)
        )


        # ====================================================
        # MATCHED SKILLS
        # ====================================================

        st.write(
            "#### ✅ Matched Skills"
        )


        matched_skills = skill_result[
            "matched_skills"
        ]


        if matched_skills:

            for skill in matched_skills:

                st.markdown(
                    f"""
                    <div class="skill-card">

                        ✅ {skill}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No required career skills were matched."
            )


        # ====================================================
        # SKILLS TO DEVELOP
        # ====================================================

        st.write(
            "#### ⚠️ Skills to Develop"
        )


        priority_skills = skill_result.get(
            "priority_skills",
            []
        )

        if not priority_skills:
            missing_skills = skill_result.get(
                "missing_skills",
                []
            )
            priority_skills = [
                {
                    "skill": skill,
                    "priority": "HIGH"
                }
                for skill in missing_skills
            ]


        if priority_skills:

            for item in priority_skills:

                if isinstance(item, dict):
                    skill = item.get(
                        "skill",
                        "Unknown Skill"
                    )
                    priority = item.get(
                        "priority",
                        "HIGH"
                    )
                else:
                    skill = str(item)
                    priority = "HIGH"


                if priority == "HIGH":

                    icon = "🔴"

                elif priority == "MEDIUM":

                    icon = "🟠"

                else:

                    icon = "🟢"


                st.markdown(
                    f"{icon} **{skill}**\n\nPriority: **{priority}**"
                )

        else:

            st.success(
                "🎉 No major skill gaps were detected."
            )




        # ====================================================
        # SKILL IMPROVEMENT VIDEOS
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                🎥 Skill Improvement Videos
            </div>
            """,
            unsafe_allow_html=True
        )


        # Curated educational videos.
        # The fallback opens a YouTube search for the exact weak skill.
        VIDEO_RESOURCES = {

            "python": {
                "title": "Python for Beginners",
                "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"
            },

            "sql": {
                "title": "SQL Tutorial - Full Database Course",
                "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"
            },

            "machine learning": {
                "title": "Machine Learning Course for Beginners",
                "url": "https://www.youtube.com/watch?v=NWONeJKn6kc"
            },

            "html": {
                "title": "Learn HTML & CSS - Full Course for Beginners",
                "url": "https://www.youtube.com/watch?v=a_iQb1lnAEQ"
            },

            "css": {
                "title": "Learn HTML & CSS - Full Course for Beginners",
                "url": "https://www.youtube.com/watch?v=a_iQb1lnAEQ"
            }
        }


        def find_video_for_skill(skill_name):

            skill_text = str(
                skill_name
            ).lower().strip()

            for keyword, resource in VIDEO_RESOURCES.items():

                if keyword in skill_text:
                    return resource

            return None


        shown_video_skills = set()

        if priority_skills:

            for item in priority_skills:

                if isinstance(item, dict):
                    weak_skill = item.get(
                        "skill",
                        ""
                    )
                else:
                    weak_skill = str(item)

                if not weak_skill:
                    continue

                normalized_skill = weak_skill.lower().strip()

                if normalized_skill in shown_video_skills:
                    continue

                shown_video_skills.add(
                    normalized_skill
                )

                resource = find_video_for_skill(
                    weak_skill
                )

                st.markdown(
                    f"#### 📚 Improve: {weak_skill}"
                )

                if resource:

                    st.write(
                        resource["title"]
                    )

                    st.video(
                        resource["url"]
                    )

                else:

                    search_url = (
                        "https://www.youtube.com/results?search_query="
                        + quote_plus(
                            f"{weak_skill} tutorial for beginners"
                        )
                    )

                    st.info(
                        "A curated video is not stored for this "
                        "skill yet. Use the button below to find "
                        "beginner-friendly learning videos for it."
                    )

                    st.link_button(
                        "🔎 Find learning videos",
                        search_url,
                        use_container_width=True
                    )

        else:

            st.success(
                "🎉 No weak skills were detected, so no skill "
                "improvement videos are required."
            )


        # ====================================================
        # PREPARATION FOCUS
        # ====================================================

        st.markdown(
            """
            <div class="section-title">
                🚀 Preparation Focus
            </div>
            """,
            unsafe_allow_html=True
        )


        if skill_coverage < 40:

            message = (

                "Your first priority should be building "
                "the fundamental skills required for "

                f"{st.session_state.preferred_career}."
            )


        elif skill_coverage < 70:

            message = (

                "You have a basic foundation. Focus on "
                "the missing skills and build practical "
                "projects."
            )


        elif skill_coverage < 90:

            message = (

                "Your skill coverage is strong. Focus on "
                "advanced skills, projects, internships "
                "and interviews."
            )


        else:

            message = (

                "Your skill coverage is excellent. Focus "
                "on interview preparation and real-world "
                "experience."
            )


        st.info(
            message
        )


    except Exception as error:

        st.error(
            "Something went wrong while generating "
            "the prediction."
        )

        st.code(
            str(error)
        )



















