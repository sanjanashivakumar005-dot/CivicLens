import streamlit as st
from datetime import datetime

from database.init_db import initialize_database

from services.issue_service import (
    create_issue,
    get_all_issues,
    get_issue_by_id
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CivicLens | Smart City",
    page_icon="🏙️",
    layout="wide"
)

CURRENT_USER_ID = 1

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;600;700&display=swap');

.stApp {
    background: #101827;
    color: #E7EDF5;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: #172235;
    border-right: 1px solid #2B3A50;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F3F7FC !important;
}

p, label {
    color: #D7E2EE;
}

.hero {
    background: linear-gradient(120deg, #182B46, #174E67);
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #2C6279;
    margin-bottom: 20px;
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #304159;
    background: #202E43;
    color: #E7EDF5;
    padding: 12px;
    font-weight: 600;
}

[data-testid="stSidebar"] .stButton button:hover {
    border-color: #43D9C3;
    background: #25485A;
    color: #43D9C3;
}

[data-testid="stMetric"] {
    background: #192438;
    border: 1px solid #34445C;
    padding: 18px;
    border-radius: 15px;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #1B2638 !important;
    color: white !important;
}

.stButton button {
    border-radius: 10px;
    font-weight: 600;
}

div[data-testid="stExpander"] {
    background-color: #192438;
    border: 1px solid #34445C;
    border-radius: 12px;
}

.footer {
    color: #8FA3BA;
    text-align: center;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# ISSUE NORMALIZATION
# =========================================================

def normalize_issue(issue):

    if isinstance(issue, dict):
        return issue

    if isinstance(issue, str):
        return {
            "issue_id": None,
            "title": issue,
            "category": "Unknown",
            "description": "",
            "status": "Unknown",
            "severity": "Medium",
            "address": "",
            "ward_zone": "",
            "upvotes_count": 0
        }

    if issue is None:
        return {}

    return {
        "issue_id": getattr(issue, "issue_id", None),
        "user_id": getattr(issue, "user_id", None),
        "assigned_staff_id": getattr(issue, "assigned_staff_id", None),
        "title": getattr(issue, "title", "Untitled Issue"),
        "category": getattr(issue, "category", "Unknown"),
        "description": getattr(issue, "description", ""),
        "status": getattr(issue, "status", "Unknown"),
        "severity": getattr(issue, "severity", "Medium"),
        "address": getattr(issue, "address", ""),
        "ward_zone": getattr(issue, "ward_zone", ""),
        "latitude": getattr(issue, "latitude", None),
        "longitude": getattr(issue, "longitude", None),
        "upvotes_count": getattr(issue, "upvotes_count", 0),
        "created_at": getattr(issue, "created_at", None),
        "updated_at": getattr(issue, "updated_at", None)
    }


# =========================================================
# SAFE VALUE ACCESS
# =========================================================

def get_value(issue, key, default=""):

    if not isinstance(issue, dict):
        issue = normalize_issue(issue)

    value = issue.get(key, default)

    return default if value is None else value


# =========================================================
# LOAD ISSUES FROM DATABASE
# =========================================================

def load_issues():

    try:

        result = get_all_issues()

        if not result:
            return []

        # IMPORTANT:
        # issue_service.get_all_issues() returns a dictionary:
        # {
        #   "success": True,
        #   "total_issues": ...,
        #   "issues": [...]
        # }

        if isinstance(result, dict):

            if not result.get("success", False):
                st.error(
                    result.get(
                        "message",
                        "Unable to load issues from database."
                    )
                )
                return []

            issues_data = result.get("issues", [])

            if not isinstance(issues_data, (list, tuple)):
                return []

            return [
                normalize_issue(issue)
                for issue in issues_data
            ]

        # Support direct list responses as well

        if isinstance(result, (list, tuple)):

            return [
                normalize_issue(issue)
                for issue in result
            ]

        return []

    except Exception as error:

        st.error(f"Database error: {error}")

        return []


# =========================================================
# DASHBOARD METRICS
# =========================================================

def calculate_metrics(issues):

    total = len(issues)

    pending = sum(
        1 for issue in issues
        if "pending" in str(
            get_value(issue, "status", "")
        ).lower()
    )

    assigned = sum(
        1 for issue in issues
        if str(
            get_value(issue, "status", "")
        ).lower() == "assigned"
    )

    in_progress = sum(
        1 for issue in issues
        if "progress" in str(
            get_value(issue, "status", "")
        ).lower()
    )

    resolved = sum(
        1 for issue in issues
        if any(
            word in str(
                get_value(issue, "status", "")
            ).lower()
            for word in [
                "resolved",
                "completed",
                "closed"
            ]
        )
    )

    return total, pending, assigned, in_progress, resolved


# =========================================================
# DISPLAY ISSUE
# =========================================================

def display_issue(issue):

    issue = normalize_issue(issue)

    issue_id = get_value(issue, "issue_id", "N/A")
    title = get_value(issue, "title", "Untitled Issue")
    category = get_value(issue, "category", "Unknown")
    description = get_value(issue, "description", "No description")
    status = get_value(issue, "status", "Unknown")
    severity = get_value(issue, "severity", "Medium")
    address = get_value(issue, "address", "Location not provided")
    ward = get_value(issue, "ward_zone", "")
    upvotes = get_value(issue, "upvotes_count", 0)

    with st.expander(f"📌 #{issue_id} — {title}"):

        st.markdown(f"**Category:** {category}")
        st.markdown(f"**Severity:** {severity}")
        st.markdown(f"**Status:** {status}")

        st.write(description)

        st.markdown(f"📍 **Location:** {address}")

        if ward:
            st.markdown(f"🏘️ **Ward / Zone:** {ward}")

        st.markdown(f"👍 **Upvotes:** {upvotes}")


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown("# 🏙️ CivicLens")
    st.caption("SMART CITY OPERATIONS")

    st.divider()

    pages = [
        "Dashboard",
        "Report Issue",
        "Explore Issues",
        "Track Complaints",
        "About CivicLens"
    ]

    icons = {
        "Dashboard": "🏙️",
        "Report Issue": "📝",
        "Explore Issues": "🔎",
        "Track Complaints": "📍",
        "About CivicLens": "ℹ️"
    }

    for page in pages:

        if st.button(
            f"{icons[page]}  {page}",
            key=f"nav_{page}",
            use_container_width=True
        ):

            st.session_state.page = page
            st.rerun()

    st.divider()

    st.caption("CIVIC TECHNOLOGY")
    st.caption("COMMUNITY • TRANSPARENCY • ACTION")


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

@st.cache_resource
def setup_database():
    initialize_database()
    return True


try:
    setup_database()
except Exception as error:
    st.error(f"Database initialization failed: {error}")
    st.stop()


# =========================================================
# LOAD DATABASE
# =========================================================

issues = load_issues()

total, pending, assigned, in_progress, resolved = calculate_metrics(issues)


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🏙️ City Operations Dashboard</h1>
        <p>A centralized view of community issues and civic activity.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 City Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🟢 TOTAL ISSUES", total)
    c2.metric("🟠 PENDING", pending)
    c3.metric("🔵 ASSIGNED", assigned)
    c4.metric("🟣 IN PROGRESS", in_progress)
    c5.metric("🟢 RESOLVED", resolved)

    st.divider()

    left, right = st.columns([1.4, 1])

    with left:

        st.subheader("🛰️ City Monitoring")

        st.info(
            "Monitor citizen-reported issues and civic service "
            "activity from a centralized platform."
        )

    with right:

        st.subheader("⚙️ System Status")

        st.success("Application Active")

        st.write("🗄️ Database connection")
        st.write("📡 Issue monitoring")
        st.write("👥 Citizen reporting system")

    st.divider()

    st.subheader("🧾 Recent Civic Issues")

    if issues:

        for issue in issues[:5]:
            display_issue(issue)

    else:

        st.info("No civic issues reported yet.")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()


# =========================================================
# REPORT ISSUE
# =========================================================

elif st.session_state.page == "Report Issue":

    st.markdown("""
    <div class="hero">
        <h1>📝 Report a Civic Issue</h1>
        <p>Help improve your community by reporting local problems.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("report_issue_form"):

        title = st.text_input(
            "Issue Title",
            placeholder="Example: Damaged road near bus stop"
        )

        category = st.selectbox(
            "Category",
            [
                "Roads",
                "Water",
                "Electricity",
                "Sanitation",
                "Public Spaces"
            ]
        )

        description = st.text_area(
            "Description",
            height=140,
            placeholder="Describe the issue in detail..."
        )

        col1, col2 = st.columns(2)

        with col1:

            severity = st.selectbox(
                "Severity",
                ["Low", "Medium", "High", "Critical"]
            )

        with col2:

            ward_zone = st.text_input("Ward / Zone")

        address = st.text_input(
            "Location / Address",
            placeholder="Enter issue location"
        )

        col1, col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude (optional)",
                value=0.0,
                format="%.6f"
            )

        with col2:

            longitude = st.number_input(
                "Longitude (optional)",
                value=0.0,
                format="%.6f"
            )

        submit = st.form_submit_button(
            "🚀 Submit Civic Report",
            use_container_width=True
        )

    if submit:

        if not title.strip():

            st.error("Please enter an issue title.")

        elif not description.strip():

            st.error("Please enter a description.")

        else:

            try:

                result = create_issue(
                    user_id=CURRENT_USER_ID,
                    title=title.strip(),
                    category=category,
                    description=description.strip(),
                    latitude=latitude if latitude != 0 else None,
                    longitude=longitude if longitude != 0 else None,
                    address=address.strip() or None,
                    ward_zone=ward_zone.strip() or None,
                    severity=severity
                )

                # Check the actual service result

                if isinstance(result, dict) and result.get("success"):

                    st.success(
                        "✅ Issue reported successfully!"
                    )

                    st.markdown(
                        f"### 🎫 Issue ID: #{result.get('issue_id', 'N/A')}"
                    )

                    st.markdown(
                        f"**Status:** {result.get('status', 'Pending Review')}"
                    )

                    st.balloons()

                elif isinstance(result, dict):

                    st.error(
                        result.get(
                            "message",
                            "Issue could not be submitted."
                        )
                    )

                else:

                    st.error(
                        "Unexpected response received while submitting the issue."
                    )

            except Exception as error:

                st.error(f"Unable to submit issue: {error}")


# =========================================================
# EXPLORE ISSUES
# =========================================================

elif st.session_state.page == "Explore Issues":

    st.markdown("""
    <div class="hero">
        <h1>🔎 Explore Civic Issues</h1>
        <p>Discover problems reported across your community.</p>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input(
        "Search",
        placeholder="Search title, description or location"
    )

    col1, col2 = st.columns(2)

    with col1:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Pending Review",
                "Assigned",
                "In Progress",
                "Resolved",
                "Reopened"
            ]
        )

    with col2:

        category_filter = st.selectbox(
            "Category",
            [
                "All",
                "Roads",
                "Water",
                "Electricity",
                "Sanitation",
                "Public Spaces"
            ]
        )

    filtered = []

    for issue in issues:

        title = str(get_value(issue, "title", ""))
        description = str(get_value(issue, "description", ""))
        address = str(get_value(issue, "address", ""))
        category = str(get_value(issue, "category", ""))
        status = str(get_value(issue, "status", ""))

        searchable = (
            f"{title} {description} {address} {category}"
        ).lower()

        search_match = (
            not search.strip()
            or search.lower() in searchable
        )

        status_match = (
            status_filter == "All"
            or status.lower() == status_filter.lower()
        )

        category_match = (
            category_filter == "All"
            or category.lower() == category_filter.lower()
        )

        if search_match and status_match and category_match:

            filtered.append(issue)

    st.markdown(f"### 📋 {len(filtered)} Issues Found")

    if filtered:

        for issue in filtered:
            display_issue(issue)

    else:

        st.info("No issues match your filters.")

    if st.button("🔄 Refresh Issues"):
        st.rerun()


# =========================================================
# TRACK COMPLAINTS
# =========================================================

elif st.session_state.page == "Track Complaints":

    st.markdown("""
    <div class="hero">
        <h1>📍 Track Your Complaint</h1>
        <p>Check the status of your complaint using the Issue ID.</p>
    </div>
    """, unsafe_allow_html=True)

    issue_id = st.number_input(
        "Enter Issue ID",
        min_value=1,
        step=1,
        value=1
    )

    if st.button("🔍 Track Issue", use_container_width=True):

        try:

            result = get_issue_by_id(int(issue_id))

            # get_issue_by_id returns a wrapper dictionary:
            # {
            #     "success": True,
            #     "issue": {...}
            # }

            if isinstance(result, dict) and result.get("success"):

                issue_data = result.get("issue", {})

                issue = normalize_issue(issue_data)

                st.success("Issue found!")

                display_issue(issue)

                status = str(
                    get_value(issue, "status", "Unknown")
                ).lower()

                if "pending" in status:

                    st.warning(
                        "⏳ Complaint awaiting review."
                    )

                elif "assign" in status:

                    st.info(
                        "👷 Complaint has been assigned."
                    )

                elif "progress" in status:

                    st.info(
                        "🔧 Work is in progress."
                    )

                elif any(
                    x in status
                    for x in [
                        "resolved",
                        "completed",
                        "closed"
                    ]
                ):

                    st.success(
                        "✅ Complaint resolved."
                    )

                else:

                    st.info(
                        f"Current status: {status}"
                    )

            elif isinstance(result, dict):

                st.error(
                    result.get(
                        "message",
                        "Issue not found. Check the Issue ID."
                    )
                )

            else:

                st.error(
                    "Issue not found. Check the Issue ID."
                )

        except Exception as error:

            st.error(f"Tracking failed: {error}")


# =========================================================
# ABOUT CIVICLENS
# =========================================================

elif st.session_state.page == "About CivicLens":

    st.markdown("""
    <div class="hero">
        <h1>ℹ️ About CivicLens</h1>
        <p>Technology for transparent, connected and responsive communities.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🌆 Our Mission")

    st.write("""
    CivicLens is a civic engagement platform designed to connect
    citizens with civic issue management.

    Citizens can report infrastructure problems, explore reported issues
    and monitor the progress of their complaints.
    """)

    st.subheader("🎯 Objectives")

    objectives = [
        "Simplify civic issue reporting",
        "Improve communication between citizens and authorities",
        "Provide transparent complaint tracking",
        "Support faster identification of civic problems",
        "Create a centralized civic issue management platform"
    ]

    for objective in objectives:

        st.markdown(f"✔️ {objective}")

    st.subheader("🛠️ Technology Stack")

    st.write("🐍 Python")
    st.write("🎨 Streamlit")
    st.write("🗄️ SQLite")
    st.write("🔗 SQLAlchemy")
    st.write("🔐 Authentication and password hashing")


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    CivicLens Smart City Platform<br>
    Building cleaner, safer and smarter communities.
</div>
""", unsafe_allow_html=True)
