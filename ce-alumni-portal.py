import io
import os
import re
import csv
import json
import datetime
import pandas as pd
import streamlit as st

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION & BRANDING
# ==============================================================================
st.set_page_config(
    page_title="USJ-R Civil Engineering - Alumni Registry Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Clean White Background, USJ-R Branding & High Contrast Inputs
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Montserrat:wght@700;800;900&display=swap');

    /* Clean Crisp White Main Theme */
    .stApp {
        background-color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Compact Mobile & Desktop Container */
    @media (min-width: 992px) {
        .main .block-container {
            max-width: 880px;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            margin: 0 auto;
        }
    }

    /* Centered Compact Header Card Styling */
    .header-card {
        background: linear-gradient(135deg, #004d25 0%, #006633 60%, #15803d 100%);
        color: white;
        padding: 1.2rem 1.4rem;
        border-radius: 12px;
        text-align: center;
        margin: 0 auto 1.2rem auto;
        max-width: 860px;
        box-shadow: 0 4px 12px rgba(0,77,37,0.2);
        border-bottom: 4px solid #ffcc00;
    }
    .header-card h3 {
        margin: 0;
        font-family: 'Cinzel', serif;
        font-size: 0.92rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.3;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .header-card h2 {
        margin: 0.4rem 0 0.2rem 0;
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffcc00;
        line-height: 1.25;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .header-card h1 {
        margin: 0.3rem 0 0.1rem 0;
        font-family: 'Montserrat', sans-serif;
        font-size: 1.85rem;
        font-weight: 900;
        background: linear-gradient(185deg, #FFFFFF 0%, #FFE259 60%, #FFA751 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        letter-spacing: 2px;
        text-transform: uppercase;
        filter: drop-shadow(0px 2px 5px rgba(0,0,0,0.4));
    }

    /* Section Divider Styling (Clean text, no icons) */
    .section-header {
        color: #004d25;
        font-size: 1.1rem;
        font-weight: 700;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #ffcc00;
        margin-top: 1.1rem;
        margin-bottom: 0.85rem;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background-color: #ffffff;
        border-left: 5px solid #006633;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        border-left-width: 5px;
        margin-bottom: 0.8rem;
    }
    .kpi-title {
        font-size: 0.78rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #004d25;
    }

    /* History & Logbook Cards */
    .history-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #004d25;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
    }
    .history-card h4 {
        margin: 0 0 0.35rem 0;
        color: #004d25;
        font-size: 1.02rem;
        font-weight: 700;
    }
    .history-card p {
        margin: 0.15rem 0;
        font-size: 0.88rem;
        color: #334155;
    }

    /* Form Labels & High Contrast Inputs */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label, .stRadio > label, .stMultiselect > label {
        font-weight: 600 !important;
        color: #0f172a !important;
        font-size: 0.88rem !important;
    }

    /* Custom Warning Card for Deletion */
    .delete-warning-card {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .delete-warning-card h5 {
        color: #991b1b;
        margin: 0 0 0.25rem 0;
        font-weight: 700;
    }
    .delete-warning-card p {
        color: #7f1d1d;
        margin: 0;
        font-size: 0.85rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# FILE PATHS & CSV SCHEMAS
# ==============================================================================
FILE_ALUMNI_INFO = "alumni_information.csv"
FILE_BOARD_EXAM = "board_exam_data.csv"
FILE_TRACER = "alumni_career_tracer.csv"
FILE_GRAD_STUDIES = "graduate_studies_cpd.csv"
FILE_CQI = "cqi_interventions.csv"
FILE_FEEDBACK = "alumni_feedback.csv"

HEADERS_ALUMNI_INFO = [
    "Timestamp", "Registration_ID", "Student_ID", "First_Name", "Middle_Name", "Last_Name",
    "Civil_Status", "Date_Of_Birth", "Email", "Contact_Number", "Messaging_App", "Messaging_Handle",
    "Degree_Program", "Graduation_Year", "Graduation_Term", "Student_Classification",
    "Cumulative_GWA", "Academic_Honors", "Security_PIN", "Is_Latest"
]

HEADERS_BOARD_EXAM = [
    "Timestamp", "Entry_ID", "Student_ID", "Full_Name", "Board_Exam_Date",
    "Examinee_Category", "Perceived_Weakest_Subject", "Review_Center", "Review_Mode",
    "Overall_PRC_Rating", "MST_Rating", "HGE_Rating", "SEC_Rating", "Remarks", "PRC_License_Number"
]

HEADERS_TRACER = [
    "Timestamp", "Tracer_ID", "Student_ID", "Full_Name", "Work_Setup",
    "Employer_Or_Firm_Name", "Position_Or_Role", "Position_Level", "Job_Alignment",
    "Work_Location", "Employment_Type", "Salary_Bracket", "Start_Year", "End_Year",
    "Business_Category", "DTI_SEC_Reg", "Business_Scale", "Years_Operating"
]

HEADERS_GRAD_STUDIES = [
    "Timestamp", "Grad_ID", "Student_ID", "Full_Name", "Graduate_Degree",
    "Degree_Specified_Details", "Specialization_Track", "Institution_Name",
    "Academic_Status", "Year_Conferred"
]

HEADERS_CQI = [
    "Timestamp", "Intervention_ID", "Target_Execution_Date", "Intervention_Category",
    "Target_Cohort_Description", "Action_Taken_Description", "Faculty_In_Charge",
    "Tagged_Student_IDs", "Tagged_Student_Names", "Outcome_Notes"
]

HEADERS_FEEDBACK = [
    "Timestamp", "Feedback_ID", "Student_ID", "Full_Name", "Category",
    "Subject_Title", "Message_Content", "Status"
]

# Helper Function: Initialize CSV Files
def init_file(filename, headers):
    if not os.path.exists(filename):
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    else:
        # Self-healing header check
        try:
            df = pd.read_csv(filename, dtype=str)
            if list(df.columns) != headers:
                for h in headers:
                    if h not in df.columns:
                        df[h] = ""
                df = df[headers]
                df.to_csv(filename, index=False)
        except Exception:
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

init_file(FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO)
init_file(FILE_BOARD_EXAM, HEADERS_BOARD_EXAM)
init_file(FILE_TRACER, HEADERS_TRACER)
init_file(FILE_GRAD_STUDIES, HEADERS_GRAD_STUDIES)
init_file(FILE_CQI, HEADERS_CQI)
init_file(FILE_FEEDBACK, HEADERS_FEEDBACK)

# Helper Function: Load CSV safely
def load_csv_safely(filename, headers):
    init_file(filename, headers)
    try:
        df = pd.read_csv(filename, dtype=str, keep_default_na=False)
        for h in headers:
            if h not in df.columns:
                df[h] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=headers)

# Global Form Options (Declared universally for Student and Admin scopes)
deg_opts = [
    "BS Civil Engineering - Structural Track",
    "BS Civil Engineering - Construction Track",
    "BS Civil Engineering - Geotechnical Track",
    "BS Civil Engineering - Water Resources Track",
    "BS Civil Engineering - Transportation Track",
    "BS Civil Engineering - General Track"
]
yr_opts = [str(y) for y in range(2050, 1969, -1)]
term_opts = ["1st Semester", "2nd Semester", "Summer / Midyear"]
class_opts = ["Regular First-Degree Graduate", "Transferee / Second-Degree Graduate", "Extended Program Graduate"]
hon_opts = ["None", "Summa Cum Laude", "Magna Cum Laude", "Cum Laude", "Departmental Academic Awardee"]
weak_opts = [
    "Mathematics, Surveying & Transportation Engineering (MST)",
    "Hydraulics & Geotechnical Engineering (HGE)",
    "Structural Engineering & Construction (SEC)",
    "Balanced / No Specific Weakness"
]
rev_opts = [
    "Gillesania Engineering Review Center",
    "RIAC Review Center",
    "MegaReview and Tutorial Center",
    "Padilla Review Center",
    "Besavilla Engineering Review Center",
    "USJ-R In-House Refresher Program",
    "Self-Study / Independent Review",
    "Other Review Center"
]
rem_opts = [
    "Passed",
    "Failed / Retaking",
    "Deferred / Did Not Pursue",
    "Scheduled to Take / Upcoming Examinee"
]
setup_opts = [
    "Government / Public Sector Employee",
    "Private / Corporate Employee",
    "Academe / Educational Institution",
    "Overseas / OFW Engineer",
    "Business Owner / Entrepreneur / Independent Consultant"
]
deg_type_opts = [
    "Master's / Doctoral Degree",
    "Professional Accreditation / Specialist Membership",
    "Others / Custom Accreditation"
]
fb_cat_opts = [
    "Curriculum & Coursework Suggestions",
    "Board Exam Review & Refresher Support",
    "Department Facilities & Laboratories",
    "Career, Industry & Job Placement",
    "General Ideas & Administrative Concerns"
]

# Formatting and Helper Functions
def safe_index(options, val, default=None):
    if val is None or pd.isna(val) or str(val).strip() in ("", "N/A", "None", "nan"):
        return default
    val_str = str(val).strip()
    for i, opt in enumerate(options):
        if str(opt).strip() == val_str:
            return i
    for i, opt in enumerate(options):
        if str(opt).strip().lower() == val_str.lower():
            return i
    return default

def fmt_title(val):
    return " ".join([w.capitalize() for w in str(val).strip().split()]) if val else ""

def fmt_upper(val):
    return str(val).strip().upper() if val else ""

def fmt_lower(val):
    return str(val).strip().lower() if val else ""

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "logged_user" not in st.session_state:
    st.session_state["logged_user"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "edit_exam_id" not in st.session_state:
    st.session_state["edit_exam_id"] = None
if "edit_tracer_id" not in st.session_state:
    st.session_state["edit_tracer_id"] = None
if "edit_grad_id" not in st.session_state:
    st.session_state["edit_grad_id"] = None
if "admin_flash_msg" not in st.session_state:
    st.session_state["admin_flash_msg"] = None
if "cqi_flash_msg" not in st.session_state:
    st.session_state["cqi_flash_msg"] = None

# ==============================================================================
# CENTERED HEADER CARD
# ==============================================================================
header_c1, header_c2, header_c3 = st.columns([1, 6, 1])
with header_c2:
    st.markdown("""
        <div class="header-card">
            <h3>University of San Jose - Recoletos</h3>
            <h3>School of Engineering and Architecture</h3>
            <h2>Department of Civil Engineering</h2>
            <h1>ALUMNI REGISTRY HUB</h1>
        </div>
    """, unsafe_allow_html=True)

# Top Bar Sign Out & Session Status
if st.session_state["logged_user"]:
    user_data = st.session_state["logged_user"]
    full_n = f"{user_data.get('First_Name', '')} {user_data.get('Middle_Name', '')} {user_data.get('Last_Name', '')}".strip()
    c_wel, c_out = st.columns([5, 1])
    with c_wel:
        st.success(f"🎓 **Welcome, {full_n}!** | Student ID: `{user_data.get('Student_ID', '')}`")
    with c_out:
        if st.button("🔒 Sign Out", key="btn_signout_top"):
            st.session_state["logged_user"] = None
            st.session_state["is_admin"] = False
            st.rerun()

elif st.session_state["is_admin"]:
    c_wel, c_out = st.columns([5, 1])
    with c_wel:
        st.success("🔓 **Administrator Session Active** | Full Department Access & CQI Management Granted")
    with c_out:
        if st.button("🔒 Sign Out", key="btn_signout_admin_top"):
            st.session_state["logged_user"] = None
            st.session_state["is_admin"] = False
            st.rerun()

# ==============================================================================
# AUTHENTICATION GATEWAY (WHEN UNAUTHENTICATED)
# ==============================================================================
if not st.session_state["logged_user"] and not st.session_state["is_admin"]:
    st.markdown('<div class="section-header">Portal Gateway & Authentication</div>', unsafe_allow_html=True)

    auth_choice = st.radio(
        "Choose an action to proceed:*",
        [
            "CE Alumni Sign-In",
            "First Time Registration (Sign-up)",
            "Administrator Log-in"
        ],
        horizontal=True
    )

    st.divider()

    # --- RETURNING GRADUATE LOGIN ---
    if auth_choice == "CE Alumni Sign-In":
        st.markdown('<div class="section-header">CE Alumni Sign-In</div>', unsafe_allow_html=True)
        st.caption("Enter your 10-Digit Student ID Number or Full Name along with your 4-Digit Security PIN.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            login_identity = st.text_input("Student ID Number or Full Name*", placeholder="e.g., 2020123456 or Juan Dela Cruz")
        with col_s2:
            login_pin = st.text_input("4-Digit Security PIN*", type="password", placeholder="••••", max_chars=4)

        if st.button("Sign In to Portal", key="btn_graduate_login"):
            if not login_identity.strip() or not login_pin.strip():
                st.error("⚠️ Please provide both your Student ID/Full Name and 4-Digit Security PIN.")
            else:
                df_users = load_csv_safely(FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO)
                if df_users.empty:
                    st.error("No registered alumni found. Please complete First Time Registration.")
                else:
                    input_id_raw = login_identity.strip().upper()
                    input_id_clean = re.sub(r"[\s\-]", "", input_id_raw)
                    input_pin_clean = login_pin.strip()

                    match = None
                    for idx, row in df_users.iterrows():
                        sid_raw = str(row.get("Student_ID", "")).strip().upper()
                        sid_clean = re.sub(r"[\s\-]", "", sid_raw)
                        fn = str(row.get("First_Name", "")).strip().upper()
                        ln = str(row.get("Last_Name", "")).strip().upper()
                        full_name_clean = f"{fn} {ln}".strip()
                        pin = str(row.get("Security_PIN", "")).strip()

                        if (input_id_clean == sid_clean or input_id_clean == sid_raw or input_id_raw == full_name_clean or input_id_raw in full_name_clean) and input_pin_clean == pin:
                            match = row.to_dict()

                    if match:
                        st.session_state["logged_user"] = match
                        st.session_state["is_admin"] = False
                        st.success(f"🔓 Welcome back, {match.get('First_Name', '')}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please check your Student ID / Name and Security PIN.")

    # --- FIRST TIME REGISTRATION ---
    elif auth_choice == "First Time Registration (Sign-up)":
        st.markdown('<div class="section-header">First Time Registration</div>', unsafe_allow_html=True)
        st.caption("Create your alumni registry profile to update board exam logs, career tracer records, and graduate studies.")

        st.markdown('<div class="section-header">1. Identity Credentials & Personal Details</div>', unsafe_allow_html=True)

        id_col1, id_col2, id_col3, id_col4, id_col5 = st.columns(5)
        with id_col1:
            r_sid = st.text_input("10-Digit Student ID Number*", placeholder="e.g., 2020123456")
        with id_col2:
            r_pin = st.text_input("4-Digit Security PIN*", type="password", placeholder="••••", max_chars=4)
        with id_col3:
            r_fn = st.text_input("First Name*", placeholder="Juan")
        with id_col4:
            r_mn = st.text_input("Middle Name", placeholder="Santos")
        with id_col5:
            r_ln = st.text_input("Last Name*", placeholder="Dela Cruz")

        c1, c2, c3 = st.columns(3)
        with c1:
            r_civil = st.selectbox("Civil Status*", ["Single", "Married", "Widowed", "Separated"], index=None, placeholder="Select Civil Status...")
            r_dob = st.date_input("Date of Birth*", value=datetime.date(2000, 1, 1), min_value=datetime.date(1950, 1, 1), max_value=datetime.date(2015, 12, 31), format="MM/DD/YYYY")
        with c2:
            r_email = st.text_input("Primary Email Address*", placeholder="juan.delacruz@gmail.com")
            r_mobile = st.text_input("Mobile / Phone Number*", placeholder="09171234567")
        with c3:
            r_msg_app = st.selectbox("Preferred Messaging Channel*", ["Messenger", "Viber", "WhatsApp", "Telegram", "SMS / Direct"], index=None, placeholder="Select Messaging Channel...")
            r_msg_handle = st.text_input("Messaging Account Handle / Number*", placeholder="m.me/juandelacruz or 09171234567")

        st.markdown('<div class="section-header">2. Academic Background & Graduation Details</div>', unsafe_allow_html=True)

        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            r_degree = st.selectbox("Degree Program*", deg_opts, index=None, placeholder="Select Degree Program...")
            r_grad_year = st.selectbox("Graduation Year*", yr_opts, index=None, placeholder="Select Graduation Year...")
        with ac2:
            r_grad_term = st.selectbox("Graduation Term*", term_opts, index=None, placeholder="Select Graduation Term...")
            r_class = st.selectbox("Student Classification*", class_opts, index=None, placeholder="Select Student Classification...")
        with ac3:
            r_gwa = st.text_input("Cumulative GWA (Optional)", placeholder="e.g., 1.45 or 2.10")
            r_honors = st.selectbox("Academic Honors Conferred", hon_opts, index=None, placeholder="Select Academic Honors...")

        if st.button("Complete Registration & Save Profile", key="btn_register_save"):
            missing_fields = []
            clean_sid = re.sub(r"[\s\-]", "", r_sid.strip())
            if not r_sid.strip() or len(clean_sid) != 10 or not clean_sid.isdigit(): missing_fields.append("Valid 10-Digit Student ID Number (must be exactly 10 digits, e.g., 2020123456)")
            if not r_pin.strip() or len(r_pin.strip()) != 4 or not r_pin.strip().isdigit(): missing_fields.append("Valid 4-Digit Security PIN (4 digits)")
            if not r_fn.strip(): missing_fields.append("First Name")
            if not r_ln.strip(): missing_fields.append("Last Name")
            if not r_email.strip(): missing_fields.append("Primary Email Address")
            clean_mob = re.sub(r"[\s\-+()]", "", r_mobile.strip())
            if not r_mobile.strip() or not clean_mob.isdigit(): missing_fields.append("Valid Mobile / Phone Number (numeric only)")
            if r_gwa.strip():
                try: float(r_gwa.strip())
                except ValueError: missing_fields.append("Valid Cumulative GWA (numeric e.g., 1.45 or 2.10)")
            if not r_msg_handle.strip(): missing_fields.append("Messaging Account Handle")

            if missing_fields:
                list_str = "\n".join([f"• {m}" for m in missing_fields])
                st.error(f"⚠️ Please complete the following required fields before completing registration:\n\n{list_str}")
            else:
                sid_std = clean_sid
                df_existing = load_csv_safely(FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO)

                existing_sids = [re.sub(r"[\s\-]", "", str(s).strip().upper()) for s in df_existing["Student_ID"].values] if not df_existing.empty else []
                if not df_existing.empty and sid_std in existing_sids:
                    st.error(f"Student ID `{sid_std}` is already registered in the database. Please sign in as a returning graduate.")
                else:
                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    reg_id = f"REG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

                    new_user_row = [
                        now_str, reg_id, sid_std, fmt_title(r_fn), fmt_title(r_mn), fmt_title(r_ln),
                        r_civil, r_dob.strftime("%m/%d/%Y"), fmt_lower(r_email), r_mobile.strip(), r_msg_app, r_msg_handle.strip(),
                        r_degree, r_grad_year, r_grad_term, r_class,
                        r_gwa.strip(), r_honors, r_pin.strip(), "Yes"
                    ]

                    with open(FILE_ALUMNI_INFO, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(new_user_row)

                    st.session_state["logged_user"] = dict(zip(HEADERS_ALUMNI_INFO, new_user_row))
                    st.session_state["is_admin"] = False
                    st.success(f"🎉 Registration successful! Welcome to the portal, {fmt_title(r_fn)}.")
                    st.rerun()

    # --- ADMIN LOGIN ---
    elif auth_choice == "Administrator Log-in":
        st.markdown('<div class="section-header">Department Administrator Log-In</div>', unsafe_allow_html=True)
        st.caption("Restricted portal for Civil Engineering Department Chair and Accreditation Committee.")

        adm_c1, adm_c2 = st.columns(2)
        with adm_c1:
            adm_user = st.text_input("Administrator Username*", placeholder="CE Department")
        with adm_c2:
            adm_pass = st.text_input("Administrator Password*", type="password", placeholder="••••••••")

        if st.button("Authenticate Admin Access", key="btn_admin_login"):
            if adm_user.strip().lower() in ["ce department", "admin", "chair_ce", "usjr_ce"] and adm_pass.strip() in ["sea2026", "admin123", "usjr2026", "pass123"]:
                st.session_state["is_admin"] = True
                st.session_state["logged_user"] = None
                st.success("🔓 Administrator Access Granted!")
                st.rerun()
            else:
                st.error("Invalid Administrator Credentials. Please check username and password.")

# ==============================================================================
# PHASE A: LOGGED-IN STUDENT PORTAL (5 EXCLUSIVE TABS)
# ==============================================================================
elif st.session_state["logged_user"]:
    user_info = st.session_state["logged_user"]
    sid_user = user_info.get("Student_ID")
    full_name_user = f"{user_info.get('First_Name','')} {user_info.get('Middle_Name','')} {user_info.get('Last_Name','')}".strip()

    tab_info, tab_exam, tab_tracer, tab_grad, tab_feedback = st.tabs([
        "ALUMNI INFORMATION",
        "BOARD EXAM DATA",
        "ALUMNI CAREER TRACER",
        "GRADUATE STUDIES",
        "ALUMNI FEEDBACK"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: ALUMNI INFORMATION
    # --------------------------------------------------------------------------
    with tab_info:
        st.caption("View and update your registered contact, academic, and security details below.")

        st.markdown('<div class="section-header">1. Identity & Personal Details</div>', unsafe_allow_html=True)

        u_id1, u_id2, u_id3, u_id4, u_id5 = st.columns(5)
        with u_id1:
            st.text_input("Student ID (Read-Only)", value=user_info.get("Student_ID", ""), disabled=True)
        with u_id2:
            e_pin = st.text_input("4-Digit Security PIN*", value=user_info.get("Security_PIN", ""), type="password", max_chars=4)
        with u_id3:
            e_fn = st.text_input("First Name*", value=user_info.get("First_Name", ""))
        with u_id4:
            e_mn = st.text_input("Middle Name", value=user_info.get("Middle_Name", ""))
        with u_id5:
            e_ln = st.text_input("Last Name*", value=user_info.get("Last_Name", ""))

        e_c1, e_c2, e_c3 = st.columns(3)
        with e_c1:
            e_civil = st.selectbox("Civil Status*", ["Single", "Married", "Widowed", "Separated"], index=safe_index(["Single", "Married", "Widowed", "Separated"], user_info.get("Civil_Status", "Single")))
            try:
                dob_val = datetime.datetime.strptime(user_info.get("Date_Of_Birth", "2000-01-01"), "%Y-%m-%d").date()
            except Exception:
                dob_val = datetime.date(2000, 1, 1)
            e_dob = st.date_input("Date of Birth*", value=dob_val, format="MM/DD/YYYY")
        with e_c2:
            e_email = st.text_input("Primary Email Address*", value=user_info.get("Email", ""))
            e_mobile = st.text_input("Mobile Number*", value=user_info.get("Contact_Number", ""))
        with e_c3:
            e_msg_app = st.selectbox("Preferred Messaging Channel*", ["Messenger", "Viber", "WhatsApp", "Telegram", "SMS / Direct"], index=safe_index(["Messenger", "Viber", "WhatsApp", "Telegram", "SMS / Direct"], user_info.get("Messaging_App", "Messenger")))
            e_msg_handle = st.text_input("Messaging Account Handle / Number*", value=user_info.get("Messaging_Handle", ""))

        st.markdown('<div class="section-header">2. Graduation & Academic Details</div>', unsafe_allow_html=True)

        ea_c1, ea_c2, ea_c3 = st.columns(3)
        with ea_c1:
            e_degree = st.selectbox("Degree Program*", deg_opts, index=safe_index(deg_opts, user_info.get("Degree_Program")))
            e_grad_year = st.selectbox("Graduation Year*", yr_opts, index=safe_index(yr_opts, user_info.get("Graduation_Year"), default=26))
        with ea_c2:
            e_grad_term = st.selectbox("Graduation Term*", term_opts, index=safe_index(term_opts, user_info.get("Graduation_Term")))
            e_class = st.selectbox("Student Classification*", class_opts, index=safe_index(class_opts, user_info.get("Student_Classification")))
        with ea_c3:
            e_gwa = st.text_input("Cumulative GWA", value=user_info.get("Cumulative_GWA", ""))
            e_honors = st.selectbox("Academic Honors Conferred", hon_opts, index=safe_index(hon_opts, user_info.get("Academic_Honors")))

        if st.button("Save Profile Updates", key="btn_update_student_profile"):
            missing_info = []
            if not e_pin.strip() or len(e_pin.strip()) != 4 or not e_pin.strip().isdigit(): missing_info.append("Valid 4-Digit Security PIN")
            if not e_fn.strip(): missing_info.append("First Name")
            if not e_ln.strip(): missing_info.append("Last Name")
            if not e_email.strip(): missing_info.append("Primary Email Address")
            clean_mob = re.sub(r"[\s\-+()]", "", e_mobile.strip())
            if not e_mobile.strip() or not clean_mob.isdigit(): missing_info.append("Valid Mobile Number (numeric only)")
            if e_gwa.strip():
                try: float(e_gwa.strip())
                except ValueError: missing_info.append("Valid Cumulative GWA (numeric e.g., 1.45 or 2.10)")

            if missing_info:
                list_str = "\n".join([f"• {m}" for m in missing_info])
                st.error(f"⚠️ Please complete the following required fields before saving profile updates:\n\n{list_str}")
            else:
                df_all = load_csv_safely(FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO)

                now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                updated_user_row = [
                    now_str, user_info.get("Registration_ID", f"REG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
                    sid_user, fmt_title(e_fn), fmt_title(e_mn), fmt_title(e_ln),
                    e_civil, e_dob.strftime("%m/%d/%Y"), fmt_lower(e_email), e_mobile.strip(), e_msg_app, e_msg_handle.strip(),
                    e_degree, e_grad_year, e_grad_term, e_class,
                    e_gwa.strip(), e_honors, e_pin.strip(), "Yes"
                ]

                df_upd = df_all[df_all["Student_ID"].astype(str).str.strip().str.upper() != sid_user.upper()]
                df_upd = pd.concat([df_upd, pd.DataFrame([dict(zip(HEADERS_ALUMNI_INFO, updated_user_row))])], ignore_index=True)
                df_upd.to_csv(FILE_ALUMNI_INFO, index=False)

                st.session_state["logged_user"] = dict(zip(HEADERS_ALUMNI_INFO, updated_user_row))
                st.success("🎉 Profile information updated successfully!")
                st.rerun()

    # --------------------------------------------------------------------------
    # TAB 2: BOARD EXAM DATA
    # --------------------------------------------------------------------------
    with tab_exam:
        st.caption("Record your Philippine Licensure Examination for Civil Engineers (LECE) attempts and performance.")

        df_b = load_csv_safely(FILE_BOARD_EXAM, HEADERS_BOARD_EXAM)

        editing_entry = None
        if st.session_state["edit_exam_id"]:
            m_exam = df_b[df_b["Entry_ID"] == st.session_state["edit_exam_id"]]
            if not m_exam.empty:
                editing_entry = m_exam.iloc[-1].to_dict()

        if editing_entry:
            st.markdown('<div class="section-header">Edit Board Exam Entry</div>', unsafe_allow_html=True)
            st.warning(f"Editing Record ID: `{editing_entry['Entry_ID']}`. Click 'Cancel Editing' to return.")
        else:
            st.markdown('<div class="section-header">Add Board Exam Attempt Record</div>', unsafe_allow_html=True)

        ex_c1, ex_c2 = st.columns(2)
        with ex_c1:
            cur_cat = editing_entry.get("Examinee_Category", None) if editing_entry else None
            b_cat = st.selectbox("Examinee Category*", ["First-Time Taker", "Retaker"], index=safe_index(["First-Time Taker", "Retaker"], cur_cat, default=None), placeholder="Select Category...")

            months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            years_list = [str(y) for y in range(2000, 2041)]

            cur_date_str = editing_entry.get("Board_Exam_Date", None) if editing_entry else None
            cur_m = None
            cur_y = None
            cur_note = ""

            if cur_date_str:
                for m in months_list:
                    if m.lower() in str(cur_date_str).lower():
                        cur_m = m
                        break
                for y in years_list:
                    if y in str(cur_date_str):
                        cur_y = y
                        break
                if "(" in str(cur_date_str) and ")" in str(cur_date_str):
                    cur_note = str(cur_date_str).split("(")[1].split(")")[0].strip()

            st.markdown("**Board Exam Date Construction:**")
            m_col, y_col = st.columns(2)
            with m_col:
                b_month = st.selectbox("Exam Month*", months_list, index=safe_index(months_list, cur_m, default=None), placeholder="Select Exam Month...")
            with y_col:
                b_year = st.selectbox("Exam Year*", years_list, index=safe_index(years_list, cur_y, default=None), placeholder="Select Exam Year...")

            b_note = st.text_input("Special Session / Batch Note (Optional)", value=cur_note, placeholder="e.g., SPLE Overseas Session, 1st Batch Retake")

            cur_weak = editing_entry.get("Perceived_Weakest_Subject", None) if editing_entry else None
            b_weak = st.selectbox("Perceived Weakest Subject Area*", weak_opts, index=safe_index(weak_opts, cur_weak, default=3))

        with ex_c2:
            cur_rev = editing_entry.get("Review_Center", None) if editing_entry else None
            b_rev = st.selectbox("Review Center Attended*", rev_opts, index=safe_index(rev_opts, cur_rev, default=None), placeholder="Select Review Center...")

            cur_mode = editing_entry.get("Review_Mode", None) if editing_entry else None
            b_mode = st.selectbox("Review Delivery Mode*", ["Face-to-Face / In-Person", "Online / Virtual Review", "Hybrid (Face-to-Face & Online)", "Self-Study"], index=safe_index(["Face-to-Face / In-Person", "Online / Virtual Review", "Hybrid (Face-to-Face & Online)", "Self-Study"], cur_mode, default=None), placeholder="Select Delivery Mode...")

            cur_rem = editing_entry.get("Remarks", None) if editing_entry else None
            b_rem = st.selectbox("Exam Result / Remarks*", rem_opts, index=safe_index(rem_opts, cur_rem, default=None), placeholder="Select Exam Result / Remarks...")

        is_sched = (b_rem == "Scheduled to Take / Upcoming Examinee")

        st.markdown("**Subject Ratings & PRC Information:**")
        col_mst, _ = st.columns([1, 3])
        with col_mst:
            b_mst = st.text_input("Mathematics, Surveying and Transportation Engineering Rating (%)", value=editing_entry.get("MST_Rating", "") if editing_entry else "", placeholder="e.g., 85.00" if not is_sched else "N/A", disabled=is_sched)
        col_hge, _ = st.columns([1, 3])
        with col_hge:
            b_hge = st.text_input("Hydraulics and Geotechnical Engineering Rating (%)", value=editing_entry.get("HGE_Rating", "") if editing_entry else "", placeholder="e.g., 82.50" if not is_sched else "N/A", disabled=is_sched)
        col_sec, _ = st.columns([1, 3])
        with col_sec:
            b_sec = st.text_input("Principles of Structural Analysis and Design Rating (%)", value=editing_entry.get("SEC_Rating", "") if editing_entry else "", placeholder="e.g., 88.00" if not is_sched else "N/A", disabled=is_sched)

        r_sub1, r_sub2, _, _ = st.columns(4)
        with r_sub1:
            b_ovr = st.text_input("Overall Rating (%)" if not is_sched else "Overall Rating", value=editing_entry.get("Overall_PRC_Rating", "") if editing_entry else "", placeholder="e.g., 85.15" if not is_sched else "N/A", disabled=is_sched)
        with r_sub2:
            b_lic = st.text_input("PRC License No.", value=editing_entry.get("PRC_License_Number", "") if editing_entry else "", placeholder="e.g., 0123456" if not is_sched else "N/A", disabled=is_sched)

        btn_c1, btn_c2 = st.columns([2, 1])
        with btn_c1:
            btn_label = "💾 Save Updates to Entry" if editing_entry else "➕ Save Board Exam Attempt Record"
            if st.button(btn_label, key="btn_save_exam"):
                missing_exam = []
                if b_cat is None: missing_exam.append("Examinee Category")
                if b_month is None: missing_exam.append("Exam Month")
                if b_year is None: missing_exam.append("Exam Year")
                if b_weak is None: missing_exam.append("Perceived Weakest Subject Area")
                if b_rev is None: missing_exam.append("Review Center Attended")
                if b_mode is None: missing_exam.append("Review Delivery Mode")
                if b_rem is None: missing_exam.append("Exam Result / Remarks")
                if b_rem is not None and b_rem != "Scheduled to Take / Upcoming Examinee":
                    if not b_ovr.strip():
                        missing_exam.append("Overall PRC Rating (%)")
                    else:
                        try: float(b_ovr.strip())
                        except ValueError: missing_exam.append("Valid Overall PRC Rating (%) (numeric only)")
                    if b_mst.strip():
                        try: float(b_mst.strip())
                        except ValueError: missing_exam.append("Valid Mathematics, Surveying and Transportation Engineering Rating (%) (numeric only)")
                    if b_hge.strip():
                        try: float(b_hge.strip())
                        except ValueError: missing_exam.append("Valid Hydraulics and Geotechnical Engineering Rating (%) (numeric only)")
                    if b_sec.strip():
                        try: float(b_sec.strip())
                        except ValueError: missing_exam.append("Valid Principles of Structural Analysis and Design Rating (%) (numeric only)")

                if missing_exam:
                    st.error("⚠️ Please complete the following required fields before saving board exam record:\n\n" + "\n".join([f"• {m}" for m in missing_exam]))
                else:
                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                    full_date_str = f"{b_month} {b_year}"
                    if b_note.strip():
                        full_date_str += f" ({b_note.strip()})"

                    if editing_entry:
                        entry_id = editing_entry["Entry_ID"]
                        upd_entry = [
                            now_str, entry_id, sid_user, full_name_user, full_date_str,
                            b_cat, b_weak, b_rev, b_mode,
                            b_ovr.strip() if not is_sched else "N/A", b_mst.strip() if not is_sched else "N/A", b_hge.strip() if not is_sched else "N/A", b_sec.strip() if not is_sched else "N/A", b_rem, b_lic.strip() if not is_sched else "N/A"
                        ]
                        df_b_upd = df_b[df_b["Entry_ID"] != entry_id]
                        df_b_upd = pd.concat([df_b_upd, pd.DataFrame([dict(zip(HEADERS_BOARD_EXAM, upd_entry))])], ignore_index=True)
                        df_b_upd.to_csv(FILE_BOARD_EXAM, index=False)
                        st.session_state["edit_exam_id"] = None
                        st.success("Board exam record updated successfully!")
                        st.rerun()
                    else:
                        entry_id = f"EXAM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        new_entry = [
                            now_str, entry_id, sid_user, full_name_user, full_date_str,
                            b_cat, b_weak, b_rev, b_mode,
                            b_ovr.strip() if not is_sched else "N/A", b_mst.strip() if not is_sched else "N/A", b_hge.strip() if not is_sched else "N/A", b_sec.strip() if not is_sched else "N/A", b_rem, b_lic.strip() if not is_sched else "N/A"
                        ]
                        with open(FILE_BOARD_EXAM, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(new_entry)
                        st.success("Board exam attempt logged successfully!")
                        st.rerun()

        with btn_c2:
            if editing_entry:
                if st.button("Cancel Editing", key="btn_cancel_edit_exam"):
                    st.session_state["edit_exam_id"] = None
                    st.rerun()

        # Logged History Table
        st.markdown('<div class="section-header">Logged Board Exam Attempts</div>', unsafe_allow_html=True)
        df_my_b = df_b[df_b["Student_ID"].astype(str).str.strip().str.upper() == sid_user.upper()]
        if df_my_b.empty:
            st.info("No board exam attempt records logged yet.")
        else:
            for idx, r_b in df_my_b.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="history-card">
                            <h4>📋 {r_b['Board_Exam_Date']} — {r_b['Examinee_Category']} ({r_b['Remarks']})</h4>
                            <p><strong>Perceived Weakest Subject:</strong> {r_b['Perceived_Weakest_Subject']}</p>
                            <p><strong>Overall Rating:</strong> {r_b['Overall_PRC_Rating']}% | <strong>MSTE:</strong> {r_b['MST_Rating']}% | <strong>HPGE:</strong> {r_b['HGE_Rating']}% | <strong>PSAD:</strong> {r_b['SEC_Rating']}%</p>
                            <p><strong>Review Center:</strong> {r_b['Review_Center']} ({r_b['Review_Mode']})</p>
                            <p><strong>PRC License No:</strong> {r_b['PRC_License_Number'] if r_b['PRC_License_Number'] else 'N/A'}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    b_col1, b_col2, b_space = st.columns([1, 1, 4])
                    with b_col1:
                        if st.button("✏️ Edit Entry", key=f"btn_edit_ex_{r_b['Entry_ID']}"):
                            st.session_state["edit_exam_id"] = r_b["Entry_ID"]
                            st.rerun()
                    with b_col2:
                        if st.button("🗑️ Delete Entry", key=f"btn_del_ex_{r_b['Entry_ID']}"):
                            df_b_del = df_b[df_b["Entry_ID"] != r_b["Entry_ID"]]
                            df_b_del.to_csv(FILE_BOARD_EXAM, index=False)
                            st.success("Record deleted successfully!")
                            st.rerun()

    # --------------------------------------------------------------------------
    # TAB 3: ALUMNI CAREER TRACER
    # --------------------------------------------------------------------------
    with tab_tracer:
        st.caption("Track your professional employment history, engineering specialization, and business ventures.")

        df_t = load_csv_safely(FILE_TRACER, HEADERS_TRACER)

        editing_tracer = None
        if st.session_state["edit_tracer_id"]:
            m_tr = df_t[df_t["Tracer_ID"] == st.session_state["edit_tracer_id"]]
            if not m_tr.empty:
                editing_tracer = m_tr.iloc[-1].to_dict()

        if editing_tracer:
            st.markdown('<div class="section-header">Edit Career or Business Record</div>', unsafe_allow_html=True)
            st.warning(f"Editing Record ID: `{editing_tracer['Tracer_ID']}`. Click 'Cancel Editing' to return.")
        else:
            st.markdown('<div class="section-header">Add New Career or Business Record</div>', unsafe_allow_html=True)

        cur_setup = editing_tracer.get("Work_Setup", None) if editing_tracer else None
        t_setup = st.selectbox("Employment Sector / Work Setup*", setup_opts, index=safe_index(setup_opts, cur_setup, default=None), placeholder="Select Employment Sector...")

        is_biz = (t_setup == "Business Owner / Entrepreneur / Independent Consultant")

        tc1, tc2 = st.columns(2)
        with tc1:
            if is_biz:
                t_emp = st.text_input("Business / Firm Name*", value=editing_tracer.get("Employer_Or_Firm_Name", "") if editing_tracer else "", placeholder="e.g., Dela Cruz Engineering & Construction Services")

                cur_role = editing_tracer.get("Position_Or_Role", None) if editing_tracer else None
                role_opts = ["Founder / Owner", "Managing Partner", "Principal Structural Consultant", "General Contractor", "Independent Engineering Consultant"]
                t_pos = st.selectbox("Role / Ownership Title*", role_opts, index=safe_index(role_opts, cur_role, default=None), placeholder="Select Role / Title...")

                cur_biz_cat = editing_tracer.get("Business_Category", None) if editing_tracer else None
                cat_opts = ["PCAB Licensed Contractor", "Structural / Civil Consultancy Firm", "Construction Material Supply", "Project Management Services", "Non-Engineering Venture"]
                t_biz_cat = st.selectbox("Business / Firm Category*", cat_opts, index=safe_index(cat_opts, cur_biz_cat, default=None), placeholder="Select Business Category...")

                cur_reg = editing_tracer.get("DTI_SEC_Reg", None) if editing_tracer else None
                reg_opts = ["DTI Registered Sole Proprietorship", "SEC Registered Corporation / Partnership", "Unregistered / Informal", "In Process"]
                t_reg = st.selectbox("DTI / SEC Registration Status*", reg_opts, index=safe_index(reg_opts, cur_reg, default=None), placeholder="Select Registration Status...")

            else:
                ph_emp = "e.g., DPWH Regional Office VII / LGU Cebu City"
                if t_setup == "Private / Corporate Employee":
                    ph_emp = "e.g., Megawide Construction Corp. / MDS Structural Consultants"
                elif t_setup == "Academe / Educational Institution":
                    ph_emp = "e.g., University of San Jose - Recoletos / CTU Main Campus"
                elif t_setup == "Overseas / OFW Engineer":
                    ph_emp = "e.g., Al Habtoor Group - Dubai / Surbana Jurong - Singapore"

                ph_pos = "e.g., Project Inspector / Structural Engineer"
                if t_setup == "Academe / Educational Institution":
                    ph_pos = "e.g., Assistant Professor / Instructor / Department Chair"

                t_emp = st.text_input("Employer / Institution Name*", value=editing_tracer.get("Employer_Or_Firm_Name", "") if editing_tracer else "", placeholder=ph_emp)
                t_pos = st.text_input("Job Title / Academic Rank*", value=editing_tracer.get("Position_Or_Role", "") if editing_tracer else "", placeholder=ph_pos)

                cur_emp_type = editing_tracer.get("Employment_Type", None) if editing_tracer else None
                type_opts = ["Permanent / Regular", "Contractual / Job Order", "Probationary", "Part-Time / Project-Based"]
                t_emp_type = st.selectbox("Employment Status*", type_opts, index=safe_index(type_opts, cur_emp_type, default=None), placeholder="Select Employment Status...")

                cur_lvl = editing_tracer.get("Position_Level", None) if editing_tracer else None
                lvl_opts = ["Entry-Level / Junior Engineer", "Mid-Level / Senior Engineer", "Supervisory / Managerial", "Executive / Director / Dean"]
                t_lvl = st.selectbox("Position Level*", lvl_opts, index=safe_index(lvl_opts, cur_lvl, default=None), placeholder="Select Position Level...")

        with tc2:
            if is_biz:
                cur_scale = editing_tracer.get("Business_Scale", None) if editing_tracer else None
                scale_opts = ["Micro Enterprise (1-9 employees)", "Small Enterprise (10-49 employees)", "Medium Enterprise (50-249 employees)", "Large Enterprise (250+ employees)"]
                t_scale = st.selectbox("Business Scale & Workforce*", scale_opts, index=safe_index(scale_opts, cur_scale, default=None), placeholder="Select Business Scale...")

                cur_op_yrs = editing_tracer.get("Years_Operating", None) if editing_tracer else None
                op_opts = ["Less than 1 Year", "1–3 Years", "4–7 Years", "8+ Years"]
                t_op_yrs = st.selectbox("Years in Operation*", op_opts, index=safe_index(op_opts, cur_op_yrs, default=None), placeholder="Select Years in Operation...")

                cur_sal = editing_tracer.get("Salary_Bracket", None) if editing_tracer else None
                sal_biz_opts = ["Below ₱50,000", "₱50,000 – ₱100,000", "₱100,000 – ₱250,000", "₱250,000 – ₱500,000", "Above ₱500,000", "Prefer Not to Disclose"]
                t_sal = st.selectbox("Gross Monthly Business Revenue / Income (Optional)", sal_biz_opts, index=safe_index(sal_biz_opts, cur_sal, default=None), placeholder="Select Business Revenue (Optional)...")

                t_loc = st.text_input("Business Headquarters / Office Location*", value=editing_tracer.get("Work_Location", "") if editing_tracer else "", placeholder="e.g., Cebu City / Mandaue City")
                t_start = st.text_input("Year Business Founded*", value=editing_tracer.get("Start_Year", "") if editing_tracer else "", placeholder="e.g., 2022")
                t_end = "Present"
                t_align = "Directly Related to Civil Engineering"

            else:
                cur_sal = editing_tracer.get("Salary_Bracket", None) if editing_tracer else None
                sal_emp_opts = ["Below ₱20,000", "₱20,000 – ₱40,000", "₱40,000 – ₱70,000", "₱70,000 – ₱100,000", "Above ₱100,000", "Prefer Not to Disclose"]
                t_sal = st.selectbox("Gross Monthly Salary Bracket (Optional)", sal_emp_opts, index=safe_index(sal_emp_opts, cur_sal, default=None), placeholder="Select Salary Bracket (Optional)...")

                cur_align = editing_tracer.get("Job_Alignment", None) if editing_tracer else None
                align_opts = ["Directly Related to Civil Engineering", "Partially Related", "Unrelated"]
                t_align = st.selectbox("Job Alignment to Civil Engineering*", align_opts, index=safe_index(align_opts, cur_align, default=None), placeholder="Select Job Alignment...")

                t_loc = st.text_input("Work Location / Office Address*", value=editing_tracer.get("Work_Location", "") if editing_tracer else "", placeholder="e.g., Cebu City / Overseas - Dubai")

                tr_y1, tr_y2 = st.columns(2)
                with tr_y1:
                    t_start = st.text_input("Start Year*", value=editing_tracer.get("Start_Year", "") if editing_tracer else "", placeholder="e.g., 2021")
                with tr_y2:
                    t_end = st.text_input("End Year (or Present)*", value=editing_tracer.get("End_Year", "") if editing_tracer else "", placeholder="e.g., Present or 2023")

                t_biz_cat = "N/A"
                t_reg = "N/A"
                t_scale = "N/A"
                t_op_yrs = "N/A"

        btn_t1, btn_t2 = st.columns([2, 1])
        with btn_t1:
            lbl_tr = "💾 Save Updates to Entry" if editing_tracer else "➕ Save Career or Business Record"
            if st.button(lbl_tr, key="btn_save_tracer"):
                missing_tracer = []
                if is_biz:
                    if not t_emp.strip(): missing_tracer.append("Business / Firm Name")
                    if not t_pos.strip(): missing_tracer.append("Role / Ownership Title")
                    if not t_loc.strip(): missing_tracer.append("Business Headquarters / Location")
                    if not t_start.strip(): missing_tracer.append("Year Business Founded")
                else:
                    if not t_emp.strip(): missing_tracer.append("Employer / Institution Name")
                    if not t_pos.strip(): missing_tracer.append("Job Title / Academic Rank")
                    if not t_loc.strip(): missing_tracer.append("Work Location / Office Address")
                    if not t_start.strip(): missing_tracer.append("Start Year")

                if missing_tracer:
                    list_str = "\n".join([f"• {m}" for m in missing_tracer])
                    st.error(f"⚠️ Please complete the following required fields before saving career record:\n\n{list_str}")
                else:
                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                    if editing_tracer:
                        tr_id = editing_tracer["Tracer_ID"]
                        upd_tr_row = [
                            now_str, tr_id, sid_user, full_name_user, t_setup,
                            t_emp.strip(), t_pos.strip(), t_lvl if not is_biz else "Owner / Principal", t_align,
                            t_loc.strip(), t_emp_type if not is_biz else "Self-Employed / Owner", (t_sal if t_sal else 'Not Specified'), t_start.strip(), t_end.strip(),
                            t_biz_cat, t_reg, t_scale, t_op_yrs
                        ]
                        df_t_upd = df_t[df_t["Tracer_ID"] != tr_id]
                        df_t_upd = pd.concat([df_t_upd, pd.DataFrame([dict(zip(HEADERS_TRACER, upd_tr_row))])], ignore_index=True)
                        df_t_upd.to_csv(FILE_TRACER, index=False)
                        st.session_state["edit_tracer_id"] = None
                        st.success("Career record updated successfully!")
                        st.rerun()
                    else:
                        tr_id = f"TRACER-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        new_tr_row = [
                            now_str, tr_id, sid_user, full_name_user, t_setup,
                            t_emp.strip(), t_pos.strip(), t_lvl if not is_biz else "Owner / Principal", t_align,
                            t_loc.strip(), t_emp_type if not is_biz else "Self-Employed / Owner", (t_sal if t_sal else 'Not Specified'), t_start.strip(), t_end.strip(),
                            t_biz_cat, t_reg, t_scale, t_op_yrs
                        ]
                        with open(FILE_TRACER, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(new_tr_row)
                        st.success("Career / business entry logged successfully!")
                        st.rerun()

        with btn_t2:
            if editing_tracer:
                if st.button("Cancel Editing", key="btn_cancel_edit_tracer"):
                    st.session_state["edit_tracer_id"] = None
                    st.rerun()

        # Logged History Table
        st.markdown('<div class="section-header">Logged Career & Business History</div>', unsafe_allow_html=True)
        df_my_t = df_t[df_t["Student_ID"].astype(str).str.strip().str.upper() == sid_user.upper()]
        if df_my_t.empty:
            st.info("No career or business records logged yet.")
        else:
            for idx, r_t in df_my_t.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="history-card">
                            <h4>🏢 {r_t['Employer_Or_Firm_Name']} — {r_t['Position_Or_Role']} ({r_t['Work_Setup']})</h4>
                            <p><strong>Position Level:</strong> {r_t['Position_Level']} | <strong>Employment Status:</strong> {r_t['Employment_Type']}</p>
                            <p><strong>Work Location:</strong> {r_t['Work_Location']} | <strong>Tenure:</strong> {r_t['Start_Year']} – {r_t['End_Year']}</p>
                            <p><strong>Salary / Revenue Bracket:</strong> {r_t['Salary_Bracket']} | <strong>Job Alignment:</strong> {r_t['Job_Alignment']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    t_col1, t_col2, t_space = st.columns([1, 1, 4])
                    with t_col1:
                        if st.button("✏️ Edit Entry", key=f"btn_edit_tr_{r_t['Tracer_ID']}"):
                            st.session_state["edit_tracer_id"] = r_t["Tracer_ID"]
                            st.rerun()
                    with t_col2:
                        if st.button("🗑️ Delete Entry", key=f"btn_del_tr_{r_t['Tracer_ID']}"):
                            df_t_del = df_t[df_t["Tracer_ID"] != r_t["Tracer_ID"]]
                            df_t_del.to_csv(FILE_TRACER, index=False)
                            st.success("Record deleted successfully!")
                            st.rerun()

    # --------------------------------------------------------------------------
    # TAB 4: GRADUATE STUDIES
    # --------------------------------------------------------------------------
    with tab_grad:
        st.caption("Record your Master's/Doctoral studies, ASEAN Engineer registry, or specialized professional accreditations.")

        df_g = load_csv_safely(FILE_GRAD_STUDIES, HEADERS_GRAD_STUDIES)

        editing_grad = None
        if st.session_state["edit_grad_id"]:
            m_gr = df_g[df_g["Grad_ID"] == st.session_state["edit_grad_id"]]
            if not m_gr.empty:
                editing_grad = m_gr.iloc[-1].to_dict()

        if editing_grad:
            st.markdown('<div class="section-header">Edit Graduate Study or Accreditation Record</div>', unsafe_allow_html=True)
            st.warning(f"Editing Record ID: `{editing_grad['Grad_ID']}`. Click 'Cancel Editing' to return.")
        else:
            st.markdown('<div class="section-header">Add New Graduate Degree or Accreditation</div>', unsafe_allow_html=True)

        cur_deg_type = editing_grad.get("Graduate_Degree", None) if editing_grad else None
        g_deg_type = st.selectbox("Graduate Education or Accreditation Type*", deg_type_opts, index=safe_index(deg_type_opts, cur_deg_type, default=None), placeholder="Select Type...")

        gc1, gc2 = st.columns(2)
        with gc1:
            if g_deg_type == "Master's / Doctoral Degree":
                g_title = st.text_input("Degree Program Title*", value=editing_grad.get("Degree_Specified_Details", "") if editing_grad else "", placeholder="e.g., Master of Science in Civil Engineering - Structural Track")
                g_track = st.text_input("Specialization / Research Track*", value=editing_grad.get("Specialization_Track", "") if editing_grad else "", placeholder="e.g., Earthquake Engineering / Hydraulic Structures")
                g_inst = st.text_input("University / Graduate School*", value=editing_grad.get("Institution_Name", "") if editing_grad else "", placeholder="e.g., University of San Jose - Recoletos / UP Diliman")

                cur_status = editing_grad.get("Academic_Status", None) if editing_grad else None
                stat_opts = ["Completed / Graduated", "On-Going Coursework", "Thesis / Dissertation Defense Stage", "Completed Coursework (Units Earned)"]
                g_status = st.selectbox("Academic Status*", stat_opts, index=safe_index(stat_opts, cur_status, default=None), placeholder="Select Status...")

            elif g_deg_type == "Professional Accreditation / Specialist Membership":
                g_title = st.text_input("Accreditation Title*", value=editing_grad.get("Degree_Specified_Details", "") if editing_grad else "", placeholder="e.g., ASEAN Engineer / ASEP Structural Specialist / Master Plumber")
                g_track = st.text_input("License / Registry / Accreditation No.", value=editing_grad.get("Specialization_Track", "") if editing_grad else "", placeholder="e.g., ASEAN-ENG-2024-0123")
                g_inst = st.text_input("Conferring Body / Registry*", value=editing_grad.get("Institution_Name", "") if editing_grad else "", placeholder="e.g., ASEAN Federation of Engineering Organisations / PICE / PRC")

                cur_status = editing_grad.get("Academic_Status", None) if editing_grad else None
                stat_acc_opts = ["Active / Valid Registry", "Lifetime Fellow / Member", "In Application / Candidate Status"]
                g_status = st.selectbox("Accreditation Status*", stat_acc_opts, index=safe_index(stat_acc_opts, cur_status, default=None), placeholder="Select Status...")

            else:
                g_title = st.text_input("Custom Degree / Accreditation Title*", value=editing_grad.get("Degree_Specified_Details", "") if editing_grad else "", placeholder="e.g., Certified Safety Officer / DOLE Construction Safety Consultant")
                g_track = st.text_input("Specialization / Field", value=editing_grad.get("Specialization_Track", "") if editing_grad else "", placeholder="e.g., Construction Occupational Safety and Health")
                g_inst = st.text_input("Institution / Organization Name*", value=editing_grad.get("Institution_Name", "") if editing_grad else "", placeholder="e.g., DOLE-OSHC / PICE Disaster Preparedness Committee")
                g_status = "Active / Completed"

        with gc2:
            g_year = st.text_input("Year Conferred / Granted*", value=editing_grad.get("Year_Conferred", "") if editing_grad else "", placeholder="e.g., 2024 or On-going")

        btn_g1, btn_g2 = st.columns([2, 1])
        with btn_g1:
            lbl_gr = "💾 Save Updates to Entry" if editing_grad else "➕ Save Graduate Education / Accreditation Record"
            if st.button(lbl_gr, key="btn_save_grad"):
                missing_grad = []
                if g_deg_type is None: missing_grad.append("Graduate Education / Accreditation Type")
                if not g_title.strip(): missing_grad.append("Degree / Program / Accreditation Title")
                if not g_inst.strip(): missing_grad.append("University / Institution / Conferring Body Name")
                if g_status is None: missing_grad.append("Academic / Accreditation Status")
                if not g_year.strip(): missing_grad.append("Year Conferred / Granted")

                if missing_grad:
                    st.error("⚠️ Please complete the following required fields before saving graduate study record:\n\n" + "\n".join([f"• {m}" for m in missing_grad]))
                else:
                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                    if editing_grad:
                        gr_id = editing_grad["Grad_ID"]
                        upd_gr_row = [
                            now_str, gr_id, sid_user, full_name_user, g_deg_type,
                            g_title.strip(), g_track.strip(), g_inst.strip(), g_status, g_year.strip()
                        ]
                        df_g_upd = df_g[df_g["Grad_ID"] != gr_id]
                        df_g_upd = pd.concat([df_g_upd, pd.DataFrame([dict(zip(HEADERS_GRAD_STUDIES, upd_gr_row))])], ignore_index=True)
                        df_g_upd.to_csv(FILE_GRAD_STUDIES, index=False)
                        st.session_state["edit_grad_id"] = None
                        st.success("Graduate record updated successfully!")
                        st.rerun()
                    else:
                        gr_id = f"GRAD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        new_gr_row = [
                            now_str, gr_id, sid_user, full_name_user, g_deg_type,
                            g_title.strip(), g_track.strip(), g_inst.strip(), g_status, g_year.strip()
                        ]
                        with open(FILE_GRAD_STUDIES, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(new_gr_row)
                        st.success("Graduate degree or accreditation logged successfully!")
                        st.rerun()

        with btn_g2:
            if editing_grad:
                if st.button("Cancel Editing", key="btn_cancel_edit_grad"):
                    st.session_state["edit_grad_id"] = None
                    st.rerun()

        # Logged History Table
        st.markdown('<div class="section-header">Logged Graduate Education & Accreditations</div>', unsafe_allow_html=True)
        df_my_g = df_g[df_g["Student_ID"].astype(str).str.strip().str.upper() == sid_user.upper()]
        if df_my_g.empty:
            st.info("No graduate studies or accreditation records logged yet.")
        else:
            for idx, r_g in df_my_g.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="history-card">
                            <h4>🎓 {r_g['Degree_Specified_Details']} ({r_g['Graduate_Degree']})</h4>
                            <p><strong>Institution / Conferring Body:</strong> {r_g['Institution_Name']}</p>
                            <p><strong>Specialization / Registry:</strong> {r_g['Specialization_Track'] if r_g['Specialization_Track'] else 'N/A'}</p>
                            <p><strong>Status:</strong> {r_g['Academic_Status']} | <strong>Year:</strong> {r_g['Year_Conferred']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    g_col1, g_col2, g_space = st.columns([1, 1, 4])
                    with g_col1:
                        if st.button("✏️ Edit Entry", key=f"btn_edit_gr_{r_g['Grad_ID']}"):
                            st.session_state["edit_grad_id"] = r_g["Grad_ID"]
                            st.rerun()
                    with g_col2:
                        if st.button("🗑️ Delete Entry", key=f"btn_del_gr_{r_g['Grad_ID']}"):
                            df_g_del = df_g[df_g["Grad_ID"] != r_g["Grad_ID"]]
                            df_g_del.to_csv(FILE_GRAD_STUDIES, index=False)
                            st.success("Record deleted successfully!")
                            st.rerun()

    # --------------------------------------------------------------------------
    # TAB 5: ALUMNI FEEDBACK, IDEAS & CONCERNS
    # --------------------------------------------------------------------------
    with tab_feedback:
        st.caption("Share your constructive feedback, curriculum suggestions, facilities recommendations, or general ideas with the Department of Civil Engineering.")

        st.markdown('<div class="section-header">Submit Constructive Feedback or Department Suggestions</div>', unsafe_allow_html=True)

        fb_c1, fb_c2 = st.columns(2)
        with fb_c1:
            fb_cat = st.selectbox("Feedback Category*", fb_cat_opts, index=None, placeholder="Select Feedback Category...", key="fb_cat_sel")
            fb_title = st.text_input("Subject / Topic Title*", placeholder="e.g., Request for Advanced Structural Software Workshops", key="fb_title_inp")
        with fb_c2:
            fb_msg = st.text_area("Detailed Feedback & Suggestions*", placeholder="Write your detailed suggestions, ideas, or department concerns here...", height=120, key="fb_msg_txt")

        if st.button("📩 Submit Feedback to Department", key="btn_submit_feedback"):
            missing_fb = []
            if not fb_title.strip(): missing_fb.append("Subject / Topic Title")
            if not fb_msg.strip(): missing_fb.append("Detailed Feedback Content")

            if missing_fb:
                list_str = "\n".join([f"• {m}" for m in missing_fb])
                st.error(f"⚠️ Please complete the following required fields before submitting feedback:\n\n{list_str}")
            else:
                now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                fb_id = f"FB-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

                new_fb_row = [
                    now_str, fb_id, sid_user, full_name_user,
                    fb_cat, fb_title.strip(), fb_msg.strip(), "Submitted"
                ]

                with open(FILE_FEEDBACK, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(new_fb_row)

                st.success(f"🎉 Thank you for your feedback! Reference ID: `{fb_id}`. Your comments have been logged for departmental review.")
                st.rerun()

        # Feedback History for Logged-In User
        st.markdown('<div class="section-header">My Submitted Feedback History</div>', unsafe_allow_html=True)
        df_fb_user = load_csv_safely(FILE_FEEDBACK, HEADERS_FEEDBACK)
        df_my_fb = df_fb_user[df_fb_user["Student_ID"].astype(str).str.strip().str.upper() == sid_user.upper()]

        if df_my_fb.empty:
            st.info("You have not submitted any feedback entries yet.")
        else:
            for idx, r_fb in df_my_fb.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="history-card">
                            <h4>💬 [{r_fb['Feedback_ID']}] {r_fb['Subject_Title']} ({r_fb['Category']})</h4>
                            <p><strong>Submitted On:</strong> {r_fb['Timestamp']}</p>
                            <p><strong>Message:</strong> {r_fb['Message_Content']}</p>
                        </div>
                    """, unsafe_allow_html=True)

# ==============================================================================
# PHASE B: ADMINISTRATOR LOGGED IN (DISPLAY ONLY THE ADMIN DASHBOARD)
# ==============================================================================
elif st.session_state["is_admin"]:
    st.subheader("Department Administrative Dashboard")
    st.caption("Manage cohort performance, inspect and edit alumni records, execute CQI interventions, and export accreditation master files.")

    df_a = load_csv_safely(FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO)
    df_b = load_csv_safely(FILE_BOARD_EXAM, HEADERS_BOARD_EXAM)
    df_t = load_csv_safely(FILE_TRACER, HEADERS_TRACER)
    df_g = load_csv_safely(FILE_GRAD_STUDIES, HEADERS_GRAD_STUDIES)
    df_cqi = load_csv_safely(FILE_CQI, HEADERS_CQI)
    df_fb = load_csv_safely(FILE_FEEDBACK, HEADERS_FEEDBACK)

    if st.session_state.get("admin_flash_msg"):
        st.success(st.session_state["admin_flash_msg"])
        st.session_state["admin_flash_msg"] = None

    if st.session_state.get("cqi_flash_msg"):
        st.success(st.session_state["cqi_flash_msg"])
        st.session_state["cqi_flash_msg"] = None

    # --------------------------------------------------------------------------
    # ADMIN SECTION 1: DEPARTMENT KEY PERFORMANCE INDICATORS
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 1: Department Key Performance Indicators (KPIs)</div>', unsafe_allow_html=True)

    unique_alumni = df_a["Student_ID"].astype(str).str.strip().str.upper().nunique() if not df_a.empty else 0
    passed_cnt = df_b[df_b["Remarks"].astype(str).str.strip().str.lower() == "passed"]["Student_ID"].astype(str).str.strip().str.upper().nunique() if not df_b.empty else 0
    unique_tracer = df_t["Student_ID"].astype(str).str.strip().str.upper().nunique() if not df_t.empty else 0
    unique_grad = df_g["Student_ID"].astype(str).str.strip().str.upper().nunique() if not df_g.empty else 0
    total_feedback = len(df_fb) if not df_fb.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Registered Alumni</div><div class="kpi-value">{unique_alumni}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Licensed Engineers</div><div class="kpi-value">{passed_cnt}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Career Records</div><div class="kpi-value">{unique_tracer}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Graduate Studies</div><div class="kpi-value">{unique_grad}</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Feedback Entries</div><div class="kpi-value">{total_feedback}</div></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ADMIN SECTION 2: REGISTERED ALUMNI DIRECTORY
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 2: Registered Alumni Directory</div>', unsafe_allow_html=True)

    if df_a.empty:
        st.info("No registered alumni entries found in the database.")
    else:
        search_query = st.text_input(
            "🔍 Search Alumni Directory (by Name, Student ID, Email, or Degree):",
            placeholder="e.g., Dela Cruz, Juan, 2020123456, or Structural...",
            key="admin_sec2_search"
        ).strip().lower()

        if search_query:
            def row_matches(row):
                sid = str(row.get("Student_ID", "")).lower()
                sid_clean = re.sub(r"[\s\-]", "", sid)
                fn = str(row.get("First_Name", "")).lower()
                mn = str(row.get("Middle_Name", "")).lower()
                ln = str(row.get("Last_Name", "")).lower()
                full_n = f"{fn} {mn} {ln}".lower()
                full_n_simple = f"{fn} {ln}".lower()
                email = str(row.get("Email", "")).lower()
                degree = str(row.get("Degree_Program", "")).lower()

                q_clean = re.sub(r"[\s\-]", "", search_query)

                return (
                    search_query in sid
                    or q_clean in sid_clean
                    or search_query in fn
                    or search_query in ln
                    or search_query in full_n
                    or search_query in full_n_simple
                    or search_query in email
                    or search_query in degree
                )

            mask = df_a.apply(row_matches, axis=1)
            df_a_filtered = df_a[mask]
        else:
            df_a_filtered = df_a

        st.caption(f"Displaying **{len(df_a_filtered)}** matching record(s) out of **{len(df_a)}** total registered alumni.")

        st.dataframe(
            df_a_filtered[["Student_ID", "First_Name", "Last_Name", "Degree_Program", "Graduation_Year", "Email", "Contact_Number", "Security_PIN"]],
            use_container_width=True,
            height=380
        )

    # --------------------------------------------------------------------------
    # ADMIN SECTION 3: COMPLETE STUDENT PROFILE INSPECTOR & EDITOR
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 3: Complete Student Profile Inspector & Editor</div>', unsafe_allow_html=True)
    st.caption("Select any registered student below to inspect and edit their complete records across all categories.")

    if df_a.empty:
        st.info("No registered alumni entries found in the database.")
    else:
        df_a_unique = df_a.drop_duplicates(subset=["Student_ID"], keep="last")
        student_options = []
        for idx, r_stud in df_a_unique.iterrows():
            sid_val = str(r_stud.get('Student_ID', '')).strip().upper()
            fn_val = str(r_stud.get('First_Name', '')).strip()
            ln_val = str(r_stud.get('Last_Name', '')).strip()
            if sid_val:
                student_options.append(f"{sid_val} — {fn_val} {ln_val}")

        selected_student_str = st.selectbox(
            "Select a Student to Inspect / Edit Complete Records:",
            student_options,
            index=None,
            placeholder="Choose a student profile...",
            key="admin_student_inspector_select"
        )

        if selected_student_str:
            sel_sid = selected_student_str.split(" — ")[0].strip().upper()
            matches_a = df_a[df_a["Student_ID"].astype(str).str.strip().str.upper() == sel_sid]

            if not matches_a.empty:
                st_match = matches_a.iloc[-1].to_dict()

                st.success(f"Inspecting Profile: **{st_match.get('First_Name', '')} {st_match.get('Last_Name', '')}** (Student ID: `{st_match.get('Student_ID', '')}`)")

                exp_t1, exp_t2, exp_t3, exp_t4, exp_t5 = st.tabs([
                    "Alumni Information",
                    "Board Exam Data",
                    "Alumni Career Tracer",
                    "Graduate Studies",
                    "Alumni Feedback"
                ])

                # INSPECTOR SUB-TAB 1: ALUMNI INFORMATION
                with exp_t1:
                    st.markdown("##### Edit Profile & Security Details")

                    adm_id1, adm_id2, adm_id3, adm_id4, adm_id5 = st.columns(5)
                    with adm_id1:
                        st.text_input("Student ID (Read-Only)", value=st_match.get("Student_ID", ""), disabled=True, key=f"adm_sid_{sel_sid}")
                    with adm_id2:
                        adm_pin = st.text_input("4-Digit Security PIN*", value=st_match.get("Security_PIN", ""), key=f"adm_pin_{sel_sid}")
                    with adm_id3:
                        adm_fn = st.text_input("First Name*", value=st_match.get("First_Name", ""), key=f"adm_fn_{sel_sid}")
                    with adm_id4:
                        adm_mn = st.text_input("Middle Name", value=st_match.get("Middle_Name", ""), key=f"adm_mn_{sel_sid}")
                    with adm_id5:
                        adm_ln = st.text_input("Last Name*", value=st_match.get("Last_Name", ""), key=f"adm_ln_{sel_sid}")

                    ac_1, ac_2, ac_3 = st.columns(3)
                    with ac_1:
                        adm_email = st.text_input("Primary Email*", value=st_match.get("Email", ""), key=f"adm_email_{sel_sid}")
                        adm_mobile = st.text_input("Contact Number*", value=st_match.get("Contact_Number", ""), key=f"adm_mob_{sel_sid}")
                    with ac_2:
                        adm_degree = st.selectbox("Degree Program*", deg_opts, index=safe_index(deg_opts, st_match.get("Degree_Program")), key=f"adm_deg_{sel_sid}")
                        adm_gyear = st.selectbox("Graduation Year*", yr_opts, index=safe_index(yr_opts, st_match.get("Graduation_Year"), default=26), key=f"adm_gyr_{sel_sid}")
                    with ac_3:
                        adm_gwa = st.text_input("Cumulative GWA", value=st_match.get("Cumulative_GWA", ""), key=f"adm_gwa_{sel_sid}")
                        adm_honors = st.selectbox("Academic Honors", hon_opts, index=safe_index(hon_opts, st_match.get("Academic_Honors")), key=f"adm_hon_{sel_sid}")

                    st.divider()

                    adm_b1, adm_b2 = st.columns(2)
                    with adm_b1:
                        if st.button("💾 Save Admin Changes to Student Profile", key=f"btn_save_adm_prof_v18_{sel_sid}"):
                            missing_adm_info = []
                            clean_mob = re.sub(r"[\s\-+()]", "", adm_mobile.strip())
                            if not adm_mobile.strip() or not clean_mob.isdigit(): missing_adm_info.append("Valid Contact Number (numeric only)")
                            if adm_gwa.strip():
                                try: float(adm_gwa.strip())
                                except ValueError: missing_adm_info.append("Valid Cumulative GWA (numeric e.g., 1.45 or 2.10)")
                            if not adm_pin.strip() or len(adm_pin.strip()) != 4 or not adm_pin.strip().isdigit(): missing_adm_info.append("Valid 4-Digit Security PIN")

                            if missing_adm_info:
                                err_list = "\n".join([f"• {m}" for m in missing_adm_info])
                                st.error(f"⚠️ Please correct the following errors before saving profile changes:\n\n{err_list}")
                            else:
                                now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                            upd_row = [
                                now_str, st_match.get("Registration_ID", f"REG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
                                sel_sid, fmt_title(adm_fn), fmt_title(adm_mn), fmt_title(adm_ln),
                                st_match.get("Civil_Status", "Single"), st_match.get("Date_Of_Birth", "2000-01-01"),
                                fmt_lower(adm_email), adm_mobile.strip(), st_match.get("Messaging_App", "SMS"), st_match.get("Messaging_Handle", ""),
                                adm_degree, adm_gyear, st_match.get("Graduation_Term", "1st Semester"), st_match.get("Student_Classification", "Regular"),
                                adm_gwa.strip(), adm_honors, adm_pin.strip(), "Yes"
                            ]
                            df_a_upd = df_a[df_a["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]
                            df_a_upd = pd.concat([df_a_upd, pd.DataFrame([dict(zip(HEADERS_ALUMNI_INFO, upd_row))])], ignore_index=True)
                            df_a_upd.to_csv(FILE_ALUMNI_INFO, index=False)
                            st.session_state["admin_flash_msg"] = f"Admin changes saved for student {sel_sid}!"
                            st.rerun()

                    with adm_b2:
                        st.markdown('<div class="delete-warning-card"><h5>Permanent Record Removal</h5><p>Completely delete this student and all associated logs across all CSV database files.</p></div>', unsafe_allow_html=True)
                        confirm_del = st.checkbox(f"Confirm permanent deletion of student '{sel_sid}'", key=f"chk_del_confirm_v18_{sel_sid}")
                        if st.button(f"🗑️ Delete Entire Student Record ({sel_sid})", key=f"btn_del_entire_v18_{sel_sid}"):
                            if not confirm_del:
                                st.error("Please check the confirmation box first.")
                            else:
                                df_a_new = df_a[df_a["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]
                                df_b_new = df_b[df_b["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]
                                df_t_new = df_t[df_t["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]
                                df_g_new = df_g[df_g["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]
                                df_fb_new = df_fb[df_fb["Student_ID"].astype(str).str.strip().str.upper() != sel_sid]

                                df_a_new.to_csv(FILE_ALUMNI_INFO, index=False)
                                df_b_new.to_csv(FILE_BOARD_EXAM, index=False)
                                df_t_new.to_csv(FILE_TRACER, index=False)
                                df_g_new.to_csv(FILE_GRAD_STUDIES, index=False)
                                df_fb_new.to_csv(FILE_FEEDBACK, index=False)

                                st.session_state["admin_flash_msg"] = f"Deleted entire student record for '{sel_sid}'."
                                st.rerun()

                # INSPECTOR SUB-TAB 2: BOARD EXAM DATA
                with exp_t2:
                    df_sb = df_b[df_b["Student_ID"].astype(str).str.strip().str.upper() == sel_sid]
                    if df_sb.empty:
                        st.info("No board exam attempts logged for this student.")
                    else:
                        st.markdown("##### Logged Board Exam Attempts Summary")
                        st.dataframe(df_sb[["Entry_ID", "Board_Exam_Date", "Examinee_Category", "Perceived_Weakest_Subject", "Review_Center", "Overall_PRC_Rating", "Remarks", "PRC_License_Number"]], use_container_width=True)

                        st.divider()
                        st.markdown("##### Edit Selected Board Exam Attempt Record")
                        
                        sb_entries = [f"{r['Entry_ID']} — {r['Board_Exam_Date']} ({r['Remarks']})" for idx, r in df_sb.iterrows()]
                        sel_ex_str = st.selectbox("Select Board Exam Entry to Edit:", sb_entries, key=f"sb_ex_select_v18_{sel_sid}")
                        sel_ex_id = sel_ex_str.split(" — ")[0].strip()
                        match_ex = df_sb[df_sb["Entry_ID"] == sel_ex_id]

                        if not match_ex.empty:
                            ex_row = match_ex.iloc[-1].to_dict()

                            ex_c1, ex_c2 = st.columns(2)
                            with ex_c1:
                                adm_b_cat = st.selectbox("Examinee Category*", ["First-Time Taker", "Retaker"], index=safe_index(["First-Time Taker", "Retaker"], ex_row.get("Examinee_Category")), key=f"adm_ex_cat_{sel_ex_id}")
                                
                                months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                                years_list = [str(y) for y in range(2000, 2041)]
                                cur_date_str = ex_row.get("Board_Exam_Date", "April 2024")
                                cur_m, cur_y, cur_note = "April", "2024", ""
                                for m in months_list:
                                    if m.lower() in cur_date_str.lower(): cur_m = m; break
                                for y in years_list:
                                    if y in cur_date_str: cur_y = y; break
                                if "(" in cur_date_str and ")" in cur_date_str:
                                    cur_note = cur_date_str.split("(")[1].split(")")[0].strip()

                                m_col, y_col = st.columns(2)
                                with m_col:
                                    adm_b_month = st.selectbox("Exam Month*", months_list, index=safe_index(months_list, cur_m, default=3), key=f"adm_ex_m_{sel_ex_id}")
                                with y_col:
                                    adm_b_year = st.selectbox("Exam Year*", years_list, index=safe_index(years_list, cur_y, default=24), key=f"adm_ex_y_{sel_ex_id}")

                                adm_b_note = st.text_input("Special Batch Note (Optional)", value=cur_note, key=f"adm_ex_note_{sel_ex_id}")
                                adm_b_weak = st.selectbox("Perceived Weakest Subject Area*", weak_opts, index=safe_index(weak_opts, ex_row.get("Perceived_Weakest_Subject"), default=3), key=f"adm_ex_weak_{sel_ex_id}")

                            with ex_c2:
                                adm_b_rev = st.selectbox("Review Center Attended*", rev_opts, index=safe_index(rev_opts, ex_row.get("Review_Center")), key=f"adm_ex_rev_{sel_ex_id}")
                                adm_b_mode = st.selectbox("Review Delivery Mode*", ["Face-to-Face / In-Person", "Online / Virtual Review", "Hybrid (Face-to-Face & Online)", "Self-Study"], index=safe_index(["Face-to-Face / In-Person", "Online / Virtual Review", "Hybrid (Face-to-Face & Online)", "Self-Study"], ex_row.get("Review_Mode")), key=f"adm_ex_mode_{sel_ex_id}")
                                rem_opts = ["Passed", "Failed / Retaking", "Deferred / Did Not Pursue", "Scheduled to Take / Upcoming Examinee"]
                                adm_b_rem = st.selectbox("Exam Result / Remarks*", rem_opts, index=safe_index(rem_opts, ex_row.get("Remarks")), key=f"adm_ex_rem_{sel_ex_id}")

                            adm_is_sched = (adm_b_rem == "Scheduled to Take / Upcoming Examinee")
                            st.markdown("**Subject Ratings & PRC Information:**")
                            adm_col_mst, _ = st.columns([1, 3])
                            with adm_col_mst:
                                adm_b_mst = st.text_input("Mathematics, Surveying and Transportation Engineering Rating (%)", value=ex_row.get("MST_Rating", ""), disabled=adm_is_sched, key=f"adm_ex_mst_{sel_ex_id}")
                            adm_col_hge, _ = st.columns([1, 3])
                            with adm_col_hge:
                                adm_b_hge = st.text_input("Hydraulics and Geotechnical Engineering Rating (%)", value=ex_row.get("HGE_Rating", ""), disabled=adm_is_sched, key=f"adm_ex_hge_{sel_ex_id}")
                            adm_col_sec, _ = st.columns([1, 3])
                            with adm_col_sec:
                                adm_b_sec = st.text_input("Principles of Structural Analysis and Design Rating (%)", value=ex_row.get("SEC_Rating", ""), disabled=adm_is_sched, key=f"adm_ex_sec_{sel_ex_id}")

                            r_sub1, r_sub2, _, _ = st.columns(4)
                            with r_sub1:
                                adm_b_ovr = st.text_input("Overall PRC Rating (%)", value=ex_row.get("Overall_PRC_Rating", ""), disabled=adm_is_sched, key=f"adm_ex_ovr_{sel_ex_id}")
                            with r_sub2:
                                adm_b_lic = st.text_input("PRC License No.", value=ex_row.get("PRC_License_Number", ""), disabled=adm_is_sched, key=f"adm_ex_lic_{sel_ex_id}")

                            if st.button("💾 Save Board Exam Edits", key=f"btn_save_adm_exam_{sel_ex_id}"):
                                missing_adm_exam = []
                                if not adm_is_sched:
                                    if not adm_b_ovr.strip():
                                        missing_adm_exam.append("Overall PRC Rating (%)")
                                    else:
                                        try: float(adm_b_ovr.strip())
                                        except ValueError: missing_adm_exam.append("Valid Overall PRC Rating (%) (numeric only)")
                                    if adm_b_mst.strip():
                                        try: float(adm_b_mst.strip())
                                        except ValueError: missing_adm_exam.append("Valid Mathematics, Surveying and Transportation Engineering Rating (%) (numeric only)")
                                    if adm_b_hge.strip():
                                        try: float(adm_b_hge.strip())
                                        except ValueError: missing_adm_exam.append("Valid Hydraulics and Geotechnical Engineering Rating (%) (numeric only)")
                                    if adm_b_sec.strip():
                                        try: float(adm_b_sec.strip())
                                        except ValueError: missing_adm_exam.append("Valid Principles of Structural Analysis and Design Rating (%) (numeric only)")

                                if missing_adm_exam:
                                    err_list = "\n".join([f"• {m}" for m in missing_adm_exam])
                                    st.error(f"⚠️ Please correct the following errors before saving board exam edits:\n\n{err_list}")
                                else:
                                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                full_date_str = f"{adm_b_month} {adm_b_year}"
                                if adm_b_note.strip(): full_date_str += f" ({adm_b_note.strip()})"

                                upd_ex_entry = [
                                    now_str, sel_ex_id, sel_sid, f"{st_match.get('First_Name','')} {st_match.get('Last_Name','')}".strip(),
                                    full_date_str, adm_b_cat, adm_b_weak, adm_b_rev, adm_b_mode,
                                    adm_b_ovr.strip() if not adm_is_sched else "N/A",
                                    adm_b_mst.strip() if not adm_is_sched else "N/A",
                                    adm_b_hge.strip() if not adm_is_sched else "N/A",
                                    adm_b_sec.strip() if not adm_is_sched else "N/A",
                                    adm_b_rem,
                                    adm_b_lic.strip() if not adm_is_sched else "N/A"
                                ]
                                df_b_upd = df_b[df_b["Entry_ID"] != sel_ex_id]
                                df_b_upd = pd.concat([df_b_upd, pd.DataFrame([dict(zip(HEADERS_BOARD_EXAM, upd_ex_entry))])], ignore_index=True)
                                df_b_upd.to_csv(FILE_BOARD_EXAM, index=False)
                                st.session_state["admin_flash_msg"] = f"Board exam record '{sel_ex_id}' updated successfully!"
                                st.rerun()

                # INSPECTOR SUB-TAB 3: CAREER TRACER
                with exp_t3:
                    df_st = df_t[df_t["Student_ID"].astype(str).str.strip().str.upper() == sel_sid]
                    if df_st.empty:
                        st.info("No career or business entries logged for this student.")
                    else:
                        st.markdown("##### Logged Career & Business History Summary")
                        st.dataframe(df_st[["Tracer_ID", "Employer_Or_Firm_Name", "Position_Or_Role", "Work_Setup", "Job_Alignment", "Work_Location", "Salary_Bracket", "Start_Year", "End_Year"]], use_container_width=True)

                        st.divider()
                        st.markdown("##### Edit Selected Career or Business Record")

                        st_entries = [f"{r['Tracer_ID']} — {r['Employer_Or_Firm_Name']} | {r['Position_Or_Role']} ({r['Work_Setup']})" for idx, r in df_st.iterrows()]
                        sel_tr_str = st.selectbox("Select Career/Business Record to Edit:", st_entries, key=f"st_tr_select_v18_{sel_sid}")
                        sel_tr_id = sel_tr_str.split(" — ")[0].strip()
                        match_tr = df_st[df_st["Tracer_ID"] == sel_tr_id]

                        if not match_tr.empty:
                            tr_row = match_tr.iloc[-1].to_dict()

                            setup_opts = [
                                "Government / Public Sector Employee",
                                "Private / Corporate Employee",
                                "Academe / Educational Institution",
                                "Overseas / OFW Engineer",
                                "Business Owner / Entrepreneur / Independent Consultant"
                            ]
                            adm_t_setup = st.selectbox("Employment Sector / Work Setup*", setup_opts, index=safe_index(setup_opts, tr_row.get("Work_Setup"), default=1), key=f"adm_tr_setup_{sel_tr_id}")
                            adm_is_biz = (adm_t_setup == "Business Owner / Entrepreneur / Independent Consultant")

                            tc1, tc2 = st.columns(2)
                            with tc1:
                                if adm_is_biz:
                                    adm_t_emp = st.text_input("Business / Firm Name*", value=tr_row.get("Employer_Or_Firm_Name", ""), key=f"adm_tr_emp_{sel_tr_id}")
                                    role_opts = ["Founder / Owner", "Managing Partner", "Principal Structural Consultant", "General Contractor", "Independent Engineering Consultant"]
                                    adm_t_pos = st.selectbox("Role / Ownership Title*", role_opts, index=safe_index(role_opts, tr_row.get("Position_Or_Role")), key=f"adm_tr_pos_{sel_tr_id}")
                                    cat_opts = ["PCAB Licensed Contractor", "Structural / Civil Consultancy Firm", "Construction Material Supply", "Project Management Services", "Non-Engineering Venture"]
                                    adm_t_biz_cat = st.selectbox("Business Category*", cat_opts, index=safe_index(cat_opts, tr_row.get("Business_Category")), key=f"adm_tr_cat_{sel_tr_id}")
                                    reg_opts = ["DTI Registered Sole Proprietorship", "SEC Registered Corporation / Partnership", "Unregistered / Informal", "In Process"]
                                    adm_t_reg = st.selectbox("DTI / SEC Registration Status*", reg_opts, index=safe_index(reg_opts, tr_row.get("DTI_SEC_Reg")), key=f"adm_tr_reg_{sel_tr_id}")
                                else:
                                    adm_t_emp = st.text_input("Employer / Institution / Agency Name*", value=tr_row.get("Employer_Or_Firm_Name", ""), key=f"adm_tr_emp_{sel_tr_id}")
                                    adm_t_pos = st.text_input("Job Title / Position*", value=tr_row.get("Position_Or_Role", ""), key=f"adm_tr_pos_{sel_tr_id}")
                                    type_opts = ["Permanent / Regular", "Contractual / Job Order", "Probationary", "Part-Time / Project-Based"]
                                    adm_t_emp_type = st.selectbox("Employment Status*", type_opts, index=safe_index(type_opts, tr_row.get("Employment_Type")), key=f"adm_tr_type_{sel_tr_id}")
                                    lvl_opts = ["Entry-Level / Junior Engineer", "Mid-Level / Senior Engineer", "Supervisory / Managerial", "Executive / Director"]
                                    adm_t_lvl = st.selectbox("Position Level*", lvl_opts, index=safe_index(lvl_opts, tr_row.get("Position_Level")), key=f"adm_tr_lvl_{sel_tr_id}")

                            with tc2:
                                if adm_is_biz:
                                    scale_opts = ["Micro Enterprise (1-9 employees)", "Small Enterprise (10-49 employees)", "Medium Enterprise (50-249 employees)", "Large Enterprise (250+ employees)"]
                                    adm_t_scale = st.selectbox("Business Scale*", scale_opts, index=safe_index(scale_opts, tr_row.get("Business_Scale")), key=f"adm_tr_scale_{sel_tr_id}")
                                    op_opts = ["Less than 1 Year", "1–3 Years", "4–7 Years", "8+ Years"]
                                    adm_t_op_yrs = st.selectbox("Years in Operation*", op_opts, index=safe_index(op_opts, tr_row.get("Years_Operating"), default=1), key=f"adm_tr_op_{sel_tr_id}")
                                    sal_biz_opts = ["Below ₱50,000", "₱50,000 – ₱100,000", "₱100,000 – ₱250,000", "₱250,000 – ₱500,000", "Above ₱500,000", "Prefer Not to Disclose"]
                                    adm_t_sal = st.selectbox("Gross Monthly Business Revenue*", sal_biz_opts, index=safe_index(sal_biz_opts, tr_row.get("Salary_Bracket"), default=1), key=f"adm_tr_sal_{sel_tr_id}")
                                    adm_t_loc = st.text_input("Office / Headquarters Location*", value=tr_row.get("Work_Location", ""), key=f"adm_tr_loc_{sel_tr_id}")
                                    adm_t_start = st.text_input("Year Founded*", value=tr_row.get("Start_Year", ""), key=f"adm_tr_start_{sel_tr_id}")
                                    adm_t_end, adm_t_align = "Present", "Directly Related to Civil Engineering"
                                else:
                                    sal_emp_opts = ["Below ₱20,000", "₱20,000 – ₱40,000", "₱40,000 – ₱70,000", "₱70,000 – ₱100,000", "Above ₱100,000", "Prefer Not to Disclose"]
                                    adm_t_sal = st.selectbox("Gross Monthly Salary Bracket*", sal_emp_opts, index=safe_index(sal_emp_opts, tr_row.get("Salary_Bracket"), default=1), key=f"adm_tr_sal_{sel_tr_id}")
                                    align_opts = ["Directly Related to Civil Engineering", "Partially Related", "Unrelated"]
                                    adm_t_align = st.selectbox("Job Alignment*", align_opts, index=safe_index(align_opts, tr_row.get("Job_Alignment")), key=f"adm_tr_align_{sel_tr_id}")
                                    adm_t_loc = st.text_input("Work Location*", value=tr_row.get("Work_Location", ""), key=f"adm_tr_loc_{sel_tr_id}")
                                    y1, y2 = st.columns(2)
                                    with y1: adm_t_start = st.text_input("Start Year*", value=tr_row.get("Start_Year", ""), key=f"adm_tr_start_{sel_tr_id}")
                                    with y2: adm_t_end = st.text_input("End Year (or Present)*", value=tr_row.get("End_Year", "Present"), key=f"adm_tr_end_{sel_tr_id}")
                                    adm_t_biz_cat, adm_t_reg, adm_t_scale, adm_t_op_yrs = "N/A", "N/A", "N/A", "N/A"

                            if st.button("💾 Save Career Edits", key=f"btn_save_adm_tracer_{sel_tr_id}"):
                                now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                upd_tr_entry = [
                                    now_str, sel_tr_id, sel_sid, f"{st_match.get('First_Name','')} {st_match.get('Last_Name','')}".strip(), adm_t_setup,
                                    adm_t_emp.strip(), adm_t_pos.strip(), adm_t_lvl if not adm_is_biz else "Owner / Principal", adm_t_align,
                                    adm_t_loc.strip(), adm_t_emp_type if not adm_is_biz else "Self-Employed / Owner", adm_(t_sal if t_sal else 'Not Specified'), adm_t_start.strip(), adm_t_end.strip(),
                                    adm_t_biz_cat, adm_t_reg, adm_t_scale, adm_t_op_yrs
                                ]
                                df_t_upd = df_t[df_t["Tracer_ID"] != sel_tr_id]
                                df_t_upd = pd.concat([df_t_upd, pd.DataFrame([dict(zip(HEADERS_TRACER, upd_tr_entry))])], ignore_index=True)
                                df_t_upd.to_csv(FILE_TRACER, index=False)
                                st.session_state["admin_flash_msg"] = f"Career record '{sel_tr_id}' updated successfully!"
                                st.rerun()

                # INSPECTOR SUB-TAB 4: GRADUATE STUDIES
                with exp_t4:
                    df_sg = df_g[df_g["Student_ID"].astype(str).str.strip().str.upper() == sel_sid]
                    if df_sg.empty:
                        st.info("No graduate studies or accreditation entries logged for this student.")
                    else:
                        st.markdown("##### Logged Graduate Education & Accreditations Summary")
                        st.dataframe(df_sg[["Grad_ID", "Graduate_Degree", "Degree_Specified_Details", "Institution_Name", "Academic_Status", "Year_Conferred"]], use_container_width=True)

                        st.divider()
                        st.markdown("##### Edit Selected Graduate Education or Accreditation Record")

                        sg_entries = [f"{r['Grad_ID']} — {r['Graduate_Degree']} | {r['Degree_Specified_Details']} ({r['Institution_Name']})" for idx, r in df_sg.iterrows()]
                        sel_gr_str = st.selectbox("Select Graduate Entry to Edit:", sg_entries, key=f"sg_gr_select_v18_{sel_sid}")
                        sel_gr_id = sel_gr_str.split(" — ")[0].strip()
                        match_gr = df_sg[df_sg["Grad_ID"] == sel_gr_id]

                        if not match_gr.empty:
                            gr_row = match_gr.iloc[-1].to_dict()

                            deg_type_opts = [
                                "Master's Degree (e.g., MS Civil Engineering, MS Structural)",
                                "Doctoral Degree (e.g., PhD, DEng in Civil Engineering)",
                                "Professional Accreditation / Specialist Membership (e.g., ASEAN Eng, ASEP, PICE Fellow)",
                                "Others / Custom Accreditation"
                            ]
                            adm_g_deg_type = st.selectbox("Accreditation Type*", deg_type_opts, index=safe_index(deg_type_opts, gr_row.get("Graduate_Degree")), key=f"adm_gr_type_{sel_gr_id}")

                            gc1, gc2 = st.columns(2)
                            with gc1:
                                adm_g_title = st.text_input("Degree / Accreditation Title*", value=gr_row.get("Degree_Specified_Details", ""), key=f"adm_gr_title_{sel_gr_id}")
                                adm_g_inst = st.text_input("Institution / Organization Name*", value=gr_row.get("Institution_Name", ""), key=f"adm_gr_inst_{sel_gr_id}")
                            with gc2:
                                stat_opts = ["Completed / Graduated", "On-Going Coursework", "Thesis / Dissertation Stage", "Active License / Valid Membership"]
                                adm_g_status = st.selectbox("Academic / Accreditation Status*", stat_opts, index=safe_index(stat_opts, gr_row.get("Academic_Status")), key=f"adm_gr_stat_{sel_gr_id}")
                                adm_g_year = st.text_input("Year Conferred / Granted*", value=gr_row.get("Year_Conferred", ""), key=f"adm_gr_yr_{sel_gr_id}")

                            if st.button("💾 Save Graduate Edits", key=f"btn_save_adm_grad_{sel_gr_id}"):
                                now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                upd_gr_entry = [
                                    now_str, sel_gr_id, sel_sid, f"{st_match.get('First_Name','')} {st_match.get('Last_Name','')}".strip(),
                                    adm_g_deg_type, adm_g_title.strip(), "Civil Engineering", adm_g_inst.strip(),
                                    adm_g_status, adm_g_year.strip()
                                ]
                                df_g_upd = df_g[df_g["Grad_ID"] != sel_gr_id]
                                df_g_upd = pd.concat([df_g_upd, pd.DataFrame([dict(zip(HEADERS_GRAD_STUDIES, upd_gr_entry))])], ignore_index=True)
                                df_g_upd.to_csv(FILE_GRAD_STUDIES, index=False)
                                st.session_state["admin_flash_msg"] = f"Graduate study record '{sel_gr_id}' updated successfully!"
                                st.rerun()

                # INSPECTOR SUB-TAB 5: ALUMNI FEEDBACK
                with exp_t5:
                    df_sfb = df_fb[df_fb["Student_ID"].astype(str).str.strip().str.upper() == sel_sid]
                    if df_sfb.empty:
                        st.info("No feedback entries submitted by this student.")
                    else:
                        st.markdown("##### Submitted Feedback History Summary")
                        st.dataframe(df_sfb[["Feedback_ID", "Timestamp", "Category", "Subject_Title", "Message_Content"]], use_container_width=True)

                        st.divider()
                        st.markdown("##### Edit or Delete Selected Feedback Entry")

                        sfb_entries = [f"{r['Feedback_ID']} — {r['Category']} | {r['Subject_Title']} ({r['Timestamp'][:10]})" for idx, r in df_sfb.iterrows()]
                        sel_fb_str = st.selectbox("Select Feedback Submission to Edit / Delete:", sfb_entries, key=f"sfb_select_v18_{sel_sid}")
                        sel_fb_id = sel_fb_str.split(" — ")[0].strip()
                        match_fb = df_sfb[df_sfb["Feedback_ID"] == sel_fb_id]

                        if not match_fb.empty:
                            fb_row = match_fb.iloc[-1].to_dict()

                            fb_cats = [
                                "Curriculum & Coursework",
                                "Board Exam Review Support",
                                "Department Facilities & Equipment",
                                "Career & Industry Guidance",
                                "General Ideas & Suggestions"
                            ]
                            adm_fb_cat = st.selectbox("Feedback Category*", fb_cats, index=safe_index(fb_cats, fb_row.get("Category")), key=f"adm_fb_cat_{sel_fb_id}")
                            adm_fb_title = st.text_input("Subject / Topic Title*", value=fb_row.get("Subject_Title", ""), key=f"adm_fb_title_{sel_fb_id}")
                            adm_fb_msg = st.text_area("Detailed Feedback Content*", value=fb_row.get("Message_Content", ""), key=f"adm_fb_msg_{sel_fb_id}")

                            fb_adm_c1, fb_adm_c2 = st.columns(2)
                            with fb_adm_c1:
                                if st.button("💾 Save Feedback Edits", key=f"btn_save_adm_fb_{sel_fb_id}"):
                                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                    upd_fb_entry = [
                                        now_str, sel_fb_id, sel_sid, f"{st_match.get('First_Name','')} {st_match.get('Last_Name','')}".strip(),
                                        adm_fb_cat, adm_fb_title.strip(), adm_fb_msg.strip()
                                    ]
                                    df_fb_upd = df_fb[df_fb["Feedback_ID"] != sel_fb_id]
                                    df_fb_upd = pd.concat([df_fb_upd, pd.DataFrame([dict(zip(HEADERS_FEEDBACK, upd_fb_entry))])], ignore_index=True)
                                    df_fb_upd.to_csv(FILE_FEEDBACK, index=False)
                                    st.session_state["admin_flash_msg"] = f"Feedback entry '{sel_fb_id}' updated successfully!"
                                    st.rerun()

                            with fb_adm_c2:
                                if st.button("🗑️ Delete This Feedback Entry", key=f"btn_del_adm_fb_{sel_fb_id}"):
                                    df_fb_new = df_fb[df_fb["Feedback_ID"] != sel_fb_id]
                                    df_fb_new.to_csv(FILE_FEEDBACK, index=False)
                                    st.session_state["admin_flash_msg"] = f"Deleted feedback entry '{sel_fb_id}'."
                                    st.rerun()

    # --------------------------------------------------------------------------
    # ADMIN SECTION 4: ALUMNI FEEDBACK, IDEAS & CONCERNS HUB
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 4: Alumni Feedback, Ideas & Concerns Hub</div>', unsafe_allow_html=True)
    st.caption("Inspect constructive feedback, curriculum recommendations, and departmental ideas submitted by graduates.")

    if df_fb.empty:
        st.info("No alumni feedback entries logged in the database.")
    else:
        fb_options = []
        for idx, r_fb in df_fb.iterrows():
            fb_id_val = str(r_fb.get("Feedback_ID", "")).strip()
            name_val = str(r_fb.get("Full_Name", "")).strip()
            sid_val = str(r_fb.get("Student_ID", "")).strip()
            cat_val = str(r_fb.get("Category", "")).strip()
            date_val = str(r_fb.get("Timestamp", "")).strip()[:10]
            fb_options.append(f"{fb_id_val} — {name_val} ({sid_val}) | {cat_val} ({date_val})")

        sel_fb_str = st.selectbox(
            "Select an Alumni Feedback Submission to Inspect:",
            fb_options,
            index=0,
            key="sb_admin_fb_inspect_select"
        )

        if sel_fb_str:
            sel_fb_id = sel_fb_str.split(" — ")[0].strip()
            match_fb = df_fb[df_fb["Feedback_ID"] == sel_fb_id]

            if not match_fb.empty:
                r_fb_mat = match_fb.iloc[-1].to_dict()

                fb_sid = str(r_fb_mat.get("Student_ID", "")).strip().upper()
                s_match = df_a[df_a["Student_ID"].astype(str).str.strip().str.upper() == fb_sid] if not df_a.empty else pd.DataFrame()

                s_email = s_match.iloc[-1].get("Email", "N/A") if not s_match.empty else "N/A"
                s_mob = s_match.iloc[-1].get("Contact_Number", "N/A") if not s_match.empty else "N/A"

                st.markdown(f"""
                    <div class="history-card">
                        <h4>💬 [{r_fb_mat['Feedback_ID']}] {r_fb_mat['Subject_Title']}</h4>
                        <p><strong>Submitted By:</strong> {r_fb_mat['Full_Name']} (Student ID: <code>{r_fb_mat['Student_ID']}</code>)</p>
                        <p><strong>Contact Info:</strong> Email: {s_email} | Phone: {s_mob}</p>
                        <p><strong>Submitted On:</strong> {r_fb_mat['Timestamp']} | <strong>Category:</strong> {r_fb_mat['Category']}</p>
                        <hr style="margin: 0.5rem 0; border: 0; border-top: 1px solid #cbd5e1;">
                        <p><strong>Detailed Message Content:</strong></p>
                        <p style="background-color: #ffffff; padding: 0.75rem; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.95rem; line-height: 1.4;">
                            {r_fb_mat['Message_Content']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                fb_b1, fb_b2 = st.columns([1, 3])
                with fb_b1:
                    if st.button("🗑️ Delete Selected Feedback Entry", key=f"btn_del_fb_{sel_fb_id}"):
                        df_fb_new = df_fb[df_fb["Feedback_ID"] != sel_fb_id]
                        df_fb_new.to_csv(FILE_FEEDBACK, index=False)
                        st.session_state["admin_flash_msg"] = f"Deleted feedback entry '{sel_fb_id}'."
                        st.rerun()

        st.divider()
        st.markdown("##### Master Logbook of All Alumni Feedback Submissions")
        st.dataframe(
            df_fb[["Feedback_ID", "Timestamp", "Student_ID", "Full_Name", "Category", "Subject_Title", "Message_Content"]],
            use_container_width=True
        )

    # --------------------------------------------------------------------------
    # ADMIN SECTION 5: CQI INTERVENTIONS & STUDENT TAGGING MODULE
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 5: CQI Interventions & Student Tagging Module</div>', unsafe_allow_html=True)
    st.caption("Target students needing academic support based on exam results or perceived weak subjects, and log interventions for accreditation compliance.")

    cqi_tab1, cqi_tab2 = st.tabs([
        "Filter & Tag CQI Interventions",
        "Master Logbook of CQI Actions"
    ])

    with cqi_tab1:
        st.markdown("##### 1. Filter Target Student Cohorts")
        flt_c1, flt_c2, flt_c3 = st.columns(3)
        with flt_c1:
            f_rem = st.selectbox("Filter by Exam Result Status:", ["All Results", "Failed / Retaking", "Passed", "Deferred / Did Not Pursue", "Scheduled to Take / Upcoming Examinee"], key="f_cqi_rem")
        with flt_c2:
            f_weak = st.selectbox("Filter by Perceived Weakest Subject:", ["All Subjects"] + weak_opts, key="f_cqi_weak")
        with flt_c3:
            f_cat = st.selectbox("Filter by Examinee Category:", ["All Categories", "First-Time Taker", "Retaker"], key="f_cqi_cat")

        if not df_a.empty:
            df_merged = df_a.merge(df_b, on="Student_ID", how="left", suffixes=('', '_exam'))

            if f_rem != "All Results":
                df_merged = df_merged[df_merged["Remarks"] == f_rem]
            if f_weak != "All Subjects":
                df_merged = df_merged[df_merged["Perceived_Weakest_Subject"] == f_weak]
            if f_cat != "All Categories":
                df_merged = df_merged[df_merged["Examinee_Category"] == f_cat]

            df_merged_unique = df_merged.drop_duplicates(subset=["Student_ID"], keep="last")

            st.markdown(f"**Filtered Candidates ({len(df_merged_unique)} Students Found):**")

            if df_merged_unique.empty:
                st.info("No students match the current filter criteria.")
                selected_tagged_sids = []
            else:
                st.dataframe(
                    df_merged_unique[["Student_ID", "First_Name", "Last_Name", "Degree_Program", "Perceived_Weakest_Subject", "Remarks", "Contact_Number"]],
                    use_container_width=True
                )

                student_tag_options = [f"{r['Student_ID']} — {r['First_Name']} {r['Last_Name']}" for idx, r in df_merged_unique.iterrows()]

                selected_tagged_strs = st.multiselect(
                    "Tag Selected Students for CQI Intervention:*",
                    options=student_tag_options,
                    default=[],
                    key="ms_cqi_tagged_students"
                )

                selected_tagged_sids = [s.split(" — ")[0].strip() for s in selected_tagged_strs]

            st.markdown("##### 2. Log Intervention Details")
            cq_c1, cq_c2 = st.columns(2)
            with cq_c1:
                cqi_date = st.date_input("Target / Execution Date of Intervention*", value=datetime.date.today(), format="MM/DD/YYYY", key="cqi_exec_date")
                cqi_cat = st.selectbox(
                    "Intervention Category*",
                    [
                        "Subject Refresher Webinar / Review Session",
                        "Faculty Academic Consultation / Advisory",
                        "Peer Mentorship & Tutoring Group",
                        "Mock Board Examination Session",
                        "PRC Filing & Document Assistance",
                        "Curriculum & Syllabus Enhancement"
                    ],
                    index=None, placeholder="Select Intervention Category...", key="cqi_cat_sel"
                )
                cqi_faculty = st.text_input("Faculty / Department Person-in-Charge*", placeholder="e.g., Engr. Santos / Department Chair", key="cqi_fac_incharge")

            with cq_c2:
                cqi_desc = st.text_area("Intervention Title & Action Description*", placeholder="e.g., Conducted 3-day intensive refresher on Hydraulics & Geotechnical Engineering equations.", key="cqi_desc_txt")
                cqi_notes = st.text_area("Outcome / Monitoring Notes (Optional)", placeholder="e.g., 25 out of 30 retakers attended; post-test scores improved by 18%.", key="cqi_notes_txt")

            if st.button("💾 Log CQI Intervention & Tag Selected Students", key="btn_save_cqi"):
                missing_cqi = []
                if not selected_tagged_sids: missing_cqi.append("Tagged Students (select at least 1 student)")
                if cqi_cat is None: missing_cqi.append("Intervention Category")
                if not cqi_faculty.strip(): missing_cqi.append("Faculty / Department Person-in-Charge")
                if not cqi_desc.strip(): missing_cqi.append("Intervention Title & Action Description")

                if missing_cqi:
                    st.error("⚠️ Please complete the following required fields before logging CQI intervention:\n\n" + "\n".join([f"• {m}" for m in missing_cqi]))
                else:
                    now_str = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    cqi_id = f"CQI-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

                    tagged_sids_str = ", ".join(selected_tagged_sids)
                    tagged_names_str = ", ".join([s.split(" — ")[1] for s in selected_tagged_strs])

                    new_cqi_row = [
                        now_str, cqi_id, cqi_date.strftime("%m/%d/%Y"), cqi_cat,
                        f"Targeted {len(selected_tagged_sids)} students ({f_rem}, {f_weak})",
                        cqi_desc.strip(), cqi_faculty.strip(),
                        tagged_sids_str, tagged_names_str, cqi_notes.strip()
                    ]

                    with open(FILE_CQI, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(new_cqi_row)

                    st.session_state["cqi_flash_msg"] = f"🎉 CQI Intervention '{cqi_id}' successfully logged and tagged to {len(selected_tagged_sids)} students!"
                    st.rerun()

    with cqi_tab2:
        st.markdown("##### Master Logbook of Continuous Quality Improvement Actions")
        if df_cqi.empty:
            st.info("No CQI interventions logged yet.")
        else:
            st.dataframe(
                df_cqi[["Intervention_ID", "Target_Execution_Date", "Intervention_Category", "Faculty_In_Charge", "Action_Taken_Description", "Tagged_Student_IDs"]],
                use_container_width=True
            )

            st.divider()
            st.markdown("##### Detailed Action Cards & Tagged Student Roster Inspector")

            cqi_inspect_opts = []
            for idx, c_r in df_cqi.iterrows():
                cqi_inspect_opts.append(f"{c_r['Intervention_ID']} — {c_r['Intervention_Category']} ({c_r['Target_Execution_Date']})")

            sel_cqi_str = st.selectbox(
                "Select a CQI Intervention to View Tagged Roster:",
                cqi_inspect_opts,
                index=0,
                key="sb_cqi_inspect_select"
            )

            if sel_cqi_str:
                sel_cqi_id = sel_cqi_str.split(" — ")[0].strip()
                match_cqi = df_cqi[df_cqi["Intervention_ID"] == sel_cqi_id]

                if not match_cqi.empty:
                    c_row = match_cqi.iloc[-1].to_dict()

                    st.markdown(f"""
                        <div class="history-card">
                            <h4>📋 {c_row['Intervention_ID']}: {c_row['Intervention_Category']} (Scheduled/Executed: {c_row['Target_Execution_Date']})</h4>
                            <p><strong>Faculty-in-Charge:</strong> {c_row['Faculty_In_Charge']}</p>
                            <p><strong>Target Cohort Description:</strong> {c_row['Target_Cohort_Description']}</p>
                            <p><strong>Action Description:</strong> {c_row['Action_Taken_Description']}</p>
                            <p><strong>Outcome Notes:</strong> {c_row['Outcome_Notes'] if c_row['Outcome_Notes'] else 'N/A'}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    tagged_sids = [s.strip().upper() for s in c_row['Tagged_Student_IDs'].split(",") if s.strip()]

                    st.markdown(f"**Tagged Student Roster ({len(tagged_sids)} Students):**")

                    if not df_a.empty and tagged_sids:
                        df_tagged_students = df_a[df_a["Student_ID"].astype(str).str.strip().str.upper().isin(tagged_sids)]
                        if not df_tagged_students.empty:
                            st.dataframe(
                                df_tagged_students[["Student_ID", "First_Name", "Last_Name", "Degree_Program", "Email", "Contact_Number"]],
                                use_container_width=True
                            )
                        else:
                            st.caption(f"Tagged Student IDs: `{', '.join(tagged_sids)}`")

            st.divider()

            # Delete CQI Action Option
            st.markdown("##### 🗑️ Delete CQI Action Item")
            sel_del_cqi_str = st.selectbox(
                "Select a CQI Action to Delete:",
                cqi_inspect_opts,
                key="sb_cqi_del_select"
            )
            if st.button("🗑️ Delete Selected CQI Action", key="btn_del_cqi_item"):
                sel_del_id = sel_del_cqi_str.split(" — ")[0].strip()
                df_cqi_new = df_cqi[df_cqi["Intervention_ID"] != sel_del_id]
                df_cqi_new.to_csv(FILE_CQI, index=False)
                st.session_state["cqi_flash_msg"] = f"Deleted CQI Action Item '{sel_del_id}'."
                st.rerun()

    # --------------------------------------------------------------------------
    
    # --------------------------------------------------------------------------
    # ADMIN SECTION 6: MASTER DATA MANAGEMENT (EXPORT & IMPORT)
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header">Section 6: Master Data Management (Export & Import)</div>', unsafe_allow_html=True)

    # Top row: Excel Master Download
    st.markdown("##### 📥 Export Master Database")
    
    excel_buffer = io.BytesIO()
    excel_ready = False
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_a.to_excel(writer, sheet_name='Alumni_Information', index=False)
            df_b.to_excel(writer, sheet_name='Board_Exam_Data', index=False)
            df_t.to_excel(writer, sheet_name='Career_Tracer', index=False)
            df_g.to_excel(writer, sheet_name='Graduate_Studies', index=False)
            df_cqi.to_excel(writer, sheet_name='CQI_Interventions', index=False)
            df_fb.to_excel(writer, sheet_name='Alumni_Feedback', index=False)
        excel_bytes = excel_buffer.getvalue()
        excel_ready = True
    except Exception as e:
        excel_ready = False

    c_ex1, c_ex2 = st.columns([1.2, 2.8])
    with c_ex1:
        if excel_ready:
            st.download_button(
                label="📥 Download Master Database (.xlsx)",
                data=excel_bytes,
                file_name="USJ-R_CE_Alumni_Master_Database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Install openpyxl (pip install openpyxl) for Excel export.")

    st.markdown("##### 📄 Individual CSV Downloads")
    exp_col1, exp_col2, exp_col3, exp_col4, exp_col5, exp_col6 = st.columns(6)

    with exp_col1:
        csv_a = df_a.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Alumni Info", data=csv_a, file_name="alumni_information_master.csv", mime="text/csv")
    with exp_col2:
        csv_b = df_b.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Board Exam", data=csv_b, file_name="board_exam_data_master.csv", mime="text/csv")
    with exp_col3:
        csv_t = df_t.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Career Tracer", data=csv_t, file_name="alumni_career_tracer_master.csv", mime="text/csv")
    with exp_col4:
        csv_g = df_g.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Grad Studies", data=csv_g, file_name="graduate_studies_master.csv", mime="text/csv")
    with exp_col5:
        csv_cqi = df_cqi.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CQI", data=csv_cqi, file_name="cqi_interventions_master.csv", mime="text/csv")
    with exp_col6:
        csv_fb = df_fb.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Feedback", data=csv_fb, file_name="alumni_feedback_master.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("##### 📤 Import / Restore Master Database (.xlsx or .csv)")

    restore_mode = st.radio(
        "Select Import Action Mode:",
        ["Merge & Append (Add missing entries safely)", "Full Overwrite / Restore (Replace current working database)"],
        index=0,
        horizontal=True
    )

    uploaded_file = st.file_uploader(
        "Drag and drop your master database file (.xlsx or .csv):",
        type=["xlsx", "csv"],
        key="master_db_uploader"
    )

    if uploaded_file is not None:
        if st.button("🚀 Process & Apply Database Import"):
            try:
                fname = uploaded_file.name.lower()
                success_count = 0

                db_map = {
                    "Alumni_Information": (FILE_ALUMNI_INFO, HEADERS_ALUMNI_INFO, "Student_ID"),
                    "Board_Exam_Data": (FILE_BOARD_EXAM, HEADERS_BOARD_EXAM, "Entry_ID"),
                    "Career_Tracer": (FILE_TRACER, HEADERS_TRACER, "Tracer_ID"),
                    "Graduate_Studies": (FILE_GRAD_STUDIES, HEADERS_GRAD_STUDIES, "Grad_ID"),
                    "CQI_Interventions": (FILE_CQI, HEADERS_CQI, "Intervention_ID"),
                    "Alumni_Feedback": (FILE_FEEDBACK, HEADERS_FEEDBACK, "Feedback_ID")
                }

                if fname.endswith(".xlsx"):
                    xls = pd.ExcelFile(uploaded_file)
                    for sheet_name in xls.sheet_names:
                        matched_key = None
                        for key in db_map:
                            if key.lower() in sheet_name.lower().replace(" ", "_"):
                                matched_key = key
                                break
                        if matched_key:
                            file_path, headers, pk_col = db_map[matched_key]
                            df_upload = pd.read_excel(xls, sheet_name=sheet_name).astype(str)

                            for col in headers:
                                if col not in df_upload.columns:
                                    df_upload[col] = ""
                            df_upload = df_upload[headers]

                            if "Full Overwrite" in restore_mode:
                                df_upload.to_csv(file_path, index=False, encoding="utf-8")
                                success_count += 1
                            else:
                                df_curr = load_csv_safely(file_path, headers)
                                if df_curr.empty:
                                    df_upload.to_csv(file_path, index=False, encoding="utf-8")
                                else:
                                    existing_pks = set(df_curr[pk_col].astype(str).str.strip().str.upper())
                                    new_rows = df_upload[~df_upload[pk_col].astype(str).str.strip().str.upper().isin(existing_pks)]
                                    if not new_rows.empty:
                                        df_combined = pd.concat([df_curr, new_rows], ignore_index=True)
                                        df_combined.to_csv(file_path, index=False, encoding="utf-8")
                                success_count += 1

                elif fname.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file).astype(str)
                    matched_key = None
                    for key, (f_path, headers, pk_col) in db_map.items():
                        if set(headers).issubset(set(df_upload.columns)) or pk_col in df_upload.columns:
                            matched_key = key
                            break
                    
                    if matched_key:
                        file_path, headers, pk_col = db_map[matched_key]
                        for col in headers:
                            if col not in df_upload.columns:
                                df_upload[col] = ""
                        df_upload = df_upload[headers]

                        if "Full Overwrite" in restore_mode:
                            df_upload.to_csv(file_path, index=False, encoding="utf-8")
                            success_count += 1
                        else:
                            df_curr = load_csv_safely(file_path, headers)
                            if df_curr.empty:
                                df_upload.to_csv(file_path, index=False, encoding="utf-8")
                            else:
                                existing_pks = set(df_curr[pk_col].astype(str).str.strip().str.upper())
                                new_rows = df_upload[~df_upload[pk_col].astype(str).str.strip().str.upper().isin(existing_pks)]
                                if not new_rows.empty:
                                    df_combined = pd.concat([df_curr, new_rows], ignore_index=True)
                                    df_combined.to_csv(file_path, index=False, encoding="utf-8")
                            success_count += 1
                    else:
                        st.error("Could not automatically recognize the CSV columns. Please ensure it matches one of the master database schemas.")

                if success_count > 0:
                    st.success(f"🎉 Database import completed successfully! Updated {success_count} table(s).")
                    st.rerun()

            except Exception as ex:
                st.error(f"❌ Error during database import: {str(ex)}")
