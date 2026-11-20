# 🏙️ CivicLens
### Better Streets Begin With Us.

CivicLens is a community-powered civic issue reporting and tracking platform designed to make local problems visible and improve civic participation.

It provides a digital platform where citizens can report infrastructure and community issues, helping bring attention to problems and supporting a more organized approach to issue tracking.

---

## 🎯 Project Objective

To build a digital platform that connects citizens with local civic problems through issue reporting, categorization, location awareness, prioritization, and tracking.

---

## ✨ Key Features

- 📝 Civic issue reporting
- 📍 Location-based issue information
- 🗂️ Issue categorization
- 🚦 Issue severity analysis
- 🔄 Issue status workflow
- 👥 Role-based permissions
- 🔐 Secure user authentication
- 🔎 Duplicate issue detection
- 📊 Issue prioritization
- 🗺️ Location-related services

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **SQLite**
- **SQLAlchemy**
- **Machine Learning**
- **Git & GitHub**

---

## 📁 Project Structure

```text
CivicLens/
│
├── Backend/
│   ├── authentication.py
│   ├── permissions.py
│   ├── routes.py
│   └── workflow.py
│
├── database/
│   ├── connection.py
│   ├── init_db.py
│   └── models.py
│
├── docs/
│
├── ml/
│   ├── classifier.py
│   ├── duplication_detection.py
│   └── severity_analysis.py
│
├── services/
│
├── utils/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/sanjanashivakumar005-dot/CivicLens.git
```

### Navigate into the project

```bash
cd CivicLens
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

**Windows:**

```powershell
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Initialize the database

```bash
python database/init_db.py
```

### Run the application

```bash
streamlit run app.py
```

---

## 🌍 Vision

Building a more connected community where civic issues are visible, citizens can participate, and progress can be tracked.

> Your community. Your voice. Your impact.

---

## 👩‍💻 Project

**CivicLens — Community-Powered Civic Technology**

